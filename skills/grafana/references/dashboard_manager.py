#!/usr/bin/env python3
"""
Grafana Dashboard Manager

CRUD operations for Grafana dashboards with validation and error handling.

Usage:
    from dashboard_manager import GrafanaDashboardManager

    # Use default config (auto-selected by GRAFANA_ENV)
    manager = GrafanaDashboardManager()

    # Or specify config explicitly
    manager = GrafanaDashboardManager(config_path="~/.grafana-skill/config-prod.json")

    # List dashboards
    dashboards = manager.list_dashboards()

    # Get dashboard
    dashboard = manager.get_dashboard(uid="abc123")

    # Export dashboard
    manager.export_dashboard(uid="abc123", output_file="dashboard.json")

    # Create dashboard
    manager.create_dashboard(
        title="My Dashboard",
        tags=["monitoring", "prod"],
        folder_id=0
    )
"""

import json
import os
import urllib.request
import urllib.error
from pathlib import Path
from typing import Dict, List, Optional, Any


class GrafanaDashboardManager:
    """Manager for Grafana dashboard operations."""

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
            endpoint: API endpoint (e.g., "/api/dashboards/db")
            method: HTTP method
            data: Request payload for POST/PUT

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

    def list_dashboards(
        self,
        query: str = "",
        tag: str = "",
        starred: bool = False
    ) -> List[Dict[str, Any]]:
        """
        List all dashboards.

        Args:
            query: Search term (matches title)
            tag: Filter by tag
            starred: Only starred dashboards

        Returns:
            List of dashboard objects
        """
        params = ["type=dash-db"]

        if query:
            params.append(f"query={urllib.parse.quote(query)}")
        if tag:
            params.append(f"tag={urllib.parse.quote(tag)}")
        if starred:
            params.append("starred=true")

        endpoint = f"/api/search?{'&'.join(params)}"
        return self._request(endpoint)

    def get_dashboard(self, uid: str) -> Dict[str, Any]:
        """
        Get dashboard by UID.

        Args:
            uid: Dashboard UID

        Returns:
            Dashboard object with full configuration
        """
        return self._request(f"/api/dashboards/uid/{uid}")

    def search_dashboards(self, title: str) -> List[Dict[str, Any]]:
        """
        Search dashboards by title.

        Args:
            title: Title search term

        Returns:
            List of matching dashboards
        """
        return self.list_dashboards(query=title)

    def get_dashboard_by_title(self, title: str) -> Optional[Dict[str, Any]]:
        """
        Get dashboard by exact title match.

        Args:
            title: Exact dashboard title

        Returns:
            Dashboard object or None if not found
        """
        results = self.search_dashboards(title)
        for dash in results:
            if dash.get("title") == title:
                return self.get_dashboard(dash["uid"])
        return None

    def create_dashboard(
        self,
        title: str,
        tags: List[str] = None,
        folder_id: int = 0,
        panels: List[Dict] = None,
        overwrite: bool = False
    ) -> Dict[str, Any]:
        """
        Create a new dashboard.

        Args:
            title: Dashboard title
            tags: List of tags
            folder_id: Folder ID (0 for General)
            panels: List of panel configurations
            overwrite: Overwrite if exists

        Returns:
            Created dashboard response
        """
        if tags is None:
            tags = []
        if panels is None:
            panels = []

        payload = {
            "dashboard": {
                "title": title,
                "tags": tags,
                "timezone": "browser",
                "panels": panels,
                "schemaVersion": 16,
                "version": 0,
                "refresh": "5s"
            },
            "folderId": folder_id,
            "overwrite": overwrite,
            "message": f"Created via dashboard_manager.py"
        }

        return self._request("/api/dashboards/db", method="POST", data=payload)

    def update_dashboard(
        self,
        uid: str,
        updates: Dict[str, Any],
        message: str = "Updated via dashboard_manager.py"
    ) -> Dict[str, Any]:
        """
        Update existing dashboard.

        Args:
            uid: Dashboard UID
            updates: Dictionary of fields to update
            message: Commit message

        Returns:
            Update response
        """
        # Get current dashboard
        current = self.get_dashboard(uid)

        # Update fields
        dashboard = current["dashboard"]
        for key, value in updates.items():
            dashboard[key] = value

        # Increment version
        dashboard["version"] += 1

        payload = {
            "dashboard": dashboard,
            "folderId": current["meta"].get("folderId", 0),
            "overwrite": True,
            "message": message
        }

        return self._request("/api/dashboards/db", method="POST", data=payload)

    def delete_dashboard(self, uid: str) -> Dict[str, Any]:
        """
        Delete dashboard by UID.

        Args:
            uid: Dashboard UID

        Returns:
            Deletion response
        """
        return self._request(f"/api/dashboards/uid/{uid}", method="DELETE")

    def export_dashboard(
        self,
        uid: str,
        output_file: str,
        include_meta: bool = False
    ) -> None:
        """
        Export dashboard to JSON file.

        Args:
            uid: Dashboard UID
            output_file: Output file path
            include_meta: Include metadata in export
        """
        dashboard = self.get_dashboard(uid)

        if not include_meta:
            # Remove metadata for cleaner export
            export_data = dashboard["dashboard"]
        else:
            export_data = dashboard

        output_path = Path(output_file).expanduser()
        with open(output_path, 'w') as f:
            json.dump(export_data, f, indent=2)

        print(f"Dashboard exported to: {output_path}")

    def import_dashboard(
        self,
        input_file: str,
        folder_id: int = 0,
        overwrite: bool = False
    ) -> Dict[str, Any]:
        """
        Import dashboard from JSON file.

        Args:
            input_file: Input JSON file path
            folder_id: Target folder ID
            overwrite: Overwrite if exists

        Returns:
            Import response
        """
        input_path = Path(input_file).expanduser()
        with open(input_path, 'r') as f:
            dashboard = json.load(f)

        # Reset version and ID for import
        if "id" in dashboard:
            del dashboard["id"]
        dashboard["version"] = 0

        payload = {
            "dashboard": dashboard,
            "folderId": folder_id,
            "overwrite": overwrite,
            "message": f"Imported from {input_file}"
        }

        return self._request("/api/dashboards/db", method="POST", data=payload)

    def get_dashboard_permissions(self, uid: str) -> List[Dict[str, Any]]:
        """
        Get dashboard permissions.

        Args:
            uid: Dashboard UID

        Returns:
            List of permission objects
        """
        # First get dashboard ID from UID
        dashboard = self.get_dashboard(uid)
        dashboard_id = dashboard["dashboard"]["id"]

        return self._request(f"/api/dashboards/id/{dashboard_id}/permissions")

    def format_dashboard_list(self, dashboards: List[Dict[str, Any]]) -> str:
        """
        Format dashboard list as table.

        Args:
            dashboards: List of dashboard objects

        Returns:
            Formatted table string
        """
        if not dashboards:
            return "No dashboards found"

        lines = [
            "| Title | UID | Tags | Folder | URL |",
            "|-------|-----|------|--------|-----|"
        ]

        for dash in dashboards:
            title = dash.get("title", "N/A")
            uid = dash.get("uid", "N/A")
            tags = ", ".join(dash.get("tags", [])) or "none"
            folder = dash.get("folderTitle", "General")
            url = dash.get("url", "N/A")

            lines.append(f"| {title} | {uid} | {tags} | {folder} | {url} |")

        return "\n".join(lines)


def main():
    """Example usage."""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python3 dashboard_manager.py <command> [args]")
        print("\nCommands:")
        print("  list [query]              - List dashboards")
        print("  get <uid>                 - Get dashboard by UID")
        print("  export <uid> <file>       - Export dashboard to file")
        print("  search <title>            - Search dashboards")
        sys.exit(1)

    command = sys.argv[1]
    manager = GrafanaDashboardManager()

    try:
        if command == "list":
            query = sys.argv[2] if len(sys.argv) > 2 else ""
            dashboards = manager.list_dashboards(query=query)
            print(manager.format_dashboard_list(dashboards))

        elif command == "get":
            if len(sys.argv) < 3:
                print("Error: Missing UID argument")
                sys.exit(1)
            uid = sys.argv[2]
            dashboard = manager.get_dashboard(uid)
            print(json.dumps(dashboard, indent=2))

        elif command == "export":
            if len(sys.argv) < 4:
                print("Error: Missing UID or output file argument")
                sys.exit(1)
            uid = sys.argv[2]
            output = sys.argv[3]
            manager.export_dashboard(uid, output)

        elif command == "search":
            if len(sys.argv) < 3:
                print("Error: Missing title argument")
                sys.exit(1)
            title = sys.argv[2]
            dashboards = manager.search_dashboards(title)
            print(manager.format_dashboard_list(dashboards))

        else:
            print(f"Unknown command: {command}")
            sys.exit(1)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
