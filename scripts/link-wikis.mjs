// Uses the same registry API as `openwiki link` (tested with OpenWiki 0.7.2).
import path from 'node:path';
import fs from 'node:fs/promises';
import {fileURLToPath,pathToFileURL} from 'node:url';
const central=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const packageRoot=process.env.OPENWIKI_PACKAGE_ROOT || path.join(process.env.APPDATA,'npm/node_modules/openwiki');
const api=await import(pathToFileURL(path.join(packageRoot,'dist/linking/wiki-workspaces.js')));
// Generated locally by refresh-catalog.py from the selected service manifest.
const {roots}=JSON.parse(await fs.readFile(path.join(central,'catalog/workspace-roots.json'),'utf8'));
// OpenWiki 0.7.2 accepts independent Git roots only, not monorepo subfolders.
const nested=roots.filter(root=>path.resolve(root)!==central && path.resolve(root).startsWith(central+path.sep));
if(nested.length){
 console.error('OpenWiki 0.7.2 cannot register nested service wikis without independent Git roots. Use the master wiki links or CommerceLens retrieval; existing workspace registrations are unchanged.');
 process.exit(1);
}
for(const root of roots) await fs.access(path.join(root,'openwiki/quickstart.md'));
const drafts=api.workspaceDrafts(await api.readWikiWorkspaceRegistry());
const existing=drafts.find(d=>d.name.toLowerCase()==='commercelens');
if(existing)existing.roots=[...new Set(roots)];
else drafts.push({name:'CommerceLens',roots});
await api.saveWikiWorkspaces(drafts);
for(const root of roots)await api.setActiveWikiWorkspace(root,'CommerceLens');
console.log(JSON.stringify(await api.listWorkspaceWikis(roots[0],'CommerceLens'),null,2));
