# Traefik API & CLI Reference

## Docker Labels Reference

### Router Configuration

```yaml
# Enable Traefik discovery
traefik.enable: "true"

# Router rule (Host + PathPrefix)
traefik.http.routers.NAME.rule: "Host(`workhorse.local`) && PathPrefix(`/path`)"

# Router entrypoint
traefik.http.routers.NAME.entrypoints: "web"

# Router priority (higher = evaluated first)
traefik.http.routers.NAME.priority: "100"

# Router middlewares (comma-separated)
traefik.http.routers.NAME.middlewares: "auth@docker,strip-path"

# Router TLS configuration
traefik.http.routers.NAME.tls: "true"
traefik.http.routers.NAME.tls.certresolver: "letsencrypt"
```

### Service Configuration

```yaml
# Loadbalancer backend port
traefik.http.services.NAME.loadbalancer.server.port: "8080"

# Loadbalancer backend scheme
traefik.http.services.NAME.loadbalancer.server.scheme: "http"

# Pass Host header to backend
traefik.http.services.NAME.loadbalancer.passhostheader: "true"

# Health check configuration
traefik.http.services.NAME.loadbalancer.healthcheck.path: "/health"
traefik.http.services.NAME.loadbalancer.healthcheck.interval: "30s"
traefik.http.services.NAME.loadbalancer.healthcheck.timeout: "5s"
```

### Middleware Configuration

```yaml
# BasicAuth middleware
traefik.http.middlewares.NAME.basicauth.users: "user:$$hashed$$password"
traefik.http.middlewares.NAME.basicauth.realm: "Restricted Area"

# StripPrefix middleware
traefik.http.middlewares.NAME.stripprefix.prefixes: "/api,/v1"
traefik.http.middlewares.NAME.stripprefix.forceSlash: "true"

# Headers middleware
traefik.http.middlewares.NAME.headers.customrequestheaders.X-Forwarded-Proto: "https"

# RateLimit middleware
traefik.http.middlewares.NAME.ratelimit.average: "100"
traefik.http.middlewares.NAME.ratelimit.burst: "50"
traefik.http.middlewares.NAME.ratelimit.period: "1s"

# Compress middleware
traefik.http.middlewares.NAME.compress: "true"
```

## CLI Commands

### Traefik Container Management

```bash
# Check Traefik version
docker exec traefik traefik version

# Validate static configuration
docker exec traefik traefik --configFile=/etc/traefik/traefik.yml --validate

# Health check
docker exec traefik traefik healthcheck
# Output: OK: http server is up (4 routers, 4 services, 3 middlewares)

# View static config
docker exec traefik cat /etc/traefik/traefik.yml
```

### Docker Network Inspection

```bash
# List containers on lan-open network
docker network inspect lan-open -f '{{range .Containers}}{{.Name}}: {{.IPv4Address}}{{println}}{{end}}'

# Check if service is on correct network
docker inspect SERVICE | jq '.[0].NetworkSettings.Networks | keys'
```

### Log Analysis

```bash
# Tail Traefik logs (live)
docker logs -f traefik

# Show last 100 lines
docker logs traefik --tail 100

# Filter for errors
docker logs traefik | grep -i error

# Filter for specific service
docker logs traefik | grep -i "service-name"
```

### Label Inspection

```bash
# Get all Traefik labels for a service
docker inspect SERVICE | jq '.[0].Config.Labels | with_entries(select(.key | startswith("traefik")))'

# Extract router rule for service
docker inspect SERVICE | jq -r '.[0].Config.Labels["traefik.http.routers.NAME.rule"]'

# List all enabled Traefik services
docker ps --filter "label=traefik.enable=true" --format "table {{.Names}}\t{{.Status}}"
```

## Traefik API

### API Endpoints

```bash
# Base URL: http://workhorse.local:8080/api

# Get API version
curl http://workhorse.local:8080/api/version

# List all routers
curl http://workhorse.local:8080/api/http/routers | jq

# Get specific router details
curl http://workhorse.local:8080/api/http/routers/vllm | jq

# List all services
curl http://workhorse.local:8080/api/http/services | jq

# List all middlewares
curl http://workhorse.local:8080/api/http/middlewares | jq
```

### Health & Status Checks

```bash
# Check entrypoints
curl http://workhorse.local:8080/api/entrypoints | jq

# Get overview (summary)
curl http://workhorse.local:8080/api/overview | jq

# Get raw configuration
curl http://workhorse.local:8080/api/rawdata | jq '.routers.http'
```

## Static Configuration (traefik.yml)

### Minimal LAN Configuration

```yaml
# API and Dashboard
api:
  dashboard: true
  insecure: false

# Entrypoints
entryPoints:
  web:
    address: ":80"
  metrics:
    address: ":8082"

# Providers
providers:
  docker:
    endpoint: "unix:///var/run/docker.sock"
    watch: true
    exposedByDefault: false
    network: lan-open
  
  file:
    directory: /etc/traefik/dynamic
    watch: true

# Logging
log:
  level: INFO

# Metrics
metrics:
  prometheus:
    addEntryPointsLabels: true
    addServicesLabels: true
    entryPoint: metrics
```

## Rule Syntax Reference

### Router Rules

```yaml
# Host matching
Host(`workhorse.local`)

# Path matching
Path(`/api/users`)                    # Exact path
PathPrefix(`/api`)                    # Prefix match
PathRegexp(`^/api/v[0-9]+/`)         # Regex match

# Method matching
Method(`GET`, `POST`)

# Combined rules (AND)
Host(`workhorse.local`) && PathPrefix(`/api`)

# Combined rules (OR)
Host(`workhorse.local`) || Host(`localhost`)
```
