param(
    [Parameter(Mandatory=$true)]
    [int]$Port
)

Write-Host "Stopping service on port $Port..." -ForegroundColor Yellow

try {
    $process = Get-NetTCPConnection -LocalPort $Port -ErrorAction Stop |
                Select-Object -First 1 -ExpandProperty OwningProcess

    Stop-Process -Id $process -Force
    Write-Host "Service stopped (Port $Port)" -ForegroundColor Green
} catch {
    Write-Host "No service running on port $Port" -ForegroundColor Red
}
