$ErrorActionPreference = 'Stop'
$workspace = Split-Path -Parent $PSScriptRoot
$parent = Split-Path -Parent $workspace
$services = @('customer-portal', 'order-service', 'inventory-service', 'payment-service', 'shipping-service', 'notification-worker')
foreach ($service in $services) {
    $repo = 'commercelens-' + $service
    $destination = Join-Path $parent $repo
    if (-not (Test-Path -LiteralPath $destination)) {
        git clone ('https://github.com/nagv/' + $repo + '.git') $destination
        if ($LASTEXITCODE -ne 0) { throw "Failed to clone $repo" }
    } else {
        Write-Host "Using existing checkout: $destination"
    }
}
Write-Host 'Repositories ready. From CommerceLens run: docker compose up --build -d'
