# PowerShell script for checking health of Docker containers

# Check if Docker is running
try {
    docker info | Out-Null
}
catch {
    Write-Host "Error: Docker is not running or not accessible!" -ForegroundColor Red
    exit 1
}

# Get container status
Write-Host "Checking container health status..." -ForegroundColor Cyan
$containers = docker-compose ps --format json | ConvertFrom-Json

if (-not $containers) {
    Write-Host "No containers found. Is the application deployed?" -ForegroundColor Yellow
    exit 0
}

# Display container health information
Write-Host "\nContainer Health Status:" -ForegroundColor Cyan
Write-Host "======================" -ForegroundColor Cyan

$allHealthy = $true

foreach ($container in $containers) {
    $name = $container.Name
    $state = $container.State
    $status = $container.Status
    $health = $container.Health
    
    # Set color based on state
    $color = "White"
    if ($state -eq "running") {
        if ($health -eq "healthy") {
            $color = "Green"
        }
        elseif ($health -eq "starting") {
            $color = "Yellow"
            $allHealthy = $false
        }
        elseif ($health -eq "unhealthy") {
            $color = "Red"
            $allHealthy = $false
        }
        else {
            $color = "Cyan" # Running but no health check
        }
    }
    else {
        $color = "Red"
        $allHealthy = $false
    }
    
    # Display container info
    Write-Host "$name:" -ForegroundColor $color -NoNewline
    Write-Host " $state" -ForegroundColor $color
    
    # Display additional health info if available
    if ($health) {
        Write-Host "  Health: $health" -ForegroundColor $color
    }
    
    Write-Host "  Status: $status" -ForegroundColor $color
    
    # Get container logs if unhealthy
    if ($health -eq "unhealthy") {
        Write-Host "\n  Recent logs:" -ForegroundColor Yellow
        docker logs --tail 10 $name
        Write-Host ""
    }
}

# Check backend health endpoint
Write-Host "\nChecking API health endpoint..." -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/api/health/" -Method GET -TimeoutSec 5 -ErrorAction SilentlyContinue
    
    if ($response.StatusCode -eq 200) {
        Write-Host "API Health Check: OK (Status 200)" -ForegroundColor Green
        try {
            $content = $response.Content | ConvertFrom-Json
            Write-Host "  Status: $($content.status)" -ForegroundColor Green
            Write-Host "  Database: $($content.database)" -ForegroundColor Green
            if ($content.version) {
                Write-Host "  Version: $($content.version)" -ForegroundColor Green
            }
        }
        catch {
            Write-Host "  Unable to parse response content" -ForegroundColor Yellow
        }
    }
    else {
        Write-Host "API Health Check: Failed (Status $($response.StatusCode))" -ForegroundColor Red
        $allHealthy = $false
    }
}
catch {
    Write-Host "API Health Check: Failed (Connection Error)" -ForegroundColor Red
    Write-Host "  Error: $_" -ForegroundColor Red
    $allHealthy = $false
}

# Check Nginx status
Write-Host "\nChecking Nginx status..." -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri "http://localhost/health" -Method GET -TimeoutSec 5 -ErrorAction SilentlyContinue
    
    if ($response.StatusCode -eq 200) {
        Write-Host "Nginx Health Check: OK (Status 200)" -ForegroundColor Green
    }
    else {
        Write-Host "Nginx Health Check: Failed (Status $($response.StatusCode))" -ForegroundColor Red
        $allHealthy = $false
    }
}
catch {
    Write-Host "Nginx Health Check: Failed (Connection Error)" -ForegroundColor Red
    Write-Host "  Error: $_" -ForegroundColor Red
    $allHealthy = $false
}

# Overall status
Write-Host "\nOverall System Health:" -ForegroundColor Cyan
if ($allHealthy) {
    Write-Host "All systems operational" -ForegroundColor Green
}
else {
    Write-Host "One or more systems are experiencing issues" -ForegroundColor Red
}