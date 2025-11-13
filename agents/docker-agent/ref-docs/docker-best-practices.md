# Docker Best Practices

**Purpose**: Configuration management, performance optimization, security patterns, and reliability guidelines for Docker/Docker Compose deployments.

**Last Updated**: 2025-11-06

---

## Configuration Management

### Compose File Organization

**Multi-File Strategy**:
```yaml
# Base configuration (docker-compose.yml)
version: '3.8'
services:
  app:
    image: myapp:latest

# Development overrides (docker-compose.override.yml)
services:
  app:
    build: .
    volumes:
      - ./src:/app/src

# Production overrides (docker-compose.prod.yml)
services:
  app:
    restart: unless-stopped
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 4G
```

**Deployment**:
```bash
# Development (uses .yml + .override.yml automatically)
docker-compose up -d

# Production
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

### Environment Variables

**Best Practices**:
- Store secrets in `.env` file (add to `.gitignore`)
- Use `\${VAR:-default}` syntax for optional variables with defaults
- Document all required variables in `.env.example`
- Never commit real credentials to Git

**Example .env file**:
```bash
# Database credentials
POSTGRES_PASSWORD=<secret>
POSTGRES_USER=myapp
POSTGRES_DB=myapp_prod

# API keys
API_KEY=\${API_KEY}
OPENAI_API_KEY=\${OPENAI_API_KEY}

# Application config
APP_ENV=production
LOG_LEVEL=info
```

###Volume Management

**Named Volumes vs Bind Mounts**:
```yaml
services:
  db:
    volumes:
      # Named volume (managed by Docker, survives container removal)
      - postgres_data:/var/lib/postgresql/data

      # Bind mount (direct host path access)
      - ./backups:/backups:ro  # Read-only for safety

      # Anonymous volume (deleted with container)
      - /tmp/cache

volumes:
  postgres_data:
    driver: local
```

**Volume Best Practices**:
- Use named volumes for data persistence
- Use bind mounts for configuration files and development
- Add `:ro` (read-only) flag where possible for security
- Document volume paths in compose file comments

---

## Performance Optimization

### Resource Limits

**Always set resource limits** to prevent runaway containers:
```yaml
services:
  app:
    deploy:
      resources:
        limits:
          cpus: '2.0'          # Max 2 CPU cores
          memory: 4G           # Max 4GB RAM
        reservations:
          cpus: '0.5'          # Guaranteed 0.5 cores
          memory: 1G           # Guaranteed 1GB RAM
```

**When to use limits**:
- All production services (prevent OOM, CPU starvation)
- Memory-hungry services (databases, ML models)
- Development (optional, helps test resource constraints)

### Build Optimization

**Multi-Stage Builds**:
```dockerfile
# Build stage
FROM node:18 AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --production=false
COPY . .
RUN npm run build

# Production stage
FROM node:18-alpine
WORKDIR /app
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
CMD ["node", "dist/index.js"]
```

**Benefits**:
- Smaller final image (no build tools)
- Faster deployments (less data to transfer)
- More secure (fewer attack vectors)

### Layer Caching

**Order matters** - put frequently changing files LAST:
```dockerfile
# Bad - every code change invalidates all layers
COPY . /app
RUN npm install

# Good - npm install only re-runs when package.json changes
COPY package*.json /app/
RUN npm install
COPY . /app
```

---

## Reliability Patterns

### Health Checks

**Always define health checks** for production services:
```yaml
services:
  app:
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
      interval: 30s        # Check every 30 seconds
      timeout: 10s         # Fail if takes >10s
      retries: 3           # Mark unhealthy after 3 failures
      start_period: 60s    # Grace period for app startup
```

**Common health check patterns**:
- HTTP endpoint: `curl -f http://localhost/health`
- TCP port: `nc -z localhost 5432`
- Process check: `pgrep -f myapp`
- Custom script: `["/app/health-check.sh"]`

### Restart Policies

**Choose appropriate restart behavior**:
```yaml
services:
  critical_service:
    restart: unless-stopped  # Restart always (even after reboot)

  batch_job:
    restart: on-failure      # Restart only if crashed

  dev_service:
    restart: "no"            # Never restart (debugging)
```

---

## Security Hardening

### Run as Non-Root User

**Never run containers as root** in production:
```dockerfile
# Create non-root user
RUN addgroup -S appgroup && adduser -S appuser -G appgroup
USER appuser

# Or use numeric UID (better for security scanners)
USER 1000:1000
```

```yaml
services:
  app:
    user: "1000:1000"  # Run as UID 1000, GID 1000
```

### Drop Capabilities

**Remove unnecessary Linux capabilities**:
```yaml
services:
  app:
    cap_drop:
      - ALL
    cap_add:
      - NET_BIND_SERVICE  # Only if binding to port <1024
```

### Read-Only Filesystem

**Make container filesystem read-only** where possible:
```yaml
services:
  app:
    read_only: true
    tmpfs:
      - /tmp        # Writable temp directory
      - /var/run    # Writable runtime directory
```

---

## Quick Reference Checklist

Before deploying to production, verify:

- [ ] All images use specific versions (not `latest`)
- [ ] Resource limits set (CPU, memory)
- [ ] Health checks defined for all services
- [ ] Restart policies configured
- [ ] Secrets not hardcoded (use `.env` or secrets manager)
- [ ] Containers run as non-root user
- [ ] Log rotation configured
- [ ] Volumes defined for persistent data
- [ ] Backup strategy documented
- [ ] Network isolation where appropriate
- [ ] Security scan passed (no critical CVEs)
