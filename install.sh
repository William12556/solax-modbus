#!/bin/bash
# Solax-Modbus Install Script
# Supports: Linux (Debian/Raspberry Pi), macOS
#
# Usage:
#   ./install.sh                              # fetch latest release from GitHub
#   ./install.sh <version>                    # fetch specific version from GitHub
#   ./install.sh <path-to-wheel>              # install from local wheel file
#
# Linux:  installs to /opt/solax-monitor/, manual systemd registration
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
GITHUB_REPO="William12556/solax-modbus"
GITHUB_API="https://api.github.com/repos/${GITHUB_REPO}/releases"

# ---------------------------------------------------------------------------
# Resolve wheel: local file, specific version, or latest release
# ---------------------------------------------------------------------------
WHEEL_PATH=""

if [ -z "$1" ] || [[ "$1" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    # No argument or version string: download from GitHub releases
    if ! command -v curl >/dev/null 2>&1 && ! command -v wget >/dev/null 2>&1; then
        echo "ERROR: curl or wget required for GitHub download"
        exit 1
    fi

    if [ -z "$1" ]; then
        echo "==> Fetching latest release from GitHub..."
        RELEASE_URL="${GITHUB_API}/latest"
    else
        echo "==> Fetching release $1 from GitHub..."
        RELEASE_URL="${GITHUB_API}/tags/$1"
    fi

    if command -v curl >/dev/null 2>&1; then
        RELEASE_JSON=$(curl -fsSL "$RELEASE_URL")
    else
        RELEASE_JSON=$(wget -qO- "$RELEASE_URL")
    fi

    WHEEL_URL=$(echo "$RELEASE_JSON" | grep -o '"browser_download_url": *"[^"]*\.whl"' | grep -o 'https://[^"]*')
    VERSION=$(echo "$RELEASE_JSON" | grep -o '"tag_name": *"[^"]*"' | grep -o '[0-9][^"]*')

    if [ -z "$WHEEL_URL" ]; then
        echo "ERROR: Could not find wheel asset in release"
        exit 1
    fi

    WHEEL_PATH="/tmp/solax_modbus-${VERSION}-py3-none-any.whl"
    echo "==> Downloading wheel: $WHEEL_URL"
    if command -v curl >/dev/null 2>&1; then
        curl -fsSL "$WHEEL_URL" -o "$WHEEL_PATH"
    else
        wget -qO "$WHEEL_PATH" "$WHEEL_URL"
    fi

elif [ -f "$1" ]; then
    # Local wheel file
    if [[ "$1" = /* ]]; then
        WHEEL_PATH="$1"
    else
        WHEEL_PATH="$(pwd)/$1"
    fi
    VERSION=$(basename "$WHEEL_PATH" | cut -d'-' -f2)

else
    echo "ERROR: Argument is not a file or version string: $1"
    echo "Usage: ./install.sh [version|path-to-wheel]"
    exit 1
fi

if [ ! -f "$WHEEL_PATH" ]; then
    echo "ERROR: Wheel file not found: $WHEEL_PATH"
    exit 1
fi

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
    echo "To register as a systemd service, create a unit file manually."
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
