param([string[]]$Repositories = @(
    'CommerceLens', 'commercelens-customer-portal', 'commercelens-order-service',
    'commercelens-inventory-service', 'commercelens-payment-service',
    'commercelens-shipping-service', 'commercelens-notification-worker'
))
$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
$workspaceRoot = Split-Path -Parent $projectRoot
$graphifyCommand = Join-Path $projectRoot '.graphify-venv/Scripts/graphify.exe'
if (-not (Test-Path -LiteralPath $graphifyCommand)) {
    throw 'Install first: uv venv .graphify-venv --python 3.12; uv pip install --python .graphify-venv/Scripts/python.exe "graphifyy[sql]==0.9.104" (from CommerceLens)'
}
foreach ($repository in $Repositories) {
    if ($repository -notmatch '^(CommerceLens|commercelens-(customer-portal|order-service|inventory-service|payment-service|shipping-service|notification-worker))$') {
        throw "Unknown repository: $repository"
    }
    Push-Location (Join-Path $workspaceRoot $repository)
    try {
        & $graphifyCommand extract . --code-only --force *> graphify-extract.log
        if ($LASTEXITCODE -ne 0) { throw "Extraction failed for $repository; see graphify-extract.log" }
        # No LLM naming: retain deterministic numbered communities.
        & $graphifyCommand cluster-only . --no-label *> graphify-report.log
        if ($LASTEXITCODE -ne 0) { throw "Report failed for $repository; see graphify-report.log" }
        & $graphifyCommand export wiki *> graphify-wiki.log
        if ($LASTEXITCODE -ne 0) { throw "Wiki export failed for $repository; see graphify-wiki.log" }
        foreach ($artifact in @('graph.json','GRAPH_REPORT.md','graph.html')) {
            if (-not (Test-Path -LiteralPath (Join-Path 'graphify-out' $artifact))) { throw "Missing $repository/$artifact" }
        }
        Write-Output "$repository : graph, report, HTML and Graphify wiki generated (no LLM)"
    } finally { Pop-Location }
}
