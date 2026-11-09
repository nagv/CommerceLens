// Uses the same registry API as `openwiki link` (tested with OpenWiki 0.7.2).
import path from 'node:path';
import fs from 'node:fs/promises';
import {fileURLToPath,pathToFileURL} from 'node:url';
const central=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const packageRoot=process.env.OPENWIKI_PACKAGE_ROOT || path.join(process.env.APPDATA,'npm/node_modules/openwiki');
const api=await import(pathToFileURL(path.join(packageRoot,'dist/linking/wiki-workspaces.js')));
const services=['customer-portal','order-service','inventory-service','payment-service','shipping-service','notification-worker'];
const roots=services.map(name=>path.resolve(central,'../commercelens-'+name));
try {await fs.access(path.join(central,'openwiki/.last-update.json')); roots.push(central);} catch {}
for(const root of roots) await fs.access(path.join(root,'openwiki/quickstart.md'));
const drafts=api.workspaceDrafts(await api.readWikiWorkspaceRegistry());
const existing=drafts.find(d=>d.name.toLowerCase()==='commercelens');
if(existing)existing.roots=[...new Set([...existing.roots,...roots])];
else drafts.push({name:'CommerceLens',roots});
await api.saveWikiWorkspaces(drafts);
for(const root of roots)await api.setActiveWikiWorkspace(root,'CommerceLens');
console.log(JSON.stringify(await api.listWorkspaceWikis(roots[0],'CommerceLens'),null,2));
