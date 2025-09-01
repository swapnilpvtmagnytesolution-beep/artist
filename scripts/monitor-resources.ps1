# PowerShell script for monitoring Docker container resources

param (
    [Parameter(Mandatory=$false)]
    [int]$RefreshInterval = 5,
    
    [Parameter(Mandatory=$false)]
    [switch]$IncludeVolumes = $false
)

# Check if Docker is running
try {
    docker info | Out-Null
}
catch {
    Write-Host "Error: Docker is not running or not accessible!" -ForegroundColor Red
    exit 1
}

# Function to clear the console and display header
function Show-Header {
    Clear-Host
    Write-Host "=== Eddits Docker Container Monitor ===" -ForegroundColor Cyan
    Write-Host "Refresh interval: $RefreshInterval seconds" -ForegroundColor DarkGray
    Write-Host "Press Ctrl+C to exit" -ForegroundColor Yellow
    Write-Host "Updated: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor DarkGray
    Write-Host "=======================================" -ForegroundColor Cyan
}

# Function to display container stats
function Show-ContainerStats {
    $stats = docker stats --no-stream --format "{{.Name}}|{{.CPUPerc}}|{{.MemUsage}}|{{.MemPerc}}|{{.NetIO}}|{{.BlockIO}}|{{.PIDs}}"
    
    if (-not $stats) {
        Write-Host "No containers running." -ForegroundColor Yellow
        return
    }
    
    $containerStats = @()
    
    foreach ($line in $stats) {
        $parts = $line -split '\|'
        if ($parts.Count -ge 7) {
            $containerStats += [PSCustomObject]@{
                Name = $parts[0]
                CPU = $parts[1]
                Memory = $parts[2]
                MemPerc = $parts[3]
                Network = $parts[4]
                DiskIO = $parts[5]
                Processes = $parts[6]
            }
        }
    }
    
    # Display container stats
    Write-Host "\nCONTAINER RESOURCES:" -ForegroundColor Green
    $containerStats | Format-Table -Property @{
        Label = "CONTAINER"
        Expression = {$_.Name}
        Width = 25
    }, @{
        Label = "CPU"
        Expression = {$_.CPU}
        Width = 10
    }, @{
        Label = "MEMORY"
        Expression = {$_.Memory}
        Width = 20
    }, @{
        Label = "MEM %"
        Expression = {$_.MemPerc}
        Width = 10
    }, @{
        Label = "NETWORK I/O"
        Expression = {$_.Network}
        Width = 20
    }, @{
        Label = "DISK I/O"
        Expression = {$_.DiskIO}
        Width = 20
    }, @{
        Label = "PROCS"
        Expression = {$_.Processes}
        Width = 8
    }
}

# Function to display volume information
function Show-VolumeInfo {
    if (-not $IncludeVolumes) {
        return
    }
    
    $volumes = docker volume ls --format "{{.Name}}|{{.Driver}}|{{.Mountpoint}}"
    
    if (-not $volumes) {
        Write-Host "\nNo volumes found." -ForegroundColor Yellow
        return
    }
    
    $volumeInfo = @()
    
    foreach ($line in $volumes) {
        $parts = $line -split '\|'
        if ($parts.Count -ge 3) {
            $volumeInfo += [PSCustomObject]@{
                Name = $parts[0]
                Driver = $parts[1]
                Mountpoint = $parts[2]
            }
        }
    }
    
    # Display volume info
    Write-Host "\nVOLUME INFORMATION:" -ForegroundColor Green
    $volumeInfo | Format-Table -Property @{
        Label = "VOLUME"
        Expression = {$_.Name}
        Width = 40
    }, @{
        Label = "DRIVER"
        Expression = {$_.Driver}
        Width = 15
    }, @{
        Label = "MOUNTPOINT"
        Expression = {$_.Mountpoint}
        Width = 60
    }
}

# Function to display system-wide Docker info
function Show-SystemInfo {
    # Get Docker system info
    $info = docker system df --format json | ConvertFrom-Json
    
    Write-Host "\nSYSTEM OVERVIEW:" -ForegroundColor Green
    
    # Images
    $images = $info.Images
    Write-Host "Images:" -ForegroundColor Cyan
    Write-Host "  Total: $($images.TotalCount)" -ForegroundColor White
    Write-Host "  Size: $($images.Size)" -ForegroundColor White
    Write-Host "  Reclaimable: $($images.Reclaimable)" -ForegroundColor White
    
    # Containers
    $containers = $info.Containers
    Write-Host "Containers:" -ForegroundColor Cyan
    Write-Host "  Total: $($containers.TotalCount)" -ForegroundColor White
    Write-Host "  Size: $($containers.Size)" -ForegroundColor White
    Write-Host "  Reclaimable: $($containers.Reclaimable)" -ForegroundColor White
    
    # Volumes
    $volumes = $info.Volumes
    Write-Host "Volumes:" -ForegroundColor Cyan
    Write-Host "  Total: $($volumes.TotalCount)" -ForegroundColor White
    Write-Host "  Size: $($volumes.Size)" -ForegroundColor White
    Write-Host "  Reclaimable: $($volumes.Reclaimable)" -ForegroundColor White
    
    # Build Cache
    $buildCache = $info.BuildCache
    Write-Host "Build Cache:" -ForegroundColor Cyan
    Write-Host "  Total: $($buildCache.TotalCount)" -ForegroundColor White
    Write-Host "  Size: $($buildCache.Size)" -ForegroundColor White
    Write-Host "  Reclaimable: $($buildCache.Reclaimable)" -ForegroundColor White
}

# Main monitoring loop
try {
    while ($true) {
        Show-Header
        Show-ContainerStats
        Show-SystemInfo
        Show-VolumeInfo
        
        Start-Sleep -Seconds $RefreshInterval
    }
}
catch {
    Write-Host "\nMonitoring stopped: $_" -ForegroundColor Red
}
finally {
    Write-Host "\nExiting monitor..." -ForegroundColor Yellow
}