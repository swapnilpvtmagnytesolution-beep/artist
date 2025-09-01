# PowerShell script for Docker deployment and management

param (
    [Parameter(Mandatory=$false)]
    [ValidateSet("start", "stop", "restart", "build", "logs", "status", "backup", "help")]
    [string]$Command = "help",
    
    [Parameter(Mandatory=$false)]
    [string]$Service = ""
)

# Function to display help information
function Show-Help {
    Write-Host "Eddits Docker Deployment Helper" -ForegroundColor Cyan
    Write-Host "===========================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Usage: .\docker-deploy.ps1 [command] [service]" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Commands:" -ForegroundColor Green
    Write-Host "  start   - Start all or specified services"
    Write-Host "  stop    - Stop all or specified services"
    Write-Host "  restart - Restart all or specified services"
    Write-Host "  build   - Rebuild all or specified services"
    Write-Host "  logs    - View logs for all or specified services"
    Write-Host "  status  - Check status of all services"
    Write-Host "  backup  - Backup the database"
    Write-Host "  help    - Show this help message"
    Write-Host ""
    Write-Host "Examples:" -ForegroundColor Green
    Write-Host "  .\docker-deploy.ps1 start        # Start all services"
    Write-Host "  .\docker-deploy.ps1 logs backend # View backend logs"
    Write-Host "  .\docker-deploy.ps1 build        # Rebuild all services"
    Write-Host ""
}

# Function to check if .env file exists
function Check-EnvFile {
    if (-not (Test-Path ".env")) {
        Write-Host "Error: .env file not found!" -ForegroundColor Red
        Write-Host "Please create a .env file based on .env.example" -ForegroundColor Yellow
        exit 1
    }
}

# Function to check if Docker is installed
function Check-Docker {
    try {
        docker --version | Out-Null
    }
    catch {
        Write-Host "Error: Docker is not installed or not in PATH!" -ForegroundColor Red
        exit 1
    }
    
    try {
        docker-compose --version | Out-Null
    }
    catch {
        Write-Host "Error: Docker Compose is not installed or not in PATH!" -ForegroundColor Red
        exit 1
    }
}

# Function to start services
function Start-Services {
    param ([string]$ServiceName)
    
    if ($ServiceName) {
        Write-Host "Starting service: $ServiceName..." -ForegroundColor Cyan
        docker-compose up -d $ServiceName
    }
    else {
        Write-Host "Starting all services..." -ForegroundColor Cyan
        docker-compose up -d
    }
    
    Write-Host "Services started successfully!" -ForegroundColor Green
}

# Function to stop services
function Stop-Services {
    param ([string]$ServiceName)
    
    if ($ServiceName) {
        Write-Host "Stopping service: $ServiceName..." -ForegroundColor Cyan
        docker-compose stop $ServiceName
    }
    else {
        Write-Host "Stopping all services..." -ForegroundColor Cyan
        docker-compose down
    }
    
    Write-Host "Services stopped successfully!" -ForegroundColor Green
}

# Function to restart services
function Restart-Services {
    param ([string]$ServiceName)
    
    if ($ServiceName) {
        Write-Host "Restarting service: $ServiceName..." -ForegroundColor Cyan
        docker-compose restart $ServiceName
    }
    else {
        Write-Host "Restarting all services..." -ForegroundColor Cyan
        docker-compose restart
    }
    
    Write-Host "Services restarted successfully!" -ForegroundColor Green
}

# Function to build services
function Build-Services {
    param ([string]$ServiceName)
    
    if ($ServiceName) {
        Write-Host "Building service: $ServiceName..." -ForegroundColor Cyan
        docker-compose build $ServiceName
        docker-compose up -d $ServiceName
    }
    else {
        Write-Host "Building all services..." -ForegroundColor Cyan
        docker-compose up -d --build
    }
    
    Write-Host "Services built successfully!" -ForegroundColor Green
}

# Function to view logs
function Show-Logs {
    param ([string]$ServiceName)
    
    if ($ServiceName) {
        Write-Host "Showing logs for service: $ServiceName..." -ForegroundColor Cyan
        docker-compose logs -f $ServiceName
    }
    else {
        Write-Host "Showing logs for all services..." -ForegroundColor Cyan
        docker-compose logs -f
    }
}

# Function to check status
function Show-Status {
    Write-Host "Checking service status..." -ForegroundColor Cyan
    docker-compose ps
}

# Function to backup database
function Backup-Database {
    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $backupFile = "backup_${timestamp}.sql"
    
    Write-Host "Backing up database to $backupFile..." -ForegroundColor Cyan
    docker-compose exec -T db pg_dump -U postgres eddits_db > $backupFile
    
    if (Test-Path $backupFile) {
        Write-Host "Database backup created successfully: $backupFile" -ForegroundColor Green
    }
    else {
        Write-Host "Error: Database backup failed!" -ForegroundColor Red
    }
}

# Main script execution
Check-Docker

# Process commands
switch ($Command) {
    "start" {
        Check-EnvFile
        Start-Services -ServiceName $Service
    }
    "stop" {
        Stop-Services -ServiceName $Service
    }
    "restart" {
        Check-EnvFile
        Restart-Services -ServiceName $Service
    }
    "build" {
        Check-EnvFile
        Build-Services -ServiceName $Service
    }
    "logs" {
        Show-Logs -ServiceName $Service
    }
    "status" {
        Show-Status
    }
    "backup" {
        Backup-Database
    }
    "help" {
        Show-Help
    }
    default {
        Write-Host "Error: Unknown command '$Command'" -ForegroundColor Red
        Show-Help
        exit 1
    }
}