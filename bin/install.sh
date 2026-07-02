#!/bin/bash
# Solax-Modbus Install Script
# Supports: Linux (Debian/Raspberry Pi)
#
# Usage:
#   ./install.sh                              # fetch latest release from GitHub
#   ./install.sh <version>                    # fetch specific version from GitHub
#   ./install.sh <path-to-wheel>              # install from local wheel file
#
# Optional flags (for automatic systemd service registration):
#   --ip IP               Inverter IP address (triggers systemd service creation)
#   --port PORT           Modbus TCP port (passed to solax-monitor --port)
#   --unit-id ID          Modbus unit ID (passed to solax-monitor --unit-id)
#   --interval SECONDS    Polling interval (passed to solax-monitor --interval)
#   --serve               Enable HTTP server (passed to solax-monitor --serve)
#   --http-port PORT      HTTP server port (passed to solax-monitor --http-port)
#   --allow CIDR          Allowed CIDR for HTTP (repeatable, passed as --allow)
#
# Examples:
#   ./install.sh --ip 192.168.1.100
#   ./install.sh 1.0.0 --ip 192.168.1.100 --serve --http-port 8080
#   ./install.sh --ip 192.168.1.100 --allow 10.0.0.0/24 --allow 192.168.1.0/24
#
# Linux:  installs to /opt/solax-monitor/, symlink in /usr/local/bin/

set -e  # Exit on error

# ---------------------------------------------------------------------------
# OS detection
# ---------------------------------------------------------------------------
OS="$(uname -s)"
case "$OS" in
    Linux*)
        INSTALL_DIR="/opt/solax-monitor"
        ;;
    *)
        echo "ERROR: Unsupported operating system: $OS"
        echo "This installer supports Linux (Debian/Raspberry Pi) only."
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

if [ -z "$1" ] || [[ "$1" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]] || [[ "$1" == --* ]]; then
    # No argument, version string, or flag: download from GitHub releases
    if ! command -v curl >/dev/null 2>&1 && ! command -v wget >/dev/null 2>&1; then
        echo "ERROR: curl or wget required for GitHub download"
        exit 1
    fi

    if [ -z "$1" ] || [[ "$1" == --* ]]; then
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
# Parse service flags (--ip, --port, --unit-id, --interval, --serve, etc.)
# ---------------------------------------------------------------------------
IP=""
MODBUS_PORT_ARG=""
UNIT_ID_ARG=""
INTERVAL_ARG=""
SERVE_FLAG=""
HTTP_PORT_ARG=""
ALLOW_ARGS=()

# Shift off the positional argument if one was provided (not a flag)
if [ -n "$1" ] && [[ "$1" != --* ]]; then
    shift
fi

# Parse remaining arguments
while [ $# -gt 0 ]; do
    case "$1" in
        --ip)
            IP="$2"
            shift 2
            ;;
        --port)
            MODBUS_PORT_ARG="$2"
            shift 2
            ;;
        --unit-id)
            UNIT_ID_ARG="$2"
            shift 2
            ;;
        --interval)
            INTERVAL_ARG="$2"
            shift 2
            ;;
        --serve)
            SERVE_FLAG="1"
            shift
            ;;
        --http-port)
            HTTP_PORT_ARG="$2"
            shift 2
            ;;
        --allow)
            ALLOW_ARGS+=("$2")
            shift 2
            ;;
        *)
            echo "ERROR: Unknown option: $1"
            exit 1
            ;;
    esac
done

# ---------------------------------------------------------------------------
# python3 availability check
# ---------------------------------------------------------------------------
if ! command -v python3 &>/dev/null; then
    echo "ERROR: python3 not found in PATH"
    echo "Install Python 3:  sudo apt-get install python3 python3-venv"
    exit 1
fi

# ---------------------------------------------------------------------------
# Virtual environment setup
# ---------------------------------------------------------------------------
if [ ! -d "$VENV_DIR" ]; then
    echo "==> Creating virtual environment at $VENV_DIR"
    # /opt requires elevated privileges
    sudo mkdir -p "$INSTALL_DIR"
    sudo python3 -m venv "$VENV_DIR"
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
# PATH configuration
# ---------------------------------------------------------------------------
# Symlink into /usr/local/bin (already in PATH on Debian/Raspberry Pi)
SYMLINK="/usr/local/bin/solax-monitor"
TARGET="$VENV_DIR/bin/solax-monitor"

if [ -L "$SYMLINK" ] && [ "$(readlink "$SYMLINK")" = "$TARGET" ]; then
    echo "==> Symlink already correct: $SYMLINK"
else
    echo "==> Configuring symlink: $SYMLINK -> $TARGET"
    sudo ln -sf "$TARGET" "$SYMLINK"
fi

# ---------------------------------------------------------------------------
# Systemd service registration (if --ip was provided)
# ---------------------------------------------------------------------------
if [ -n "$IP" ]; then
    echo "==> Generating systemd service unit..."

    # Build ExecStart command
    EXEC_START="$VENV_DIR/bin/solax-monitor \"$IP\""

    if [ -n "$MODBUS_PORT_ARG" ]; then
        EXEC_START="$EXEC_START --port $MODBUS_PORT_ARG"
    fi

    if [ -n "$UNIT_ID_ARG" ]; then
        EXEC_START="$EXEC_START --unit-id $UNIT_ID_ARG"
    fi

    if [ -n "$INTERVAL_ARG" ]; then
        EXEC_START="$EXEC_START --interval $INTERVAL_ARG"
    fi

    if [ -n "$SERVE_FLAG" ]; then
        EXEC_START="$EXEC_START --serve"
    fi

    if [ -n "$HTTP_PORT_ARG" ]; then
        EXEC_START="$EXEC_START --http-port $HTTP_PORT_ARG"
    fi

    for CIDR in "${ALLOW_ARGS[@]}"; do
        EXEC_START="$EXEC_START --allow $CIDR"
    done

    # Write systemd unit file
    sudo tee /etc/systemd/system/solax-monitor.service > /dev/null <<EOF
[Unit]
Description=Solax Modbus Monitor
After=network-online.target
Wants=network-online.target

[Service]
ExecStart=$EXEC_START
User=root
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOF

    echo "==> Reloading systemd daemon..."
    sudo systemctl daemon-reload

    echo "==> Enabling and starting solax-monitor service..."
    sudo systemctl enable --now solax-monitor

    echo ""
    echo "✓ Systemd service installed and started"
    echo ""
    echo "Service status:"
    echo "  systemctl status solax-monitor"
    echo ""
    echo "View logs:"
    echo "  journalctl -u solax-monitor -f"
else
    # ---------------------------------------------------------------------------
    # Post-install instructions (no systemd)
    # ---------------------------------------------------------------------------
    echo ""
    echo "Run monitor with:"
    echo "  solax-monitor <inverter-ip> [options]"
    echo ""
    echo "To register as a systemd service, re-run install.sh with --ip:"
    echo "  ./install.sh --ip <inverter-ip> [--serve] [--http-port PORT]"
    echo ""
    echo "Options:"
    echo "  --port PORT         Modbus TCP port (default: 502)"
    echo "  --unit-id ID        Modbus unit ID (default: 1)"
    echo "  --interval SECONDS  Polling interval (default: 5)"
    echo "  --debug             Enable debug logging"
fi
