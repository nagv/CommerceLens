// Finalize human/host-reviewed pages using OpenWiki 0.7.2 lifecycle gates.
// This does not generate or independently fact-check prose.
import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const pkg=process.env.OPENWIKI_PACKAGE_ROOT||path.join(process.env.APPDATA,'npm/node_modules/openwiki');
const api=await import(pathToFileURL(path.join(pkg,'dist/generation/repository-run.js')));
const statements=JSON.parse(await fs.readFile(path.join(root,'catalog/page-claims.json'),'utf8'));
const {run,view}=await api.beginRepositoryRun({root,mode:'update',force:true,actor:{producerActor:'codex/openwiki-lifecycle-review',metadataModel:'codex-host-review'}});
if(view.status==='noop')process.exit(0);
if(run.state.phase==='planning')await api.submitRepositoryPlan(run,{pages:Object.keys(statements).map(name=>({path:'/openwiki/'+name,title:name.replace('.md',''),purpose:'Reviewed application-wide catalog with source provenance',seedPaths:['catalog/source-evidence.json','compose.yaml']})),deletePages:[]});
while(true){
 const next=await api.nextRepositoryPage(run);
 if(next.status==='complete')break;
 if(next.job.claimsRequiringAttention.length)throw new Error('Review stale claims before finalizing: '+next.job.path);
 const entries=statements[path.basename(next.job.path)];
 await api.submitRepositoryPage(run,{jobId:next.job.id,...(next.job.existingClaimCount?{}:{claims:entries.map(statement=>({statement,evidence:[{resource:'repo://catalog/source-evidence.json'},{resource:'repo://compose.yaml'}]}))})});
}
console.log(await api.finishRepositoryRun(run));
