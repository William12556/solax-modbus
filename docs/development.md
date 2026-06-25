Created: 2026 June 25

# Development Guide

---

## Table of Contents

[1.0 Build and Release](<#1.0 build and release>)
[2.0 Developer Installation](<#2.0 developer installation>)
[2.1 Raspberry Pi](<#2.1 raspberry pi>)
[2.2 macOS](<#2.2 macos>)
[3.0 Local Development](<#3.0 local development>)
[3.1 Tests](<#3.1 tests>)
[3.2 Emulator](<#3.2 emulator>)
[4.0 Components](<#4.0 components>)
[Version History](<#version history>)

---

## 1.0 Build and Release

Performed on macOS. Produces a GitHub release containing the wheel and `install.sh`.

**Prerequisites:**
- Python 3.9+
- `pip install build`
- `gh` CLI: `brew install gh`, then `gh auth login`

**Build:**

```bash
cd /path/to/solax-modbus
chmod +x build.sh
./build.sh
```

**Publish release:**

```bash
chmod +x release.sh
./release.sh
```

`release.sh` invokes `build.sh`, tags the release from `pyproject.toml` version, and uploads the wheel and `install.sh` to GitHub.

**Updates:** Increment `version` in `pyproject.toml`, then repeat the build and release workflow above.

[Return to Table of Contents](<#table of contents>)

---

## 2.0 Developer Installation

### 2.1 Raspberry Pi

For development or pre-release testing. Build on macOS first, then transfer and install:

```bash
# Mac
scp dist/solax_modbus-*.whl install.sh pi@<hostname>:/tmp/

# Pi
chmod +x /tmp/install.sh && /tmp/install.sh /tmp/solax_modbus-*.whl
```

[Return to Table of Contents](<#table of contents>)

### 2.2 macOS

After running `build.sh` locally:

```bash
chmod +x install.sh && ./install.sh dist/solax_modbus-*.whl
```

[Return to Table of Contents](<#table of contents>)

---

## 3.0 Local Development

### 3.1 Tests

```bash
cd /path/to/solax-modbus
source venv/bin/activate
pytest
pytest --cov=src --cov-report=html
```

[Return to Table of Contents](<#table of contents>)

### 3.2 Emulator

The emulator runs on macOS and Linux. Port 502 requires elevated privileges on both platforms; use `--port` to specify an unprivileged port instead.

```bash
# Terminal 1: Start emulator on an unprivileged port
python -m solax_modbus.emulator.solax_emulator --port 5020

# Terminal 2: Connect monitor to emulator port
solax-monitor 127.0.0.1 --port 5020
```

To use the default port 502, `sudo` is required on both macOS and Linux:

```bash
sudo python -m solax_modbus.emulator.solax_emulator
```

See [Development Testing Guide](development-testing-guide.md) for Raspberry Pi emulator deployment.

[Return to Table of Contents](<#table of contents>)

---

## 4.0 Components

| Component | Description |
|---|---|
| `SolaxInverterClient` | Modbus TCP communication with exponential backoff |
| `InverterDisplay` | Formatted telemetry output with power flow visualisation |
| `SolaxEmulator` | Offline development emulator |

[Return to Table of Contents](<#table of contents>)

---

## Version History

| Version | Date | Description |
|---|---|---|
| 1.0 | 2026-06-25 | Initial document — developer content extracted from README |

---

Copyright (c) 2025 William Watson. This work is licensed under the MIT License.
