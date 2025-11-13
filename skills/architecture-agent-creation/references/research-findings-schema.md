# Research Findings Schema for Infrastructure Agents

This document defines the standardized format for documenting research findings when creating infrastructure agent definitions. Use this schema to organize all research before writing agent prompts.

## Purpose

The research findings document serves as the source material for creating complete agent definitions. It captures all essential information about the target technology in a structured format that can be directly translated into agent prompts and reference documentation.

## Document Structure

### 1. Technology Overview

**Purpose**: Provide high-level understanding of what the technology does and why it exists.

**Required Content**:
- Technology name and current stable version
- Primary purpose (what problem does it solve?)
- Architecture overview (how does it work?)
- Key concepts and terminology
- Common use cases

**Example (Grafana)**:
```markdown
## Technology Overview

**Name**: Grafana
**Version**: 11.x (latest stable)
**Purpose**: Open-source observability platform for creating dashboards and visualizing metrics, logs, and traces from multiple data sources.

**Architecture**: Grafana operates as a web application that queries data sources (Prometheus, Loki, databases) via plugins, processes queries, and renders visualizations in dashboards. Data sources are configured via API or provisioning files.

**Key Concepts**:
- **Dashboard**: Collection of panels displaying data visualizations
- **Panel**: Individual visualization (graph, gauge, table) within a dashboard
- **Data Source**: Backend system providing metrics/logs (Prometheus, Loki, MySQL)
- **Query**: Expression (PromQL, LogQL, SQL) fetching data from data source
- **Provisioning**: Configuration-as-code for dashboards and data sources

**Common Use Cases**:
- System metrics monitoring (CPU, memory, disk, network)
- Application performance monitoring (request rates, latencies, errors)
- Business metrics dashboards (revenue, user activity)
- Alerting on metric thresholds
```

### 2. Tool Ecosystem

**Purpose**: Document all tools, APIs, and interfaces for interacting with the technology.

**Required Content**:
- CLI tools (name, purpose, key commands)
- HTTP APIs (base URL, authentication, key endpoints)
- Configuration methods (files, environment variables, UI)
- SDKs or libraries (if applicable)

**Example (Grafana)**:
```markdown
## Tool Ecosystem

### CLI: grafana-cli

**Purpose**: Plugin management, admin tasks, provisioning

**Key Commands**:
```bash
# List available plugins
grafana-cli plugins list-remote

# Install plugin
grafana-cli plugins install <plugin-name>

# Reset admin password
grafana-cli admin reset-admin-password <password>
```

### HTTP API

**Base URL**: `http://grafana:3000/api`
**Authentication**: `Authorization: Bearer <API_TOKEN>` header

**Key Endpoints**:

**Dashboards**:
- `POST /api/dashboards/db` - Create/update dashboard
- `GET /api/dashboards/uid/<uid>` - Get dashboard by UID
- `DELETE /api/dashboards/uid/<uid>` - Delete dashboard
- `GET /api/search?query=<name>` - Search dashboards

**Data Sources**:
- `GET /api/datasources` - List data sources
- `POST /api/datasources` - Create data source
- `POST /api/datasources/<id>/health` - Test data source connection
- `DELETE /api/datasources/<id>` - Delete data source

**Example Request**:
```bash
curl -X POST -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d @dashboard.json \
  "http://grafana:3000/api/dashboards/db"
```

**Expected Response**:
```json
{
  "id": 1,
  "slug": "my-dashboard",
  "status": "success",
  "uid": "abc123",
  "url": "/d/abc123/my-dashboard",
  "version": 1
}
```

### Configuration Methods

**Provisioning (preferred for production)**:
- Location: `/etc/grafana/provisioning/`
- Formats: YAML for data sources, JSON for dashboards
- Benefit: Version-controlled, declarative configuration

**API (for dynamic operations)**:
- Use for runtime dashboard creation, testing
- Requires API token with appropriate permissions

**UI (for prototyping only)**:
- Dashboard editor for rapid prototyping
- Export JSON for version control
```

### 3. Integration Patterns

**Purpose**: Document how the technology connects with other systems.

**Required Content**:
- Common integrations (what systems does it connect to?)
- Connection methods (API, network protocols, file formats)
- Authentication patterns
- Data flow (how data moves between systems)

**Example (Grafana)**:
```markdown
## Integration Patterns

### Data Source Integrations

**Prometheus** (most common):
```yaml
# provisioning/datasources/prometheus.yaml
apiVersion: 1
datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
```

**Loki** (logs):
```yaml
# provisioning/datasources/loki.yaml
apiVersion: 1
datasources:
  - name: Loki
    type: loki
    access: proxy
    url: http://loki:3100
```

**PostgreSQL** (relational data):
```yaml
# provisioning/datasources/postgres.yaml
apiVersion: 1
datasources:
  - name: PostgreSQL
    type: postgres
    url: postgres:5432
    database: mydb
    user: grafana
    secureJsonData:
      password: ${POSTGRES_PASSWORD}
```

### Authentication Patterns

**API Token** (for automation):
- Create service account in Grafana UI
- Generate token with required scopes (Dashboard Editor, Data Source Reader)
- Pass in `Authorization: Bearer <token>` header

**BasicAuth via Traefik** (for web access):
```yaml
# traefik/middlewares/grafana-auth.yaml
http:
  middlewares:
    grafana-auth:
      basicAuth:
        users:
          - "admin:$apr1$xyz..."  # htpasswd hash
```

### Alerting Integration

**Alertmanager** (external alert routing):
- Grafana sends alerts to Alertmanager
- Alertmanager handles deduplication, grouping, routing
- Configure notification receivers in Alertmanager

**Direct Notification Channels** (simple setup):
- Slack, PagerDuty, Email configured in Grafana
- Grafana sends notifications directly
```

### 4. Common Workflows

**Purpose**: Document typical operational procedures and tasks.

**Required Content**:
- Step-by-step procedures for common tasks
- Decision points (when to use which approach)
- Command sequences with expected output
- Gotchas and common mistakes

**Example (Grafana)**:
```markdown
## Common Workflows

### Workflow 1: Create Dashboard from Scratch

**When**: Need new dashboard for monitoring a service

**Steps**:
1. **Identify metrics** - Query Prometheus for available metrics:
   ```bash
   curl 'http://prometheus:9090/api/v1/label/__name__/values' | jq -r '.data[]' | grep <service_name>
   ```

2. **Draft dashboard JSON** - Create basic structure:
   ```json
   {
     "dashboard": {
       "title": "Service Monitoring",
       "uid": "service-monitor",
       "panels": [
         {
           "id": 1,
           "title": "Request Rate",
           "type": "graph",
           "targets": [{"expr": "rate(requests_total[5m])"}],
           "gridPos": {"h": 8, "w": 12, "x": 0, "y": 0}
         }
       ]
     }
   }
   ```

3. **Test query in Grafana Explore** - Validate PromQL works
4. **Deploy via API**:
   ```bash
   curl -X POST -H "Authorization: Bearer $TOKEN" \
     -d @dashboard.json \
     http://grafana:3000/api/dashboards/db
   ```

5. **Commit to Git** - Save dashboard JSON for version control

**Common Mistake**: Editing dashboard in UI without exporting JSON afterward - changes get lost on Grafana restart.

### Workflow 2: Configure Alert Rule

**When**: Need notification when metric crosses threshold

**Steps**:
1. **Write alert query** - Test in Grafana Explore:
   ```promql
   rate(errors_total[5m]) > 0.05
   ```

2. **Create alert rule** via API:
   ```json
   {
     "name": "HighErrorRate",
     "interval": "1m",
     "rules": [
       {
         "expr": "rate(errors_total[5m]) > 0.05",
         "for": "5m",
         "labels": {
           "severity": "warning"
         },
         "annotations": {
           "summary": "High error rate on {{ $labels.instance }}"
         },
         "grafana_alert": {
           "title": "High Error Rate",
           "condition": "C",
           "data": [
             {
               "refId": "A",
               "queryType": "",
               "relativeTimeRange": { "from": 300, "to": 0 },
               "datasourceUid": "prometheus_uid",
               "model": {
                 "expr": "rate(errors_total[5m]) > 0.05",
                 "intervalMs": 1000,
                 "maxDataPoints": 43200
               }
             }
           ]
         }
       }
     ]
   }
   ```

3. **Configure notification channel** (Slack):
   ```json
   {
     "name": "Slack Ops",
     "type": "slack",
     "settings": {
       "url": "https://hooks.slack.com/services/XXX/YYY/ZZZ"
     }
   }
   ```

4. **Test alert** - Simulate high error rate or use Grafana's test feature

**Gotcha**: Alert won't fire until condition met for full `for` duration (5m in example).
```

### 5. Best Practices

**Purpose**: Capture production-proven patterns and anti-patterns.

**Required Content**:
- Configuration management recommendations
- Performance optimization tips
- Security hardening steps
- Reliability patterns
- Common pitfalls to avoid

**Example (Grafana)**:
```markdown
## Best Practices

### Configuration Management

**DO**:
- ✅ Store dashboards in Git as JSON files
- ✅ Use provisioning for data sources (not manual UI configuration)
- ✅ Reference secrets via environment variables: `${GRAFANA_API_KEY}`
- ✅ Version dashboards (increment `version` field on changes)

**DON'T**:
- ❌ Edit dashboards only in UI without exporting JSON
- ❌ Hardcode credentials in YAML configs
- ❌ Use SQLite database for production (use PostgreSQL/MySQL)

### Performance Optimization

**DO**:
- ✅ Use recording rules for expensive PromQL aggregations
- ✅ Set reasonable refresh intervals (not <30s for heavy queries)
- ✅ Limit panels per dashboard to 20-30
- ✅ Split complex dashboards into overview + drill-down

**DON'T**:
- ❌ Query large time ranges with high-resolution data
- ❌ Use inefficient queries with multiple `join` operations

### Security Hardening

**DO**:
- ✅ Disable default `admin:admin` login immediately
- ✅ Use TLS for Grafana web interface
- ✅ Rotate API tokens regularly (90 days)
- ✅ Use minimal-privilege service account tokens
- ✅ Enable audit logging for config changes

**DON'T**:
- ❌ Expose Grafana publicly without authentication
- ❌ Use admin tokens for automation (create service accounts)
- ❌ Store tokens in plaintext in scripts

### Reliability Patterns

**DO**:
- ✅ Run multiple Grafana instances behind load balancer
- ✅ Use external database (PostgreSQL) for shared state
- ✅ Monitor Grafana's `/metrics` endpoint with Prometheus
- ✅ Backup dashboards regularly (Git + periodic exports)

**DON'T**:
- ❌ Rely on single Grafana instance for critical monitoring
- ❌ Skip health checks on Grafana itself
```

### 6. Error Scenarios

**Purpose**: Document common failures, symptoms, and resolutions.

**Required Content**:
- Error message or symptom
- Root cause explanation
- Step-by-step resolution
- Prevention measures

**Example (Grafana)**:
```markdown
## Error Scenarios

### Error 1: "Data source not found"

**Symptom**: Dashboard panel shows "Data source not found" error

**Root Cause**: Data source UID changed (often after provisioning update) or data source was deleted

**Resolution**:
1. List current data sources:
   ```bash
   curl -H "Authorization: Bearer $TOKEN" \
     http://grafana:3000/api/datasources | jq '.[] | {name, uid}'
   ```
2. Update panel's `datasource` field in dashboard JSON with correct UID
3. Re-save dashboard via API

**Prevention**: Use data source UIDs instead of names in panel definitions. UIDs are immutable and prevent dashboards from breaking if a data source is renamed.

### Error 2: API returns 401 Unauthorized

**Symptom**: All API calls fail with 401 status

**Root Cause**: API token expired, revoked, or has insufficient permissions

**Resolution**:
1. Generate new API token in Grafana UI:
   - Settings → Service Accounts → Add service account
   - Assign required roles (Dashboard Editor, Data Source Reader)
   - Generate token
2. Update `$GRAFANA_API_TOKEN` environment variable
3. Retry API call

**Prevention**: Set token expiration reminder (90 days), store in secrets manager

### Error 3: Alert not firing despite condition being true

**Symptom**: Metric crosses threshold but no notification sent

**Root Causes**:
1. **`for` duration not met** - Alert must be in alerting state for specified duration
2. **Query returns no data** - PromQL expression invalid or metric doesn't exist
3. **Notification channel misconfigured** - Webhook URL wrong, Slack token invalid

**Resolution**:
1. Test query in Grafana Explore - verify returns data
2. Check alert state in Alerting UI - should show "Alerting" not "Pending"
3. Test notification channel:
   ```bash
   curl -X POST -H "Authorization: Bearer $TOKEN" \
     -d '{"alertId": 1}' \
     http://grafana:3000/api/alert-notifications/<id>/test
   ```
4. Check Grafana logs for notification errors:
   ```bash
   tail -f /var/log/grafana/grafana.log | grep -i "notification"
   ```

**Prevention**: Always test alerts after creation, monitor Grafana's own alerting metrics

### Error 4: Dashboard loads slowly (>10 seconds)

**Symptom**: Dashboard takes long time to load, panels show loading spinners

**Root Causes**:
1. **Heavy queries** - Complex PromQL aggregations over large time ranges
2. **Too many panels** - 50+ panels on single dashboard
3. **High refresh rate** - Auto-refresh set to <30s

**Resolution**:
1. Identify slow panels using browser DevTools Network tab
2. Optimize queries:
   - Use Prometheus recording rules for expensive aggregations
   - Reduce time range (last 1h instead of 7d)
   - Add rate() or increase() to reduce cardinality
3. Reduce panel count - split into multiple dashboards
4. Increase refresh interval to 1m or 5m
5. Enable query caching in Grafana config

**Prevention**: Test dashboard performance before deploying, set query timeout limits
```

### 7. Tool Installation

**Purpose**: Provide exact commands for installing all required tools.

**Required Content**:
- Installation commands for each tool
- Verification commands
- Version checking
- Platform-specific instructions (if needed)

**Example (Grafana)**:
```markdown
## Tool Installation

### Grafana Server

**Debian/Ubuntu**:
```bash
# Add APT repository (modern keyring method)
sudo apt-get install -y apt-transport-https software-properties-common wget
sudo mkdir -p /etc/apt/keyrings/
wget -q -O - https://packages.grafana.com/gpg.key | gpg --dearmor | sudo tee /etc/apt/keyrings/grafana.gpg > /dev/null
echo "deb [signed-by=/etc/apt/keyrings/grafana.gpg] https://packages.grafana.com/oss/deb stable main" | sudo tee /etc/apt/sources.list.d/grafana.list

# Install
sudo apt-get update
sudo apt-get install grafana

# Start service
sudo systemctl start grafana-server
sudo systemctl enable grafana-server

# Verify
curl http://localhost:3000/api/health
```

**Docker**:
```bash
docker run -d \
  --name grafana \
  -p 3000:3000 \
  -v grafana-storage:/var/lib/grafana \
  grafana/grafana:11.0.0
```

### CLI Tools

**jq** (JSON processor):
```bash
# Debian/Ubuntu
sudo apt-get install jq

# macOS
brew install jq

# Verify
jq --version  # Expected: jq-1.6 or newer
```

**htpasswd** (BasicAuth hash generator):
```bash
# Debian/Ubuntu
sudo apt-get install apache2-utils

# RHEL/CentOS
sudo yum install httpd-tools

# macOS
brew install httpd

# Verify
htpasswd -V  # Expected: 2.4.x or newer
```

**httpie** (API testing):
```bash
# Python pip
pip install httpie

# macOS
brew install httpie

# Verify
http --version  # Expected: 3.x or newer
```

### Grafana CLI

**Included with Grafana installation** - no separate install needed

**Verify**:
```bash
grafana-cli --version  # Expected: 11.0.0 or newer
```

### API Token Setup

**Generate token for automation**:
1. Log into Grafana UI (http://grafana:3000)
2. Settings → Service Accounts → Add service account
3. Name: "automation-agent"
4. Role: Editor
5. Generate token → Copy token value
6. Store in environment:
   ```bash
   export GRAFANA_API_TOKEN="<token>"
   ```

**Verify token works**:
```bash
curl -H "Authorization: Bearer $GRAFANA_API_TOKEN" \
  http://grafana:3000/api/org
```

**Expected response**:
```json
{
  "id": 1,
  "name": "Main Org."
}
```
```

## Research Validation Checklist

Before using research findings to create agent prompt, verify:

- [ ] Technology overview includes current stable version number
- [ ] Tool ecosystem documents ALL interfaces (CLI, API, config files)
- [ ] API examples include full curl commands and expected JSON responses
- [ ] Integration patterns show actual config file formats (YAML/JSON)
- [ ] Common workflows have step-by-step commands (not placeholders)
- [ ] Best practices have concrete DO/DON'T examples
- [ ] Error scenarios include exact error messages and resolutions
- [ ] Tool installation has commands for all required tools
- [ ] All code examples are copy-pasteable and runnable
- [ ] External documentation sources cited (official docs, community guides)

## Word Count Guidelines

**Total research findings**: 2,500-3,500 words

**Section breakdown**:
- Technology Overview: 300-400 words
- Tool Ecosystem: 500-700 words
- Integration Patterns: 400-600 words
- Common Workflows: 500-700 words
- Best Practices: 400-600 words
- Error Scenarios: 400-600 words
- Tool Installation: 200-300 words

## Output Format

Save research findings as markdown file:
```
docs/.scratch/<issue-id>/research/<technology>-research-findings.md
```

This file serves as source material for creating:
1. Agent prompt (`.claude/agents/<technology>-agent.md`)
2. Best practices reference (`docs/agents/<technology>-agent/ref-docs/<technology>-best-practices.md`)
3. API reference (`docs/agents/<technology>-agent/ref-docs/<technology>-api-reference.md`)
4. Troubleshooting guide (`docs/agents/<technology>-agent/ref-docs/<technology>-troubleshooting.md`)
