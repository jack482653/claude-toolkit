#!/usr/bin/env python3
"""
Generate Grafana datasources configuration file.

This script fetches all datasources from your Grafana instance and creates
a config file at ~/.grafana-skill/ with proper UIDs and IDs.

Requirements:
- GRAFANA_URL environment variable
- GRAFANA_API_TOKEN environment variable

Usage:
    # Generate default config.json
    export GRAFANA_URL="http://grafana.example.com"
    export GRAFANA_API_TOKEN="your_api_token"
    python3 generate_datasources.py

    # Generate environment-specific config
    export GRAFANA_URL="http://grafana-prod.example.com"
    export GRAFANA_API_TOKEN="your_prod_token"
    export GRAFANA_ENV="prod"
    python3 generate_datasources.py

    # This will create config-prod.json
"""

import os
import sys
import json
import urllib.request
import urllib.error
from pathlib import Path


def get_env_var(name: str) -> str:
    """Get environment variable or exit with error."""
    value = os.environ.get(name)
    if not value:
        print(f"Error: {name} environment variable not set", file=sys.stderr)
        print(f"Please set it with: export {name}=<value>", file=sys.stderr)
        sys.exit(1)
    return value


def fetch_datasources(grafana_url: str, api_token: str) -> list:
    """Fetch all datasources from Grafana API."""
    url = f"{grafana_url}/api/datasources"

    req = urllib.request.Request(url)
    req.add_header("Authorization", f"Bearer {api_token}")
    req.add_header("Content-Type", "application/json")

    try:
        with urllib.request.urlopen(req) as response:
            data = response.read()
            return json.loads(data)
    except urllib.error.HTTPError as e:
        print(f"Error: HTTP {e.code} - {e.reason}", file=sys.stderr)
        if e.code == 401:
            print("Invalid API token. Please check GRAFANA_API_TOKEN", file=sys.stderr)
        elif e.code == 403:
            print("Access denied. Your API token may lack permissions", file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"Error: Could not connect to Grafana at {grafana_url}", file=sys.stderr)
        print(f"Reason: {e.reason}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)


def build_config(grafana_url: str, api_token: str, datasources: list) -> dict:
    """Build configuration dictionary from datasources."""
    config = {
        "grafana_url": grafana_url,
        "api_token": api_token,
        "default_datasource": None,
        "datasources": {}
    }

    default_datasource_name = None

    for ds in datasources:
        name = ds.get("name")
        uid = ds.get("uid")
        ds_id = ds.get("id")
        is_default = ds.get("isDefault", False)

        if name and uid:
            config["datasources"][name] = {
                "uid": uid,
                "id": ds_id,
                "is_default": is_default
            }

            # Track default datasource
            if is_default:
                default_datasource_name = name

    # Set default datasource reference
    if default_datasource_name:
        config["default_datasource"] = default_datasource_name

    return config


def save_config(config: dict, config_path: Path) -> None:
    """Save configuration to JSON file."""
    # Create directory if it doesn't exist
    config_path.parent.mkdir(parents=True, exist_ok=True)

    # Write config file
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)

    # Set secure permissions (owner read/write only)
    os.chmod(config_path, 0o600)


def main():
    """Main execution function."""
    print("Grafana Datasource Configuration Generator")
    print("=" * 50)

    # Get environment variables
    grafana_url = get_env_var("GRAFANA_URL").rstrip('/')
    api_token = get_env_var("GRAFANA_API_TOKEN")
    env = os.environ.get("GRAFANA_ENV", "").strip()

    # Determine config file name
    config_dir = Path.home() / ".grafana-skill"
    if env:
        config_filename = f"config-{env}.json"
        print(f"Environment: {env}")
    else:
        config_filename = "config.json"
        print("Environment: default")

    config_path = config_dir / config_filename

    print(f"Grafana URL: {grafana_url}")
    print(f"Config file: {config_path}")
    print("Fetching datasources...")

    # Fetch datasources
    datasources = fetch_datasources(grafana_url, api_token)

    if not datasources:
        print("Warning: No datasources found", file=sys.stderr)
        sys.exit(1)

    print(f"Found {len(datasources)} datasources:")
    for ds in datasources:
        default_marker = " [DEFAULT]" if ds.get("isDefault") else ""
        print(f"  - {ds.get('name')} (type: {ds.get('type')}, uid: {ds.get('uid')}){default_marker}")

    # Build configuration
    config = build_config(grafana_url, api_token, datasources)

    # Display default datasource info
    if config["default_datasource"]:
        print(f"\nDefault datasource: {config['default_datasource']}")
    else:
        print("\nNote: No default datasource found. You may need to manually specify datasources in queries.")

    # Save to file
    save_config(config, config_path)

    print(f"\nConfiguration saved to: {config_path}")
    print(f"File permissions: 600 (owner read/write only)")
    print("\nYou can now use the Grafana skill!")

    if env:
        print(f"\nTo use this config, set: export GRAFANA_ENV={env}")

    print("\nTo update the configuration in the future, simply run this script again.")


if __name__ == "__main__":
    main()
