# Dristhi Deployment Guide

## Overview

This guide provides detailed instructions for deploying the Dristhi application in different environments. Dristhi is an AI-powered life improvement platform built with a React frontend, FastAPI backend, and various supporting services including PostgreSQL, Redis, Ollama (for local LLM capabilities), Prometheus, Grafana, and Celery for background task processing.

## System Requirements

### Minimum Hardware Requirements

- **CPU**: 2+ cores
- **RAM**: 4GB minimum (8GB+ recommended)
- **Storage**: 20GB available space

### Software Requirements

- **Docker**: 20.10.x or newer
- **Docker Compose**: 2.x or newer
- **Git**: 2.x or newer
- **Node.js**: 16.x or newer (for development only)
- **Python**: 3.9+ (for development only)

## Deployment Options

Dristhi can be deployed using the following methods:

1. **Docker Compose** (Recommended for most deployments)
2. **Manual Deployment** (For customized setups)
3. **Development Setup** (For local development)
4. **Cloud Deployment** (For production environments)
   - AWS
   - Azure
   - Google Cloud Platform

## Docker Compose Deployment

### Prerequisites

- Docker and Docker Compose installed
- Access to the Dristhi repository

### Steps

1. **Clone the repository**

   ```bash
   git clone https://github.com/your-organization/dristhi.git
   cd dristhi
   ```

2. **Configure environment variables**

   Copy the example environment files and modify them according to your environment:

   ```bash
   cp backend/.env.example backend/.env
   cp frontend/.env.example frontend/.env
   ```

   Edit the `.env` files with appropriate values (see Environment Configuration section below).

3. **Build and start the containers**

   ```bash
   docker-compose up -d
   ```

   This command will build the images if they don't exist and start all services defined in the docker-compose.yml file.

4. **Initialize the database**

   ```bash
   docker-compose exec backend alembic upgrade head
   ```

5. **Verify the deployment**

   Access the application at `http://localhost:3000` and the API at `http://localhost:8000`.

### Updating the Deployment

1. **Pull the latest changes**

   ```bash
   git pull
   ```

2. **Rebuild and restart the containers**

   ```bash
   docker-compose down
   docker-compose up -d --build
   ```

3. **Apply database migrations if needed**

   ```bash
   docker-compose exec backend alembic upgrade head
   ```

## Manual Deployment

### Backend Deployment

1. **Set up a Python environment**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**

   ```bash
   cd backend
   pip install -r requirements.txt
   ```

3. **Configure environment variables**

   Copy the example environment file and modify it:

   ```bash
   cp .env.example .env
   ```

4. **Initialize the database**

   ```bash
   alembic upgrade head
   ```

5. **Start the backend server**

   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```

### Frontend Deployment

1. **Install dependencies**

   ```bash
   cd frontend
   npm install
   ```

2. **Configure environment variables**

   Copy the example environment file and modify it:

   ```bash
   cp .env.example .env
   ```

3. **Build the frontend**

   ```bash
   npm run build
   ```

4. **Serve the built files**

   You can use Nginx, Apache, or any other web server to serve the static files from the `build` directory.

   Example Nginx configuration:

   ```nginx
   server {
       listen 80;
       server_name your-domain.com;

       location / {
           root /path/to/dristhi/frontend/build;
           try_files $uri /index.html;
       }

       location /api/ {
           proxy_pass http://localhost:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

## Environment Configuration

### Backend Environment Variables

| Variable | Description | Example |
|----------|-------------|--------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://user:password@db:5432/dristhi` |
| `SECRET_KEY` | JWT secret key | `your-secret-key` |
| `ALGORITHM` | JWT algorithm | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | JWT token expiration in minutes | `30` |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Refresh token expiration in days | `7` |
| `ENABLE_AI_FEATURES` | Enable/disable AI features | `true` |
| `OLLAMA_BASE_URL` | Ollama API URL | `http://ollama:11434` |
| `OLLAMA_MODEL` | Ollama model to use | `llama2` |
| `REDIS_URL` | Redis connection string | `redis://redis:6379/0` |
| `CELERY_BROKER_URL` | Celery broker URL | `redis://redis:6379/1` |
| `CELERY_RESULT_BACKEND` | Celery result backend URL | `redis://redis:6379/2` |
| `CORS_ORIGINS` | Allowed CORS origins | `http://localhost:3000,https://your-domain.com` |
| `LOG_LEVEL` | Logging level | `INFO` |
| `ENVIRONMENT` | Deployment environment | `production` |

### Frontend Environment Variables

| Variable | Description | Example |
|----------|-------------|--------|
| `REACT_APP_API_URL` | Backend API URL | `http://localhost:8000/api/v1` |
| `REACT_APP_ENABLE_AI_FEATURES` | Enable/disable AI features in UI | `true` |
| `REACT_APP_ENVIRONMENT` | Deployment environment | `production` |

## Monitoring and Maintenance

### Logs

In Docker Compose deployment, you can view logs with:

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
```

### Monitoring with Prometheus and Grafana

Dristhi includes Prometheus and Grafana for monitoring. Access them at:

- Prometheus: `http://localhost:9090`
- Grafana: `http://localhost:3001` (default credentials: admin/admin)

### Backup and Restore

#### Database Backup

```bash
# For Docker Compose deployment
docker-compose exec db pg_dump -U postgres dristhi > backup.sql

# For manual deployment
pg_dump -U your_user dristhi > backup.sql
```

#### Database Restore

```bash
# For Docker Compose deployment
cat backup.sql | docker-compose exec -T db psql -U postgres dristhi

# For manual deployment
psql -U your_user dristhi < backup.sql
```

## Cloud Deployment

### AWS Deployment

#### Prerequisites

- AWS account with appropriate permissions
- AWS CLI installed and configured
- Docker installed locally

#### Using AWS Elastic Container Service (ECS)

1. **Create an ECR repository for each service**

   ```bash
   aws ecr create-repository --repository-name dristhi-backend
   aws ecr create-repository --repository-name dristhi-frontend
   ```

2. **Build and push Docker images**

   ```bash
   # Login to ECR
   aws ecr get-login-password --region your-region | docker login --username AWS --password-stdin your-account-id.dkr.ecr.your-region.amazonaws.com
   
   # Build and push backend
   docker build -t your-account-id.dkr.ecr.your-region.amazonaws.com/dristhi-backend:latest ./backend
   docker push your-account-id.dkr.ecr.your-region.amazonaws.com/dristhi-backend:latest
   
   # Build and push frontend
   docker build -t your-account-id.dkr.ecr.your-region.amazonaws.com/dristhi-frontend:latest ./frontend
   docker push your-account-id.dkr.ecr.your-region.amazonaws.com/dristhi-frontend:latest
   ```

3. **Create ECS cluster**

   ```bash
   aws ecs create-cluster --cluster-name dristhi-cluster
   ```

4. **Create task definitions for each service**

   Create JSON files for each task definition and register them:

   ```bash
   aws ecs register-task-definition --cli-input-json file://backend-task-definition.json
   aws ecs register-task-definition --cli-input-json file://frontend-task-definition.json
   ```

5. **Create services in the cluster**

   ```bash
   aws ecs create-service --cluster dristhi-cluster --service-name backend-service --task-definition dristhi-backend --desired-count 2 --launch-type FARGATE --network-configuration "awsvpcConfiguration={subnets=[subnet-12345,subnet-67890],securityGroups=[sg-12345],assignPublicIp=ENABLED}"
   
   aws ecs create-service --cluster dristhi-cluster --service-name frontend-service --task-definition dristhi-frontend --desired-count 2 --launch-type FARGATE --network-configuration "awsvpcConfiguration={subnets=[subnet-12345,subnet-67890],securityGroups=[sg-12345],assignPublicIp=ENABLED}"
   ```

6. **Set up an Application Load Balancer**

   Create an ALB to route traffic to your services.

#### Using AWS Elastic Beanstalk (Simpler Alternative)

1. **Install the EB CLI**

   ```bash
   pip install awsebcli
   ```

2. **Initialize EB application**

   ```bash
   eb init -p docker dristhi
   ```

3. **Create an environment and deploy**

   ```bash
   eb create dristhi-production
   ```

### Azure Deployment

#### Prerequisites

- Azure account
- Azure CLI installed and configured
- Docker installed locally

#### Using Azure Container Instances

1. **Create a resource group**

   ```bash
   az group create --name dristhi-resources --location eastus
   ```

2. **Create an Azure Container Registry**

   ```bash
   az acr create --resource-group dristhi-resources --name dristhiregistry --sku Basic
   ```

3. **Build and push Docker images**

   ```bash
   # Login to ACR
   az acr login --name dristhiregistry
   
   # Build and push backend
   docker build -t dristhiregistry.azurecr.io/dristhi-backend:latest ./backend
   docker push dristhiregistry.azurecr.io/dristhi-backend:latest
   
   # Build and push frontend
   docker build -t dristhiregistry.azurecr.io/dristhi-frontend:latest ./frontend
   docker push dristhiregistry.azurecr.io/dristhi-frontend:latest
   ```

4. **Deploy containers**

   ```bash
   az container create --resource-group dristhi-resources --name dristhi-backend --image dristhiregistry.azurecr.io/dristhi-backend:latest --dns-name-label dristhi-backend --ports 8000
   
   az container create --resource-group dristhi-resources --name dristhi-frontend --image dristhiregistry.azurecr.io/dristhi-frontend:latest --dns-name-label dristhi-frontend --ports 3000
   ```

### Google Cloud Platform Deployment

#### Prerequisites

- GCP account
- gcloud CLI installed and configured
- Docker installed locally

#### Using Google Kubernetes Engine (GKE)

1. **Create a GKE cluster**

   ```bash
   gcloud container clusters create dristhi-cluster --num-nodes=3 --zone=us-central1-a
   ```

2. **Configure kubectl**

   ```bash
   gcloud container clusters get-credentials dristhi-cluster --zone=us-central1-a
   ```

3. **Build and push Docker images to Google Container Registry**

   ```bash
   # Configure Docker to use gcloud as a credential helper
   gcloud auth configure-docker
   
   # Build and push backend
   docker build -t gcr.io/your-project-id/dristhi-backend:latest ./backend
   docker push gcr.io/your-project-id/dristhi-backend:latest
   
   # Build and push frontend
   docker build -t gcr.io/your-project-id/dristhi-frontend:latest ./frontend
   docker push gcr.io/your-project-id/dristhi-frontend:latest
   ```

4. **Create Kubernetes deployments**

   Create YAML files for each deployment and apply them:

   ```bash
   kubectl apply -f backend-deployment.yaml
   kubectl apply -f frontend-deployment.yaml
   ```

5. **Expose services**

   ```bash
   kubectl expose deployment dristhi-backend --type=LoadBalancer --port=8000
   kubectl expose deployment dristhi-frontend --type=LoadBalancer --port=3000
   ```

## Scaling

### Horizontal Scaling

For higher load environments, you can scale the backend services:

```bash
docker-compose up -d --scale backend=3
```

Note: When scaling horizontally, ensure you're using a load balancer in front of the backend services.

### Vertical Scaling

You can adjust the resources allocated to containers in the `docker-compose.yml` file:

```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 1G
```

## Troubleshooting

### Common Issues

1. **Database connection errors**
   - Check if the database container is running
   - Verify DATABASE_URL environment variable
   - Ensure the database user has proper permissions

2. **API not accessible**
   - Check if the backend container is running
   - Verify network settings in docker-compose.yml
   - Check for errors in backend logs

3. **Frontend not loading**
   - Verify REACT_APP_API_URL is set correctly
   - Check for build errors in frontend logs
   - Ensure the web server is properly configured

4. **AI features not working**
   - Verify ENABLE_AI_FEATURES is set to true
   - Check if Ollama service is running
   - Verify OLLAMA_BASE_URL and OLLAMA_MODEL settings

### Health Check Endpoints

Use these endpoints to verify service health:

- Backend health: `GET /api/v1/health`
- Database health: `GET /api/v1/health/db`
- AI service health: `GET /api/v1/health/ai`

## Security Considerations

### General Security Best Practices

1. **Production Deployments**
   - Use HTTPS for all traffic with proper TLS/SSL certificates
   - Set strong, unique SECRET_KEY values and rotate them periodically
   - Restrict access to admin endpoints with IP whitelisting
   - Configure proper firewall rules at both network and application levels
   - Use a Web Application Firewall (WAF) for additional protection
   - Implement Content Security Policy (CSP) headers
   - Enable HTTP Strict Transport Security (HSTS)

2. **Database Security**
   - Use strong, unique passwords for database accounts
   - Implement database connection pooling with proper timeout settings
   - Restrict network access to the database (use private subnets in cloud deployments)
   - Regularly backup the database and test restoration procedures
   - Encrypt sensitive data at rest
   - Use parameterized queries to prevent SQL injection
   - Implement proper database user permissions (principle of least privilege)

3. **API Security**
   - Configure proper CORS settings to restrict cross-origin requests
   - Implement rate limiting to prevent abuse and DoS attacks
   - Use proper authentication for all endpoints (JWT with short expiration times)
   - Validate all input data on the server side
   - Implement proper error handling that doesn't expose sensitive information
   - Use API keys for service-to-service communication
   - Implement request logging and monitoring

4. **Container Security**
   - Use minimal base images (Alpine or distroless)
   - Scan container images for vulnerabilities before deployment
   - Run containers with non-root users
   - Implement resource limits for all containers
   - Use read-only file systems where possible
   - Regularly update base images and dependencies

5. **Cloud-Specific Security**
   - Use IAM roles with least privilege principle
   - Enable audit logging for all cloud resources
   - Implement network segmentation with security groups/VPCs
   - Use managed secrets services (AWS Secrets Manager, Azure Key Vault, GCP Secret Manager)
   - Enable MFA for all cloud console access
   - Implement proper key rotation policies

### Security Hardening Checklist

- [ ] All secrets stored in environment variables or dedicated secrets management
- [ ] No hardcoded credentials in code or configuration files
- [ ] All HTTP traffic redirected to HTTPS
- [ ] Security headers implemented in web server configuration
- [ ] Regular security updates applied to all components
- [ ] Automated vulnerability scanning implemented
- [ ] Proper logging and monitoring in place
- [ ] Data backups configured and tested
- [ ] Incident response plan documented
- [ ] Security compliance requirements identified and met

## Support and Resources

- **Documentation**: [Project Wiki](https://github.com/your-organization/dristhi/wiki)
- **Issue Tracker**: [GitHub Issues](https://github.com/your-organization/dristhi/issues)
- **Contact**: support@dristhi.example.com