# PowerShell script for database backup in Docker environment

param (
    [Parameter(Mandatory=$false)]
    [string]$BackupDir = "./backups",
    
    [Parameter(Mandatory=$false)]
    [switch]$Compress = $false
)

# Create backup directory if it doesn't exist
if (-not (Test-Path $BackupDir)) {
    New-Item -ItemType Directory -Force -Path $BackupDir | Out-Null
    Write-Host "Created backup directory: $BackupDir" -ForegroundColor Green
}

# Generate timestamp for backup filename
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$backupFile = "${BackupDir}/eddits_db_${timestamp}.sql"

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

# Perform database backup
Write-Host "Backing up database to $backupFile..." -ForegroundColor Cyan
try {
    docker-compose exec -T db pg_dump -U postgres eddits_db > $backupFile
    
    if (Test-Path $backupFile) {
        $fileSize = (Get-Item $backupFile).Length / 1MB
        Write-Host "Database backup created successfully: $backupFile (Size: $($fileSize.ToString("0.00")) MB)" -ForegroundColor Green
        
        # Compress backup if requested
        if ($Compress) {
            $compressedFile = "${backupFile}.zip"
            Write-Host "Compressing backup to $compressedFile..." -ForegroundColor Cyan
            Compress-Archive -Path $backupFile -DestinationPath $compressedFile -Force
            
            if (Test-Path $compressedFile) {
                $compressedSize = (Get-Item $compressedFile).Length / 1MB
                Write-Host "Backup compressed successfully: $compressedFile (Size: $($compressedSize.ToString("0.00")) MB)" -ForegroundColor Green
                
                # Remove original file after compression
                Remove-Item $backupFile -Force
                Write-Host "Removed original backup file" -ForegroundColor Yellow
            }
            else {
                Write-Host "Error: Failed to compress backup file!" -ForegroundColor Red
            }
        }
    }
    else {
        Write-Host "Error: Database backup failed!" -ForegroundColor Red
        exit 1
    }
}
catch {
    Write-Host "Error during backup: $_" -ForegroundColor Red
    exit 1
}

# List all backups
Write-Host "\nAvailable backups:" -ForegroundColor Cyan
if ($Compress) {
    Get-ChildItem "${BackupDir}/*.zip" | Sort-Object LastWriteTime -Descending | Format-Table Name, @{Name="Size (MB)"; Expression={($_.Length / 1MB).ToString("0.00")}}, LastWriteTime
}
else {
    Get-ChildItem "${BackupDir}/*.sql" | Sort-Object LastWriteTime -Descending | Format-Table Name, @{Name="Size (MB)"; Expression={($_.Length / 1MB).ToString("0.00")}}, LastWriteTime
}