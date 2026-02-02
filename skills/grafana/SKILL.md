---
name: grafana
description: Interact with Grafana v7.5 for dashboard management, alert monitoring, and metric queries across multiple datasources (Prometheus, Azure Monitor, GCP). Use when tasks involve listing/viewing/creating/modifying Grafana dashboards, querying metrics or time-series data, managing alerts (view/pause/configure), exploring available metrics via prom-cli, working with Grafana datasources, or exporting dashboard configurations. Automatically handles authentication, API interactions, and metric discovery.
---

# Grafana Management Skill

## Overview

This skill enables comprehensive interaction with Grafana v7.5 instances, providing capabilities for:
- Dashboard management (list, view, create, modify, export)
- Metrics querying across multiple datasources (Prometheus, Azure Monitor, GCP)
- Alert configuration and monitoring
- Metric discovery using prom-cli
- Multi-datasource support with automatic configuration

## When to Use This Skill

Trigger this skill when the user:
- Asks about Grafana dashboards (e.g., "Grafana 上有哪些 dashboard")
- Requests metric queries (e.g., "查詢 worker 的 QPS")
- Wants to view or manage alerts
- Needs to explore available metrics
- Requests dashboard creation or modification
- Wants to export dashboard configurations
- Mentions specific dashboard names (e.g., "Instance Group Dashboard")

Example trigger phrases:
- "Grafana 上有哪些 dashboard"
- "請幫我到 Grafana 查詢 Instance Group Dashboard 各個 instance group 的 instance 數量狀態"
- "使用 Grafana 查詢服務一天內不同的 region 的 QPS"
- "查看 Grafana 的 alert 狀態"
- "匯出 dashboard 配置"

## Configuration

### Config File Location

Default: `~/.grafana-skill/config.json`

**Multiple Environments Support:**
You can maintain separate configs for different environments:
- `~/.grafana-skill/config.json` (default)
- `~/.grafana-skill/config-prod.json` (production)
- `~/.grafana-skill/config-staging.json` (staging)
- `~/.grafana-skill/config-dev.json` (development)

Use `GRAFANA_ENV` environment variable to switch between configs:
```bash
export GRAFANA_ENV=prod      # Uses config-prod.json
export GRAFANA_ENV=staging   # Uses config-staging.json
unset GRAFANA_ENV            # Uses config.json (default)
```

### Config File Format
```json
{
  "grafana_url": "http://grafana.example.com",
  "api_token": "YOUR_API_TOKEN",
  "default_datasource": "Prometheus 1",
  "datasources": {
    "Prometheus 1": {
      "uid": "000000001",
      "id": 1,
      "is_default": true
    },
    "Prometheus 2": {
      "uid": "000000002",
      "id": 2,
      "is_default": false
    }
  }
}
```

### Initial Setup

Before using this skill:

1. **Check if config exists**:
   ```bash
   ls -la ~/.grafana-skill/config.json
   ```

2. **Generate datasources configuration**:
   ```bash
   # Generate default config.json
   export GRAFANA_URL="http://grafana.example.com"
   export GRAFANA_API_TOKEN="your_api_token"
   python3 ~/.grafana-skill/scripts/generate_datasources.py
   ```

   **For multiple environments:**
   ```bash
   # Generate config-prod.json
   export GRAFANA_URL="http://grafana-prod.example.com"
   export GRAFANA_API_TOKEN="your_prod_token"
   export GRAFANA_ENV="prod"
   python3 ~/.grafana-skill/scripts/generate_datasources.py

   # Generate config-staging.json
   export GRAFANA_URL="http://grafana-staging.example.com"
   export GRAFANA_API_TOKEN="your_staging_token"
   export GRAFANA_ENV="staging"
   python3 ~/.grafana-skill/scripts/generate_datasources.py
   ```

   This script will:
   - Fetch all datasources from your Grafana instance
   - Generate the config file with proper UIDs and IDs
   - Automatically detect default datasource
   - Save to config.json or config-{GRAFANA_ENV}.json

3. **Verify prom installation**:
   ```bash
   which prom
   ```

   If not installed, install via npm:
   ```bash
   npm install -g github:jack482653/prom-cli
   ```

## Core Capabilities

### 1. Dashboard Management

#### List All Dashboards
```bash
curl -H "Authorization: Bearer ${API_TOKEN}" \
  "${GRAFANA_URL}/api/search?type=dash-db"
```

Returns: Array of dashboard objects with id, uid, title, url, tags

#### Get Dashboard by UID
```bash
curl -H "Authorization: Bearer ${API_TOKEN}" \
  "${GRAFANA_URL}/api/dashboards/uid/${DASHBOARD_UID}"
```

Returns: Complete dashboard JSON including panels, variables, and settings

#### Search Dashboards
```bash
curl -H "Authorization: Bearer ${API_TOKEN}" \
  "${GRAFANA_URL}/api/search?query=${QUERY}&tag=${TAG}"
```

Parameters:
- `query`: Search term (matches title)
- `tag`: Filter by tag
- `starred`: true/false (user's starred dashboards)

#### Create Dashboard
```bash
curl -X POST -H "Authorization: Bearer ${API_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "dashboard": {
      "title": "New Dashboard",
      "tags": ["automated"],
      "timezone": "browser",
      "panels": [],
      "schemaVersion": 16
    },
    "folderId": 0,
    "overwrite": false
  }' \
  "${GRAFANA_URL}/api/dashboards/db"
```

#### Update Dashboard
Use the same endpoint as create with `"overwrite": true` and existing dashboard UID

#### Export Dashboard
Simply retrieve dashboard JSON via GET and save to file:
```bash
curl -H "Authorization: Bearer ${API_TOKEN}" \
  "${GRAFANA_URL}/api/dashboards/uid/${DASHBOARD_UID}" \
  > dashboard_export.json
```

### 2. Metrics Querying

#### Recommended: Prometheus Direct API (Most Reliable)
```bash
# Query via datasource proxy - directly accesses Prometheus
curl -H "Authorization: Bearer ${API_TOKEN}" \
  "${GRAFANA_URL}/api/datasources/proxy/${DATASOURCE_ID}/api/v1/query_range?query=up&start=1769598000&end=1769599800&step=15"
```

**Time format**: Unix timestamp in **seconds** (not milliseconds)

**Why use this?**
- ✅ More reliable for historical data queries
- ✅ Consistent with Grafana Web UI behavior
- ✅ Direct Prometheus response format
- ✅ No data transformation by Grafana layer

#### Alternative: Grafana Unified Query API
```bash
# For recent data with relative time ranges
curl -X POST -H "Authorization: Bearer ${API_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "queries": [{
      "refId": "A",
      "datasource": {"uid": "DATASOURCE_UID", "type": "prometheus"},
      "expr": "rate(http_requests_total[5m])",
      "range": true
    }],
    "from": "now-1h",
    "to": "now"
  }' \
  "${GRAFANA_URL}/api/ds/query"
```

**Time formats**:
- Relative: "now-1h", "now-24h", "now-7d"
- Absolute: Unix timestamp in **milliseconds**

#### Discover Available Metrics

Use `prom` to explore metrics (see Metric Discovery section below)

### 3. Alert Management

#### List All Alerts
```bash
curl -H "Authorization: Bearer ${API_TOKEN}" \
  "${GRAFANA_URL}/api/alerts"
```

Returns: All alert rules with state, evaluation info, and conditions

#### Get Alert by ID
```bash
curl -H "Authorization: Bearer ${API_TOKEN}" \
  "${GRAFANA_URL}/api/alerts/${ALERT_ID}"
```

#### Pause/Unpause Alert
```bash
curl -X POST -H "Authorization: Bearer ${API_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"paused": true}' \
  "${GRAFANA_URL}/api/alerts/${ALERT_ID}/pause"
```

#### Get Alert History
```bash
curl -H "Authorization: Bearer ${API_TOKEN}" \
  "${GRAFANA_URL}/api/annotations?dashboardId=${DASHBOARD_ID}&panelId=${PANEL_ID}&type=alert"
```

Parameters:
- `from`: Start time (unix timestamp ms)
- `to`: End time (unix timestamp ms)
- `limit`: Max results (default 100)

#### Create/Update Alert Rule

Alerts are embedded in dashboard panels. To modify:
1. GET dashboard JSON
2. Update panel's `alert` property
3. POST updated dashboard with `overwrite: true`

Alert structure:
```json
{
  "alert": {
    "name": "Panel Title alert",
    "message": "Alert message",
    "frequency": "60s",
    "handler": 1,
    "conditions": [
      {
        "evaluator": {
          "params": [90],
          "type": "gt"
        },
        "operator": {
          "type": "and"
        },
        "query": {
          "params": ["A", "5m", "now"]
        },
        "type": "query"
      }
    ]
  }
}
```

### 4. Datasource Operations

**Best Practice**: Always check `~/.grafana-skill/config.json` first for datasource information. Only query the API if config is missing or outdated.

#### Get Datasources from Config (Recommended)
```bash
# Read from local config (fast, no API call)
cat ~/.grafana-skill/config.json | jq '.datasources'

# Get specific datasource
cat ~/.grafana-skill/config.json | jq '.datasources["Prometheus 1"]'

# Get default datasource
cat ~/.grafana-skill/config.json | jq -r '.default_datasource'
```

#### List All Datasources (API fallback)
```bash
# Only use if config.json doesn't exist or needs refresh
curl -H "Authorization: Bearer ${API_TOKEN}" \
  "${GRAFANA_URL}/api/datasources"
```

#### Get Datasource by UID
```bash
curl -H "Authorization: Bearer ${API_TOKEN}" \
  "${GRAFANA_URL}/api/datasources/uid/${DATASOURCE_UID}"
```

#### Query Datasource Health
```bash
curl -H "Authorization: Bearer ${API_TOKEN}" \
  "${GRAFANA_URL}/api/datasources/${DATASOURCE_ID}/health"
```

## Metric Discovery with prom-cli

When users need to query metrics but don't know the exact metric names, use `prom`:

### Check Installation
```bash
if ! command -v prom &> /dev/null; then
  npm install -g github:jack482653/prom-cli
fi
```

### Configure Prometheus URL
```bash
# Set default Prometheus URL (saves to ~/.prom-cli/config.json)
prom config "${PROM_URL}"
```

### Check Prometheus Status
```bash
prom status
```

### Instant Query
```bash
# Query current metric value
prom query "up"
prom query "rate(http_requests_total[5m])"
```

### Range Query
```bash
# Query time range (supports relative time)
prom query-range "rate(http_requests_total[5m])" --start "1h" --end "now"
prom query-range "up{job=\"api\"}" --start "24h" --end "now"

# Query with absolute time (ISO 8601 format)
prom query-range "up" --start "2024-01-01T00:00:00Z" --end "2024-01-01T23:59:59Z"
```

### List Targets
```bash
prom targets
```

Note: Prometheus URLs can be extracted from Grafana datasource configs or inferred from datasource names. The `prom` command stores configuration in `~/.prom-cli/config.json` for convenience.

## Output Formatting

Based on user request and data type, choose appropriate format:

### Tables
Best for: Dashboard lists, alert summaries, datasource info

Example:
```
| Dashboard | UID | Tags | URL |
|-----------|-----|------|-----|
| Instance Group | abc | prod | /d/abc |
```

### Graphs/Charts
Best for: Time-series metrics, trend visualization

Use ASCII charts for CLI or suggest Grafana dashboard URLs

### JSON
Best for: Export operations, detailed configurations, API responses

Pretty-print JSON for readability

### Text Description
Best for: Status summaries, single values, explanations

Example:
```
Worker QPS (last 24h):
- us-east-1: 1,250 req/s
- us-west-2: 980 req/s
- ap-northeast-1: 1,100 req/s
```

## Python Helper Usage

The Python scripts in `references/` provide simplified interfaces:

### Query Metrics (Recommended Method)
```python
from query_helper import GrafanaQueryHelper

# Use default config (auto-selected by GRAFANA_ENV)
helper = GrafanaQueryHelper()

# Or specify config explicitly
helper = GrafanaQueryHelper("~/.grafana-skill/config-prod.json")

# Method 1: Relative time (last 1 hour)
result = helper.query(
    datasource_name="Prometheus 1",
    query='up{job="api"}',
    time_range="1h"
)

# Method 2: Absolute time with ISO format
result = helper.query(
    datasource_name="Prometheus 1",
    query='rate(http_requests_total[5m])',
    start_time="2026-01-28 19:00:00",
    end_time="2026-01-28 19:30:00"
)

# Method 3: Unix timestamps
result = helper.query(
    datasource_name="Prometheus 1",
    query='up',
    start_time="1769598000",  # Seconds, not milliseconds
    end_time="1769599800"
)

# Format results
print(helper.format_prometheus_result(result, format_type="table"))
```

### Manage Dashboards
```python
from dashboard_manager import GrafanaDashboardManager

manager = GrafanaDashboardManager()

# List dashboards
dashboards = manager.list_dashboards(query="Redis")

# Get dashboard details
dashboard = manager.get_dashboard("DshZWWW")

# Export dashboard
manager.export_dashboard("DshZWWW", "dashboard_backup.json")
```

### Manage Alerts
```python
from alert_manager import GrafanaAlertManager

manager = GrafanaAlertManager()

# List alerting alerts
alerts = manager.get_alerting_alerts()

# Pause alert
manager.pause_alert(alert_id=123)

# Get alert history
history = manager.get_alert_history(hours=24)
```

## Workflow Examples

### Example 0: Multiple Environment Setup
```bash
# Setup production environment
export GRAFANA_URL="http://grafana-prod.example.com"
export GRAFANA_API_TOKEN="prod_token"
export GRAFANA_ENV="prod"
python3 ~/.grafana-skill/scripts/generate_datasources.py

# Setup staging environment
export GRAFANA_URL="http://grafana-staging.example.com"
export GRAFANA_API_TOKEN="staging_token"
export GRAFANA_ENV="staging"
python3 ~/.grafana-skill/scripts/generate_datasources.py

# Use production config
export GRAFANA_ENV=prod
python3 -c "
from query_helper import GrafanaQueryHelper
helper = GrafanaQueryHelper()
print(f'Using config: {helper.config_file}')
print(f'Grafana URL: {helper.grafana_url}')
"

# Use staging config
export GRAFANA_ENV=staging
python3 -c "
from query_helper import GrafanaQueryHelper
helper = GrafanaQueryHelper()
print(f'Using config: {helper.config_file}')
print(f'Grafana URL: {helper.grafana_url}')
"
```

### Example 1: List Dashboards
```bash
# Load config
CONFIG=$(cat ~/.grafana-skill/config.json)
GRAFANA_URL=$(echo $CONFIG | jq -r '.grafana_url')
API_TOKEN=$(echo $CONFIG | jq -r '.api_token')

# Fetch dashboards
curl -H "Authorization: Bearer ${API_TOKEN}" \
  "${GRAFANA_URL}/api/search?type=dash-db" | jq -r '.[] | "\(.title) (\(.uid))"'
```

### Example 2: Query Metrics from Dashboard
```bash
# 1. Search for dashboard
DASHBOARD_UID=$(curl -s -H "Authorization: Bearer ${API_TOKEN}" \
  "${GRAFANA_URL}/api/search?query=Instance%20Group" | jq -r '.[0].uid')

# 2. Get dashboard details
DASHBOARD=$(curl -s -H "Authorization: Bearer ${API_TOKEN}" \
  "${GRAFANA_URL}/api/dashboards/uid/${DASHBOARD_UID}")

# 3. Extract queries from panels
echo "$DASHBOARD" | jq '.dashboard.panels[].targets[].expr'

# 4. Execute queries via datasource
# (Extract datasource UID from panel config, then query)
```

### Example 3: Check Alert Status
```bash
# Get all alerts
curl -s -H "Authorization: Bearer ${API_TOKEN}" \
  "${GRAFANA_URL}/api/alerts" | \
  jq -r '.[] | "\(.name): \(.state)"'
```

### Example 4: Discover Metrics and Query
```bash
# 1. Configure Prometheus URL
prom config "${PROM_URL}"

# 2. Check available targets
prom targets

# 3. Query instant value
prom query "up{job=\"worker\"}"

# 4. Query time range for worker metrics
prom query-range "rate(worker_requests_total[5m])" --start "24h" --end "now"

# 5. Build complex query and execute via Grafana API
QUERY='sum by (region) (rate(worker_requests_total[5m]))'

curl -X POST -H "Authorization: Bearer ${API_TOKEN}" \
  -H "Content-Type: application/json" \
  -d "{
    \"queries\": [{
      \"refId\": \"A\",
      \"datasource\": {\"uid\": \"${DATASOURCE_UID}\"},
      \"expr\": \"${QUERY}\",
      \"range\": true
    }],
    \"from\": \"now-24h\",
    \"to\": \"now\"
  }" \
  "${GRAFANA_URL}/api/ds/query"
```

## Python Helper Scripts

For complex operations, use Python scripts in `references/` directory:

### Query Helper
```python
# references/query_helper.py
# Simplifies metric queries with retry logic and formatting
```

### Dashboard Manager
```python
# references/dashboard_manager.py
# CRUD operations for dashboards with validation
```

### Alert Manager
```python
# references/alert_manager.py
# Alert rule creation and management
```

## Best Practices

1. **Always load config first**: Check for `~/.grafana-skill/config.json` before operations
2. **Use config for datasource info**: Read datasource UIDs/IDs from config.json instead of calling `/api/datasources` API - it's faster and avoids unnecessary API calls
3. **Multiple environments**: Use separate config files for prod/staging/dev environments via `GRAFANA_ENV` variable
4. **Environment isolation**: Set `GRAFANA_ENV` in your shell profile or CI/CD pipeline to ensure correct environment
5. **Validate datasource UIDs**: Use the generated config to get correct UIDs
6. **Handle rate limits**: Add delays between bulk operations
7. **Pretty-print output**: Format JSON and tables for readability
8. **Error handling**: Check HTTP status codes and provide clear error messages
9. **Time ranges**: Default to sensible ranges (e.g., "now-1h" for recent data)
10. **Metric discovery**: Use `prom` command when metric names are unknown
11. **Security**: Never log or display API tokens in output; use file permissions 600 for config files

## API Reference

Grafana v7.5 HTTP API Documentation:
https://grafana.com/docs/grafana/v7.5/http_api/

Key endpoints:
- `/api/search` - Search dashboards and folders
- `/api/dashboards/*` - Dashboard CRUD operations
- `/api/alerts` - Alert management
- `/api/datasources` - Datasource configuration
- `/api/ds/query` - Query datasources
- `/api/annotations` - Alert history and annotations

## Troubleshooting

### Config Not Found
```bash
if [ ! -f ~/.grafana-skill/config.json ]; then
  echo "Config not found. Please set GRAFANA_URL and GRAFANA_API_TOKEN, then run:"
  echo "python3 ~/.grafana-skill/scripts/generate_datasources.py"
fi
```

### Invalid API Token
Check for 401 responses and prompt user to update token in config

### Datasource UID Mismatch
Re-generate config with `generate_datasources.py`

### prom Command Not Found
Install via npm: `npm install -g github:jack482653/prom-cli`

### Query Returns No Data
- Verify time range
- Check metric existence with `prom` command
- Validate datasource UID
- Test query in Grafana UI first
