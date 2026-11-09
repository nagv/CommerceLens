"""Documentation-only, deterministic corpus and relationship construction."""
import hashlib
import json
import re
import subprocess
from collections import deque
from pathlib import Path

import yaml


def _hash(text):
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def _manifest(root, path):
    path = Path(path) if path else root / 'services.example.yaml'
    if not path.is_absolute(): path = root / path
    value = yaml.safe_load(path.read_text(encoding='utf-8'))
    ids = [s['id'] for s in value['services']]
    if len(ids) != len(set(ids)): raise ValueError('Duplicate service IDs')
    return value, path.parent


def _body(text):
    text = text.replace('\r\n', '\n')
    text = re.sub(r'\A---\n.*?\n---\s*\n', '', text, flags=re.S)
    return re.sub(r'^\[Master entry point\].*$', '', text, flags=re.M).strip()


def _repository_url(repo, configured=''):
    value=configured
    if not value:
        result=subprocess.run(['git','-C',str(repo),'config','--get','remote.origin.url'],capture_output=True,text=True,check=False)
        value=result.stdout.strip() if result.returncode==0 else ''
    value=re.sub(r'^git@([^:]+):',r'https://\1/',value)
    value=re.sub(r'^ssh://git@', 'https://',value).removesuffix('.git').rstrip('/')
    return value if value.startswith('https://') else ''


def _sections(text, limit=5000):
    """Retain heading ancestry; split oversized sections on paragraph boundaries."""
    headings=[]; lines=[]; sections=[]; fenced=False
    def flush():
        body='\n'.join(lines).strip()
        if body: sections.append((' > '.join(headings), body))
    for line in text.splitlines():
        if line.lstrip().startswith('```'): fenced=not fenced
        match=re.match(r'^(#{1,6})\s+(.+)',line) if not fenced else None
        if match:
            flush(); lines=[]; depth=len(match[1])
            headings=headings[:depth-1]+[match[2]]
        else: lines.append(line)
    flush()
    for topic, body in sections:
        if re.search(r'related documentation|navigation|table of contents',topic,re.I): continue
        prefix=topic+'\n\n' if topic else ''
        budget=max(256,limit-len(prefix))
        while body:
            end=min(len(body),budget)
            if end<len(body):
                split=body.rfind('\n',0,end)
                if split>budget//2: end=split
            yield topic,prefix+body[:end].strip()
            body=body[end:].strip()


def build_corpus(root: Path, manifest_path: Path | None = None) -> list[dict]:
    root=Path(root).resolve(); manifest,base=_manifest(root,manifest_path)
    app=manifest['application']['id']; sources=[(root,'','master',_repository_url(root,manifest['application'].get('repository','')))]
    sources += [((base/s['path']).resolve(),s['id'],'service',_repository_url((base/s['path']).resolve(),s.get('repository',''))) for s in manifest['services']]
    chunks=[]; seen=set()
    for repo,sid,level,url in sources:
        wiki=repo/'openwiki'
        label=sid or 'master'
        if not wiki.is_dir(): raise ValueError(f'{label}: configured wiki missing: {wiki}')
        start_count=len(chunks)
        for path in sorted(wiki.rglob('*.md')):
            if path.name.lower() in {'index.md','instructions.md','agents.md','quickstart.md','readme.md'}: continue
            # Never follow links or symlinks out of the documentation directory.
            if not path.resolve().is_relative_to(wiki.resolve()): continue
            body=_body(path.read_text(encoding='utf-8')); version=_hash(body)
            rel=path.relative_to(repo).as_posix()
            for number,(topic,text) in enumerate(_sections(body)):
                digest=_hash(text)
                if (sid,digest) in seen: continue
                seen.add((sid,digest))
                metadata={'application_id':app,'service_id':sid,'level':level,'topic':topic,
                          'source_path':rel,'source_url':url+'/blob/main/'+rel if url else '',
                          'source_version':version,'content_hash':digest,'chunk_index':number}
                identifier=_hash('|'.join([app,sid,rel,version,str(number)]))
                chunks.append({'id':identifier,'text':text,'metadata':metadata})
        if len(chunks)==start_count: raise ValueError(f'{label}: wiki has no substantive documentation: {wiki}')
    return chunks


def _normalize(value):
    return re.sub(r'[\s_]+','-',value.strip().lower())


def build_relationships(root: Path, manifest_path: Path | None = None) -> dict:
    root=Path(root).resolve(); manifest,base=_manifest(root,manifest_path)
    aliases={}; nodes={}; edges=[]; warnings=[]
    for service in manifest['services']:
        sid=service['id']; nodes[sid]={'id':sid,'name':sid,'type':'service','aliases':service.get('aliases',[])}
        for alias in [sid,*service.get('aliases',[])]:
            key=_normalize(alias)
            if key in aliases and aliases[key]!=sid: raise ValueError('Ambiguous service alias: '+alias)
            aliases[key]=sid
    for service in manifest['services']:
        sid=service['id']; card_path=root/'catalog/service-cards'/f'{sid}.json'
        if not card_path.exists():
            warnings.append('Missing service card: '+sid); continue
        card=json.loads(card_path.read_text(encoding='utf-8'))
        repository=_repository_url((base/service['path']).resolve(),card.get('repository') or service.get('repository',''))
        for dep in card.get('summary',{}).get('dependencies',[]):
            raw=dep['target']; target=aliases.get(_normalize(raw),raw)
            kind=dep['kind']; purpose=dep.get('interface',''); evidence=dep.get('evidence','')
            raw_kind=kind
            if kind=='consumes' and re.search(r'\bHTTP\b|\b(?:GET|POST|PUT|DELETE)\s+/',purpose,re.I):
                kind='http'
            if target not in nodes:
                nodes[target]={'id':target,'name':raw,'type':'external'}
                warnings.append(f'{sid}: unregistered target {raw}')
            if kind in {'publishes','consumes'}:
                # The first explicit queue is the active channel; DLX/DLQ mentions
                # describe a separate failure route, never a consumer subscription.
                explicit=re.findall(r'\b(?:queue|topic)\s+[`\"\']?([a-zA-Z][\w.-]*)',purpose,re.I)
                explicit += re.findall(r'[`\"\']?([a-zA-Z][\w.-]*)[`\"\']?\s+(?:queue|topic)\b',purpose,re.I)
                matches=explicit or re.findall(r'\b[a-zA-Z][\w-]*(?:\.[\w-]+)+\b',purpose)
                queue=next((q for q in matches if not q.endswith(('.dead','.dlq'))),None)
                if queue:
                    target='queue:'+queue
                    nodes[target]={'id':target,'name':queue,'type':'queue','broker':raw}
                else: warnings.append(f'{sid}: no exact queue documented for {kind} {raw}')
            source,dest=(target,sid) if kind=='consumes' else (sid,target)
            edges.append({'from':source,'to':dest,'type':kind,'purpose':purpose,
                          'evidence':evidence,'evidence_service':sid,'raw_target':raw,'raw_kind':raw_kind,
                          'evidence_url':repository+'/blob/main/'+evidence if repository else '',
                          'evidence_version':card.get('page_hashes',{}).get(evidence,'')})
    edges.sort(key=lambda e:(e['from'],e['to'],e['type'],e['purpose']))
    result={'schema_version':1,'application_id':manifest['application']['id'],
            'nodes':sorted(nodes.values(),key=lambda n:n['id']),'edges':edges,'warnings':sorted(set(warnings))}
    result['version']=_hash(json.dumps(result,sort_keys=True))
    return result


def get_dependencies(graph, service_id, direction='both', max_hops=1):
    if direction not in {'both','inbound','outbound'}: raise ValueError('Invalid dependency direction')
    if not isinstance(max_hops,int) or not 0<=max_hops<=8: raise ValueError('max_hops must be between 0 and 8')
    nodes={n['id']:n for n in graph['nodes']}
    if service_id not in nodes: return {'services':[],'edges':[]}
    distance={service_id:0}; pending=deque([service_id]); selected={}; services=set()
    while pending:
        current=pending.popleft(); depth=distance[current]
        if depth>=max_hops: continue
        for i,edge in enumerate(graph['edges']):
            next_id=None
            if direction!='inbound' and edge['from']==current: next_id=edge['to']
            elif direction!='outbound' and edge['to']==current: next_id=edge['from']
            if next_id is None: continue
            selected[i]=edge
            is_queue=nodes.get(next_id,{}).get('type')=='queue'
            cost=0 if is_queue else 1
            new_depth=depth+cost
            if nodes.get(next_id,{}).get('type')=='service' and next_id!=service_id: services.add(next_id)
            # Only service and queue nodes are traversal conduits. Shared databases
            # and broker names do not imply a relationship between services.
            if nodes.get(next_id,{}).get('type') not in {'service','queue'}: continue
            if new_depth<distance.get(next_id,999):
                distance[next_id]=new_depth; pending.append(next_id)
    return {'services':sorted(services),'edges':[selected[i] for i in sorted(selected)]}
