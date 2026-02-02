#!/usr/bin/env python3
"""
Grafana Alert Manager

Manage Grafana alerts including viewing, pausing, and checking alert history.

Usage:
    from alert_manager import GrafanaAlertManager

    # Use default config (auto-selected by GRAFANA_ENV)
    manager = GrafanaAlertManager()

    # Or specify config explicitly
    manager = GrafanaAlertManager(config_path="~/.grafana-skill/config-prod.json")

    # List all alerts
    alerts = manager.list_alerts()

    # Get alert details
    alert = manager.get_alert(alert_id=123)

    # Pause alert
    manager.pause_alert(alert_id=123)

    # Get alert history
    history = manager.get_alert_history(dashboard_id=1, hours=24)
"""

import json
import os
import urllib.request
import urllib.error
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta


class GrafanaAlertManager:
    """Manager for Grafana alert operations."""

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize with config file.

        Config file selection priority:
        1. If config_path is provided, use it directly
        2. If GRAFANA_ENV is set, use config-{GRAFANA_ENV}.json
        3. Otherwise, use config.json

        Args:
            config_path: Path to Grafana config JSON file (optional)

        Environment Variables:
            GRAFANA_ENV: Environment name (e.g., 'prod', 'staging')
        """
        config_file = self._resolve_config_path(config_path)

        if not config_file.exists():
            raise FileNotFoundError(
                f"Config file not found: {config_file}\n"
                "Run generate_datasources.py first"
            )

        with open(config_file, 'r') as f:
            self.config = json.load(f)

        self.grafana_url = self.config["grafana_url"]
        self.api_token = self.config["api_token"]

    def _resolve_config_path(self, config_path: Optional[str] = None) -> Path:
        """
        Resolve config file path based on priority.

        Priority:
        1. Explicit config_path parameter
        2. GRAFANA_ENV environment variable
        3. Default config.json
        """
        config_dir = Path.home() / ".grafana-skill"

        if config_path:
            return Path(config_path).expanduser()

        env = os.environ.get("GRAFANA_ENV")
        if env:
            env_config = config_dir / f"config-{env}.json"
            if env_config.exists():
                return env_config
            print(f"Warning: GRAFANA_ENV={env} but {env_config} not found, using default config.json")

        return config_dir / "config.json"

    def _request(
        self,
        endpoint: str,
        method: str = "GET",
        data: Optional[Dict] = None
    ) -> Any:
        """
        Make HTTP request to Grafana API.

        Args:
            endpoint: API endpoint
            method: HTTP method
            data: Request payload

        Returns:
            Parsed JSON response

        Raises:
            Exception: On HTTP errors
        """
        url = f"{self.grafana_url}{endpoint}"

        req = urllib.request.Request(url, method=method)
        req.add_header("Authorization", f"Bearer {self.api_token}")
        req.add_header("Content-Type", "application/json")

        if data:
            req.data = json.dumps(data).encode('utf-8')

        try:
            with urllib.request.urlopen(req) as response:
                return json.loads(response.read())
        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8') if e.fp else ""
            raise Exception(
                f"API request failed: HTTP {e.code} - {e.reason}\n"
                f"Endpoint: {endpoint}\n"
                f"Response: {error_body}"
            )
        except urllib.error.URLError as e:
            raise Exception(f"Connection failed: {e.reason}")

    def list_alerts(self, state: str = "") -> List[Dict[str, Any]]:
        """
        List all alerts.

        Args:
            state: Filter by state ("alerting", "ok", "paused", "pending", "no_data")

        Returns:
            List of alert objects
        """
        endpoint = "/api/alerts"
        if state:
            endpoint += f"?state={state}"

        return self._request(endpoint)

    def get_alert(self, alert_id: int) -> Dict[str, Any]:
        """
        Get alert by ID.

        Args:
            alert_id: Alert ID

        Returns:
            Alert object with full details
        """
        return self._request(f"/api/alerts/{alert_id}")

    def pause_alert(self, alert_id: int, paused: bool = True) -> Dict[str, Any]:
        """
        Pause or unpause an alert.

        Args:
            alert_id: Alert ID
            paused: True to pause, False to unpause

        Returns:
            Response with updated alert state
        """
        data = {"paused": paused}
        return self._request(
            f"/api/alerts/{alert_id}/pause",
            method="POST",
            data=data
        )

    def unpause_alert(self, alert_id: int) -> Dict[str, Any]:
        """
        Unpause an alert.

        Args:
            alert_id: Alert ID

        Returns:
            Response with updated alert state
        """
        return self.pause_alert(alert_id, paused=False)

    def get_alert_history(
        self,
        dashboard_id: Optional[int] = None,
        panel_id: Optional[int] = None,
        hours: int = 24,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get alert history from annotations.

        Args:
            dashboard_id: Filter by dashboard ID
            panel_id: Filter by panel ID
            hours: Hours of history to retrieve
            limit: Maximum results

        Returns:
            List of alert annotation objects
        """
        now = int(datetime.now().timestamp() * 1000)
        from_time = int((datetime.now() - timedelta(hours=hours)).timestamp() * 1000)

        params = [
            f"from={from_time}",
            f"to={now}",
            "type=alert",
            f"limit={limit}"
        ]

        if dashboard_id:
            params.append(f"dashboardId={dashboard_id}")
        if panel_id:
            params.append(f"panelId={panel_id}")

        endpoint = f"/api/annotations?{'&'.join(params)}"
        return self._request(endpoint)

    def get_alerts_by_dashboard(self, dashboard_uid: str) -> List[Dict[str, Any]]:
        """
        Get all alerts for a specific dashboard.

        Args:
            dashboard_uid: Dashboard UID

        Returns:
            List of alerts from that dashboard
        """
        all_alerts = self.list_alerts()
        return [
            alert for alert in all_alerts
            if alert.get("dashboardUid") == dashboard_uid
        ]

    def get_alerting_alerts(self) -> List[Dict[str, Any]]:
        """
        Get all currently alerting alerts.

        Returns:
            List of alerting alerts
        """
        return self.list_alerts(state="alerting")

    def get_paused_alerts(self) -> List[Dict[str, Any]]:
        """
        Get all paused alerts.

        Returns:
            List of paused alerts
        """
        return self.list_alerts(state="paused")

    def format_alert_list(
        self,
        alerts: List[Dict[str, Any]],
        include_details: bool = False
    ) -> str:
        """
        Format alert list as table.

        Args:
            alerts: List of alert objects
            include_details: Include additional details

        Returns:
            Formatted table string
        """
        if not alerts:
            return "No alerts found"

        if include_details:
            lines = [
                "| ID | Name | State | Dashboard | Panel | Message |",
                "|----|------|-------|-----------|-------|---------|"
            ]
        else:
            lines = [
                "| ID | Name | State | Dashboard |",
                "|----|------|-------|-----------|"
            ]

        for alert in alerts:
            alert_id = alert.get("id", "N/A")
            name = alert.get("name", "N/A")
            state = alert.get("state", "N/A")
            dashboard = alert.get("dashboardSlug", "N/A")

            if include_details:
                panel = alert.get("panelId", "N/A")
                message = alert.get("message", "")[:50]  # Truncate
                lines.append(
                    f"| {alert_id} | {name} | {state} | {dashboard} | {panel} | {message} |"
                )
            else:
                lines.append(f"| {alert_id} | {name} | {state} | {dashboard} |")

        return "\n".join(lines)

    def format_alert_history(
        self,
        history: List[Dict[str, Any]]
    ) -> str:
        """
        Format alert history as table.

        Args:
            history: List of alert history objects

        Returns:
            Formatted table string
        """
        if not history:
            return "No alert history found"

        lines = [
            "| Time | Alert | State | Message |",
            "|------|-------|-------|---------|"
        ]

        for event in history:
            timestamp = event.get("time", 0)
            time_str = datetime.fromtimestamp(timestamp / 1000).strftime(
                "%Y-%m-%d %H:%M:%S"
            )
            alert_name = event.get("alertName", "N/A")
            state = event.get("newState", "N/A")
            message = event.get("text", "")[:50]  # Truncate

            lines.append(f"| {time_str} | {alert_name} | {state} | {message} |")

        return "\n".join(lines)

    def get_alert_summary(self) -> Dict[str, int]:
        """
        Get summary of alert states.

        Returns:
            Dictionary with counts by state
        """
        alerts = self.list_alerts()

        summary = {
            "total": len(alerts),
            "alerting": 0,
            "ok": 0,
            "paused": 0,
            "pending": 0,
            "no_data": 0
        }

        for alert in alerts:
            state = alert.get("state", "unknown")
            if state in summary:
                summary[state] += 1

        return summary

    def format_alert_summary(self) -> str:
        """
        Format alert summary as text.

        Returns:
            Formatted summary string
        """
        summary = self.get_alert_summary()

        lines = [
            "Alert Summary:",
            f"  Total: {summary['total']}",
            f"  Alerting: {summary['alerting']}",
            f"  OK: {summary['ok']}",
            f"  Paused: {summary['paused']}",
            f"  Pending: {summary['pending']}",
            f"  No Data: {summary['no_data']}"
        ]

        return "\n".join(lines)


def main():
    """Example usage."""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python3 alert_manager.py <command> [args]")
        print("\nCommands:")
        print("  list [state]          - List alerts (optionally filtered by state)")
        print("  get <id>              - Get alert details")
        print("  pause <id>            - Pause alert")
        print("  unpause <id>          - Unpause alert")
        print("  history [hours]       - Get alert history (default: 24h)")
        print("  summary               - Get alert state summary")
        print("  alerting              - List currently alerting alerts")
        sys.exit(1)

    command = sys.argv[1]
    manager = GrafanaAlertManager()

    try:
        if command == "list":
            state = sys.argv[2] if len(sys.argv) > 2 else ""
            alerts = manager.list_alerts(state=state)
            print(manager.format_alert_list(alerts, include_details=True))

        elif command == "get":
            if len(sys.argv) < 3:
                print("Error: Missing alert ID argument")
                sys.exit(1)
            alert_id = int(sys.argv[2])
            alert = manager.get_alert(alert_id)
            print(json.dumps(alert, indent=2))

        elif command == "pause":
            if len(sys.argv) < 3:
                print("Error: Missing alert ID argument")
                sys.exit(1)
            alert_id = int(sys.argv[2])
            result = manager.pause_alert(alert_id)
            print(f"Alert {alert_id} paused successfully")

        elif command == "unpause":
            if len(sys.argv) < 3:
                print("Error: Missing alert ID argument")
                sys.exit(1)
            alert_id = int(sys.argv[2])
            result = manager.unpause_alert(alert_id)
            print(f"Alert {alert_id} unpaused successfully")

        elif command == "history":
            hours = int(sys.argv[2]) if len(sys.argv) > 2 else 24
            history = manager.get_alert_history(hours=hours)
            print(manager.format_alert_history(history))

        elif command == "summary":
            print(manager.format_alert_summary())

        elif command == "alerting":
            alerts = manager.get_alerting_alerts()
            print(manager.format_alert_list(alerts, include_details=True))

        else:
            print(f"Unknown command: {command}")
            sys.exit(1)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
