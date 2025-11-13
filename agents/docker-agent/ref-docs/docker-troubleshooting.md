# Docker Troubleshooting Guide

**Purpose**: Diagnostic procedures, common errors, and resolutions for Docker/Docker Compose issues.

**Last Updated**: 2025-11-06

---

## Container Startup Failures

### Container Exits Immediately

**Symptom**: Container starts then immediately exits with status code

**Diagnosis**:
```bash
# Check exit code and reason
docker ps -a --filter "name=myapp"

# View logs
docker logs myapp

# Inspect detailed state
docker inspect --format='{{.State.ExitCode}}: {{.State.Error}}' myapp
```

**Common Causes & Resolutions**:

**Exit Code 1 (General error)**:
- **Cause**: Application crashed or config error
- **Resolution**: Check logs for error messages, validate config files

**Exit Code 126 (Permission denied)**:
- **Cause**: Entrypoint script not executable
- **Resolution**: `chmod +x entrypoint.sh` in Dockerfile or host

**Exit Code 127 (Command not found)**:
- **Cause**: Entrypoint or CMD references non-existent binary
- **Resolution**: Verify binary exists in image, check PATH

**Exit Code 137 (SIGKILL - OOM)**:
- **Cause**: Container killed by OOM (out of memory)
- **Resolution**: Increase memory limit, fix memory leaks
```yaml
deploy:
  resources:
    limits:
      memory: 4G  # Increase from 2G
```

**Exit Code 143 (SIGTERM)**:
- **Cause**: Container received SIGTERM (normal shutdown or timeout)
- **Resolution**: If unexpected, increase `stop_grace_period`

---

### Port Binding Failures

**Symptom**: `Error starting userland proxy: listen tcp 0.0.0.0:8080: bind: address already in use`

**Diagnosis**:
```bash
# Find what's using the port
sudo lsof -i :8080
sudo netstat -tlnp | grep :8080
sudo ss -tlnp | grep :8080

# Docker-specific check
docker ps --format "{{.Names}}: {{.Ports}}"
```

**Resolutions**:

**Option 1 - Change port mapping**:
```yaml
services:
  app:
    ports:
      - "8081:8080"  # Use different host port
```

**Option 2 - Stop conflicting service**:
```bash
# Kill process using port
sudo kill $(sudo lsof -t -i:8080)

# Or stop Docker container
docker stop <conflicting-container>
```

**Option 3 - Use dynamic port**:
```yaml
services:
  app:
    ports:
      - "8080"  # Docker assigns random host port
```

---

### Health Check Failures

**Symptom**: Container shows as "unhealthy" in `docker ps`

**Diagnosis**:
```bash
# View health check logs
docker inspect --format='{{json .State.Health}}' myapp | jq

# Test health check manually
docker exec myapp curl -f http://localhost:8080/health
```

**Common Causes & Resolutions**:

**Health check command fails**:
- **Cause**: Command not found in container (e.g., `curl` not installed)
- **Resolution**: Install required tools or use different check method
```dockerfile
# Install curl in Alpine
RUN apk add --no-cache curl

# Or use wget (usually pre-installed)
healthcheck:
  test: ["CMD", "wget", "--spider", "-q", "http://localhost/health"]
```

**Timeout too short**:
- **Cause**: App takes longer than timeout to respond
- **Resolution**: Increase timeout value
```yaml
healthcheck:
  timeout: 30s  # Increase from 10s
```

**Start period too short**:
- **Cause**: App not fully initialized before health checks start
- **Resolution**: Increase start_period
```yaml
healthcheck:
  start_period: 120s  # Increase from 60s
```

**Wrong endpoint or port**:
- **Cause**: Health check hits wrong URL
- **Resolution**: Verify endpoint and port
```bash
# Test from inside container
docker exec myapp curl -v http://localhost:8080/health
```

---

## Network Issues

### Cannot Connect to Other Containers

**Symptom**: `curl: (6) Could not resolve host: db` or connection refused

**Diagnosis**:
```bash
# Check if containers on same network
docker inspect <container1> | jq '.[0].NetworkSettings.Networks'
docker inspect <container2> | jq '.[0].NetworkSettings.Networks'

# Test DNS resolution
docker exec myapp nslookup db
docker exec myapp ping -c 3 db

# Test port connectivity
docker exec myapp nc -zv db 5432
```

**Resolutions**:

**Different networks**:
```yaml
services:
  web:
    networks:
      - frontend  # Add missing network
      - backend

  db:
    networks:
      - backend
```

**Wrong service name**:
```yaml
# Use service name from compose file
DATABASE_URL: postgresql://db:5432/mydb  # "db" must match service name
```

**Port not exposed**:
```yaml
services:
  db:
    expose:
      - "5432"  # Expose port to other containers
```

**Container not started**:
```bash
# Ensure dependency is running
docker-compose ps db
docker-compose logs db
```

---

### Traefik Routing 404/502

**Symptom**: Traefik returns 404 Not Found or 502 Bad Gateway

**Diagnosis**:
```bash
# Check Traefik dashboard (if enabled)
curl http://localhost:8080/api/http/routers

# Inspect container labels
docker inspect myapp | jq '.[0].Config.Labels'

# Check container is on correct network
docker inspect myapp | jq '.[0].NetworkSettings.Networks | keys'

# Test service directly (bypass Traefik)
docker exec -it traefik wget -O- http://myapp:80
```

**Common Causes & Resolutions**:

**404 - Router not found**:
- **Cause**: Labels missing or incorrect
- **Resolution**: Verify Traefik labels
```yaml
labels:
  traefik.enable: "true"
  traefik.http.routers.myapp.rule: "Host(`example.com`)"
```

**404 - Wrong network**:
- **Cause**: Service not on Traefik's network
- **Resolution**: Add service to Traefik network
```yaml
services:
  myapp:
    networks:
      - traefik_network  # Must match Traefik's network

networks:
  traefik_network:
    external: true
```

**502 - Service unreachable**:
- **Cause**: Wrong port in loadbalancer config
- **Resolution**: Match service's actual port
```yaml
labels:
  traefik.http.services.myapp.loadbalancer.server.port: "8080"  # Match app's port
```

**502 - Service not healthy**:
- **Cause**: Container unhealthy or crashed
- **Resolution**: Check container status and logs
```bash
docker ps -a | grep myapp
docker logs myapp
```

---

## Volume and Data Issues

### Permission Denied in Volume

**Symptom**: `Permission denied` errors when writing to mounted volume

**Diagnosis**:
```bash
# Check volume mount permissions
docker exec myapp ls -la /data

# Check host directory permissions (bind mount)
ls -la /host/path/to/data

# Check container user
docker exec myapp id
```

**Resolutions**:

**UID/GID mismatch**:
```yaml
# Run container as specific user matching host
services:
  app:
    user: "1000:1000"  # Match host user's UID:GID
```

```dockerfile
# Or set ownership in Dockerfile
RUN chown -R 1000:1000 /data
USER 1000:1000
```

**SELinux blocking access**:
```yaml
# Add :z or :Z suffix (SELinux relabeling)
volumes:
  - ./data:/data:z  # Shared label
  - ./config:/config:Z  # Private label
```

**Read-only mount**:
```yaml
# Remove :ro flag if write access needed
volumes:
  - ./data:/data  # Remove :ro
```

---

### Volume Not Persisting Data

**Symptom**: Data lost after container restart

**Diagnosis**:
```bash
# Check if volume is defined
docker volume ls | grep myapp

# Inspect volume
docker volume inspect myapp_data

# Check if container uses volume
docker inspect myapp | jq '.[0].Mounts'
```

**Resolutions**:

**Anonymous volume**:
```yaml
# Use named volume instead
services:
  db:
    volumes:
      - postgres_data:/var/lib/postgresql/data  # Named volume

volumes:
  postgres_data:  # Define at top level
```

**Wrong path**:
```yaml
# Verify path matches application's data directory
volumes:
  - db_data:/var/lib/postgresql/data  # PostgreSQL default path
```

**Volume removed on down**:
```bash
# Don't use -v flag when stopping
docker-compose down  # Keeps volumes
# NOT: docker-compose down -v  # Removes volumes
```

---

## Build Failures

### Image Build Fails

**Symptom**: `docker build` or `docker-compose build` fails with error

**Diagnosis**:
```bash
# Build with verbose output
docker build --progress=plain --no-cache -t myapp .

# Check Dockerfile syntax
docker run --rm -i hadolint/hadolint < Dockerfile
```

**Common Causes & Resolutions**:

**Base image not found**:
```dockerfile
# Specify exact tag (not latest)
FROM node:18-alpine  # Instead of node:latest
```

**COPY source doesn't exist**:
```dockerfile
# Verify source path relative to build context
COPY package*.json ./  # Files must exist in build context
```

**RUN command fails**:
```dockerfile
# Chain commands with && and exit on error
RUN apt-get update && \
    apt-get install -y curl && \
    rm -rf /var/lib/apt/lists/*
```

**Build context too large**:
```bash
# Add .dockerignore file
node_modules
.git
*.log
.env
```

---

## Resource Issues

### Container Out of Memory (OOM)

**Symptom**: Container killed with exit code 137, `docker inspect` shows OOMKilled: true

**Diagnosis**:
```bash
# Check if OOM killed
docker inspect --format='{{.State.OOMKilled}}' myapp

# Check memory limits
docker inspect --format='{{.HostConfig.Memory}}' myapp

# Monitor memory usage
docker stats myapp
```

**Resolutions**:

**Increase memory limit**:
```yaml
services:
  app:
    deploy:
      resources:
        limits:
          memory: 4G  # Increase limit
```

**Fix memory leak**:
- Profile application to find leak
- Restart container periodically as workaround
```yaml
healthcheck:
  test: ["CMD-SHELL", "if [ $(ps aux | awk '{sum+=$6} END {print sum}') -gt 3800000 ]; then exit 1; fi"]
```

**Reduce memory usage**:
- Optimize application code
- Use Alpine base images
- Disable debug logging in production

---

### High CPU Usage

**Symptom**: Container consuming excessive CPU

**Diagnosis**:
```bash
# Monitor CPU usage
docker stats myapp

# Check processes inside container
docker exec myapp ps aux

# View CPU limit
docker inspect --format='{{.HostConfig.NanoCpus}}' myapp
```

**Resolutions**:

**Set CPU limit**:
```yaml
services:
  app:
    deploy:
      resources:
        limits:
          cpus: '2.0'  # Max 2 cores
```

**Identify hot loop**:
```bash
# Profile application
docker exec myapp top

# Check for stuck processes
docker exec myapp strace -p <PID>
```

---

## Disk Space Issues

### No Space Left on Device

**Symptom**: `ERROR: no space left on device` during build or run

**Diagnosis**:
```bash
# Check Docker disk usage
docker system df

# Detailed breakdown
docker system df -v

# Check host disk space
df -h /var/lib/docker
```

**Resolutions**:

**Clean up unused resources**:
```bash
# Remove unused images, containers, volumes
docker system prune -a --volumes

# Or selectively
docker image prune -a  # Remove unused images
docker volume prune    # Remove unused volumes
docker container prune # Remove stopped containers
```

**Increase Docker storage**:
```bash
# Check current storage driver
docker info | grep "Storage Driver"

# For overlay2, clean up old layers
docker system prune -a
```

**Configure log rotation**:
```yaml
services:
  app:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

---

## Docker Compose Issues

### Service Dependency Not Ready

**Symptom**: Service starts before dependency is ready, causing connection errors

**Resolution**:

**Use health checks with depends_on**:
```yaml
services:
  web:
    depends_on:
      db:
        condition: service_healthy

  db:
    healthcheck:
      test: ["CMD", "pg_isready", "-U", "postgres"]
      interval: 5s
      retries: 5
```

**Implement retry logic in application**:
```javascript
async function connectWithRetry(maxRetries = 5) {
  for (let i = 0; i < maxRetries; i++) {
    try {
      await db.connect();
      return;
    } catch (err) {
      console.log(`Connection attempt ${i+1} failed, retrying...`);
      await sleep(5000);
    }
  }
  throw new Error('Failed to connect after retries');
}
```

---

### Environment Variables Not Working

**Symptom**: Container can't see environment variables from `.env` file

**Diagnosis**:
```bash
# Check if .env file exists
ls -la .env

# View environment variables in container
docker exec myapp env

# Check compose config resolution
docker-compose config | grep -A 5 environment
```

**Resolutions**:

**Verify .env file location**:
```bash
# Must be in same directory as docker-compose.yml
ls .env docker-compose.yml
```

**Check variable syntax**:
```yaml
# Correct syntax
environment:
  API_KEY: \${API_KEY}  # From .env
  LOG_LEVEL: info       # Hardcoded
```

**Restart after .env changes**:
```bash
# Restart to pick up new variables
docker-compose down
docker-compose up -d
```

---

## Quick Diagnostic Commands

**Container not starting**:
```bash
docker logs <container>
docker inspect <container> | jq '.State'
```

**Network issues**:
```bash
docker exec <container> ping <other-container>
docker inspect <container> | jq '.[0].NetworkSettings.Networks'
```

**Performance problems**:
```bash
docker stats
docker system df
```

**Configuration validation**:
```bash
docker-compose config
docker run --rm -i hadolint/hadolint < Dockerfile
```

**Complete cleanup**:
```bash
docker-compose down -v
docker system prune -a --volumes
```
