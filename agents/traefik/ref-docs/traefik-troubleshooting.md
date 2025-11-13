# Traefik Troubleshooting Guide

## Diagnostic Procedures

### Health Check Workflow

```bash
# 1. Check Traefik container status
docker ps | grep traefik
# Expected: Container running, status "Up X minutes"

# 2. Verify Traefik health endpoint
docker exec traefik traefik healthcheck
# Expected: OK: http server is up (X routers, Y services, Z middlewares)

# 3. Check API overview
curl http://workhorse.local:8080/api/overview | jq
# Expected: No errors or warnings in output

# 4. Inspect router configuration
curl http://workhorse.local:8080/api/http/routers | jq '.[] | {name: .name, rule: .rule, status: .status}'
# Expected: All routers show status: "enabled"

# 5. Check service backend health
curl http://workhorse.local:8080/api/http/services | jq '.[] | {name: .name, serverStatus: .serverStatus}'
# Expected: All servers show "UP" status
```

### Network Connectivity Test

```bash
# 1. Verify lan-open network exists
docker network ls | grep lan-open

# 2. List containers on network
docker network inspect lan-open -f '{{range .Containers}}{{.Name}}: {{.IPv4Address}}{{println}}{{end}}'

# 3. Test ping from Traefik to backend
docker exec traefik ping -c 3 SERVICE-CONTAINER
# Expected: 0% packet loss

# 4. Test HTTP connectivity
docker exec traefik wget -O- --timeout=5 http://SERVICE-CONTAINER:PORT/
# Expected: HTTP response (200 OK or valid HTML)
```

## Common Errors & Resolutions

### Error 1: 404 Not Found

**Symptom**: Service returns 404 with message "404 page not found"

**Diagnosis**:
```bash
# Check if router exists
curl http://workhorse.local:8080/api/http/routers | jq '.[] | select(.name | contains("service"))'

# Check service labels
docker inspect SERVICE | jq '.[0].Config.Labels | with_entries(select(.key | startswith("traefik")))'
```

**Cause 1: Router rule doesn't match**
```yaml
# Wrong: Missing Host matcher
rule: "PathPrefix(`/service`)"

# Correct: Include Host matcher
rule: "Host(`workhorse.local`) && PathPrefix(`/service`)"
```

**Resolution**:
```bash
# Fix labels in docker-compose.yml
docker-compose up -d SERVICE

# Verify router registered
curl http://workhorse.local:8080/api/http/routers | grep service
```

### Error 2: 502 Bad Gateway

**Symptom**: Service returns "502 Bad Gateway" error

**Diagnosis**:
```bash
# Check backend health
curl http://workhorse.local:8080/api/http/services | jq '.[] | select(.name | contains("service")) | .serverStatus'

# Test direct backend access
docker inspect SERVICE | grep IPAddress
curl http://BACKEND-IP:PORT/
```

**Cause 1: Backend container not running**
```bash
# Check container status
docker ps -a | grep SERVICE

# Restart container
docker-compose up -d SERVICE
```

**Cause 2: Wrong backend port**
```yaml
# Correct: Match container port
traefik.http.services.SERVICE.loadbalancer.server.port: "5000"
```

### Error 3: 401 Unauthorized (BasicAuth Issues)

**Symptom**: Valid credentials return 401 Unauthorized

**Cause: Htpasswd hash not escaped**
```yaml
# Wrong: Single $ sign
- "traefik.http.middlewares.auth.basicauth.users=admin:$2y$05$xyz"

# Correct: Double $$ for docker-compose
- "traefik.http.middlewares.auth.basicauth.users=admin:$$2y$$05$$xyz"
```

**Resolution**:
```bash
# Regenerate escaped hash
echo $(htpasswd -nbB admin tonto989) | sed 's/\$/\$\$/g'

# Update label in docker-compose.yml
docker-compose up -d traefik
```

### Error 4: Path Not Stripped

**Symptom**: Backend receives full path `/service/path` instead of `/path`

**Cause: StripPrefix middleware not configured**

**Resolution**:
```yaml
# Add StripPrefix middleware
labels:
  - "traefik.http.routers.service.middlewares=auth@docker,strip-service"
  - "traefik.http.middlewares.strip-service.stripprefix.prefixes=/service"

# Restart service
docker-compose up -d SERVICE
```

### Error 5: Middleware Not Found

**Symptom**: Traefik logs show "middleware 'auth' not found"

**Cause: Middleware provider not specified**

```yaml
# Wrong: No provider specified
middlewares: "auth"

# Correct: Explicit provider
middlewares: "auth@docker"  # Docker provider
# or
middlewares: "auth@file"    # File provider
```

## Performance Issues

### High Latency

**Diagnosis**:
```bash
# Measure latency breakdown
curl -w "\nDNS: %{time_namelookup}s\nConnect: %{time_connect}s\nTTFB: %{time_starttransfer}s\nTotal: %{time_total}s\n" \
  -u admin:tonto989 http://workhorse.local/service/
```

**Cause: Too many middlewares**
```yaml
# Bad: 7 middlewares (adds ~50ms)
middlewares: "auth,strip,compress,ratelimit,headers,redirect,errors"

# Better: 3 essential middlewares (~15ms)
middlewares: "auth,strip,compress"
```

## Security Incidents

### Unauthorized Access Attempt

**Diagnosis**:
```bash
# Parse access logs for 401s
docker logs traefik | jq 'select(.DownstreamStatus == 401) | {time: .StartLocal, ip: .ClientHost, path: .RequestPath}'
```

**Resolution**:
```yaml
# Add rate limiting middleware
http:
  middlewares:
    rate-limit:
      rateLimit:
        average: 10
        burst: 5
        period: 1m
```
