# PowerShell script for scaling Docker services

param (
    [Parameter(Mandatory=$false)]
    [string]$Service = "",
    
    [Parameter(Mandatory=$false)]
    [int]$Instances = 0,
    
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
        
        # Get current scale
        $scale = (docker-compose ps $svc | Measure-Object).Count
        
        Write-Host "- $svc" -ForegroundColor $color -NoNewline
        Write-Host " ($state, instances: $scale)" -ForegroundColor $color
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
    
    Write-Host "Select a service to scale:" -ForegroundColor Cyan
    
    $index = 1
    $serviceMap = @{}
    
    foreach ($svc in $services) {
        if ($svc -eq "db" -or $svc -eq "nginx") {
            continue  # Skip database and nginx as they shouldn't be scaled
        }
        
        $status = docker-compose ps $svc --format json | ConvertFrom-Json
        $state = $status.State
        $color = if ($state -eq "running") { "Green" } else { "Red" }
        
        # Get current scale
        $scale = (docker-compose ps $svc | Measure-Object).Count
        
        Write-Host "$index." -ForegroundColor White -NoNewline
        Write-Host " $svc" -ForegroundColor $color -NoNewline
        Write-Host " ($state, current instances: $scale)" -ForegroundColor $color
        
        $serviceMap[$index] = $svc
        $index++
    }
    
    if ($index -eq 1) {
        Write-Host "No scalable services found." -ForegroundColor Yellow
        exit 0
    }
    
    $selection = Read-Host "\nEnter number (1-$($index-1))"
    
    if (-not $serviceMap.ContainsKey([int]$selection)) {
        Write-Host "Invalid selection!" -ForegroundColor Red
        exit 1
    }
    
    $Service = $serviceMap[[int]$selection]
}

# Check if service is valid for scaling
if ($Service -eq "db" -or $Service -eq "nginx") {
    Write-Host "Error: $Service should not be scaled. It could cause data inconsistency or routing issues." -ForegroundColor Red
    exit 1
}

# If no instance count specified, prompt user
if ($Instances -le 0) {
    # Get current scale
    $currentScale = (docker-compose ps $Service | Measure-Object).Count
    
    Write-Host "Current number of $Service instances: $currentScale" -ForegroundColor Cyan
    $Instances = Read-Host "Enter new number of instances (1-10)"
    
    if (-not [int]::TryParse($Instances, [ref]$null) -or [int]$Instances -lt 1 -or [int]$Instances -gt 10) {
        Write-Host "Invalid number of instances! Please enter a number between 1 and 10." -ForegroundColor Red
        exit 1
    }
}

# Scale the service
Write-Host "Scaling $Service to $Instances instance(s)..." -ForegroundColor Cyan

try {
    docker-compose up -d --scale "$Service=$Instances" --no-recreate
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Service $Service successfully scaled to $Instances instance(s)!" -ForegroundColor Green
        
        # Show the new container distribution
        Write-Host "\nCurrent $Service containers:" -ForegroundColor Cyan
        docker-compose ps $Service
    }
    else {
        Write-Host "Error scaling service!" -ForegroundColor Red
        exit 1
    }
}
catch {
    Write-Host "Error: $_" -ForegroundColor Red
    exit 1
}