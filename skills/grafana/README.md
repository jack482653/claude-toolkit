# Grafana

Interact with Grafana for dashboard management, metrics querying, and alert monitoring.

## Installation

1. Download `grafana.zip` from the [releases page](https://github.com/jack482653/claude-toolkit/releases)
2. Go to Claude.ai → Settings → Capabilities → Skills
3. Upload the ZIP file

## Setup

### 1. Generate Configuration

Set environment variables:
```bash
export GRAFANA_URL="http://your-grafana-instance.com"
export GRAFANA_API_TOKEN="your_api_token_here"
```

Generate datasources config:
```bash
# The script is in the Grafana skill's references/ directory
python3 /path/to/grafana-skill/references/generate_datasources.py
```

This creates `~/.grafana-skill/config.json` with your Grafana datasources.

### 2. Install prom-cli (Optional)

For metric discovery:
```bash
# The script is in the Grafana skill's references/ directory
bash /path/to/grafana-skill/references/install_promcli.sh
```

Or install manually:
```bash
npm install -g github:jack482653/prom-cli
```

## Features

### Dashboard Management
- List all dashboards
- Search dashboards by name or tag
- View dashboard details and panels
- Create new dashboards
- Modify existing dashboards
- Export dashboard configurations

### Metrics Querying
- Query Prometheus datasources
- Support for multiple datasources (Prometheus, Azure Monitor, GCP)
- Time-series data retrieval
- Custom time ranges (relative or absolute)
- Metric discovery with prom-cli

### Alert Management
- List all alerts with status
- View alert details and conditions
- Pause/unpause alerts
- View alert history
- Create/modify alert rules

### Datasource Operations
- List all configured datasources
- Get datasource details
- Check datasource health
- Auto-configuration via generation script

## Usage

### Basic Queries

List dashboards:
```
Grafana 上有哪些 dashboard
```

Query metrics:
```
請幫我到 Grafana 查詢 Instance Group Dashboard 各個 instance group 的 instance 數量狀態
```

Time-series queries:
```
使用 Grafana 查詢服務一天內不同的 region 的 QPS
```

### Alert Management

Check alert status:
```
查看 Grafana 的 alert 狀態
```

View alert history:
```
顯示過去 24 小時的 alert 歷史記錄
```

### Dashboard Operations

Export dashboard:
```
匯出 Instance Group Dashboard 的配置
```

Create dashboard:
```
建立一個新的 dashboard 來監控 API latency
```

### Metric Discovery

Find available metrics:
```
查詢有哪些與服務相關的 metrics
```

## Output Formats

The skill automatically selects appropriate output format based on your request:

- **Tables**: Dashboard lists, alert summaries, datasource info
- **Graphs**: Time-series metrics, trends (ASCII charts or Grafana URLs)
- **JSON**: Export operations, detailed configs
- **Text**: Status summaries, single values, explanations

## Configuration File

Location: `~/.grafana-skill/config.json`

Example structure:
```json
{
  "grafana_url": "http://grafana.example.com",
  "api_token": "YOUR_API_TOKEN",
  "datasources": {
    "Prometheus Main": {
      "uid": "000000001",
      "id": 1
    },
    "Azure Monitor": {
      "uid": "000000008",
      "id": 8
    }
  }
}
```

## Supported Grafana Version

This skill is designed for Grafana v7.5. Most features should work with newer versions, but API compatibility is guaranteed for v7.5.

## API Reference

Full Grafana v7.5 HTTP API documentation:
https://grafana.com/docs/grafana/v7.5/http_api/

## Troubleshooting

### Config not found
Run the datasource generation script:
```bash
python3 /path/to/grafana-skill/references/generate_datasources.py
```

### Authentication errors
Update your API token in `~/.grafana-skill/config.json`

### prom-cli not found
Install via the provided script:
```bash
bash /path/to/grafana-skill/references/install_promcli.sh
```

### No data returned
- Check time range (try "now-1h" for recent data)
- Verify metric name with prom-cli
- Validate datasource UID in config
- Test query in Grafana UI first

## Security Notes

- API tokens are stored in `~/.grafana-skill/config.json`
- Keep your config file secure with proper permissions: `chmod 600 ~/.grafana-skill/config.json`
- Never commit config files with real tokens to version control
- Use read-only API tokens when possible

## Examples

### Example 1: Dashboard Overview
**Query**: "列出所有 production 相關的 dashboard"

**Response**: Table showing dashboard names, UIDs, tags, and URLs

### Example 2: Real-time Metrics
**Query**: "查詢 API Gateway 過去一小時的 request rate"

**Response**: Time-series data with per-region breakdown and trend summary

### Example 3: Alert Investigation
**Query**: "為什麼 database alert 在觸發?"

**Response**: Alert status, conditions, recent history, and current metric values

### Example 4: Dashboard Export
**Query**: "匯出 Monitoring Dashboard 的 JSON 配置"

**Response**: Complete dashboard JSON saved to file

## Contributing

Report issues or suggest features at:
https://github.com/jack482653/claude-toolkit/issues
