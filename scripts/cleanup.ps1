# PowerShell script for cleaning up Docker resources

param (
    [Parameter(Mandatory=$false)]
    [switch]$Prune = $false,
    
    [Parameter(Mandatory=$false)]
    [switch]$PruneVolumes = $false,
    
    [Parameter(Mandatory=$false)]
    [switch]$RemoveUnused = $false,
    
    [Parameter(Mandatory=$false)]
    [switch]$Force = $false
)

# Check if Docker is running
try {
    docker info | Out-Null
}
catch {
    Write-Host "Error: Docker is not running or not accessible!" -ForegroundColor Red
    exit 1
}

# Display current Docker disk usage
Write-Host "Current Docker disk usage:" -ForegroundColor Cyan
docker system df

# If no specific options are provided, show menu
if (-not ($Prune -or $PruneVolumes -or $RemoveUnused)) {
    Write-Host "\nSelect cleanup option:" -ForegroundColor Cyan
    Write-Host "1. Prune containers, networks, and dangling images" -ForegroundColor Yellow
    Write-Host "2. Prune volumes (WARNING: This will remove all unused volumes)" -ForegroundColor Red
    Write-Host "3. Remove all unused images (not just dangling ones)" -ForegroundColor Yellow
    Write-Host "4. Full cleanup (all of the above)" -ForegroundColor Red
    Write-Host "5. Exit" -ForegroundColor Green
    
    $choice = Read-Host "\nEnter your choice (1-5)"
    
    switch ($choice) {
        "1" { $Prune = $true }
        "2" { $PruneVolumes = $true }
        "3" { $RemoveUnused = $true }
        "4" { $Prune = $true; $PruneVolumes = $true; $RemoveUnused = $true }
        "5" { exit 0 }
        default { 
            Write-Host "Invalid choice!" -ForegroundColor Red
            exit 1
        }
    }
}

# Confirm potentially destructive operations
if (($PruneVolumes -or $RemoveUnused) -and -not $Force) {
    Write-Host "\nWARNING: This operation may remove data that is still needed." -ForegroundColor Red
    $confirmation = Read-Host "Are you sure you want to proceed? (y/N)"
    
    if ($confirmation -ne "y" -and $confirmation -ne "Y") {
        Write-Host "Operation cancelled." -ForegroundColor Yellow
        exit 0
    }
}

# Perform cleanup operations
if ($Prune) {
    Write-Host "\nPruning containers, networks, and dangling images..." -ForegroundColor Cyan
    docker system prune -f
}

if ($PruneVolumes) {
    Write-Host "\nPruning volumes..." -ForegroundColor Cyan
    docker volume prune -f
}

if ($RemoveUnused) {
    Write-Host "\nRemoving unused images..." -ForegroundColor Cyan
    docker image prune -a -f
}

# Display new Docker disk usage
Write-Host "\nNew Docker disk usage:" -ForegroundColor Green
docker system df

Write-Host "\nCleanup completed!" -ForegroundColor Green