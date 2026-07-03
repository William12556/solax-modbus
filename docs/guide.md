Created: 2026 July 02

# Solax-Modbus Guide

## Table of Contents

- [1. Overview](<#1 overview>)
- [2. Prerequisites](<#2 prerequisites>)
- [3. Build and Release](<#3 build and release>)
- [4. Installation](<#4 installation>)
  - [4.1 Development Deployment](<#4.1 development deployment>)
  - [4.2 General Deployment](<#4.2 general deployment>)
  - [4.3 Service Configuration](<#4.3 service configuration>)
- [5. Local Development](<#5 local development>)
  - [5.1 Tests](<#5.1 tests>)
  - [5.2 Emulator](<#5.2 emulator>)
- [6. Testing](<#6 testing>)
  - [6.1 Emulator Testing Workflow](<#6.1 emulator testing workflow>)
  - [6.2 Hardware Validation](<#6.2 hardware validation>)
  - [6.3 Validation Checklist](<#6.3 validation checklist>)
- [7. Service Operations](<#7 service operations>)
- [8. Updates](<#8 updates>)
- [9. Uninstallation](<#9 uninstallation>)
- [10. Architecture](<#10 architecture>)
- [11. Project Status](<#11 project status>)
- [12. Components](<#12 components>)
- [13. Troubleshooting](<#13 troubleshooting>)
- [14. Version History](<#14 version history>)

[Return to Table of Contents](<#table of contents>)

## 1. Overview

solax-modbus is a read-only Modbus TCP monitor for Solax X3 Hybrid 6.0-D inverters. Development and builds occur on macOS; production deployment targets Raspberry Pi / Debian. An included emulator permits development and testing without physical inverter hardware.

[Return to Table of Contents](<#table of contents>)

## 2. Prerequisites

**Development machine (macOS):**
- Python 3.9+
- Build module: `pip install build`
- Project repository: `/Users/<user_name>/Documents/GitHub/solax-modbus`
- `gh` CLI for release publishing: `brew install gh`, then `gh auth login`

**Raspberry Pi (production deployment):**
- Debian 13 (trixie)
- Python 3.9+
- Network connectivity to inverter
- Root/sudo access

**Verify prerequisites:**

```bash
# On Mac
python3 --version  # 3.9+
python3 -m pip show build
gh --version             # required for release.sh only

# On Pi
python3 --version  # 3.9+
ping <INVERTER-IP>
```

[Return to Table of Contents](<#table of contents>)

## 3. Build and Release

Performed on macOS. Produces a GitHub release containing the wheel and `install.sh`.

```bash
cd /Users/<user_name>/Documents/GitHub/solax-modbus

# One-time
chmod +x build.sh install.sh release.sh

./build.sh
```

`build.sh` verifies prerequisites, builds the wheel into `dist/`, and prints next-step commands.

**Publish release:**

```bash
./release.sh
```

`release.sh` invokes `build.sh`, tags the release from the `pyproject.toml` version, and uploads the wheel and `install.sh` to GitHub as release assets.

[Return to Table of Contents](<#table of contents>)

## 4. Installation

Two workflows are provided.

### 4.1 Development Deployment

For use during development and testing. The wheel is built locally and transferred directly to the Pi via SCP. No GitHub release is created.

```bash
# Mac
./build.sh
scp dist/solax_modbus-*.whl install.sh pi@<hostname>:/tmp/

# Pi
ssh pi@<hostname>
chmod +x /tmp/install.sh && /tmp/install.sh /tmp/solax_modbus-*.whl
```

### 4.2 General Deployment

For publishing a release to GitHub and installing from it.

**Option A — curl (recommended)**

```bash
curl -fsSL https://github.com/William12556/solax-modbus/releases/latest/download/install.sh -o install.sh
chmod +x install.sh && ./install.sh
```

Or with wget:

```bash
wget -qO install.sh https://github.com/William12556/solax-modbus/releases/latest/download/install.sh
chmod +x install.sh && ./install.sh
```

To install a specific version:

```bash
./install.sh 0.1.5
```

**Option B — pipe to bash**

```bash
curl -fsSL https://github.com/William12556/solax-modbus/releases/latest/download/install.sh | bash
```

Note: the script executes without prior inspection.

`install.sh` (all options): creates a virtual environment at `/opt/solax-monitor/venv/`, installs the wheel, and verifies the installed version.

### 4.3 Service Configuration

systemd registration is manual. Create a unit file after installation:

```bash
sudo tee /etc/systemd/system/solax-monitor.service << 'EOF'
[Unit]
Description=Solax X3 Hybrid Inverter Monitor
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/opt/solax-monitor
Environment=PYTHONUNBUFFERED=1
ExecStart=/opt/solax-monitor/venv/bin/solax-monitor --ip <INVERTER-IP> --interval 5
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF
```

**Replace `<INVERTER-IP>` with the inverter's IP address.**

Configuration parameters:
- `--ip`: Inverter IP address (required)
- `--port`: Modbus TCP port (default: 502)
- `--interval`: Polling interval in seconds (default: 5, minimum: 1)
- `--unit-id`: Modbus unit ID (default: 1)

Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable solax-monitor
sudo systemctl start solax-monitor

# Verify
sudo systemctl status solax-monitor
sudo journalctl -u solax-monitor -f
```

Expected: service active, Modbus connection established, telemetry display active.

[Return to Table of Contents](<#table of contents>)

## 5. Local Development

### 5.1 Tests

```bash
cd /Users/<user_name>/Documents/GitHub/solax-modbus

# Setup (one-time)
python3 -m venv venv
source venv/bin/activate
pip install -e ".[dev]"
deactivate

# Run tests
source venv/bin/activate
pytest
pytest --cov=src --cov-report=html
deactivate
```

### 5.2 Emulator

The emulator is pure Python with no OS-specific dependencies; it runs on macOS or Linux. Port 502 requires elevated privileges on both platforms; use `--port` to specify an unprivileged port instead.

```bash
# Terminal 1: Start emulator on an unprivileged port
python -m solax_modbus.emulator.solax_emulator --port 5020

# Terminal 2: Connect monitor to emulator port
solax-monitor 127.0.0.1 --port 5020
```

To use the default port 502, `sudo` is required:

```bash
sudo python -m solax_modbus.emulator.solax_emulator
```

**Behavior:**

- *PV generation:* sinusoidal curve, 06:00–18:00, peak 3300W per string (6600W total), ±10% random variation; zero generation 18:00–06:00.
- *Battery:* 10000Wh @ 51.2V capacity, 75% initial SOC; charges at 500W when PV > 1000W and SOC < 100%; discharges at 300W when PV < 500W and SOC > 10%; temperature rises to 30°C when SOC > 90%.
- *Grid:* 230V per phase nominal, 50Hz, simplified export/import model; feed-in calculated from PV surplus.
- *Update cycle:* state recalculated every 1.0 seconds (PV power, battery SOC, temperature, register values).

[Return to Table of Contents](<#table of contents>)

## 6. Testing

### 6.1 Emulator Testing Workflow

**Basic:**

1. Start the emulator (see [5.2 Emulator](<#5.2 emulator>)).
2. Run the monitor against it in a separate session:
   ```bash
   solax-monitor 127.0.0.1 --port 5020 --interval 5
   ```
3. Observe: PV power varies with simulated time of day; battery SOC changes with PV generation; temperature adjusts dynamically.
4. Stop both processes with `Ctrl+C`.

**Extended:**

```bash
# Run for 1 hour with 10-second updates
solax-monitor 127.0.0.1 --port 5020 --interval 10 --duration 3600
```

Observe: battery charging during simulated midday, discharging during simulated night, temperature increases with high PV generation.

Note: PV generation is calculated from system time; testing outside 06:00–18:00 local time produces zero PV output.

### 6.2 Hardware Validation

**CLI test:**

```bash
/opt/solax-monitor/venv/bin/solax-monitor --ip <INVERTER-IP> --interval 5
```

Expected: connection established; system status, grid metrics (3-phase voltage, current, power), PV generation (per-string and total), and battery metrics (voltage, current, SOC, temperature) displayed continuously. Press `Ctrl+C` to stop.

**Service test:**

```bash
sudo systemctl status solax-monitor
sudo journalctl -u solax-monitor -n 50
sudo journalctl -u solax-monitor -f   # monitor for 5 minutes
```

Expected: stable operation, no errors.

**Connection test:**

```bash
ping <INVERTER-IP>
nc -zv <INVERTER-IP> 502
```

Expected: ping succeeds, port 502 open.

**Restart test:**

```bash
sudo systemctl restart solax-monitor
sudo journalctl -u solax-monitor -f
```

Expected: clean restart, telemetry resumes.

**Boot persistence test:**

```bash
sudo reboot
# After reboot
sudo systemctl status solax-monitor
```

Expected: service starts automatically.

### 6.3 Validation Checklist

- [ ] Package installs without errors
- [ ] Service active and running
- [ ] Modbus connection established
- [ ] Telemetry displays at configured interval
- [ ] All metrics present (grid, PV, battery)
- [ ] Stable operation (5+ minutes)
- [ ] Service restart maintains operation
- [ ] Boot auto-start functions

[Return to Table of Contents](<#table of contents>)

## 7. Service Operations

### 7.1 Control

```bash
# Status
sudo systemctl status solax-monitor

# Start/stop/restart
sudo systemctl start solax-monitor
sudo systemctl stop solax-monitor
sudo systemctl restart solax-monitor

# Enable/disable auto-start
sudo systemctl enable solax-monitor
sudo systemctl disable solax-monitor
```

### 7.2 Logs

```bash
# Real-time
sudo journalctl -u solax-monitor -f

# Recent entries
sudo journalctl -u solax-monitor -n 100

# Time-based
sudo journalctl -u solax-monitor --since "1 hour ago"
sudo journalctl -u solax-monitor --since "2026-01-09 10:00"
```

**Remote monitoring from Mac:**

```bash
ssh pi@<hostname> 'sudo journalctl -u solax-monitor -f'
ssh pi@<hostname> 'sudo journalctl -u solax-monitor -f' | tee solax-monitor.log
```

### 7.3 Configuration

Files:
- Service: `/etc/systemd/system/solax-monitor.service`
- Installation: `/opt/solax-monitor/`
- Virtual environment: `/opt/solax-monitor/venv/`

[Return to Table of Contents](<#table of contents>)

## 8. Updates

Increment `version` in `pyproject.toml`, then follow the same workflow used for initial installation (see [4. Installation](<#4 installation>)).

```bash
# Development deployment (Mac)
./build.sh
scp dist/solax_modbus-*.whl install.sh pi@<hostname>:/tmp/
# (Pi)
/tmp/install.sh /tmp/solax_modbus-*.whl

# General deployment (Mac)
./release.sh
# (Pi, Option A)
./install.sh
# (Pi, Option B)
curl -fsSL https://github.com/William12556/solax-modbus/releases/latest/download/install.sh | bash
```

**Verify:**

```bash
sudo journalctl -u solax-monitor -f
```

Expected: service restarts and telemetry resumes.

[Return to Table of Contents](<#table of contents>)

## 9. Uninstallation

```bash
# Stop and disable service
sudo systemctl stop solax-monitor
sudo systemctl disable solax-monitor

# Remove service file
sudo rm -f /etc/systemd/system/solax-monitor.service
sudo systemctl daemon-reload

# Remove installation
sudo rm -rf /opt/solax-monitor
```

**Verify removal:**

```bash
sudo systemctl status solax-monitor  # "could not be found"
ls /opt/solax-monitor/               # "No such file or directory"
python3 -c "import solax_modbus"     # ModuleNotFoundError
```

[Return to Table of Contents](<#table of contents>)

## 10. Architecture

```
Raspberry Pi ──Modbus TCP (port 502)──> Solax X3 Hybrid Inverter
     │
     ├──> Console Display (journalctl logs)
     └──> Web UI (optional, --serve)
```

**System Requirements:**

| Platform | Requirement |
|---|---|
| Raspberry Pi 4 | Debian 13 (trixie), 100MB disk, network to inverter |

[Return to Table of Contents](<#table of contents>)

## 11. Project Status

**Current Implementation:**
- Single-inverter monitoring (read-only)
- Validated with Solax X3 Hybrid 6.0-D
- Debian 13 deployment on Raspberry Pi 4
- Scripted build and installation workflow

**Important Notice:**
Experimental software in active development. Read-only operation ensures safe monitoring without inverter control risks. Fitness for production use not guaranteed.

[Return to Table of Contents](<#table of contents>)

## 12. Components

| Component | Description |
|---|---|
| `SolaxInverterClient` | Modbus TCP communication with exponential backoff |
| `InverterDisplay` | Formatted telemetry output with power flow visualisation |
| `SolaxEmulator` | Offline development emulator |

[Return to Table of Contents](<#table of contents>)

## 13. Troubleshooting

### 13.1 Build Script Failures

**Python version:**
```bash
python3 --version  # Must be 3.9+
```

**Build module missing:**
```bash
python3 -m pip install build
```

**Permission errors:**
```bash
chmod +x build.sh
```

### 13.2 Install Script Failures

**Virtual environment missing:** indicates first-time installation. Follow [4. Installation](<#4 installation>).

**Version mismatch:** the script verifies installed version matches the wheel. If mismatch occurs:
```bash
sudo /opt/solax-monitor/venv/bin/pip install --force-reinstall /tmp/solax_modbus-*.whl
```

### 13.3 Service Won't Start

```bash
sudo systemctl status solax-monitor
sudo journalctl -u solax-monitor -n 50
```

Common causes: Python < 3.9 (`python3 --version`); package not installed (`/opt/solax-monitor/venv/bin/pip list | grep solax-modbus`); invalid inverter IP in service file; network issues (`ping <INVERTER-IP>`); port blocked (`nc -zv <INVERTER-IP> 502`).

### 13.4 Connection Failures

```bash
ping <INVERTER-IP>
nc -zv <INVERTER-IP> 502
sudo iptables -L  # Check firewall
```

Common causes: inverter powered off or rebooting; WiFi dongle not configured; wrong subnet; firewall blocking port 502; incorrect IP in service configuration.

### 13.5 Data Display Issues

```bash
sudo journalctl -u solax-monitor | grep -i "error\|exception"
```

Common causes: register read failures (verify inverter model compatibility); scaling errors (check register mappings); type conversion errors (signed/unsigned handling).

### 13.6 Log Analysis

```bash
sudo journalctl -u solax-monitor | grep -i "error\|exception\|traceback"
sudo journalctl -u solax-monitor | grep "connect"
sudo journalctl -u solax-monitor | grep "Grid\|PV\|Battery"
```

### 13.7 Emulator Issues

**Port already in use:**
```bash
sudo lsof -i :502
sudo kill -9 <PID>
```
Or run the emulator on an unprivileged port instead: `--port 5020`.

**Permission denied on port 502:** use `sudo`, or avoid the requirement entirely with `--port`.

**Monitor connection refused:** verify the emulator is running and that host/port parameters match between emulator and monitor.

**PV power always zero:** the emulator derives PV output from system time; run during 06:00–18:00 local time, or test other metrics outside that window.

[Return to Table of Contents](<#table of contents>)

## 14. Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-07-02 | Consolidated from deployment-guide.md, development.md, and development-testing-guide.md. Removed superseded manual-script emulator deployment procedure (development-testing-guide.md, pre-package emulator invocation); retained current package-based emulator workflow. Updated Raspberry Pi OS reference from Debian 12 to Debian 13 (trixie). Source documents moved to docs/closed/. |
| 1.1 | 2026-07-03 | Added §10 Architecture and §11 Project Status, migrated from README.md §8.0 and §9.0; corrected stale Debian 12 reference to Debian 13; renumbered Components/Troubleshooting/Version History to §12–§14. |

---

Copyright (c) 2025 William Watson. This work is licensed under the MIT License.
