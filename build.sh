#!/bin/bash
# Solax-Modbus Build Script
# Cleans previous builds, updates version, creates distribution package

set -e  # Exit on error

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT"

# Verify python3 is available and meets minimum version
if ! command -v python3 >/dev/null 2>&1; then
    echo "ERROR: python3 not found"
    exit 1
fi

# Check Python version >= 3.9
PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
MAJOR=$(echo "$PYTHON_VERSION" | cut -d. -f1)
MINOR=$(echo "$PYTHON_VERSION" | cut -d. -f2)

if [ "$MAJOR" -lt 3 ] || ([ "$MAJOR" -eq 3 ] && [ "$MINOR" -lt 9 ]); then
    echo "ERROR: Python 3.9+ required, found $PYTHON_VERSION"
    exit 1
fi

# Verify build module is available
if ! python3 -m build --version >/dev/null 2>&1; then
    echo "ERROR: build module not found"
    echo "Install: python3 -m pip install build"
    exit 1
fi

# Extract version from pyproject.toml
VERSION=$(grep '^version = ' pyproject.toml | cut -d'"' -f2)

if [ -z "$VERSION" ]; then
    echo "ERROR: Could not extract version from pyproject.toml"
    exit 1
fi

echo "==> Building solax-modbus version $VERSION"

# Update __init__.py with version
echo "==> Updating version in __init__.py..."
echo "__version__ = '$VERSION'" > src/solax_modbus/__init__.py

# Clean previous builds
echo "==> Cleaning previous builds..."
rm -rf dist/ build/ *.egg-info/ src/*.egg-info/

# Build distribution
echo "==> Building distribution..."
python3 -m build

# Verify wheel exists
WHEEL="dist/solax_modbus-${VERSION}-py3-none-any.whl"
if [ ! -f "$WHEEL" ]; then
    echo "ERROR: Expected wheel not found: $WHEEL"
    exit 1
fi

echo ""
echo "✓ Build successful: version $VERSION"
ls -lh "$WHEEL"
echo ""
echo "Transfer to Pi: scp dist/solax_modbus-${VERSION}-py3-none-any.whl pi@<hostname>:/tmp/"
