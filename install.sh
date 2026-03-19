#!/bin/bash
# Solax-Modbus Install Script
# Supports: Linux (Debian/Raspberry Pi), macOS
# Usage: ./install.sh <path-to-wheel>
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
    echo "ERROR: Wheel path required"
    echo "Usage: ./install.sh <path-to-wheel>"
    echo "Example: ./install.sh dist/solax_modbus-0.1.0-py3-none-any.whl"
    exit 1
fi

# Resolve wheel path: absolute paths used as-is; relative paths resolved
# against the current working directory
if [[ "$1" = /* ]]; then
    WHEEL_PATH="$1"
else
    WHEEL_PATH="$(pwd)/$1"
fi

if [ ! -f "$WHEEL_PATH" ]; then
    echo "ERROR: Wheel file not found: $WHEEL_PATH"
    exit 1
fi

WHEEL_FILE="$(basename "$WHEEL_PATH")"
VERSION=$(echo "$WHEEL_FILE" | cut -d'-' -f2)

echo "==> Installing solax-modbus version $VERSION"
echo "==> Platform: $OS"
echo "==> Install directory: $INSTALL_DIR"
echo "==> Wheel: $WHEEL_PATH"

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
# Post-install: platform-specific instructions
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
