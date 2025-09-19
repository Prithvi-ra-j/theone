# Dristhi Environment Configurations

## Overview

This document details the environment-specific configurations for the Dristhi application across different deployment environments: development, testing, staging, and production. Proper configuration is essential for security, performance, and functionality.

## Configuration Files

Dristhi uses environment variables for configuration, typically stored in `.env` files. Each environment should have its own configuration file:

- Development: `.env.development`
- Testing: `.env.testing`
- Staging: `.env.staging`
- Production: `.env.production`

## Backend Configuration

### Core Settings

| Variable | Development | Testing | Staging | Production |
|----------|-------------|---------|---------|------------|
| `ENVIRONMENT` | `development` | `testing` | `staging` | `production` |
| `DEBUG` | `true` | `false` | `false` | `false` |
| `LOG_LEVEL` | `DEBUG` | `INFO` | `INFO` | `WARNING` |
| `TESTING` | `false` | `true` | `false` | `false` |

### Database Settings

| Variable | Development | Testing | Staging | Production |
|----------|-------------|---------|---------|------------|
| `DATABASE_URL` | `postgresql://postgres:postgres@localhost:5432/dristhi_dev` | `postgresql://postgres:postgres@localhost:5432/dristhi_test` | `postgresql://dristhi_user:password@db:5432/dristhi_staging` | `postgresql://dristhi_user:strong_password@db:5432/dristhi_prod` |
| `DB_POOL_SIZE` | `5` | `5` | `10` | `20` |
| `DB_MAX_OVERFLOW` | `10` | `10` | `20` | `40` |
| `DB_POOL_TIMEOUT` | `30` | `30` | `60` | `60` |

### Security Settings

| Variable | Development | Testing | Staging | Production |
|----------|-------------|---------|---------|------------|
| `SECRET_KEY` | `dev_secret_key` | `test_secret_key` | `unique_staging_secret_key` | `strong_unique_production_secret_key` |
| `ALGORITHM` | `HS256` | `HS256` | `HS256` | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `60` | `60` | `30` | `15` |
| `REFRESH_TOKEN_EXPIRE_DAYS` | `7` | `7` | `7` | `7` |
| `CORS_ORIGINS` | `http://localhost:3000` | `http://localhost:3000` | `https://staging.dristhi.example.com` | `https://dristhi.example.com` |
| `ALLOW_CREDENTIALS` | `true` | `true` | `true` | `true` |

### AI Service Settings

| Variable | Development | Testing | Staging | Production |
|----------|-------------|---------|---------|------------|
| `ENABLE_AI_FEATURES` | `true` | `true` | `true` | `true` |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | `http://localhost:11434` | `http://ollama:11434` | `http://ollama:11434` |
| `OLLAMA_MODEL` | `llama2` | `llama2` | `llama2` | `llama2` |
| `AI_REQUEST_TIMEOUT` | `30` | `10` | `20` | `20` |
| `AI_CACHE_TTL` | `3600` | `3600` | `7200` | `7200` |

### Redis and Celery Settings

| Variable | Development | Testing | Staging | Production |
|----------|-------------|---------|---------|------------|
| `REDIS_URL` | `redis://localhost:6379/0` | `redis://localhost:6379/1` | `redis://redis:6379/0` | `redis://redis:6379/0` |
| `CELERY_BROKER_URL` | `redis://localhost:6379/1` | `redis://localhost:6379/2` | `redis://redis:6379/1` | `redis://redis:6379/1` |
| `CELERY_RESULT_BACKEND` | `redis://localhost:6379/2` | `redis://localhost:6379/3` | `redis://redis:6379/2` | `redis://redis:6379/2` |
| `CELERY_TASK_ALWAYS_EAGER` | `false` | `true` | `false` | `false` |

## Frontend Configuration

### Core Settings

| Variable | Development | Testing | Staging | Production |
|----------|-------------|---------|---------|------------|
| `REACT_APP_ENVIRONMENT` | `development` | `testing` | `staging` | `production` |
| `REACT_APP_API_URL` | `http://localhost:8000/api/v1` | `http://localhost:8000/api/v1` | `https://staging-api.dristhi.example.com/api/v1` | `https://api.dristhi.example.com/api/v1` |
| `REACT_APP_ENABLE_AI_FEATURES` | `true` | `true` | `true` | `true` |
| `REACT_APP_DEBUG` | `true` | `false` | `false` | `false` |

### Feature Flags

| Variable | Development | Testing | Staging | Production |
|----------|-------------|---------|---------|------------|
| `REACT_APP_ENABLE_GAMIFICATION` | `true` | `true` | `true` | `true` |
| `REACT_APP_ENABLE_NOTIFICATIONS` | `true` | `true` | `true` | `true` |
| `REACT_APP_ENABLE_ANALYTICS` | `false` | `true` | `true` | `true` |
| `REACT_APP_ENABLE_FEEDBACK` | `true` | `true` | `true` | `true` |

## Monitoring Configuration

### Prometheus Settings

The `prometheus.yml` file should be configured differently for each environment:

#### Development

```yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'dristhi_backend'
    static_configs:
      - targets: ['localhost:8000']
  - job_name: 'dristhi_frontend'
    static_configs:
      - targets: ['localhost:3000']
```

#### Production

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'dristhi_backend'
    static_configs:
      - targets: ['backend:8000']
  - job_name: 'dristhi_frontend'
    static_configs:
      - targets: ['frontend:3000']
  - job_name: 'node_exporter'
    static_configs:
      - targets: ['node-exporter:9100']
  - job_name: 'cadvisor'
    static_configs:
      - targets: ['cadvisor:8080']
```

### Grafana Dashboards

Grafana dashboards should be configured to monitor different metrics based on the environment:

- Development: Focus on API response times, error rates, and database query performance
- Testing: Focus on test coverage, test success rates, and performance benchmarks
- Staging/Production: Focus on user metrics, system health, resource utilization, and business KPIs

## Docker Compose Configuration

### Development

```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    volumes:
      - ./backend:/app
    environment:
      - ENVIRONMENT=development
      - DEBUG=true
    ports:
      - "8000:8000"

  frontend:
    build: ./frontend
    volumes:
      - ./frontend:/app
      - /app/node_modules
    environment:
      - REACT_APP_ENVIRONMENT=development
    ports:
      - "3000:3000"

  db:
    image: postgres:14
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
      - POSTGRES_DB=dristhi_dev
    volumes:
      - postgres_data_dev:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:7
    ports:
      - "6379:6379"

  ollama:
    image: ollama/ollama:latest
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama

volumes:
  postgres_data_dev:
  ollama_data:
```

### Production

```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    restart: always
    environment:
      - ENVIRONMENT=production
      - DEBUG=false
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 1G

  frontend:
    build: ./frontend
    restart: always
    environment:
      - REACT_APP_ENVIRONMENT=production
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 512M

  db:
    image: postgres:14
    restart: always
    environment:
      - POSTGRES_USER=dristhi_user
      - POSTGRES_PASSWORD=strong_password
      - POSTGRES_DB=dristhi_prod
    volumes:
      - postgres_data_prod:/var/lib/postgresql/data
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 1G

  redis:
    image: redis:7
    restart: always
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 512M

  ollama:
    image: ollama/ollama:latest
    restart: always
    volumes:
      - ollama_data:/root/.ollama
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 4G

  nginx:
    image: nginx:alpine
    restart: always
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/conf.d:/etc/nginx/conf.d
      - ./nginx/ssl:/etc/nginx/ssl
      - ./frontend/build:/usr/share/nginx/html
    depends_on:
      - backend
      - frontend

  prometheus:
    image: prom/prometheus
    restart: always
    volumes:
      - ./prometheus:/etc/prometheus
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
    ports:
      - "9090:9090"

  grafana:
    image: grafana/grafana
    restart: always
    volumes:
      - grafana_data:/var/lib/grafana
    ports:
      - "3001:3000"
    depends_on:
      - prometheus

  node-exporter:
    image: prom/node-exporter
    restart: always
    volumes:
      - /proc:/host/proc:ro
      - /sys:/host/sys:ro
      - /:/rootfs:ro
    command:
      - '--path.procfs=/host/proc'
      - '--path.sysfs=/host/sys'
      - '--collector.filesystem.ignored-mount-points=^/(sys|proc|dev|host|etc)($$|/)'

  cadvisor:
    image: gcr.io/cadvisor/cadvisor
    restart: always
    volumes:
      - /:/rootfs:ro
      - /var/run:/var/run:ro
      - /sys:/sys:ro
      - /var/lib/docker/:/var/lib/docker:ro
    ports:
      - "8080:8080"

volumes:
  postgres_data_prod:
  redis_data:
  ollama_data:
  prometheus_data:
  grafana_data:
```

## Environment-Specific Backup Strategies

### Development

- Database: Weekly backups
- Code: Git version control

### Testing

- Database: Snapshot before and after test runs
- Test results: Archived for regression analysis

### Staging

- Database: Daily backups
- Application state: Weekly snapshots

### Production

- Database: Daily automated backups with point-in-time recovery
- Weekly full system backups
- Offsite backup storage
- Regular backup restoration drills

## Logging Configuration

### Development

```python
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
        },
    },
    "root": {"level": "DEBUG", "handlers": ["console"]},
}
```

### Production

```python
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        },
        "json": {
            "()" : "app.core.logging.JsonFormatter",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "json",
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "json",
            "filename": "/var/log/dristhi/app.log",
            "maxBytes": 10485760,  # 10MB
            "backupCount": 10,
        },
    },
    "root": {"level": "WARNING", "handlers": ["console", "file"]},
    "loggers": {
        "app": {"level": "INFO", "handlers": ["console", "file"], "propagate": False},
        "uvicorn": {"level": "INFO", "handlers": ["console", "file"], "propagate": False},
        "sqlalchemy.engine": {"level": "WARNING", "handlers": ["console", "file"], "propagate": False},
    },
}
```

## Security Hardening by Environment

### Development

- Basic authentication
- Default CORS settings
- Debug mode enabled

### Testing

- Similar to development but with test-specific users
- Isolated test database

### Staging

- Production-like security settings
- Sanitized production data
- HTTPS enabled

### Production

- Strong password policies
- JWT with short expiration times
- HTTPS required
- Restricted CORS settings
- Rate limiting enabled
- IP filtering for admin endpoints
- Regular security audits
- Vulnerability scanning

## Conclusion

Proper environment configuration is critical for the security, performance, and reliability of the Dristhi application. Each environment serves a specific purpose in the development lifecycle, and configurations should be tailored accordingly. Always follow the principle of least privilege and ensure that sensitive information is properly secured in all environments.