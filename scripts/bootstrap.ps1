$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
$services = @('customer-portal','order-service','inventory-service','payment-service','shipping-service','notification-worker')
foreach ($service in $services) {
    $destination = Join-Path $projectRoot ('services/' + $service)
    if (-not (Test-Path -LiteralPath (Join-Path $destination 'Dockerfile'))) { throw "Missing service: $destination. Clone the complete CommerceLens repository." }
    Write-Output "Using bundled service: $destination"
}
Write-Output 'Services ready. From CommerceLens run: docker compose up --build -d'
