# Eddits Application Utility Scripts

This directory contains utility scripts for managing the Eddits application deployment with Docker, Nginx, and Gunicorn.

## Available Scripts

### Docker Deployment

- **docker-deploy.ps1**: Main deployment script with commands for starting, stopping, building, and managing the Docker environment
  ```powershell
  # Start the application
  .\docker-deploy.ps1 -Start
  
  # Stop the application
  .\docker-deploy.ps1 -Stop
  
  # Rebuild and start
  .\docker-deploy.ps1 -Build -Start
  ```

### Database Management

- **backup-db.ps1**: Create database backups
  ```powershell
  # Create a backup
  .\backup-db.ps1
  
  # Create a compressed backup
  .\backup-db.ps1 -Compress
  
  # Specify backup directory
  .\backup-db.ps1 -BackupDir "D:\backups"
  ```

- **restore-db.ps1**: Restore database from backups
  ```powershell
  # Restore from a backup file
  .\restore-db.ps1 -BackupFile "backups\eddits_db_20230101_120000.sql"
  
  # Force restore without confirmation
  .\restore-db.ps1 -BackupFile "backups\eddits_db_20230101_120000.sql" -Force
  ```

### Monitoring and Maintenance

- **check-health.ps1**: Check the health status of all containers and services
  ```powershell
  # Run health check
  .\check-health.ps1
  ```

- **view-logs.ps1**: View logs from Docker containers
  ```powershell
  # List available services
  .\view-logs.ps1 -ListServices
  
  # View logs for a specific service
  .\view-logs.ps1 -Service backend
  
  # Follow logs in real-time
  .\view-logs.ps1 -Service backend -Follow
  
  # View last 500 lines
  .\view-logs.ps1 -Service backend -Lines 500
  ```

- **monitor-resources.ps1**: Monitor Docker container resource usage
  ```powershell
  # Monitor with default refresh interval (5 seconds)
  .\monitor-resources.ps1
  
  # Set custom refresh interval
  .\monitor-resources.ps1 -RefreshInterval 10
  
  # Include volume information
  .\monitor-resources.ps1 -IncludeVolumes
  ```

- **scale-service.ps1**: Scale services up or down
  ```powershell
  # List available services
  .\scale-service.ps1 -ListServices
  
  # Scale a service to specific number of instances
  .\scale-service.ps1 -Service backend -Instances 3
  ```

## Requirements

- PowerShell 5.1 or higher
- Docker and Docker Compose installed
- Administrative privileges (for some operations)

## Notes

- These scripts are designed to work with the Eddits application Docker setup
- Always ensure you have proper backups before performing maintenance operations
- For production environments, consider additional security and monitoring tools