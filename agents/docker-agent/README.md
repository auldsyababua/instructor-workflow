# Docker Agent

**Version**: 1.0.0  
**Domain**: Infrastructure  
**Status**: Production-Ready

---

## Purpose

The Docker Agent manages all Docker and Docker Compose operations across projects in a project-agnostic manner. It deploys services, configures reverse proxy integrations (Traefik/Nginx/Caddy), allocates GPU resources, orchestrates multi-service stacks, debugs container issues, monitors resource usage, validates configurations, handles migrations/backups, scans for security vulnerabilities, and integrates with CI/CD pipelines.

**Key Differentiator**: Reads project-specific context from `.project-context.md` (NOT a separate `.docker.project-context.md`), enabling the same agent to work across all projects with project-tailored Docker expertise.

---

## When to Use

Invoke the Docker Agent when:
- Deploying services with Docker Compose
- Configuring reverse proxy routing (Traefik labels, Nginx upstreams, Caddy configuration)
- Allocating GPU resources for ML/AI workloads
- Debugging container failures (crash loops, OOM, network issues)
- Optimizing resource usage (CPU, memory, disk cleanup)
- Validating compose files for best practices
- Implementing blue-green or canary deployments
- Creating backup and restore procedures
- Scanning images for security vulnerabilities
- Generating deployment templates and infrastructure-as-code

---

## Quick Start

### Prerequisites

- Docker Engine 27.4.0+ installed
- Docker Compose v2.30.0+ installed
- (Optional) NVIDIA Container Toolkit for GPU workloads
- (Optional) Reverse proxy (Traefik/Nginx/Caddy) for web services

### Invocation

#### CLI (if agent aliases configured):
```bash
@docker-agent deploy web service with traefik integration
@docker-agent debug container crash loop for myapp
@docker-agent configure GPU access for ML container
```

#### Via Traycer (conversational delegation):
```
User: I need to deploy my Next.js app with PostgreSQL and Redis, accessible via Traefik
Traycer: @docker-agent [delegates task]
```

### Basic Usage Examples

**Deploy service**:
```bash
@docker-agent create compose file for myapp with traefik labels and health checks
```

**Debug issue**:
```bash
@docker-agent investigate why myapp container keeps restarting
```

**Optimize resources**:
```bash
@docker-agent analyze docker disk usage and recommend cleanup
```

**Configure GPU**:
```bash
@docker-agent set up NVIDIA GPU access for pytorch container
```

---

## Capabilities

### 1. Reverse Proxy Integration
- Generate Traefik v3 labels (HTTP/HTTPS routing, TLS, middleware)
- Configure Nginx reverse proxy with SSL termination
- Set up Caddy automatic HTTPS
- Validate routing and debug 404/502 errors
- Handle WebSocket support and sticky sessions

### 2. GPU Resource Management
- Configure NVIDIA GPU access (runtime, device allocation)
- Set up AMD ROCm for AMD GPUs
- Monitor GPU utilization (nvidia-smi, DCGM metrics)
- Debug GPU not accessible errors
- Optimize multi-GPU workload scheduling

### 3. Multi-Stack Orchestration
- Design dependency graphs for startup order
- Implement health check-based readiness gates
- Configure graceful shutdown sequences
- Orchestrate zero-downtime deployments (blue-green, canary)
- Manage environment-specific overrides (dev/staging/prod)

### 4. Container Debugging
- Parse logs to identify error patterns
- Detect OOM kills and memory issues
- Diagnose crash loops and network connectivity
- Debug port conflicts and volume permissions
- Investigate health check failures

### 5. Resource Monitoring & Cleanup
- Monitor CPU, memory, network, disk usage per container
- Track disk space by images/containers/volumes
- Implement automated cleanup strategies
- Configure log rotation
- Export Prometheus metrics

### 6. Compose File Intelligence
- Validate syntax and detect anti-patterns
- Suggest best practice improvements
- Identify security issues (secrets, privileged mode)
- Check port conflicts and resource limits
- Optimize for production readiness

### 7. Service Deployment Wizards
- Generate complete stacks from templates
- Create optimized Dockerfiles
- Configure database persistence
- Set up monitoring exporters
- Generate backup/restore scripts

### 8. Migration & Backup
- Backup volumes to tar.gz archives
- Create database-specific backups (pg_dump, mysqldump)
- Implement automated backup schedules
- Restore with verification
- Handle service migrations between hosts

### 9. Security Validation
- Scan images for CVEs (Trivy)
- Validate Dockerfiles (Hadolint)
- Detect secrets and misconfigurations
- Check privilege escalation risks
- Generate security reports

### 10. CI/CD Integration
- Generate pipeline templates
- Implement pre-commit hooks
- Create automated testing workflows
- Set up deployment automation
- Configure rollback procedures

---

## Technology Stack

**Docker**: Engine 27.4.0, Compose v2.30.0 (spec v3.8+)

**Reverse Proxies**:
- Traefik v3.2.3
- Nginx 1.27.x
- Caddy 2.8.x

**GPU Runtimes**:
- NVIDIA Container Toolkit 1.16.2
- ROCm 6.2.4

**Security**:
- Trivy 0.57.0
- Hadolint 2.12.0

**Monitoring**:
- cAdvisor 0.49.1
- node-exporter 1.8.2
- DCGM Exporter 3.3.9-3.6.0

---

## Configuration

### Project Context Integration

The Docker Agent reads Docker-specific configuration from `.project-context.md`. Example structure:

```markdown
## Docker Configuration

**Reverse Proxy**: Traefik v3.2.3
**Network**: homelab_network
**GPU**: NVIDIA RTX 5090 (32GB VRAM)

**Service Groups**:
- Core: traefik, docker-socket-proxy
- Data: postgres, redis, qdrant
- Apps: web, api, worker

**Compose Locations**:
- /srv/services/compose/*.yml

**Security Policies**:
- root_user: error
- secrets_in_env: error
- privileged_mode: warn
```

This allows the agent to:
- Generate correct Traefik labels for your reverse proxy version
- Use your network naming conventions
- Configure GPU access for your hardware
- Follow your security policies

### Skills Used

The Docker Agent operates without additional skills (self-contained).

### Commands Available

No agent-specific commands (invoked via @mention or Traycer delegation).

### Hooks Enforced

No agent-specific hooks. Security validation provided via compose file analysis.

---

## Standard Operating Procedures

The Docker Agent follows these SOPs (documented in agent prompt):

1. **Deploy New Service with Traefik Integration**: Complete compose file with Traefik labels, health checks, resource limits
2. **Debug Container Crash Loop**: 10-step diagnostic procedure for identifying and resolving crash causes
3. **Optimize Docker Disk Usage**: Analysis and cleanup procedures to reclaim disk space
4. **Configure GPU Access for Container**: NVIDIA Container Toolkit setup and verification
5. **Backup and Restore Service Data**: Volume and database backup procedures with restoration steps

---

## Example Workflows

### Deploy Multi-Service Stack

**Scenario**: Deploy Next.js web app + PostgreSQL + Redis + Traefik from scratch

**Agent creates**:
- Complete `docker-compose.yml` with 4 services
- Traefik configuration with automatic TLS
- Health checks for all services
- Dependency management (web waits for DB healthy)
- Network isolation (backend internal, web exposed)
- `.env` template for secrets
- Resource limits for production

**Result**: Full stack running, accessible via HTTPS, all health checks passing

---

### Debug Traefik 404 Error

**Scenario**: Service returns 404 when accessing via Traefik

**Agent performs**:
1. Verify service running
2. Check Traefik labels
3. Validate network connectivity
4. Test loadbalancer port configuration
5. Inspect Traefik router detection
6. Restart Traefik if needed

**Result**: Routing issue identified (wrong network), fixed by adding service to Traefik's network

---

### Blue-Green Deployment

**Scenario**: Deploy new app version with zero downtime

**Agent implements**:
1. Deploy Green (v1.1.0) alongside Blue (v1.0.0)
2. Test Green in isolation
3. Atomically switch Traefik labels (Blue→Green)
4. Monitor for issues
5. Keep Blue running for quick rollback
6. Remove Blue after stability window

**Result**: New version deployed with 0 seconds downtime, instant rollback capability

---

## Coordination

### Delegates To

- **Prometheus Agent**: For metrics scraping setup (cAdvisor, DCGM exporters)
- **Grafana Agent**: For dashboard creation from Docker metrics
- **Security Agent**: For critical CVE review and remediation decisions
- **DevOps Agent**: For host-level issues (firewall, kernel parameters, disk expansion)
- **Network Agent**: For complex networking beyond Docker (VPN, external load balancers)

### Receives From

- **Traycer**: User requests for Docker operations
- **Application Agents**: Deployment requests for their services
- **Database Agent**: Container deployment for databases
- **Monitoring Agents**: Requests to deploy exporters

---

## Critical Constraints

The Docker Agent enforces these constraints:

- ✅ MUST validate compose files before deployment (`docker-compose config`)
- ✅ MUST scan images for CVEs (Trivy) before production
- ✅ MUST set resource limits (CPU, memory) for production services
- ✅ MUST use specific version tags (never `latest`)
- ✅ MUST store secrets in `.env` (never hardcode)
- ✅ MUST run containers as non-root user (documented exceptions only)
- ✅ MUST define health checks for long-running services
- ✅ MUST configure log rotation
- ✅ MUST document backup/restore procedures
- ✅ MUST test Traefik routing after deployment

---

## Security Considerations

**Secrets Management**:
- Secrets stored in `.env` file (added to `.gitignore`)
- Never commit credentials to Git
- Use Docker secrets (Swarm) or external secrets managers for production
- Validate `.env.example` documents required variables

**Image Security**:
- Scan all images with Trivy before deployment
- Use specific tags (e.g., `nginx:1.27-alpine`), never `latest`
- Prefer minimal base images (Alpine, distroless)
- Regular security updates and rebuilds

**Container Hardening**:
- Run as non-root user
- Drop unnecessary Linux capabilities
- Use read-only filesystem where possible
- Avoid privileged mode and host network
- Implement network isolation (internal networks)

**Common Vulnerabilities Fixed**:
- Hardcoded secrets → Use environment variables
- Root user → Create non-root user in Dockerfile
- Exposed ports without auth → Traefik BasicAuth middleware
- Unscanned images → CI/CD integration with Trivy
- Privileged containers → Drop privileges, document exceptions

---

## Troubleshooting

### Issue: Container Exits Immediately

**Symptom**: Container starts then exits with error code

**Diagnosis**:
```bash
docker logs <container>
docker inspect --format='{{.State.ExitCode}}' <container>
```

**Common Causes**:
- Exit 1: Application error (check logs)
- Exit 126: Permission denied (chmod +x entrypoint)
- Exit 127: Command not found (verify CMD/ENTRYPOINT)
- Exit 137: OOM killed (increase memory limit)

**Solution**: Documented in agent prompt SOP-2 "Debug Container Crash Loop"

---

### Issue: Traefik Returns 404

**Symptom**: Service not accessible via Traefik

**Diagnosis**:
```bash
docker inspect <container> | jq '.[0].Config.Labels'
docker inspect <container> | jq '.[0].NetworkSettings.Networks'
```

**Common Causes**:
- Wrong network (not on Traefik's network)
- Missing/incorrect labels
- Wrong port in loadbalancer configuration

**Solution**: Documented in agent prompt Example Workflow "Debug Container Not Accessible via Traefik"

---

### Issue: High Memory Usage

**Symptom**: Container consuming excessive memory, possibly OOM killed

**Diagnosis**:
```bash
docker stats <container>
docker inspect --format='{{.State.OOMKilled}}' <container>
```

**Solutions**:
- Increase memory limit if legitimate usage
- Fix memory leaks in application
- Implement batch processing instead of loading all data
- Configure swap limits

**Solution**: Documented in agent prompt Example Workflow "Analyze and Fix High Resource Usage"

---

### Issue: GPU Not Accessible

**Symptom**: nvidia-smi not working inside container

**Diagnosis**:
```bash
docker run --rm --gpus all nvidia/cuda:12.3.0-base-ubuntu22.04 nvidia-smi
```

**Common Causes**:
- NVIDIA Container Toolkit not installed
- Docker not configured to use nvidia runtime
- Wrong GPU device specification

**Solution**: Documented in agent prompt SOP-4 "Configure GPU Access for Container"

---

## Reference Documentation

**Internal Docs** (stored in `docs/agents/docker-agent/ref-docs/`):
- `docker-best-practices.md` - Configuration, performance, security patterns (264 lines)
- `docker-api-reference.md` - CLI commands, API endpoints, schemas (712 lines)
- `docker-troubleshooting.md` - Diagnostic procedures, error resolutions (668 lines)

**External Resources**:
- Docker Documentation: https://docs.docker.com/
- Docker Compose File Reference: https://docs.docker.com/compose/compose-file/compose-file-v3/
- Traefik v3 Documentation: https://doc.traefik.io/traefik/v3.2/
- NVIDIA Container Toolkit: https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/
- Trivy Security Scanner: https://aquasecurity.github.io/trivy/

---

## Performance Metrics

**Agent Capabilities**:
- 10 major capability areas
- 5 complete SOPs
- 5 detailed workflow examples
- 8+ error scenarios with diagnostics
- 6+ security issues documented
- 3 reference docs (1,644 total lines)
- 1,443-line agent prompt

**Pattern Compliance**:
- ✅ 15/15 P0 patterns from grafana-agent analysis
- ✅ Extended YAML frontmatter
- ✅ Agent Identity section
- ✅ Capability-Tool Mapping (10 categories)
- ✅ Technology Stack with versions
- ✅ 5 Complete SOPs
- ✅ Three-Tier Reference Documentation
- ✅ Error Handling with retry strategy
- ✅ Security Considerations
- ✅ 5 Example Workflows
- ✅ Quality Checklist

---

## Version History

**v1.0.0** (2025-11-06):
- Initial release
- 10 capability categories
- Traefik v3, NVIDIA Toolkit 1.16.2, Docker 27.4.0 support
- Complete SOPs and workflow examples
- Three-tier reference documentation
- 15/15 P0 pattern compliance

---

## Contributing

This agent is part of the Traycer Enforcement Framework. Improvements should follow TEF standards:

1. Test changes in real projects
2. Document new capabilities in agent prompt
3. Update reference docs if adding significant features
4. Ensure 15/15 P0 pattern compliance
5. Update version number and changelog

---

## Support

For issues with the Docker Agent:
1. Check troubleshooting section in this README
2. Consult reference docs in `ref-docs/` directory
3. Review example workflows in agent prompt
4. Escalate to Traycer if task is out of scope

For Docker-specific questions beyond agent scope, consult official Docker documentation.
