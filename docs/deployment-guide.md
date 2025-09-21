# Beacon Travel Agent - Deployment Guide

## Prerequisites

### System Requirements

- **Operating System**: Linux, macOS, or Windows
- **Python**: 3.11.6 or higher
- **Node.js**: 18.0 or higher
- **Memory**: Minimum 4GB RAM
- **Storage**: 2GB available space
- **Network**: Internet connection for API calls

### Current System Status

- **All Agents**: ✅ Running and healthy
- **UI**: ✅ Fully functional on port 3000
- **Real Data**: ✅ BrightData API integration working
- **Booking Links**: ✅ All services have direct booking integration

### Required API Keys

1. **BrightData API Key**: For web scraping services
2. **AI21 API Key**: For AI-powered data enhancement

## Quick Start

### 1. Clone Repository

```bash
git clone https://github.com/your-org/beacon-travel-agent.git
cd beacon-travel-agent
```

### 2. Environment Setup

Create environment files for each agent:

```bash
# Copy example environment files
cp agents/flight/env_example.txt agents/flight/.env
cp agents/food/env_example.txt agents/food/.env
cp agents/stay/env_example.txt agents/stay/.env
cp agents/work/env_example.txt agents/work/.env
cp agents/leisure/env_example.txt agents/leisure/.env
cp agents/shopping/env_example.txt agents/shopping/.env
```

### 3. Configure API Keys

Edit each `.env` file with your API keys:

```bash
# Example for agents/flight/.env
AI21_API_KEY=your_ai21_api_key_here
BRIGHTDATA_API_KEY=your_brightdata_api_key_here
```

### 4. Install Dependencies

#### Backend Dependencies

```bash
# Install Python dependencies for each agent
cd agents/flight && pip install -r requirements.txt
cd ../food && pip install -r requirements.txt
cd ../stay && pip install -r requirements.txt
cd ../work && pip install -r requirements.txt
cd ../leisure && pip install -r requirements.txt
cd ../shopping && pip install -r requirements.txt
```

#### Frontend Dependencies

```bash
cd ui
npm install
```

### 5. Start Services

#### Option A: Start All Services (Recommended)

```bash
# From project root
./start_all.sh
```

#### Option B: Manual Start

```bash
# Terminal 1: Start Flight Agent
cd agents/flight && python main.py &

# Terminal 2: Start Food Agent
cd agents/food && python main.py &

# Terminal 3: Start Stay Agent
cd agents/stay && python main.py &

# Terminal 4: Start Work Agent
cd agents/work && python main.py &

# Terminal 5: Start Leisure Agent
cd agents/leisure && python main.py &

# Terminal 6: Start Shopping Agent
cd agents/shopping && python main.py &

# Terminal 7: Start UI
cd ui && npm run dev
```

### 6. Verify Deployment

Check that all services are running:

```bash
# Check agent health
curl http://localhost:8000/health  # Flight Agent
curl http://localhost:8001/health  # Food Agent
curl http://localhost:8002/health  # Leisure Agent
curl http://localhost:8003/health  # Shopping Agent
curl http://localhost:8004/health  # Stay Agent
curl http://localhost:8005/health  # Work Agent

# Check UI
curl http://localhost:3000
```

## Production Deployment

### Docker Deployment

#### 1. Create Dockerfile for Agents

```dockerfile
# agents/Dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["python", "main.py"]
```

#### 2. Create Docker Compose

```yaml
# docker-compose.yml
version: '3.8'

services:
  flight-agent:
    build: ./agents/flight
    ports:
      - "8000:8000"
    environment:
      - AI21_API_KEY=${AI21_API_KEY}
      - BRIGHTDATA_API_KEY=${BRIGHTDATA_API_KEY}
    restart: unless-stopped

  food-agent:
    build: ./agents/food
    ports:
      - "8001:8001"
    environment:
      - AI21_API_KEY=${AI21_API_KEY}
      - BRIGHTDATA_API_KEY=${BRIGHTDATA_API_KEY}
    restart: unless-stopped

  stay-agent:
    build: ./agents/stay
    ports:
      - "8004:8004"
    environment:
      - AI21_API_KEY=${AI21_API_KEY}
      - BRIGHTDATA_API_KEY=${BRIGHTDATA_API_KEY}
    restart: unless-stopped

  work-agent:
    build: ./agents/work
    ports:
      - "8005:8005"
    environment:
      - AI21_API_KEY=${AI21_API_KEY}
      - BRIGHTDATA_API_KEY=${BRIGHTDATA_API_KEY}
    restart: unless-stopped

  leisure-agent:
    build: ./agents/leisure
    ports:
      - "8002:8002"
    environment:
      - AI21_API_KEY=${AI21_API_KEY}
      - BRIGHTDATA_API_KEY=${BRIGHTDATA_API_KEY}
    restart: unless-stopped

  shopping-agent:
    build: ./agents/shopping
    ports:
      - "8003:8003"
    environment:
      - AI21_API_KEY=${AI21_API_KEY}
      - BRIGHTDATA_API_KEY=${BRIGHTDATA_API_KEY}
    restart: unless-stopped

  ui:
    build: ./ui
    ports:
      - "3000:3000"
    depends_on:
      - flight-agent
      - food-agent
      - stay-agent
      - work-agent
      - leisure-agent
      - shopping-agent
    restart: unless-stopped
```

#### 3. Deploy with Docker Compose

```bash
# Create environment file
echo "AI21_API_KEY=your_key" > .env
echo "BRIGHTDATA_API_KEY=your_key" >> .env

# Start all services
docker-compose up -d

# Check status
docker-compose ps
```

### Kubernetes Deployment

#### 1. Create Kubernetes Manifests

```yaml
# k8s/namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: beacon-travel
```

```yaml
# k8s/configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: beacon-config
  namespace: beacon-travel
data:
  AI21_API_KEY: "your_ai21_key"
  BRIGHTDATA_API_KEY: "your_brightdata_key"
```

```yaml
# k8s/flight-agent-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: flight-agent
  namespace: beacon-travel
spec:
  replicas: 2
  selector:
    matchLabels:
      app: flight-agent
  template:
    metadata:
      labels:
        app: flight-agent
    spec:
      containers:
      - name: flight-agent
        image: beacon/flight-agent:latest
        ports:
        - containerPort: 8000
        envFrom:
        - configMapRef:
            name: beacon-config
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
---
apiVersion: v1
kind: Service
metadata:
  name: flight-agent-service
  namespace: beacon-travel
spec:
  selector:
    app: flight-agent
  ports:
  - port: 8000
    targetPort: 8000
  type: ClusterIP
```

#### 2. Deploy to Kubernetes

```bash
# Apply manifests
kubectl apply -f k8s/

# Check deployment
kubectl get pods -n beacon-travel
kubectl get services -n beacon-travel
```

## Environment Configuration

### Development Environment

```bash
# .env.development
NODE_ENV=development
LOG_LEVEL=debug
API_TIMEOUT=30
CACHE_TTL=300
```

### Production Environment

```bash
# .env.production
NODE_ENV=production
LOG_LEVEL=info
API_TIMEOUT=60
CACHE_TTL=600
ENABLE_METRICS=true
```

## Monitoring and Logging

### Health Checks

```bash
# Create health check script
cat > health_check.sh << 'EOF'
#!/bin/bash
AGENTS=("8000:flight" "8001:food" "8002:leisure" "8003:shopping" "8004:stay" "8005:work")

for agent in "${AGENTS[@]}"; do
    port=$(echo $agent | cut -d: -f1)
    name=$(echo $agent | cut -d: -f2)
    
    if curl -s "http://localhost:$port/health" > /dev/null; then
        echo "✅ $name agent is healthy"
    else
        echo "❌ $name agent is down"
    fi
done
EOF

chmod +x health_check.sh
./health_check.sh
```

### Log Management

```bash
# View logs for all agents
tail -f agents/*/logs/*.log

# View specific agent logs
tail -f agents/flight/logs/flight_agent.log
```

## Performance Optimization

### 1. Resource Allocation

```bash
# Set Python memory limits
export PYTHONHASHSEED=0
export PYTHONUNBUFFERED=1

# Set Node.js memory limits
export NODE_OPTIONS="--max-old-space-size=2048"
```

### 2. Caching Configuration

```python
# Add to each agent's main.py
import os
from functools import lru_cache

# Enable response caching
CACHE_TTL = int(os.getenv('CACHE_TTL', 300))
```

### 3. Database Integration (Optional)

```python
# Add to requirements.txt
redis==4.5.0
sqlalchemy==2.0.0

# Configure Redis caching
import redis
redis_client = redis.Redis(host='localhost', port=6379, db=0)
```

## Security Configuration

### 1. API Key Security

```bash
# Use environment variables
export AI21_API_KEY="your_secure_key"
export BRIGHTDATA_API_KEY="your_secure_key"

# Never commit keys to version control
echo "*.env" >> .gitignore
echo ".env*" >> .gitignore
```

### 2. Network Security

```bash
# Configure firewall
ufw allow 3000  # UI
ufw allow 8000  # Flight Agent
ufw allow 8001  # Food Agent
ufw allow 8002  # Leisure Agent
ufw allow 8003  # Shopping Agent
ufw allow 8004  # Stay Agent
ufw allow 8005  # Work Agent
```

### 3. HTTPS Configuration

```nginx
# nginx.conf
server {
    listen 443 ssl;
    server_name your-domain.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Troubleshooting

### Common Issues

#### 1. Port Already in Use

```bash
# Find process using port
lsof -i :8000

# Kill process
kill -9 <PID>

# Or use pkill
pkill -f "python agents/flight/main.py"
```

#### 2. API Key Issues

```bash
# Check environment variables
echo $AI21_API_KEY
echo $BRIGHTDATA_API_KEY

# Test API connectivity
curl -H "Authorization: Bearer $BRIGHTDATA_API_KEY" \
     https://api.brightdata.com/request
```

#### 3. Memory Issues

```bash
# Check memory usage
free -h
ps aux --sort=-%mem | head

# Increase swap if needed
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

### Debug Mode

```bash
# Enable debug logging
export LOG_LEVEL=debug
export PYTHONPATH=.

# Run with debug output
python -u agents/flight/main.py
```

## Backup and Recovery

### 1. Configuration Backup

```bash
# Backup all configurations
tar -czf beacon-config-backup.tar.gz agents/*/.env ui/.env.local
```

### 2. Data Backup

```bash
# Backup response cache
tar -czf beacon-data-backup.tar.gz agents/*/brightdata_*_response.json
```

### 3. Recovery

```bash
# Restore configurations
tar -xzf beacon-config-backup.tar.gz

# Restart services
./start_all.sh
```

## Scaling

### Horizontal Scaling

```bash
# Run multiple instances of each agent
python agents/flight/main.py --port 8000 &
python agents/flight/main.py --port 8010 &
python agents/flight/main.py --port 8020 &
```

### Load Balancing

```nginx
# nginx load balancer configuration
upstream flight_agents {
    server localhost:8000;
    server localhost:8010;
    server localhost:8020;
}

server {
    location /api/flight/ {
        proxy_pass http://flight_agents/;
    }
}
```

This deployment guide provides comprehensive instructions for setting up the Beacon Travel Agent in various environments, from development to production scale.
