# Deployment Guide

This guide covers different deployment options for the Compliance Master API.

## Table of Contents

1. [Local Development](#local-development)
2. [Docker Deployment](#docker-deployment)
3. [Production Deployment](#production-deployment)
4. [WatsonX Orchestrate Integration](#watsonx-orchestrate-integration)
5. [Monitoring and Maintenance](#monitoring-and-maintenance)

## Local Development

### Quick Start

```bash
# Clone and navigate to project
cd /Users/mattiasacosta/Documents/Programming_Projects/Compliance_Master

# Run the setup script
./run.sh
```

### Manual Setup

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp env.template .env
# Edit .env with your credentials

# Start server
uvicorn main:app --reload --host 0.0.0.0 --port 8765
```

### Development Tips

- Use `--reload` flag for auto-reloading during development
- Access Swagger docs at http://localhost:8765/docs
- Check logs in the console for debugging
- Use the example_usage.py script for testing

## Docker Deployment

### Prerequisites

- Docker installed (https://docs.docker.com/get-docker/)
- Docker Compose installed (comes with Docker Desktop)

### Build and Run

```bash
# Set environment variables
cp env.template .env
# Edit .env with your credentials

# Build the Docker image
docker build -t compliance-master-api .

# Run with Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the service
docker-compose down
```

### Docker Commands

```bash
# Build image
docker build -t compliance-master-api:latest .

# Run container
docker run -d \
  --name compliance-master-api \
  -p 8765:8765 \
  --env-file .env \
  compliance-master-api:latest

# View logs
docker logs -f compliance-master-api

# Stop container
docker stop compliance-master-api

# Remove container
docker rm compliance-master-api
```

### Docker Compose Options

```bash
# Start in detached mode
docker-compose up -d

# Start with build
docker-compose up --build

# Scale the service (not recommended for this API)
docker-compose up --scale compliance-master-api=2

# View resource usage
docker-compose stats

# Restart service
docker-compose restart
```

## Production Deployment

### Environment Configuration

Create a production `.env` file with secure values:

```env
WATSONX_API_KEY=<your-production-api-key>
WATSONX_PROJECT_ID=<your-production-project-id>
WATSONX_URL=https://us-south.ml.cloud.ibm.com
GRANITE_MODEL_ID=ibm/granite-13b-chat-v2
API_TITLE=Compliance Master API
API_VERSION=1.0.0
```

### Deployment Options

#### Option 1: Traditional Server Deployment

```bash
# Install production ASGI server
pip install gunicorn

# Run with Gunicorn
gunicorn main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8765 \
  --timeout 120 \
  --access-logfile logs/access.log \
  --error-logfile logs/error.log
```

#### Option 2: Kubernetes Deployment

Create `k8s-deployment.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: compliance-master-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: compliance-master-api
  template:
    metadata:
      labels:
        app: compliance-master-api
    spec:
      containers:
      - name: api
        image: compliance-master-api:latest
        ports:
        - containerPort: 8765
        env:
        - name: WATSONX_API_KEY
          valueFrom:
            secretKeyRef:
              name: watsonx-credentials
              key: api-key
        - name: WATSONX_PROJECT_ID
          valueFrom:
            secretKeyRef:
              name: watsonx-credentials
              key: project-id
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8765
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8765
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: compliance-master-api-service
spec:
  selector:
    app: compliance-master-api
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8765
  type: LoadBalancer
```

Deploy to Kubernetes:

```bash
# Create secrets
kubectl create secret generic watsonx-credentials \
  --from-literal=api-key='your-api-key' \
  --from-literal=project-id='your-project-id'

# Deploy
kubectl apply -f k8s-deployment.yaml

# Check status
kubectl get pods
kubectl get services

# View logs
kubectl logs -f deployment/compliance-master-api
```

#### Option 3: IBM Cloud Code Engine

```bash
# Install IBM Cloud CLI
# https://cloud.ibm.com/docs/cli

# Login
ibmcloud login

# Target Code Engine
ibmcloud target -g <resource-group> -r <region>

# Create Code Engine project
ibmcloud ce project create --name compliance-master

# Build and deploy
ibmcloud ce application create \
  --name compliance-master-api \
  --build-source . \
  --port 8765 \
  --min-scale 1 \
  --max-scale 5 \
  --cpu 1 \
  --memory 2G \
  --env-from-secret watsonx-credentials

# Get application URL
ibmcloud ce application get --name compliance-master-api
```

### Reverse Proxy Configuration (Nginx)

Create `/etc/nginx/sites-available/compliance-master`:

```nginx
upstream compliance_master {
    server 127.0.0.1:8765;
}

server {
    listen 80;
    server_name api.compliance-master.com;

    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.compliance-master.com;

    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/api.compliance-master.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.compliance-master.com/privkey.pem;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;

    # Proxy settings
    location / {
        proxy_pass http://compliance_master;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts for large files
        proxy_connect_timeout 300s;
        proxy_send_timeout 300s;
        proxy_read_timeout 300s;
        
        # Upload size limit
        client_max_body_size 50M;
    }

    # Health check endpoint
    location /health {
        proxy_pass http://compliance_master/health;
        access_log off;
    }
}
```

Enable the site:

```bash
sudo ln -s /etc/nginx/sites-available/compliance-master /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### SSL Certificate (Let's Encrypt)

```bash
# Install Certbot
sudo apt-get update
sudo apt-get install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d api.compliance-master.com

# Auto-renewal is configured by default
# Test renewal
sudo certbot renew --dry-run
```

## WatsonX Orchestrate Integration

### Export OpenAPI Specification

```bash
# Start your API locally or access production URL
curl http://localhost:8765/openapi.json > compliance_master_openapi.json
```

### Import to WatsonX Orchestrate

1. **Login to WatsonX Orchestrate**
   - Navigate to https://www.ibm.com/products/watsonx-orchestrate
   - Login with your IBM Cloud credentials

2. **Add Skills**
   - Click on "Skills" in the left sidebar
   - Click "Add Skills" button
   - Select "Import from OpenAPI"

3. **Upload Specification**
   - Upload the `compliance_master_openapi.json` file
   - Or provide the URL: `https://your-domain.com/openapi.json`

4. **Configure Connection**
   - **Base URL**: Your API URL (e.g., https://api.compliance-master.com)
   - **Authentication**: None (or add if you've implemented auth)
   - **Headers**: Add any required headers

5. **Test Skills**
   - Use the skill tester to verify each operation
   - Test with sample documents

6. **Create Automation**
   - Navigate to "Automations"
   - Create new automation workflow
   - Add the imported skills
   - Configure the workflow logic

### Available Skills

After import, you'll have these skills:

- **parseDocument**: Parse document and extract text
- **extractFields**: Extract specific fields using AI
- **generateISOTemplate**: Generate ISO template
- **processComplete**: Complete end-to-end processing

### Example Automation Workflow

```
1. Trigger: New document uploaded to SharePoint
2. Action: parseDocument skill
3. Action: extractFields skill
4. Action: generateISOTemplate skill
5. Action: Save generated template to SharePoint
6. Action: Send notification email
```

## Monitoring and Maintenance

### Health Checks

```bash
# Check API health
curl http://localhost:8765/health

# Expected response
{
  "status": "healthy",
  "version": "1.0.0"
}
```

### Logging

Configure logging in production:

```python
# In main.py
import logging
from logging.handlers import RotatingFileHandler

# Configure file handler
handler = RotatingFileHandler(
    'logs/app.log',
    maxBytes=10485760,  # 10MB
    backupCount=10
)
handler.setFormatter(logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
))

logging.basicConfig(
    level=logging.INFO,
    handlers=[handler]
)
```

### Monitoring Tools

1. **Application Performance Monitoring (APM)**
   ```bash
   # Install New Relic APM
   pip install newrelic
   
   # Run with New Relic
   NEW_RELIC_CONFIG_FILE=newrelic.ini newrelic-admin run-program uvicorn main:app
   ```

2. **Prometheus Metrics**
   ```bash
   # Install prometheus client
   pip install prometheus-fastapi-instrumentator
   ```

3. **Log Aggregation**
   - Use ELK Stack (Elasticsearch, Logstash, Kibana)
   - Or use cloud services (IBM Log Analysis, Datadog, etc.)

### Backup and Recovery

```bash
# Backup configuration
tar -czf backup_$(date +%Y%m%d).tar.gz .env config.py

# Restore configuration
tar -xzf backup_YYYYMMDD.tar.gz
```

### Updates and Upgrades

```bash
# Update dependencies
pip list --outdated
pip install --upgrade package-name

# Update requirements.txt
pip freeze > requirements.txt

# Test after updates
pytest
```

### Performance Tuning

1. **Increase workers**
   ```bash
   # Formula: (2 x $num_cores) + 1
   gunicorn main:app --workers 5
   ```

2. **Enable caching**
   - Add Redis for caching parsed documents
   - Cache LLM responses for common queries

3. **Load balancing**
   - Use Nginx or HAProxy for load balancing
   - Deploy multiple instances

### Security Best Practices

1. **API Authentication**
   - Implement API key authentication
   - Use OAuth 2.0 for user authentication

2. **Rate Limiting**
   ```python
   from slowapi import Limiter
   from slowapi.util import get_remote_address
   
   limiter = Limiter(key_func=get_remote_address)
   app.state.limiter = limiter
   ```

3. **Input Validation**
   - Already implemented via Pydantic models
   - Add file size limits
   - Validate file types

4. **HTTPS Only**
   - Force HTTPS in production
   - Use HSTS headers

5. **Regular Updates**
   - Keep dependencies updated
   - Monitor security advisories

### Troubleshooting

**High Memory Usage**
- Reduce MAX_NEW_TOKENS parameter
- Implement request queuing
- Add more workers with less memory per worker

**Slow Response Times**
- Check WatsonX API latency
- Optimize document parsing
- Implement caching
- Add timeout configurations

**Connection Errors to WatsonX**
- Verify API key and project ID
- Check network connectivity
- Review rate limits
- Ensure correct region URL

## Support and Resources

- **API Documentation**: http://localhost:8765/docs
- **IBM WatsonX Docs**: https://www.ibm.com/docs/en/watsonx-as-a-service
- **Docling Documentation**: https://ds4sd.github.io/docling/
- **FastAPI Documentation**: https://fastapi.tiangolo.com/

## License

MIT License - See LICENSE file for details

