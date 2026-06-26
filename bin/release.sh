#!/bin/bash
# Solax-Modbus Release Script
# Builds the wheel and publishes a GitHub release with wheel and install.sh as assets.
# Requires: gh CLI (brew install gh) authenticated via gh auth login

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT"

# ---------------------------------------------------------------------------
# Prerequisites
# ---------------------------------------------------------------------------
if ! command -v gh >/dev/null 2>&1; then
    echo "ERROR: gh CLI not found"
    echo "Install: brew install gh"
    echo "Auth:    gh auth login"
    exit 1
fi

if ! gh auth status >/dev/null 2>&1; then
    echo "ERROR: gh CLI not authenticated"
    echo "Run: gh auth login"
    exit 1
fi

# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------
chmod +x build.sh
./build.sh

VERSION=$(grep '^version = ' pyproject.toml | cut -d'"' -f2)
WHEEL="dist/solax_modbus-${VERSION}-py3-none-any.whl"

if [ ! -f "$WHEEL" ]; then
    echo "ERROR: Wheel not found: $WHEEL"
    exit 1
fi

# ---------------------------------------------------------------------------
# Publish release
# ---------------------------------------------------------------------------
TAG="v${VERSION}"
echo ""
echo "==> Creating GitHub release $TAG..."

gh release create "$TAG" \
    "$WHEEL" \
    "install.sh" \
    --title "v${VERSION}" \
    --notes "Release v${VERSION}"

echo ""
echo "Release published: https://github.com/William12556/solax-modbus/releases/tag/${TAG}"
echo ""
echo "Install on Pi:"
echo "  curl -fsSL https://github.com/William12556/solax-modbus/releases/latest/download/install.sh -o install.sh"
echo "  chmod +x install.sh && ./install.sh"
