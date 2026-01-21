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

# Verify venv exists
if [ ! -d "/opt/solax-monitor/venv" ]; then
    echo "ERROR: Virtual environment not found at /opt/solax-monitor/venv"
    echo "For first-time installation, create virtual environment:"
    echo "  sudo mkdir -p /opt/solax-monitor"
    echo "  sudo python3 -m venv /opt/solax-monitor/venv"
    exit 1
fi

# Uninstall existing package (pip handles cleanup)
echo "==> Cleaning existing installation..."
/opt/solax-monitor/venv/bin/pip uninstall -y solax-modbus 2>/dev/null || true

# Install new version
# Handle both relative and absolute paths
if [[ "$WHEEL" = /* ]]; then
    WHEEL_PATH="$WHEEL"
else
    WHEEL_PATH="/tmp/$WHEEL"
fi

echo "==> Installing from $WHEEL_PATH"
/opt/solax-monitor/venv/bin/pip install "$WHEEL_PATH"

# Verify version
echo "==> Verifying installation..."
INSTALLED=$(/opt/solax-monitor/venv/bin/python -c "import solax_modbus; print(solax_modbus.__version__)")

if [ "$INSTALLED" != "$VERSION" ]; then
    echo "ERROR: Version mismatch - expected $VERSION, got $INSTALLED"
    exit 1
fi

echo ""
echo "✓ Installation successful: version $INSTALLED"
echo ""
echo "Run monitor with:"
echo "  /opt/solax-monitor/venv/bin/solax-monitor <inverter-ip> [options]"
echo ""
echo "Options:"
echo "  --port PORT         Modbus TCP port (default: 502)"
echo "  --unit-id ID        Modbus unit ID (default: 1)"
echo "  --interval SECONDS  Polling interval (default: 5)"
echo "  --debug             Enable debug logging"
