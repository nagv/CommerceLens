"""Capture explicit, reviewed source inputs; this does not infer relationships."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
JAVA = 'src/main/java/com/commercelens/orders/'
INPUTS = {
    'customer-portal': ['nginx.conf', 'src/api.ts', 'src/main.tsx'],
    'order-service': [JAVA + f + '.java' for f in ['RemoteServices', 'OrderStore', 'OutboxPublisher', 'Checkout', 'OrderController']] + ['src/main/resources/schema.sql', 'src/main/resources/application.properties'],
    'inventory-service': ['main.go'],
    'payment-service': ['app.py'],
    'shipping-service': ['Program.cs'],
    'notification-worker': ['src/main.ts', 'src/delivery.ts', 'src/lifecycle.ts'],
}

def snapshot(check=False):
    records = []
    for service, files in INPUTS.items():
        repo = ROOT.parent / ('commercelens-' + service)
        commit = subprocess.check_output(['git', '-C', str(repo), 'rev-parse', 'HEAD'], text=True).strip()
        for filename in files:
            content = (repo / filename).read_text(encoding='utf-8').replace('\r\n', '\n')
            committed = subprocess.check_output(['git', '-C', str(repo), 'show', f'{commit}:{filename}']).decode('utf-8').replace('\r\n', '\n')
            if content != committed:
                raise SystemExit(f'Commit source changes before snapshotting: {repo.name}/{filename}')
            records.append(dict(service=service, repository=f'https://github.com/nagv/{repo.name}', commit=commit,
                                path=filename, sha256=hashlib.sha256(content.encode()).hexdigest(),
                                url=f'https://github.com/nagv/{repo.name}/blob/{commit}/{filename}', content=content))
    target = ROOT / 'catalog/source-evidence.json'
    if check:
        old = json.loads(target.read_text())['sources']
        before = {(x['service'], x['path']): x['sha256'] for x in old}
        after = {(x['service'], x['path']): x['sha256'] for x in records}
        if before != after:
            raise SystemExit('Catalog source changed: review relationships and pages, then refresh evidence.')
        print(f'Catalog evidence current: {len(records)} source files')
        return
    target.parent.mkdir(exist_ok=True)
    target.write_text(json.dumps({'schema_version': 1, 'purpose': 'Reviewed source snapshot for central OpenWiki grounding; not an automatic dependency detector.', 'sources': records}, indent=2) + '\n', encoding='utf-8')
    print(f'Captured {len(records)} source files. Review catalog pages before finalizing OpenWiki.')

if __name__ == '__main__':
    import sys
    snapshot('--check' in sys.argv)
