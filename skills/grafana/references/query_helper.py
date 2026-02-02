#!/usr/bin/env python3
"""
Grafana Query Helper

Simplifies metric queries with retry logic, formatting, and error handling.

Usage:
    from query_helper import GrafanaQueryHelper

    # Use default config (auto-selected by GRAFANA_ENV)
    helper = GrafanaQueryHelper()

    # Or specify config explicitly
    helper = GrafanaQueryHelper(config_path="~/.grafana-skill/config-prod.json")

    result = helper.query(
        datasource_name="Prometheus 1",
        query="rate(http_requests_total[5m])",
        time_range="1h"
    )
"""

import json
import os
import urllib.request
import urllib.parse
import urllib.error
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import time


class GrafanaQueryHelper:
    """Helper class for Grafana metric queries."""

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
                        Maps to config-{env}.json file

        Examples:
            # Use default config (config.json)
            helper = GrafanaQueryHelper()

            # Use environment-specific config
            # export GRAFANA_ENV=prod
            helper = GrafanaQueryHelper()  # Uses config-prod.json

            # Use explicit config path
            helper = GrafanaQueryHelper("~/.grafana-skill/config-staging.json")
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
        self.datasources = self.config["datasources"]
        self.config_file = config_file

    def _resolve_config_path(self, config_path: Optional[str] = None) -> Path:
        """
        Resolve config file path based on priority.

        Priority:
        1. Explicit config_path parameter
        2. GRAFANA_ENV environment variable
        3. Default config.json

        Args:
            config_path: Optional explicit config path

        Returns:
            Resolved Path object
        """
        config_dir = Path.home() / ".grafana-skill"

        # Priority 1: Explicit path provided
        if config_path:
            return Path(config_path).expanduser()

        # Priority 2: Environment variable
        env = os.environ.get("GRAFANA_ENV")
        if env:
            env_config = config_dir / f"config-{env}.json"
            if env_config.exists():
                return env_config
            # If env-specific config doesn't exist, print warning and fall through
            print(f"Warning: GRAFANA_ENV={env} but {env_config} not found, using default config.json")

        # Priority 3: Default config.json
        return config_dir / "config.json"

    def get_datasource_uid(self, datasource_name: str) -> str:
        """
        Get datasource UID by name.

        Args:
            datasource_name: Name of the datasource

        Returns:
            Datasource UID

        Raises:
            KeyError: If datasource not found
        """
        if datasource_name not in self.datasources:
            available = ", ".join(self.datasources.keys())
            raise KeyError(
                f"Datasource '{datasource_name}' not found.\n"
                f"Available datasources: {available}"
            )
        return self.datasources[datasource_name]["uid"]

    def _parse_time_range(self, time_range: str) -> tuple:
        """
        Parse time range string to Grafana format.

        Args:
            time_range: Time range like "1h", "24h", "7d" or absolute timestamps

        Returns:
            Tuple of (from_time, to_time) in Grafana format
        """
        # If already in Grafana format (starts with "now")
        if time_range.startswith("now"):
            return f"now-{time_range[3:]}", "now"

        # Parse simple duration format (e.g., "1h", "24h", "7d")
        units = {
            's': 'seconds',
            'm': 'minutes',
            'h': 'hours',
            'd': 'days',
            'w': 'weeks'
        }

        time_range = time_range.strip()
        if time_range[-1] in units:
            return f"now-{time_range}", "now"

        # Default to 1 hour
        return "now-1h", "now"

    def query(
        self,
        datasource_name: str,
        query: str,
        time_range: str = "1h",
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        step: int = 15,
        max_retries: int = 3
    ) -> Dict[str, Any]:
        """
        Smart query method that automatically chooses the best API.

        Supports both relative and absolute time ranges:
        - Relative: time_range="1h", "24h", "7d"
        - Absolute: start_time="2026-01-28 19:00:00", end_time="2026-01-28 19:30:00"
        - Unix timestamps: start_time="1769598000", end_time="1769599800"

        Args:
            datasource_name: Name of Prometheus datasource
            query: PromQL query string
            time_range: Relative time range (e.g., "1h", "24h", "7d")
            start_time: Absolute start time (ISO format or Unix timestamp)
            end_time: Absolute end time (ISO format or Unix timestamp)
            step: Query resolution step in seconds (default: 15)
            max_retries: Maximum retry attempts

        Returns:
            Prometheus query result dictionary

        Examples:
            # Relative time (last 1 hour)
            result = helper.query("Prometheus 1", "up", time_range="1h")

            # Absolute time with ISO format
            result = helper.query(
                "Prometheus 1",
                "up",
                start_time="2026-01-28 19:00:00",
                end_time="2026-01-28 19:30:00"
            )

            # Absolute time with Unix timestamps
            result = helper.query(
                "Prometheus 1",
                "up",
                start_time="1769598000",
                end_time="1769599800"
            )
        """
        # If absolute time specified, use direct API
        if start_time and end_time:
            # Parse time strings to Unix timestamps (seconds)
            start_ts = self._parse_absolute_time(start_time)
            end_ts = self._parse_absolute_time(end_time)

            return self.query_prometheus_direct(
                datasource_name=datasource_name,
                query=query,
                start_timestamp=start_ts,
                end_timestamp=end_ts,
                step=step,
                max_retries=max_retries
            )

        # For relative time, check if it's recent (< 1 hour) or older
        # For better reliability, always use direct API
        now = int(datetime.now().timestamp())

        # Parse relative time range
        duration_seconds = self._parse_duration_to_seconds(time_range)
        start_ts = now - duration_seconds
        end_ts = now

        return self.query_prometheus_direct(
            datasource_name=datasource_name,
            query=query,
            start_timestamp=start_ts,
            end_timestamp=end_ts,
            step=step,
            max_retries=max_retries
        )

    def _parse_absolute_time(self, time_str: str) -> int:
        """
        Parse absolute time string to Unix timestamp (seconds).

        Supports:
        - Unix timestamp: "1769598000"
        - ISO format: "2026-01-28 19:00:00"
        - ISO with timezone: "2026-01-28T19:00:00+08:00"

        Args:
            time_str: Time string

        Returns:
            Unix timestamp in seconds
        """
        # Check if already a Unix timestamp
        if time_str.isdigit():
            return int(time_str)

        # Try parsing ISO format
        try:
            # Try with timezone first
            if 'T' in time_str or '+' in time_str or 'Z' in time_str:
                dt = datetime.fromisoformat(time_str.replace('Z', '+00:00'))
                return int(dt.timestamp())
            else:
                # Assume local time
                dt = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
                return int(dt.timestamp())
        except ValueError:
            raise ValueError(
                f"Cannot parse time string: {time_str}\n"
                "Supported formats: Unix timestamp, 'YYYY-MM-DD HH:MM:SS', or ISO format"
            )

    def _parse_duration_to_seconds(self, duration: str) -> int:
        """
        Parse duration string to seconds.

        Args:
            duration: Duration like "1h", "24h", "7d"

        Returns:
            Duration in seconds
        """
        units = {
            's': 1,
            'm': 60,
            'h': 3600,
            'd': 86400,
            'w': 604800
        }

        duration = duration.strip()
        if duration[-1] in units:
            value = int(duration[:-1])
            unit = duration[-1]
            return value * units[unit]

        # Default to seconds if no unit
        return int(duration)

    def query_prometheus_direct(
        self,
        datasource_name: str,
        query: str,
        start_timestamp: int,
        end_timestamp: int,
        step: int = 15,
        max_retries: int = 3
    ) -> Dict[str, Any]:
        """
        Query Prometheus directly via /api/v1/query_range endpoint.

        This bypasses Grafana's query API and goes directly to Prometheus,
        which is more reliable for historical data queries.

        Args:
            datasource_name: Name of Prometheus datasource
            query: PromQL query string
            start_timestamp: Start time (Unix timestamp in seconds)
            end_timestamp: End time (Unix timestamp in seconds)
            step: Query resolution step in seconds (default: 15)
            max_retries: Maximum retry attempts

        Returns:
            Prometheus query_range result dictionary
        """
        datasource_id = self.datasources[datasource_name].get("id")

        # Build URL with query parameters
        params = [
            f"query={urllib.parse.quote(query)}",
            f"start={start_timestamp}",
            f"end={end_timestamp}",
            f"step={step}"
        ]

        url = f"{self.grafana_url}/api/datasources/proxy/{datasource_id}/api/v1/query_range?{'&'.join(params)}"

        for attempt in range(max_retries):
            try:
                req = urllib.request.Request(url, method="GET")
                req.add_header("Authorization", f"Bearer {self.api_token}")
                req.add_header("Accept", "application/json")

                with urllib.request.urlopen(req) as response:
                    return json.loads(response.read())

            except urllib.error.HTTPError as e:
                if attempt == max_retries - 1:
                    error_body = e.read().decode('utf-8') if e.fp else ""
                    raise Exception(
                        f"Query failed: HTTP {e.code} - {e.reason}\n"
                        f"Response: {error_body}"
                    )
                time.sleep(1 * (attempt + 1))

            except urllib.error.URLError as e:
                if attempt == max_retries - 1:
                    raise Exception(f"Connection failed: {e.reason}")
                time.sleep(1 * (attempt + 1))

    def query_prometheus_absolute(
        self,
        datasource_name: str,
        query: str,
        from_timestamp: int,
        to_timestamp: int,
        interval: str = "",
        legend_format: str = "",
        max_retries: int = 3
    ) -> Dict[str, Any]:
        """
        Query Prometheus datasource with absolute timestamps.

        Args:
            datasource_name: Name of Prometheus datasource
            query: PromQL query string
            from_timestamp: Start time (Unix timestamp in milliseconds)
            to_timestamp: End time (Unix timestamp in milliseconds)
            interval: Query interval (auto if empty)
            legend_format: Legend format string
            max_retries: Maximum retry attempts

        Returns:
            Query result dictionary
        """
        datasource_uid = self.get_datasource_uid(datasource_name)
        datasource_id = self.datasources[datasource_name].get("id")

        datasource_obj = {
            "uid": datasource_uid,
            "type": "prometheus"
        }
        if datasource_id is not None:
            datasource_obj["id"] = datasource_id

        payload = {
            "queries": [{
                "refId": "A",
                "datasource": datasource_obj,
                "datasourceId": datasource_id,
                "expr": query,
                "interval": interval,
                "legendFormat": legend_format,
                "range": True
            }],
            "from": str(from_timestamp),
            "to": str(to_timestamp)
        }

        url = f"{self.grafana_url}/api/ds/query"

        for attempt in range(max_retries):
            try:
                req = urllib.request.Request(
                    url,
                    data=json.dumps(payload).encode('utf-8'),
                    headers={
                        "Authorization": f"Bearer {self.api_token}",
                        "Content-Type": "application/json"
                    },
                    method="POST"
                )

                with urllib.request.urlopen(req) as response:
                    return json.loads(response.read())

            except urllib.error.HTTPError as e:
                if attempt == max_retries - 1:
                    error_body = e.read().decode('utf-8') if e.fp else ""
                    raise Exception(
                        f"Query failed: HTTP {e.code} - {e.reason}\n"
                        f"Response: {error_body}"
                    )
                time.sleep(1 * (attempt + 1))

            except urllib.error.URLError as e:
                if attempt == max_retries - 1:
                    raise Exception(f"Connection failed: {e.reason}")
                time.sleep(1 * (attempt + 1))

    def query_prometheus(
        self,
        datasource_name: str,
        query: str,
        time_range: str = "1h",
        interval: str = "",
        legend_format: str = "",
        max_retries: int = 3
    ) -> Dict[str, Any]:
        """
        Query Prometheus datasource via Grafana API.

        Args:
            datasource_name: Name of Prometheus datasource
            query: PromQL query string
            time_range: Time range (e.g., "1h", "24h", "7d")
            interval: Query interval (auto if empty)
            legend_format: Legend format string
            max_retries: Maximum retry attempts

        Returns:
            Query result dictionary

        Raises:
            Exception: If query fails after retries
        """
        datasource_uid = self.get_datasource_uid(datasource_name)
        datasource_id = self.datasources[datasource_name].get("id")
        from_time, to_time = self._parse_time_range(time_range)

        # Build datasource object with both UID and ID (if available)
        datasource_obj = {
            "uid": datasource_uid,
            "type": "prometheus"
        }
        if datasource_id is not None:
            datasource_obj["id"] = datasource_id

        payload = {
            "queries": [{
                "refId": "A",
                "datasource": datasource_obj,
                "datasourceId": datasource_id,  # v7.5 may need this
                "expr": query,
                "interval": interval,
                "legendFormat": legend_format,
                "range": True
            }],
            "from": from_time,
            "to": to_time
        }

        url = f"{self.grafana_url}/api/ds/query"

        for attempt in range(max_retries):
            try:
                req = urllib.request.Request(
                    url,
                    data=json.dumps(payload).encode('utf-8'),
                    headers={
                        "Authorization": f"Bearer {self.api_token}",
                        "Content-Type": "application/json"
                    },
                    method="POST"
                )

                with urllib.request.urlopen(req) as response:
                    return json.loads(response.read())

            except urllib.error.HTTPError as e:
                if attempt == max_retries - 1:
                    error_body = e.read().decode('utf-8') if e.fp else ""
                    raise Exception(
                        f"Query failed: HTTP {e.code} - {e.reason}\n"
                        f"Response: {error_body}"
                    )
                time.sleep(1 * (attempt + 1))  # Exponential backoff

            except urllib.error.URLError as e:
                if attempt == max_retries - 1:
                    raise Exception(f"Connection failed: {e.reason}")
                time.sleep(1 * (attempt + 1))

    def format_prometheus_result(
        self,
        result: Dict[str, Any],
        format_type: str = "table",
        max_series: int = 20,
        max_points: int = 10
    ) -> str:
        """
        Format Prometheus native API result for display.

        Args:
            result: Result from query() or query_prometheus_direct()
            format_type: Output format ("table", "simple", "json")
            max_series: Maximum number of series to display
            max_points: Maximum number of data points per series

        Returns:
            Formatted string
        """
        if not result:
            return "No data"

        # Check for Prometheus native format
        if result.get("status") == "success":
            data = result.get("data", {})
            results = data.get("result", [])

            if not results:
                return "No data points"

            if format_type == "json":
                return json.dumps(result, indent=2)

            if format_type == "simple":
                lines = []
                for series in results[:max_series]:
                    metric = series.get("metric", {})
                    values = series.get("values", [])

                    # Get instance or first useful label
                    instance = metric.get("instance") or metric.get("job") or "Series"

                    if values:
                        # Show latest value
                        _, latest_val = values[-1]
                        lines.append(f"{instance}: {latest_val}")

                if len(results) > max_series:
                    lines.append(f"... and {len(results) - max_series} more series")

                return "\n".join(lines)

            # Table format
            lines = ["| Time | Metric | Value |", "|------|--------|-------|"]

            for series in results[:max_series]:
                metric = series.get("metric", {})
                values = series.get("values", [])

                # Format metric name
                instance = metric.get("instance", "")
                job = metric.get("job", "")
                metric_name = f"{job}/{instance}" if job and instance else str(metric)

                # Show last N points
                for ts, val in values[-max_points:]:
                    time_str = datetime.fromtimestamp(int(ts)).strftime("%H:%M:%S")
                    lines.append(f"| {time_str} | {metric_name[:30]} | {val} |")

            if len(results) > max_series:
                lines.append(f"| ... | ({len(results) - max_series} more series) | ... |")

            return "\n".join(lines)

        # Fall back to Grafana format
        return self.format_series_data(result, format_type)

    def format_series_data(
        self,
        result: Dict[str, Any],
        format_type: str = "table"
    ) -> str:
        """
        Format query result for display.

        Args:
            result: Query result from query_prometheus()
            format_type: Output format ("table", "json", "simple")

        Returns:
            Formatted string
        """
        if not result or "results" not in result:
            return "No data"

        if format_type == "json":
            return json.dumps(result, indent=2)

        # Extract series data - support both frames (v8+) and series (v7.5) format
        try:
            result_data = result["results"]["A"]

            # Try frames format first (v8+)
            if "frames" in result_data:
                frames = result_data["frames"]
                if not frames:
                    return "No data points"

                if format_type == "simple":
                    lines = []
                    for frame in frames:
                        name = frame.get("schema", {}).get("name", "Series")
                        values = frame.get("data", {}).get("values", [])
                        if len(values) >= 2:
                            vals = values[1]
                            if vals:
                                latest = vals[-1] if vals else "N/A"
                                lines.append(f"{name}: {latest}")
                    return "\n".join(lines)

                # Table format
                lines = ["| Time | Series | Value |", "|------|--------|-------|"]
                for frame in frames:
                    name = frame.get("schema", {}).get("name", "Series")
                    values = frame.get("data", {}).get("values", [])
                    if len(values) >= 2:
                        times = values[0]
                        vals = values[1]
                        for i in range(max(0, len(times) - 10), len(times)):
                            timestamp = datetime.fromtimestamp(times[i] / 1000).strftime("%Y-%m-%d %H:%M:%S")
                            value = f"{vals[i]:.2f}" if isinstance(vals[i], (int, float)) else str(vals[i])
                            lines.append(f"| {timestamp} | {name} | {value} |")
                return "\n".join(lines)

            # Try series format (v7.5)
            elif "series" in result_data:
                series_list = result_data["series"]
                if not series_list:
                    return "No data points"

                if format_type == "simple":
                    lines = []
                    for series in series_list[:20]:  # Limit to first 20 series
                        name = series.get("name", "Series")
                        points = series.get("points", [])
                        if points:
                            # Points are [value, timestamp] pairs
                            latest_point = points[-1]
                            latest_value = latest_point[0] if latest_point else "N/A"
                            lines.append(f"{name}: {latest_value}")
                    if len(series_list) > 20:
                        lines.append(f"... and {len(series_list) - 20} more series")
                    return "\n".join(lines)

                # Table format
                lines = ["| Time | Series | Value |", "|------|--------|-------|"]
                for series in series_list[:10]:  # Limit to first 10 series
                    name = series.get("name", "Series")
                    points = series.get("points", [])
                    # Show last 5 points of each series
                    for point in points[-5:]:
                        if len(point) >= 2:
                            value = point[0]
                            timestamp = point[1]
                            time_str = datetime.fromtimestamp(timestamp / 1000).strftime("%Y-%m-%d %H:%M:%S")
                            value_str = f"{value:.2f}" if isinstance(value, (int, float)) else str(value)
                            lines.append(f"| {time_str} | {name[:40]}... | {value_str} |")
                if len(series_list) > 10:
                    lines.append(f"| ... | ({len(series_list) - 10} more series) | ... |")
                return "\n".join(lines)
            else:
                return "Unknown response format"

        except (KeyError, IndexError) as e:
            return f"Error formatting data: {e}\n{json.dumps(result, indent=2)}"

    def list_datasources(self) -> List[str]:
        """
        List all configured datasources.

        Returns:
            List of datasource names
        """
        return list(self.datasources.keys())

    def test_connection(self) -> bool:
        """
        Test connection to Grafana.

        Returns:
            True if connection successful
        """
        try:
            url = f"{self.grafana_url}/api/health"
            req = urllib.request.Request(url)
            req.add_header("Authorization", f"Bearer {self.api_token}")

            with urllib.request.urlopen(req) as response:
                return response.status == 200
        except Exception:
            return False


def main():
    """Example usage."""
    import sys

    if len(sys.argv) < 3:
        print("Usage: python3 query_helper.py <datasource> <query> [options]")
        print("\nOptions:")
        print("  Relative time:")
        print('    python3 query_helper.py "Datasource" "up" "1h"')
        print("\n  Absolute time:")
        print('    python3 query_helper.py "Datasource" "up" "2026-01-28 19:00:00" "2026-01-28 19:30:00"')
        print("\n  Unix timestamps:")
        print('    python3 query_helper.py "Datasource" "up" 1769598000 1769599800')
        sys.exit(1)

    datasource = sys.argv[1]
    query = sys.argv[2]

    helper = GrafanaQueryHelper()

    try:
        # Check if absolute time range provided
        if len(sys.argv) >= 5:
            start_time = sys.argv[3]
            end_time = sys.argv[4]

            print(f"Query: {query}")
            print(f"Datasource: {datasource}")
            print(f"Time range: {start_time} to {end_time}")
            print()

            result = helper.query(
                datasource_name=datasource,
                query=query,
                start_time=start_time,
                end_time=end_time
            )
        else:
            # Relative time range
            time_range = sys.argv[3] if len(sys.argv) > 3 else "1h"

            print(f"Query: {query}")
            print(f"Datasource: {datasource}")
            print(f"Time range: {time_range}")
            print()

            result = helper.query(
                datasource_name=datasource,
                query=query,
                time_range=time_range
            )

        # Format and display result
        print(helper.format_prometheus_result(result, format_type="table"))

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
