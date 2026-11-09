# CommerceLens Graphify documentation

Generated locally on 2026-11-08 using Graphify 0.9.104 with its SQL extra. All seven repositories were processed independently, using `graphify extract . --code-only --force`, followed by `graphify cluster-only . --no-label` and `graphify export wiki`. No LLM calls or API keys were used; token cost is zero. These are structural Graphify wiki exports, not OpenWiki-generated documentation.

| Repository | Nodes | Edges | Scanned code/config files | Report | Interactive graph | Wiki |
| --- | ---: | ---: | ---: | --- | --- | --- |
| CommerceLens | 160 | 191 | 7 | [Report](../graphify-out/GRAPH_REPORT.md) | [HTML](../graphify-out/graph.html) | [Wiki](../graphify-out/wiki/index.md) |
| Customer Portal | 65 | 98 | 7 | [Report](https://github.com/nagv/commercelens-customer-portal/blob/main/graphify-out/GRAPH_REPORT.md) | [HTML](https://github.com/nagv/commercelens-customer-portal/blob/main/graphify-out/graph.html) | [Wiki](https://github.com/nagv/commercelens-customer-portal/blob/main/graphify-out/wiki/index.md) |
| Order Service | 136 | 275 | 10 | [Report](https://github.com/nagv/commercelens-order-service/blob/main/graphify-out/GRAPH_REPORT.md) | [HTML](https://github.com/nagv/commercelens-order-service/blob/main/graphify-out/graph.html) | [Wiki](https://github.com/nagv/commercelens-order-service/blob/main/graphify-out/wiki/index.md) |
| Inventory Service | 47 | 73 | 4 | [Report](https://github.com/nagv/commercelens-inventory-service/blob/main/graphify-out/GRAPH_REPORT.md) | [HTML](https://github.com/nagv/commercelens-inventory-service/blob/main/graphify-out/graph.html) | [Wiki](https://github.com/nagv/commercelens-inventory-service/blob/main/graphify-out/wiki/index.md) |
| Payment Service | 29 | 38 | 2 | [Report](https://github.com/nagv/commercelens-payment-service/blob/main/graphify-out/GRAPH_REPORT.md) | [HTML](https://github.com/nagv/commercelens-payment-service/blob/main/graphify-out/graph.html) | [Wiki](https://github.com/nagv/commercelens-payment-service/blob/main/graphify-out/wiki/index.md) |
| Shipping Service | 40 | 69 | 4 | [Report](https://github.com/nagv/commercelens-shipping-service/blob/main/graphify-out/GRAPH_REPORT.md) | [HTML](https://github.com/nagv/commercelens-shipping-service/blob/main/graphify-out/graph.html) | [Wiki](https://github.com/nagv/commercelens-shipping-service/blob/main/graphify-out/wiki/index.md) |
| Notification Worker | 54 | 75 | 7 | [Report](https://github.com/nagv/commercelens-notification-worker/blob/main/graphify-out/GRAPH_REPORT.md) | [HTML](https://github.com/nagv/commercelens-notification-worker/blob/main/graphify-out/graph.html) | [Wiki](https://github.com/nagv/commercelens-notification-worker/blob/main/graphify-out/wiki/index.md) |

Total: **531 nodes, 819 edges, 41 scanned files**. Each graph's JSON parsed successfully, every edge endpoint references an existing node, required report/HTML/wiki files are nonempty, and source paths do not include dependency or build directories. Links assume the repositories remain sibling directories locally.

## Coverage limits

- Code-only extraction skips prose documents and semantic interpretation. It does not prove complete runtime dependencies between services or inspect live databases.
- The SQL parser was installed and Order Service extraction rerun to include `src/main/resources/schema.sql`. Embedded SQL strings in Go/TypeScript are not equivalent to live schema extraction.
- Graphify reported no extracted symbols for central `scripts/bootstrap.ps1` and `scripts/graphify.ps1`, portal `vite.config.ts`, orders `pom.xml`, inventory `go.mod`, and notification `test/delivery.test.ts` and `test/lifecycle.test.ts`. File nodes can still exist for these; file presence is not proof of symbol coverage.
- Dockerfiles, `.properties`, and some other extensions were not classified. Compose YAML is represented structurally, not as a fully resolved deployment dependency model.
- Communities retain numbered names because LLM naming was disabled. Reports show cohesion values and zero model token usage.
- Graphs describe the working-tree snapshot, including the new refresh script. `built_at_commit` records the repository HEAD, not a guarantee that all scanned files were committed.
- Source `lib` and `pages` directories are not globally excluded. Generated output, vendor/dependency directories, caches, build directories, and the local Graphify environment are excluded.

## Regenerate

From CommerceLens in PowerShell:

```powershell
# One-time installation (already installed in this checkout)
uv venv .graphify-venv --python 3.12
uv pip install --python .graphify-venv/Scripts/python.exe "graphifyy[sql]==0.9.104"

# Rebuild all seven local graphs, reports, HTML views, and Graphify wikis
./scripts/graphify.ps1
```

Logs are stored in each repository as `graphify-extract.log`, `graphify-report.log`, and `graphify-wiki.log`. Machine-readable graphs and extraction manifests are in `graphify-out/`. Open `graph.html` in a browser. Run OpenWiki only after this Graphify step, as planned.
