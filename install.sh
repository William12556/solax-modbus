#!/bin/bash
# Solax-Modbus Install Script
# Clean uninstall, fresh install, version verification
# Usage: ./install.sh <wheel-filename>

set -e  # Exit on error

if [ -z "$1" ]; then
    echo "ERROR: Wheel filename required"
    echo "Usage: ./install.sh solax_modbus-X.Y.Z-py3-none-any.whl"
    exit 1
fi

WHEEL="$1"
VERSION=$(echo "$WHEEL" | cut -d'-' -f2)

echo "==> Installing solax-modbus version $VERSION"

# Stop service (ignore if not running)
echo "==> Stopping service..."
sudo systemctl stop solax-monitor || true

# Uninstall existing package
echo "==> Cleaning existing installation..."
sudo /opt/solax-monitor/venv/bin/pip uninstall -y solax-modbus 2>/dev/null || true

# Verify venv exists
if [ ! -d "/opt/solax-monitor/venv" ]; then
    echo "ERROR: Virtual environment not found at /opt/solax-monitor/venv"
    echo "For first-time installation, follow deployment guide initial setup procedures"
    exit 1
fi

# Clear cache
echo "==> Clearing package cache..."
sudo rm -rf /opt/solax-monitor/venv/lib/python*/site-packages/solax_modbus*

# Install new version
echo "==> Installing from /tmp/$WHEEL"
sudo /opt/solax-monitor/venv/bin/pip install "/tmp/$WHEEL"

# Verify version
echo "==> Verifying installation..."
INSTALLED=$(/opt/solax-monitor/venv/bin/python -c "import solax_modbus; print(solax_modbus.__version__)")

if [ "$INSTALLED" != "$VERSION" ]; then
    echo "ERROR: Version mismatch - expected $VERSION, got $INSTALLED"
    exit 1
fi

# Start service
echo "==> Starting service..."
sudo systemctl start solax-monitor

echo ""
echo "✓ Installation successful: version $INSTALLED"
echo ""
sudo systemctl status solax-monitor --no-pager -l | head -10
