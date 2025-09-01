# PowerShell script for database restoration in Docker environment

param (
    [Parameter(Mandatory=$true)]
    [string]$BackupFile,
    
    [Parameter(Mandatory=$false)]
    [switch]$Force = $false
)

# Check if backup file exists
if (-not (Test-Path $BackupFile)) {
    Write-Host "Error: Backup file not found: $BackupFile" -ForegroundColor Red
    exit 1
}

# Check if Docker is running
try {
    $dockerStatus = docker ps | Out-String
    if (-not $dockerStatus.Contains("db")) {
        Write-Host "Error: Database container is not running!" -ForegroundColor Red
        exit 1
    }
}
catch {
    Write-Host "Error: Docker is not running or not accessible!" -ForegroundColor Red
    exit 1
}

# Confirm restoration if not forced
if (-not $Force) {
    Write-Host "WARNING: This will overwrite the current database with the backup." -ForegroundColor Yellow
    Write-Host "All current data will be lost!" -ForegroundColor Red
    $confirmation = Read-Host "Are you sure you want to proceed? (y/N)"
    
    if ($confirmation -ne "y" -and $confirmation -ne "Y") {
        Write-Host "Restoration cancelled." -ForegroundColor Yellow
        exit 0
    }
}

# Extract backup if it's compressed
$tempFile = $BackupFile
if ($BackupFile.EndsWith(".zip")) {
    $tempDir = [System.IO.Path]::GetTempPath() + [System.Guid]::NewGuid().ToString()
    New-Item -ItemType Directory -Force -Path $tempDir | Out-Null
    
    Write-Host "Extracting compressed backup..." -ForegroundColor Cyan
    try {
        Expand-Archive -Path $BackupFile -DestinationPath $tempDir -Force
        $extractedFiles = Get-ChildItem -Path $tempDir -Filter "*.sql"
        
        if ($extractedFiles.Count -eq 0) {
            Write-Host "Error: No SQL files found in the compressed backup!" -ForegroundColor Red
            Remove-Item -Path $tempDir -Recurse -Force
            exit 1
        }
        
        $tempFile = $extractedFiles[0].FullName
        Write-Host "Using extracted file: $tempFile" -ForegroundColor Green
    }
    catch {
        Write-Host "Error extracting backup: $_" -ForegroundColor Red
        if (Test-Path $tempDir) {
            Remove-Item -Path $tempDir -Recurse -Force
        }
        exit 1
    }
}

# Perform database restoration
Write-Host "Restoring database from $BackupFile..." -ForegroundColor Cyan
try {
    # Drop existing connections
    docker-compose exec -T db psql -U postgres -c "SELECT pg_terminate_backend(pg_stat_activity.pid) FROM pg_stat_activity WHERE pg_stat_activity.datname = 'eddits_db' AND pid <> pg_backend_pid();" postgres
    
    # Drop and recreate database
    docker-compose exec -T db psql -U postgres -c "DROP DATABASE IF EXISTS eddits_db;" postgres
    docker-compose exec -T db psql -U postgres -c "CREATE DATABASE eddits_db;" postgres
    
    # Restore from backup
    Get-Content $tempFile | docker-compose exec -T db psql -U postgres eddits_db
    
    Write-Host "Database restored successfully!" -ForegroundColor Green
    
    # Clean up temporary files if we extracted from zip
    if ($BackupFile.EndsWith(".zip") -and (Test-Path $tempDir)) {
        Remove-Item -Path $tempDir -Recurse -Force
        Write-Host "Temporary files cleaned up." -ForegroundColor Yellow
    }
    
    # Restart backend service to apply changes
    Write-Host "Restarting backend service..." -ForegroundColor Cyan
    docker-compose restart backend
    Write-Host "Backend service restarted." -ForegroundColor Green
}
catch {
    Write-Host "Error during restoration: $_" -ForegroundColor Red
    
    # Clean up temporary files if we extracted from zip
    if ($BackupFile.EndsWith(".zip") -and (Test-Path $tempDir)) {
        Remove-Item -Path $tempDir -Recurse -Force
    }
    
    exit 1
}