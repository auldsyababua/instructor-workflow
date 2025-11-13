# Docker API Reference

**Purpose**: CLI commands, API endpoints, compose file schemas, and command patterns for Docker/Docker Compose operations.

**Last Updated**: 2025-11-06

---

## Essential Docker CLI Commands

### Container Management

**List containers**:
```bash
# Running containers only
docker ps

# All containers (including stopped)
docker ps -a

# Filter by label
docker ps --filter "label=traefik.enable=true"

# Custom format
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
```

**Start/Stop/Restart**:
```bash
# Start container
docker start <container-name>

# Stop gracefully (sends SIGTERM, waits for stop_grace_period)
docker stop <container-name>

# Restart
docker restart <container-name>

# Kill immediately (SIGKILL, no graceful shutdown)
docker kill <container-name>
```

**Inspect containers**:
```bash
# Full JSON output
docker inspect <container-name>

# Extract specific field
docker inspect --format='{{.State.Status}}' <container-name>

# Get IP address
docker inspect --format='{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' <container-name>
```

**Execute commands**:
```bash
# Interactive shell
docker exec -it <container-name> /bin/bash

# Single command
docker exec <container-name> ls /app

# As specific user
docker exec -u 1000:1000 <container-name> whoami
```

**View logs**:
```bash
# Follow logs (like tail -f)
docker logs -f <container-name>

# Last 100 lines
docker logs --tail=100 <container-name>

# Timestamp each line
docker logs --timestamps <container-name>

# Since specific time
docker logs --since=2h <container-name>
```

### Image Management

**Build images**:
```bash
# Build from Dockerfile
docker build -t myapp:1.0.0 .

# With build args
docker build --build-arg NODE_ENV=production -t myapp:1.0.0 .

# No cache (force rebuild)
docker build --no-cache -t myapp:1.0.0 .

# Multi-platform
docker buildx build --platform linux/amd64,linux/arm64 -t myapp:1.0.0 --push .
```

**List/Remove images**:
```bash
# List images
docker images

# Remove image
docker rmi myapp:1.0.0

# Remove all unused images
docker image prune -a
```

**Tag and push**:
```bash
# Tag image
docker tag myapp:1.0.0 registry.example.com/myapp:1.0.0

# Push to registry
docker push registry.example.com/myapp:1.0.0
```

### Volume Management

**List volumes**:
```bash
# All volumes
docker volume ls

# With filters
docker volume ls --filter "dangling=true"
```

**Inspect/Create/Remove**:
```bash
# Create volume
docker volume create mydata

# Inspect volume
docker volume inspect mydata

# Remove volume
docker volume rm mydata

# Remove all unused volumes
docker volume prune
```

**Backup/Restore volumes**:
```bash
# Backup
docker run --rm -v mydata:/data -v $(pwd):/backup alpine tar czf /backup/mydata.tar.gz -C /data .

# Restore
docker run --rm -v mydata:/data -v $(pwd):/backup alpine tar xzf /backup/mydata.tar.gz -C /data
```

### Network Management

**List networks**:
```bash
docker network ls
```

**Create/Inspect/Remove**:
```bash
# Create network
docker network create my-network

# With specific subnet
docker network create --subnet=172.20.0.0/16 my-network

# Inspect network
docker network inspect my-network

# Remove network
docker network rm my-network
```

**Connect/Disconnect containers**:
```bash
# Connect container to network
docker network connect my-network <container-name>

# Disconnect
docker network disconnect my-network <container-name>
```

---

## Docker Compose Commands

### Service Management

**Start services**:
```bash
# Start all services (detached)
docker-compose up -d

# Start specific services
docker-compose up -d web db

# With build
docker-compose up -d --build

# Force recreate
docker-compose up -d --force-recreate
```

**Stop/Down**:
```bash
# Stop services (keeps containers)
docker-compose stop

# Stop and remove containers
docker-compose down

# Remove volumes too
docker-compose down -v

# Remove images too
docker-compose down --rmi all
```

**View status**:
```bash
# List services
docker-compose ps

# View logs
docker-compose logs -f --tail=100

# Logs for specific service
docker-compose logs -f web
```

**Scale services**:
```bash
# Run 3 instances of web service
docker-compose up -d --scale web=3
```

### Configuration Management

**Validate compose file**:
```bash
# Check syntax
docker-compose config

# Resolve and display full config
docker-compose config --resolve-image-digests

# Use specific file
docker-compose -f docker-compose.prod.yml config
```

**Override files**:
```bash
# Use multiple files (merged left-to-right)
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

### Service Operations

**Execute commands**:
```bash
# Run command in running service
docker-compose exec web /bin/bash

# Run one-off command (creates new container)
docker-compose run --rm web python manage.py migrate
```

**Restart services**:
```bash
# Restart all
docker-compose restart

# Restart specific service
docker-compose restart web
```

---

## Docker Compose File Reference

### Version 3.8 Schema

**Basic structure**:
```yaml
version: '3.8'

services:
  # Service definitions
  web:
    image: nginx:alpine
    # ... config ...

networks:
  # Network definitions
  frontend:
    driver: bridge

volumes:
  # Volume definitions
  data:
    driver: local

configs:
  # Config file definitions (Swarm only)
  app_config:
    file: ./config.yml

secrets:
  # Secret definitions (Swarm only)
  db_password:
    external: true
```

### Service Configuration Options

**Image and build**:
```yaml
services:
  app:
    # Use pre-built image
    image: myapp:1.0.0

    # Or build from Dockerfile
    build:
      context: .
      dockerfile: Dockerfile.prod
      args:
        NODE_ENV: production
      target: production  # Multi-stage build target
```

**Environment variables**:
```yaml
services:
  app:
    environment:
      # Inline definition
      NODE_ENV: production
      LOG_LEVEL: info

      # From host environment
      API_KEY: \${API_KEY}

    # Or from file
    env_file:
      - .env
      - .env.production
```

**Ports and networking**:
```yaml
services:
  web:
    ports:
      # host:container
      - "8080:80"

      # Range
      - "8000-8005:8000-8005"

      # UDP
      - "53:53/udp"

    expose:
      # Internal ports (not published to host)
      - "8080"

    networks:
      - frontend
      - backend

networks:
  frontend:
  backend:
    internal: true  # No external access
```

**Volumes**:
```yaml
services:
  db:
    volumes:
      # Named volume
      - db_data:/var/lib/mysql

      # Bind mount (relative path)
      - ./config:/etc/mysql/conf.d:ro

      # Bind mount (absolute path)
      - /srv/data:/data

      # tmpfs mount
      - type: tmpfs
        target: /tmp

volumes:
  db_data:
```

**Resource limits**:
```yaml
services:
  app:
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 4G
        reservations:
          cpus: '0.5'
          memory: 1G

      # Swarm mode only
      replicas: 3
      placement:
        constraints:
          - node.role == worker
```

**Health checks**:
```yaml
services:
  web:
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 60s

    # Disable inherited healthcheck
    healthcheck:
      disable: true
```

**Dependencies**:
```yaml
services:
  web:
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_started

  db:
    healthcheck:
      test: ["CMD", "pg_isready"]
```

**Logging**:
```yaml
services:
  app:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

    # Or use external logging driver
    logging:
      driver: "syslog"
      options:
        syslog-address: "tcp://192.168.0.42:123"
```

**Restart policies**:
```yaml
services:
  app:
    restart: unless-stopped
    # Options: "no", "always", "on-failure", "unless-stopped"
```

**Labels**:
```yaml
services:
  web:
    labels:
      # Traefik integration
      traefik.enable: "true"
      traefik.http.routers.web.rule: "Host(`example.com`)"
      traefik.http.services.web.loadbalancer.server.port: "80"

      # Prometheus monitoring
      prometheus.scrape: "true"
      prometheus.port: "9090"
```

---

## Docker HTTP API

**Base URL**: `http://localhost/v1.43` (Unix socket: `/var/run/docker.sock`)

### Container Operations

**List containers**:
```bash
curl --unix-socket /var/run/docker.sock http://localhost/v1.43/containers/json
```

**Create container**:
```bash
curl --unix-socket /var/run/docker.sock \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{"Image":"nginx:alpine","Name":"my-nginx"}' \
  http://localhost/v1.43/containers/create
```

**Start container**:
```bash
curl --unix-socket /var/run/docker.sock \
  -X POST \
  http://localhost/v1.43/containers/my-nginx/start
```

**Inspect container**:
```bash
curl --unix-socket /var/run/docker.sock \
  http://localhost/v1.43/containers/my-nginx/json
```

**Container stats (streaming)**:
```bash
curl --unix-socket /var/run/docker.sock \
  http://localhost/v1.43/containers/my-nginx/stats
```

### Image Operations

**List images**:
```bash
curl --unix-socket /var/run/docker.sock \
  http://localhost/v1.43/images/json
```

**Pull image**:
```bash
curl --unix-socket /var/run/docker.sock \
  -X POST \
  http://localhost/v1.43/images/create?fromImage=nginx&tag=alpine
```

**Build image**:
```bash
tar czf - Dockerfile | curl --unix-socket /var/run/docker.sock \
  -X POST \
  -H "Content-Type: application/x-tar" \
  --data-binary @- \
  http://localhost/v1.43/build?t=myapp:1.0.0
```

---

## GPU Configuration (NVIDIA)

### Docker Runtime Setup

**Install NVIDIA Container Toolkit**:
```bash
# Add repository
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg

# Install toolkit
sudo apt-get update
sudo apt-get install -y nvidia-container-toolkit

# Configure Docker
sudo nvidia-ctk runtime configure --runtime=docker

# Restart Docker
sudo systemctl restart docker
```

**Compose file with GPU**:
```yaml
services:
  ml-app:
    image: pytorch/pytorch:latest
    runtime: nvidia
    environment:
      NVIDIA_VISIBLE_DEVICES: all
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1  # Use 1 GPU
              capabilities: [gpu]
```

**Test GPU access**:
```bash
docker run --rm --gpus all nvidia/cuda:12.3.0-base-ubuntu22.04 nvidia-smi
```

---

## Traefik Label Patterns

### Basic HTTP Service

```yaml
services:
  web:
    labels:
      traefik.enable: "true"
      traefik.http.routers.web.rule: "Host(`example.com`)"
      traefik.http.routers.web.entrypoints: "websecure"
      traefik.http.routers.web.tls: "true"
      traefik.http.routers.web.tls.certresolver: "letsencrypt"
      traefik.http.services.web.loadbalancer.server.port: "80"
```

### Path-Based Routing

```yaml
services:
  api:
    labels:
      traefik.enable: "true"
      traefik.http.routers.api.rule: "Host(`example.com`) && PathPrefix(`/api`)"
      traefik.http.routers.api.middlewares: "api-stripprefix"
      traefik.http.middlewares.api-stripprefix.stripprefix.prefixes: "/api"
      traefik.http.services.api.loadbalancer.server.port: "8080"
```

### Basic Auth Middleware

```yaml
services:
  admin:
    labels:
      traefik.enable: "true"
      traefik.http.routers.admin.rule: "Host(`admin.example.com`)"
      traefik.http.routers.admin.middlewares: "admin-auth"
      traefik.http.middlewares.admin-auth.basicauth.users: "admin:\$apr1\$..hash.."
```

---

## Expected Responses

### Successful Operations

**docker ps** (no containers):
```
CONTAINER ID   IMAGE     COMMAND   CREATED   STATUS    PORTS     NAMES
```

**docker-compose up -d** (success):
```
Creating network "myapp_default" with the default driver
Creating myapp_db_1  ... done
Creating myapp_web_1 ... done
```

**docker logs** (healthy service):
```
[2025-11-06 12:00:00] INFO: Server started on port 8080
[2025-11-06 12:00:01] INFO: Connected to database
[2025-11-06 12:00:01] INFO: Application ready
```

### Error Responses

**Port already in use**:
```
Error starting userland proxy: listen tcp4 0.0.0.0:8080: bind: address already in use
```

**Image not found**:
```
Error response from daemon: pull access denied for myapp, repository does not exist
```

**Compose syntax error**:
```
ERROR: yaml.parser.ParserError: while parsing a block mapping
  in "./docker-compose.yml", line 5, column 3
```

---

## Quick Command Reference

**Lifecycle**:
- `docker-compose up -d` - Start all services
- `docker-compose down` - Stop and remove containers
- `docker-compose restart` - Restart services
- `docker-compose stop` - Stop without removing

**Logs and status**:
- `docker-compose logs -f` - Follow logs
- `docker-compose ps` - List services
- `docker stats` - Resource usage

**Cleanup**:
- `docker system prune` - Remove unused data
- `docker volume prune` - Remove unused volumes
- `docker image prune -a` - Remove all unused images

**Debugging**:
- `docker exec -it <name> /bin/bash` - Interactive shell
- `docker inspect <name>` - Full container details
- `docker logs <name>` - View container logs
