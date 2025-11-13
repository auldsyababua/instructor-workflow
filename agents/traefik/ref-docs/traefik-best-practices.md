# Traefik Best Practices

## Configuration Management

### Label Organization

Structure Docker labels consistently for maintainability:

```yaml
labels:
  # Enable Traefik (required)
  - "traefik.enable=true"
  
  # Router configuration
  - "traefik.http.routers.SERVICE.rule=Host(`workhorse.local`) && PathPrefix(`/SERVICE`)"
  - "traefik.http.routers.SERVICE.entrypoints=web"
  - "traefik.http.routers.SERVICE.middlewares=auth@docker,strip-SERVICE"
  
  # Service configuration
  - "traefik.http.services.SERVICE.loadbalancer.server.port=PORT"
  
  # Middleware configuration
  - "traefik.http.middlewares.strip-SERVICE.stripprefix.prefixes=/SERVICE"
```

**Best practices**:
- Use lowercase service names in labels for consistency
- Name routers/services/middlewares with descriptive patterns
- Group related labels together for readability
- Always specify loadbalancer port explicitly

## Performance Optimization

### Connection Pooling

Configure backend connection reuse:

```yaml
labels:
  - "traefik.http.services.SERVICE.loadbalancer.passhostheader=true"
  - "traefik.http.services.SERVICE.loadbalancer.healthcheck.path=/health"
  - "traefik.http.services.SERVICE.loadbalancer.healthcheck.interval=30s"
```

### Middleware Optimization

Limit middleware chains to 4-5 per route. Each middleware adds ~1-5ms latency.

## Security Hardening

### Global Authentication

Protect all services with BasicAuth middleware:

```yaml
# File provider: /etc/traefik/dynamic/auth.yml
http:
  middlewares:
    global-auth:
      basicAuth:
        usersFile: /etc/traefik/.htpasswd
        realm: "Workhorse Services"
```

### Rate Limiting

Prevent DoS attacks:

```yaml
http:
  middlewares:
    rate-limit:
      rateLimit:
        average: 100
        burst: 50
        period: 1s
```

## Common Pitfalls

### PathPrefix Trailing Slash

Use StripPrefix middleware to avoid path confusion:

```yaml
- "traefik.http.middlewares.strip-service.stripprefix.prefixes=/service"
```

### Dollar Sign Escaping

Escape $ signs in docker-compose files:

```yaml
# Correct:
- "traefik.http.middlewares.auth.basicauth.users=admin:$$2y$$05$$xyz"
```
