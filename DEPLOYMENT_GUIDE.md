# Eddits Application Deployment Guide

## Overview

This guide provides instructions for deploying the Eddits application using Docker, Nginx, and Gunicorn. The deployment architecture consists of:

- **PostgreSQL**: Database server
- **Django Backend**: API server running with Gunicorn
- **Nginx**: Web server for static files and reverse proxy
- **Admin Portal**: Next.js application

## Prerequisites

- Docker and Docker Compose installed
- Git
- Basic knowledge of Docker, Nginx, and Django

## Deployment Steps

### 1. Clone the Repository

```bash
git clone <repository-url>
cd Eddits_By_Meet_Dudhwala_Application
```

### 2. Environment Configuration

1. Create a `.env` file based on the provided `.env.example`:

```bash
cp .env.example .env
```

2. Edit the `.env` file with your specific configuration values:
   - Generate a secure Django secret key
   - Set database credentials
   - Configure email settings
   - Set up storage backend (AWS S3, Google Cloud Storage, etc.)
   - Configure JWT settings

### 3. SSL Certificate Setup

#### For Development (Self-signed certificates)

Run the provided PowerShell script to generate self-signed certificates:

```powershell
cd nginx
.\generate-ssl-certs.ps1
```

#### For Production

Obtain SSL certificates from a trusted certificate authority (e.g., Let's Encrypt) and place them in the `nginx/ssl` directory:

- `eddits.crt`: SSL certificate
- `eddits.key`: Private key

### 4. Build and Start the Services

```bash
docker-compose up -d --build
```

This command will:
- Build the Docker images for the backend and admin portal
- Create and start the containers for all services
- Set up the necessary volumes for data persistence

### 5. Database Initialization

The database migrations will be automatically applied during container startup. However, you can manually apply migrations if needed:

```bash
docker-compose exec backend python manage.py migrate
```

To create a superuser for the Django admin:

```bash
docker-compose exec backend python manage.py createsuperuser
```

### 6. Populate Initial Data

Run the management command to populate initial email templates:

```bash
docker-compose exec backend python manage.py populate_email_templates
```

### 7. Verify Deployment

- Django Backend: https://localhost/api/
- Django Admin: https://localhost/admin/
- Admin Portal: https://localhost/

## Configuration Details

### Docker Compose

The `docker-compose.yml` file defines the following services:

- **db**: PostgreSQL database
- **backend**: Django application with Gunicorn
- **nginx**: Web server and reverse proxy
- **admin-portal**: Next.js admin interface

### Nginx Configuration

The Nginx configuration in `nginx/conf.d/default.conf` handles:

- SSL termination
- Static and media file serving
- Reverse proxy to the Django backend and admin portal
- HTTP to HTTPS redirection
- Security headers

### Gunicorn

Gunicorn is configured in the backend Dockerfile with the following settings:

- 3 worker processes
- 120-second timeout
- Binding to 0.0.0.0:8000

## Scaling and Performance

### Scaling the Application

To scale the backend service:

```bash
docker-compose up -d --scale backend=3
```

### Performance Tuning

- **Gunicorn Workers**: Adjust the number of workers based on available CPU cores (typically 2-4 × cores + 1)
- **Database Connection Pooling**: Consider using PgBouncer for high-traffic deployments
- **Caching**: Implement Redis for caching frequently accessed data

## Monitoring and Maintenance

### Logs

View container logs:

```bash
docker-compose logs -f [service_name]
```

### Backups

Backup the PostgreSQL database:

```bash
docker-compose exec db pg_dump -U postgres eddits_db > backup.sql
```

### Updates

To update the application:

1. Pull the latest code:
   ```bash
   git pull
   ```

2. Rebuild and restart the containers:
   ```bash
   docker-compose up -d --build
   ```

## Security Considerations

- Keep all software updated
- Use strong, unique passwords for database and admin accounts
- Regularly rotate API keys and secrets
- Implement rate limiting for API endpoints
- Configure proper file permissions
- Use HTTPS for all communications

## Troubleshooting

### Common Issues

1. **Database Connection Errors**
   - Verify database credentials in the `.env` file
   - Check if the database container is running

2. **Static Files Not Loading**
   - Ensure the collectstatic command ran successfully
   - Check Nginx configuration for static file paths

3. **SSL Certificate Issues**
   - Verify certificate and key files exist in the correct location
   - Check certificate validity and expiration

4. **Permission Errors**
   - Check volume mount permissions
   - Ensure proper ownership of files

## Production Deployment Considerations

For production environments, consider the following additional steps:

1. **Domain Configuration**: Update Nginx configuration with your domain name
2. **CDN Integration**: Set up a CDN for static and media files
3. **Backup Strategy**: Implement automated backups
4. **Monitoring**: Set up monitoring tools (e.g., Prometheus, Grafana)
5. **CI/CD Pipeline**: Automate the deployment process

## Conclusion

This deployment setup provides a robust, scalable, and secure environment for the Eddits application. By following this guide, you should have a fully functional deployment using Docker, Nginx, and Gunicorn.