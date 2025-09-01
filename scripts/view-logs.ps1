# PowerShell script for viewing Docker container logs

param (
    [Parameter(Mandatory=$false)]
    [string]$Service = "",
    
    [Parameter(Mandatory=$false)]
    [int]$Lines = 100,
    
    [Parameter(Mandatory=$false)]
    [switch]$Follow = $false,
    
    [Parameter(Mandatory=$false)]
    [switch]$ListServices = $false
)

# Check if Docker is running
try {
    docker info | Out-Null
}
catch {
    Write-Host "Error: Docker is not running or not accessible!" -ForegroundColor Red
    exit 1
}

# List available services if requested
if ($ListServices) {
    Write-Host "Available services:" -ForegroundColor Cyan
    $services = docker-compose ps --services
    
    if (-not $services) {
        Write-Host "No services found. Is the application deployed?" -ForegroundColor Yellow
        exit 0
    }
    
    foreach ($svc in $services) {
        $status = docker-compose ps $svc --format json | ConvertFrom-Json
        $state = $status.State
        $color = if ($state -eq "running") { "Green" } else { "Red" }
        
        Write-Host "- $svc" -ForegroundColor $color -NoNewline
        Write-Host " ($state)" -ForegroundColor $color
    }
    
    exit 0
}

# If no service specified, prompt user to select one
if (-not $Service) {
    $services = docker-compose ps --services
    
    if (-not $services) {
        Write-Host "No services found. Is the application deployed?" -ForegroundColor Yellow
        exit 0
    }
    
    Write-Host "Select a service to view logs:" -ForegroundColor Cyan
    
    $index = 1
    $serviceMap = @{}
    
    foreach ($svc in $services) {
        $status = docker-compose ps $svc --format json | ConvertFrom-Json
        $state = $status.State
        $color = if ($state -eq "running") { "Green" } else { "Red" }
        
        Write-Host "$index." -ForegroundColor White -NoNewline
        Write-Host " $svc" -ForegroundColor $color -NoNewline
        Write-Host " ($state)" -ForegroundColor $color
        
        $serviceMap[$index] = $svc
        $index++
    }
    
    $selection = Read-Host "\nEnter number (1-$($index-1))"
    
    if (-not $serviceMap.ContainsKey([int]$selection)) {
        Write-Host "Invalid selection!" -ForegroundColor Red
        exit 1
    }
    
    $Service = $serviceMap[[int]$selection]
}

# Build the log command
$logCommand = "docker-compose logs --timestamps"

if ($Lines -gt 0) {
    $logCommand += " --tail=$Lines"
}

if ($Follow) {
    $logCommand += " --follow"
}

$logCommand += " $Service"

# Display log header
Write-Host "\nViewing logs for $Service" -ForegroundColor Cyan
Write-Host "Command: $logCommand" -ForegroundColor DarkGray
Write-Host "Press Ctrl+C to exit if following logs\n" -ForegroundColor Yellow

# Execute the log command
Invoke-Expression $logCommand