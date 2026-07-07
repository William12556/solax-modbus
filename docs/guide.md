Created: 2026 July 02

# Solax-Modbus Guide

## Table of Contents

- [1. Overview](<#1-overview>)
- [2. Prerequisites](<#2-prerequisites>)
- [3. Build and Release](<#3-build-and-release>)
- [4. Raspberry Pi Setup](<#4-raspberry-pi-setup>)
  - [4.1 Hardware](<#41-hardware>)
  - [4.2 Operating System](<#42-operating-system>)
  - [4.3 Boot Configuration](<#43-boot-configuration>)
  - [4.4 Development Access (USB OTG)](<#44-development-access-usb-otg>)
- [5. Installation](<#5-installation>)
  - [5.1 Development Deployment](<#51-development-deployment>)
  - [5.2 General Deployment](<#52-general-deployment>)
  - [5.3 Service Configuration](<#53-service-configuration>)
- [6. Local Development](<#6-local-development>)
  - [6.1 Tests](<#61-tests>)
  - [6.2 Emulator](<#62-emulator>)
- [7. Testing](<#7-testing>)
  - [7.1 Emulator Testing Workflow](<#71-emulator-testing-workflow>)
  - [7.2 Hardware Validation](<#72-hardware-validation>)
  - [7.3 Validation Checklist](<#73-validation-checklist>)
- [8. Service Operations](<#8-service-operations>)
- [9. Updates](<#9-updates>)
- [10. Uninstallation](<#10-uninstallation>)
- [11. Architecture](<#11-architecture>)
- [12. Project Status](<#12-project-status>)
- [13. Components](<#13-components>)
- [14. Troubleshooting](<#14-troubleshooting>)
- [15. Version History](<#15-version-history>)

[Return to Table of Contents](<#table-of-contents>)

## 1. Overview

solax-modbus is a read-only Modbus TCP monitor for Solax X3 Hybrid 6.0-D inverters. Development and builds occur on macOS; production deployment targets Raspberry Pi / Debian. An included emulator permits development and testing without physical inverter hardware.

[Return to Table of Contents](<#table-of-contents>)

## 2. Prerequisites

**Development machine (macOS):**
- Python 3.9+
- Build module: `pip install build`
- Project repository: `~/Documents/GitHub/solax-modbus`
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

[Return to Table of Contents](<#table-of-contents>)

## 3. Build and Release

Performed on macOS. Produces a GitHub release containing the wheel and `install.sh`.

```bash
cd ~/Documents/GitHub/solax-modbus

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

[Return to Table of Contents](<#table-of-contents>)

## 4. Raspberry Pi Setup

### 4.1 Hardware

| Component | Specification |
|---|---|
| SBC | Raspberry Pi Zero 2W |
| Role | Headless Modbus TCP client |

[Return to Table of Contents](<#table-of-contents>)

### 4.2 Operating System

Debian GNU/Linux 13 (trixie), 64-bit.

Use Raspberry Pi Imager to write the image to a microSD card. Select: *Raspberry Pi OS (other)* → *Raspberry Pi OS Lite (64-bit)* — verify the image reports trixie before writing.

**Imager settings to configure before writing:**

- Hostname: `solax-modbus`
- Enable SSH: yes
- Username / password: as required
- Wi-Fi credentials: as required

The boot configuration directory is `/boot/firmware/`.

[Return to Table of Contents](<#table-of-contents>)

### 4.3 Boot Configuration

`/boot/firmware/config.txt` — append the following to enable USB OTG device mode.

```ini
# USB OTG — development access
dtoverlay=dwc2
```

Note: do not add `otg_mode=1` under `[cm4]`. That setting enables host mode and disables device mode, and is only applicable to Compute Module 4 hardware.

[Return to Table of Contents](<#table-of-contents>)

### 4.4 Development Access (USB OTG)

For development use only. Not required for normal solax-modbus operation.

The Pi Zero 2W USB OTG port provides a virtual Ethernet connection to a development laptop. This is the recommended method for SSH access when the Pi is deployed at the inverter location, where no network infrastructure may be available.

**Hardware**

| Connection | Port |
|---|---|
| Power supply | `PWR IN` (left micro-USB) |
| Laptop | `USB` (right micro-USB, OTG) |

Both ports may be used simultaneously. The `PWR IN` port is power only. The `USB` port carries data and may also supply power from the laptop.

**Pi Configuration**

One-time setup. Requires SSH access to the Pi before in-field deployment.

1. Enable the DWC2 overlay — see [4.3 Boot Configuration](<#43-boot-configuration>).

2. Load USB gadget modules. Append to `/etc/modules`:

   ```
   dwc2
   g_cdc
   ```

   `g_cdc` presents the CDC-ECM interface, which macOS supports natively. Do not use `g_ether` — it presents as RNDIS, which macOS does not support, and ARP resolution fails.

   Warning: check that `/boot/firmware/cmdline.txt` does not contain a `modules-load=` parameter referencing `g_ether`. If present, remove `g_ether` from that parameter. Having both `g_cdc` and `g_ether` loaded simultaneously causes a conflict.

3. Reboot:

   ```bash
   sudo reboot
   ```

4. Create a NetworkManager connection profile. Bookworm and trixie use NetworkManager; `usb0` requires an explicit connection profile to obtain a link-local IPv4 address.

   ```bash
   nmcli connection add type ethernet ifname usb0 con-name usb0 \
     ipv4.method link-local \
     ipv6.method ignore
   ```

5. Bring up the interface:

   ```bash
   nmcli connection up usb0
   ```

   This profile persists across reboots. `usb0` activates automatically when a USB host is connected.

**Laptop Connection**

Connect a data-capable micro-USB cable to the Pi `USB` (OTG) port. A charge-only cable will not work — the cable must carry data lines.

macOS detects the Pi as a CDC Composite Gadget and creates a new network interface in System Settings → Network with a self-assigned link-local address (`169.254.x.x`).

SSH to the Pi by IP address:

```bash
# Obtain Pi IP from: ip -brief a (on Pi)
ssh admin@169.254.x.x
```

Or by hostname if avahi-daemon is running:

```bash
ssh admin@solax-modbus.local
```

Internet access: the laptop's WiFi connection is unaffected. macOS routes internet traffic over WiFi and Pi traffic over the USB interface independently.

**Verification**

```bash
# On Pi — confirm usb0 is up with a link-local address
ip -brief a

# Expected:
# usb0   UP   169.254.x.x/16   fe80::...

# On Mac — confirm reachability
ping -c 3 169.254.x.x
ssh admin@169.254.x.x
```

[Return to Table of Contents](<#table-of-contents>)

## 5. Installation

Two workflows are provided.

### 5.1 Development Deployment

For use during development and testing. The wheel is built locally and transferred directly to the Pi via SCP. No GitHub release is created.

```bash
# Mac
./build.sh
scp dist/solax_modbus-*.whl install.sh pi@<hostname>:/tmp/

# Pi
ssh pi@<hostname>
chmod +x /tmp/install.sh && /tmp/install.sh /tmp/solax_modbus-*.whl
```

### 5.2 General Deployment

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

`install.sh` (all options): creates a virtual environment at `/opt/solax-monitor/venv/`, installs the wheel, and verifies the installed version. Pass `--ip <INVERTER-IP>` to also register and start the systemd service; see [5.3 Service Configuration](<#53-service-configuration>) and `install.sh --help` for all service flags.

### 5.3 Service Configuration

`install.sh --ip <INVERTER-IP>` registers the systemd service automatically (see [5.2 General Deployment](<#52-general-deployment>)). The procedure below is for manual registration, or to modify an existing unit file.

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

[Return to Table of Contents](<#table-of-contents>)

## 6. Local Development

### 6.1 Tests

```bash
cd ~/Documents/GitHub/solax-modbus

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

### 6.2 Emulator

The emulator is a standalone script at `src/tools/emulator/solax_emulator.py`, outside the `solax_modbus` package. It requires `pymodbus>=3.11.0,<4.0.0` — the same floor `pyproject.toml` sets for the rest of the project. Debian's packaged version (`python3-pymodbus`, 3.8.6 in trixie) is below this floor; use a venv rather than the OS package. Pure Python, no OS-specific dependencies; runs on macOS or Linux. Port 502 requires elevated privileges on both platforms; use `--port` to specify an unprivileged port instead.

**Standalone installation** (e.g. on the Pi, independent of a repository checkout):

```bash
# Mac — transfer the script
scp src/tools/emulator/solax_emulator.py admin@solax-modbus.local:/tmp/

# Pi — provisioning (one-time)
sudo mkdir -p /opt/solax_emulator
sudo mv /tmp/solax_emulator.py /opt/solax_emulator/
python3 -m venv /opt/solax_emulator/venv
/opt/solax_emulator/venv/bin/pip install "pymodbus>=3.11.0,<4.0.0"

# Pi — execution
/opt/solax_emulator/venv/bin/python3 /opt/solax_emulator/solax_emulator.py --port 5020

# Terminal 2: Connect monitor to emulator port
solax-monitor 127.0.0.1 --port 5020
```

To use the default port 502, `sudo` is required:

```bash
sudo /opt/solax_emulator/venv/bin/python3 /opt/solax_emulator/solax_emulator.py
```

**Running from a repository checkout** (local development):

```bash
python3 -m venv venv
source venv/bin/activate
pip install "pymodbus>=3.11.0,<4.0.0"

python3 src/tools/solax_emulator/solax_emulator.py --port 5020
```

**Behavior:**

- *PV generation:* sinusoidal curve, 06:00–18:00, peak 3300W per string (6600W total), ±10% random variation; zero generation 18:00–06:00.
- *Battery:* 10000Wh @ 51.2V capacity, 75% initial SOC; charges at 500W when PV > 1000W and SOC < 100%; discharges at 300W when PV < 500W and SOC > 10%; temperature rises to 30°C when SOC > 90%.
- *Grid:* 230V per phase nominal, 50Hz, simplified export/import model; feed-in calculated from PV surplus.
- *Update cycle:* state recalculated every 1.0 seconds (PV power, battery SOC, temperature, register values).

[Return to Table of Contents](<#table-of-contents>)

## 7. Testing

### 7.1 Emulator Testing Workflow

**Basic:**

1. Start the emulator (see [6.2 Emulator](<#62-emulator>)).
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

### 7.2 Hardware Validation

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

### 7.3 Validation Checklist

- [ ] Package installs without errors
- [ ] Service active and running
- [ ] Modbus connection established
- [ ] Telemetry displays at configured interval
- [ ] All metrics present (grid, PV, battery)
- [ ] Stable operation (5+ minutes)
- [ ] Service restart maintains operation
- [ ] Boot auto-start functions

[Return to Table of Contents](<#table-of-contents>)

## 8. Service Operations

### 8.1 Control

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

### 8.2 Logs

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
ssh pi@solax-modbus.local 'sudo journalctl -u solax-monitor -f'
ssh pi@<solax-modbus.local 'sudo journalctl -u solax-monitor -f' | tee solax-monitor.log
```

### 8.3 Configuration

Files:
- Service: `/etc/systemd/system/solax-monitor.service`
- Installation: `/opt/solax-monitor/`
- Virtual environment: `/opt/solax-monitor/venv/`

[Return to Table of Contents](<#table-of-contents>)

## 9. Updates

Increment `version` in `pyproject.toml`, then follow the same workflow used for initial installation (see [5. Installation](<#5-installation>)).

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

[Return to Table of Contents](<#table-of-contents>)

## 10. Uninstallation

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

[Return to Table of Contents](<#table-of-contents>)

## 11. Architecture

```
Raspberry Pi ──Modbus TCP (port 502)──> Solax X3 Hybrid Inverter
     │
     ├──> Console Display (journalctl logs)
     └──> Web UI (enabled by default on port 8181; --no-serve to disable)
```

**System Requirements:**

| Platform | Requirement |
|---|---|
| Raspberry Pi 4 | Debian 13 (trixie), 100MB disk, network to inverter |

[Return to Table of Contents](<#table-of-contents>)

## 12. Project Status

**Current Implementation:**
- Single-inverter monitoring (read-only)
- Validated with Solax X3 Hybrid 6.0-D
- Debian 13 deployment on Raspberry Pi 4
- Scripted build and installation workflow

**Important Notice:**
Experimental software in active development. Read-only operation ensures safe monitoring without inverter control risks. Fitness for production use not guaranteed.

[Return to Table of Contents](<#table-of-contents>)

## 13. Components

| Component | Description |
|---|---|
| `SolaxInverterClient` | Modbus TCP communication with exponential backoff |
| `InverterDisplay` | Formatted telemetry output with power flow visualisation |
| `SolaxEmulator` | Offline development emulator |

[Return to Table of Contents](<#table-of-contents>)

## 14. Troubleshooting

### 14.1 Build Script Failures

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

### 14.2 Install Script Failures

**Virtual environment missing:** indicates first-time installation. Follow [5. Installation](<#5-installation>).

**Version mismatch:** the script verifies installed version matches the wheel. If mismatch occurs:
```bash
sudo /opt/solax-monitor/venv/bin/pip install --force-reinstall /tmp/solax_modbus-*.whl
```

### 14.3 Service Won't Start

```bash
sudo systemctl status solax-monitor
sudo journalctl -u solax-monitor -n 50
```

Common causes: Python < 3.9 (`python3 --version`); package not installed (`/opt/solax-monitor/venv/bin/pip list | grep solax-modbus`); invalid inverter IP in service file; network issues (`ping <INVERTER-IP>`); port blocked (`nc -zv <INVERTER-IP> 502`).

### 14.4 Connection Failures

```bash
ping <INVERTER-IP>
nc -zv <INVERTER-IP> 502
sudo iptables -L  # Check firewall
```

Common causes: inverter powered off or rebooting; WiFi dongle not configured; wrong subnet; firewall blocking port 502; incorrect IP in service configuration.

### 14.5 Data Display Issues

```bash
sudo journalctl -u solax-monitor | grep -i "error\|exception"
```

Common causes: register read failures (verify inverter model compatibility); scaling errors (check register mappings); type conversion errors (signed/unsigned handling).

### 14.6 Log Analysis

```bash
sudo journalctl -u solax-monitor | grep -i "error\|exception\|traceback"
sudo journalctl -u solax-monitor | grep "connect"
sudo journalctl -u solax-monitor | grep "Grid\|PV\|Battery"
```

### 14.7 Emulator Issues

**Port already in use:**
```bash
sudo lsof -i :502
sudo kill -9 <PID>
```
Or run the emulator on an unprivileged port instead: `--port 5020`.

**Permission denied on port 502:** use `sudo`, or avoid the requirement entirely with `--port`.

**Monitor connection refused:** verify the emulator is running and that host/port parameters match between emulator and monitor.

**PV power always zero:** the emulator derives PV output from system time; run during 06:00–18:00 local time, or test other metrics outside that window.

[Return to Table of Contents](<#table-of-contents>)

## 15. Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-07-02 | Consolidated from deployment-guide.md, development.md, and development-testing-guide.md. Removed superseded manual-script emulator deployment procedure (development-testing-guide.md, pre-package emulator invocation); retained current package-based emulator workflow. Updated Raspberry Pi OS reference from Debian 12 to Debian 13 (trixie). Source documents moved to docs/closed/. |
| 1.1 | 2026-07-03 | Added §10 Architecture and §11 Project Status, migrated from README.md §8.0 and §9.0; corrected stale Debian 12 reference to Debian 13; renumbered Components/Troubleshooting/Version History to §12–§14. |
| 1.2 | 2026-07-03 | Noted install.sh --ip auto-registration in §4.2 and §4.3; clarified §4.3 manual procedure applies when --ip is not used. |
| 1.3 | 2026-07-03 | Corrected all internal anchor links (TOC and cross-references) to match GitHub's anchor generation rule: periods and spaces in numbered headings stripped/hyphenated (e.g. §4.1 → #41-development-deployment). Section numbering retained. |
| 1.4 | 2026-07-03 | Merged docs/pi-setup.md into new §4 Raspberry Pi Setup (Hardware, Operating System, Boot Configuration, Development Access/USB OTG); renumbered §4–14 to §5–15 accordingly. Corrected pi-setup.md's stale Debian 12 (Bookworm) reference to Debian 13 (trixie) during merge. Converted pi-setup.md's Obsidian-style anchors to GitHub-hyphenated anchors for consistency with this document. Source document moved to docs/closed/. |
| 1.5 | 2026-07-03 | §6.2 rewritten: emulator invocation reverts to the standalone-script method (src/tools/emulator/solax_emulator.py), reversing the 1.0 decision to drop it. The package-based module invocation (python -m solax_modbus.emulator.solax_emulator) is removed — it required a package install this section never specified, and nothing in the codebase depends on the emulator being package-importable. Emulator source relocated from src/solax_modbus/emulator/ to src/tools/emulator/ (see design-c2b3c4d5 1.5). src/solax_modbus/emulator/README.md merged into this section and reduced to a stub. |
| 1.6 | 2026-07-03 | §6.2: pinned pymodbus>=3.11.0,<4.0.0 (matches project floor; Debian trixie's python3-pymodbus, 3.8.6, is below it). Added standalone installation procedure (/opt/emulator, dedicated venv, provisioning + execution) alongside the repository-checkout method. |
| 1.7 | 2026-07-03 | §6.2: added scp transfer step to standalone installation (Mac → Pi), matching the §5.1 pattern. Standalone procedure no longer assumes the script is already present on the target machine. |
| 1.8 | 2026-07-07 | §11 Architecture: Web UI now enabled by default (port 8181); `--serve` replaced by `--no-serve`. See change-a7c3e9d2. |

---

Copyright (c) 2025 William Watson. This work is licensed under the MIT License.
