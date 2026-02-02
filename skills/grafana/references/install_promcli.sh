#!/bin/bash
#
# Install prom-cli for Grafana skill
#
# This script checks if prom command is installed and installs it if needed.
# prom-cli is used for Prometheus metric discovery and querying.
#
# Repository: https://github.com/jack482653/prom-cli
#
# Requirements:
# - Node.js and npm
#
# Usage:
#   bash install_promcli.sh

set -e

echo "==================================="
echo "prom-cli Installation Script"
echo "==================================="

# Check if prom command is already installed
if command -v prom &> /dev/null; then
    echo "✓ prom command is already installed"
    echo "  Location: $(which prom)"
    prom --version 2>/dev/null || echo "  (version info not available)"
    exit 0
fi

echo "prom command not found. Attempting to install..."

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "Error: npm is not installed"
    echo ""
    echo "Please install Node.js and npm first:"
    echo "  macOS:   brew install node"
    echo "  Linux:   sudo apt install nodejs npm  (or equivalent)"
    echo "  Manual:  https://nodejs.org/"
    exit 1
fi

echo "✓ npm is installed: $(npm --version)"

# Install prom-cli via npm
echo "Installing prom-cli via npm..."
echo "  Repository: github:jack482653/prom-cli"

if npm install -g github:jack482653/prom-cli; then
    echo "✓ prom-cli installed successfully"
else
    echo "Error: Failed to install prom-cli"
    exit 1
fi

# Verify installation
if command -v prom &> /dev/null; then
    echo "✓ Verified: prom command is now available"
    echo "  Location: $(which prom)"
    prom --version 2>/dev/null || echo "  (version info not available)"
    echo ""
    echo "Installation complete!"
else
    echo "Warning: prom-cli was installed but prom command not found in PATH"
    echo ""
    echo "npm global packages are typically installed to:"
    echo "  $(npm root -g)"
    echo ""
    echo "Please check your npm global bin path:"
    echo "  npm config get prefix"
    echo ""
    echo "And ensure it's in your PATH"
    exit 1
fi

# Display usage hint
echo ""
echo "Usage Examples:"
echo "  # Configure Prometheus URL"
echo "  prom config http://localhost:9090"
echo ""
echo "  # Check status"
echo "  prom status"
echo ""
echo "  # Query instant value"
echo "  prom query \"up\""
echo ""
echo "  # Query time range"
echo "  prom query-range \"rate(http_requests_total[5m])\" --start \"1h\" --end \"now\""
echo ""
echo "For more information: prom --help"
