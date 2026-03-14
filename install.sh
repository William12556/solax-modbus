#!/bin/bash
# Solax-Modbus Install Script
# Supports: Linux (Debian/Raspberry Pi), macOS
# Usage: ./install.sh <wheel-filename>
#
# Linux:  installs to /opt/solax-monitor/, registers systemd service
# macOS:  installs to ~/.local/opt/solax-monitor/, manual start only
#
# Change: change-b4e7f1a9-macos-platform-support

set -e  # Exit on error

# ---------------------------------------------------------------------------
# OS detection
# ---------------------------------------------------------------------------
OS="$(uname -s)"
case "$OS" in
    Linux*)
        INSTALL_DIR="/opt/solax-monitor"
        ;;
    Darwin*)
        INSTALL_DIR="$HOME/.local/opt/solax-monitor"
        ;;
    *)
        echo "ERROR: Unsupported operating system: $OS"
        exit 1
        ;;
esac

VENV_DIR="$INSTALL_DIR/venv"

# ---------------------------------------------------------------------------
# Argument validation
# ---------------------------------------------------------------------------
if [ -z "$1" ]; then
    echo "ERROR: Wheel filename required"
    echo "Usage: ./install.sh solax_modbus-X.Y.Z-py3-none-any.whl"
    exit 1
fi

WHEEL="$1"
VERSION=$(echo "$WHEEL" | cut -d'-' -f2)

echo "==> Installing solax-modbus version $VERSION"
echo "==> Platform: $OS"
echo "==> Install directory: $INSTALL_DIR"

# ---------------------------------------------------------------------------
# python3 availability check
# ---------------------------------------------------------------------------
if ! command -v python3 &>/dev/null; then
    echo "ERROR: python3 not found in PATH"
    if [ "$OS" = "Darwin" ]; then
        echo "Install Python 3 via Homebrew:  brew install python3"
        echo "Or via Xcode Command Line Tools: xcode-select --install"
    else
        echo "Install Python 3:  sudo apt-get install python3 python3-venv"
    fi
    exit 1
fi

# ---------------------------------------------------------------------------
# Virtual environment setup
# ---------------------------------------------------------------------------
if [ ! -d "$VENV_DIR" ]; then
    echo "==> Creating virtual environment at $VENV_DIR"
    if [ "$OS" = "Linux" ]; then
        # Linux: /opt requires elevated privileges
        sudo mkdir -p "$INSTALL_DIR"
        sudo python3 -m venv "$VENV_DIR"
    else
        # macOS: user-owned path, no sudo required
        mkdir -p "$INSTALL_DIR"
        python3 -m venv "$VENV_DIR"
    fi
fi

# ---------------------------------------------------------------------------
# Install package
# ---------------------------------------------------------------------------
echo "==> Cleaning existing installation..."
"$VENV_DIR/bin/pip" uninstall -y solax-modbus 2>/dev/null || true

# Handle both relative and absolute wheel paths
if [[ "$WHEEL" = /* ]]; then
    WHEEL_PATH="$WHEEL"
else
    WHEEL_PATH="/tmp/$WHEEL"
fi

echo "==> Installing from $WHEEL_PATH"
"$VENV_DIR/bin/pip" install "$WHEEL_PATH"

# ---------------------------------------------------------------------------
# Version verification
# ---------------------------------------------------------------------------
echo "==> Verifying installation..."
INSTALLED=$("$VENV_DIR/bin/python" -c "import solax_modbus; print(solax_modbus.__version__)")

if [ "$INSTALLED" != "$VERSION" ]; then
    echo "ERROR: Version mismatch - expected $VERSION, got $INSTALLED"
    exit 1
fi

echo ""
echo "✓ Installation successful: version $INSTALLED"
echo ""

# ---------------------------------------------------------------------------
# Post-install: platform-specific service registration
# ---------------------------------------------------------------------------
if [ "$OS" = "Linux" ]; then
    echo "Run monitor with:"
    echo "  $VENV_DIR/bin/solax-monitor <inverter-ip> [options]"
    echo ""
    echo "Or register as a systemd service (requires root):"
    echo "  sudo systemctl enable solax-monitor"
    echo "  sudo systemctl start solax-monitor"
else
    # macOS: manual start only, no service registration
    echo "Run monitor with:"
    echo "  $VENV_DIR/bin/solax-monitor <inverter-ip> [options]"
    echo ""
    echo "Note: Automatic launch on login is not configured."
    echo "      Start the monitor manually when required."
fi

echo ""
echo "Options:"
echo "  --port PORT         Modbus TCP port (default: 502)"
echo "  --unit-id ID        Modbus unit ID (default: 1)"
echo "  --interval SECONDS  Polling interval (default: 5)"
echo "  --debug             Enable debug logging"
