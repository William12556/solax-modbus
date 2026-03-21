Created: 2026 January 09

# Solax-Modbus Deployment Guide

## Table of Contents

- [1. Prerequisites](<#1 prerequisites>)
- [2. Initial Installation](<#2 initial installation>)
- [3. Updates](<#3 updates>)
- [4. Service Operations](<#4 service operations>)
- [5. Uninstallation](<#5 uninstallation>)
- [6. Testing](<#6 testing>)
- [7. Troubleshooting](<#7 troubleshooting>)
- [8. Version History](<#8 version history>)

[Return to Table of Contents](<#table of contents>)

## 1. Prerequisites

**Development machine (Mac):**
- Python 3.9+
- Build module: `pip install build`
- Project repository: `/Users/<user_name>/Documents/GitHub/solax-modbus`
- `gh` CLI for release publishing: `brew install gh`, then `gh auth login`

**Raspberry Pi:**
- Debian-based OS (tested on Debian 12)
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

## 2. Initial Installation

Two workflows are provided: development deployment and general deployment.

---

### Development Deployment

For use during development and testing. The wheel is built locally and transferred directly to the Pi via SCP. No GitHub release is created.

**Step 1 — Build (Mac)**

```bash
cd /Users/<user_name>/Documents/GitHub/solax-modbus

# One-time
chmod +x build.sh install.sh

./build.sh
```

`build.sh` verifies prerequisites, builds the wheel into `dist/`, and prints next-step commands.

**Step 2 — Transfer and install**

```bash
# Transfer wheel and install script
scp dist/solax_modbus-*.whl install.sh pi@<hostname>:/tmp/

# Install on Pi
ssh pi@<hostname>
chmod +x /tmp/install.sh && /tmp/install.sh /tmp/solax_modbus-*.whl
```

---

### General Deployment

For publishing a release to GitHub. `release.sh` calls `build.sh`, then publishes a tagged GitHub release with the wheel and `install.sh` as downloadable assets.

**Step 1 — Build and publish (Mac)**

```bash
chmod +x release.sh
./release.sh
```

**Step 2 — Install on Pi**

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

---

`install.sh` (all options):
- Creates virtual environment at `/opt/solax-monitor/venv/` (Linux) or `~/.local/opt/solax-monitor/venv/` (macOS)
- Installs the wheel
- Verifies installed version

### 2.3. Configure Service

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

**Replace `<INVERTER-IP>` with your inverter's IP address.**

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

Expected: Service active, Modbus connection established, telemetry display active.

[Return to Table of Contents](<#table of contents>)

## 3. Updates

Increment `version` in `pyproject.toml`, then follow the same workflow used for initial installation.

**Development deployment:**

```bash
# Mac
./build.sh
scp dist/solax_modbus-*.whl install.sh pi@<hostname>:/tmp/

# Pi
/tmp/install.sh /tmp/solax_modbus-*.whl
```

**General deployment:**

```bash
# Mac
./release.sh

# Pi — Option A
./install.sh

# Pi — Option B
curl -fsSL https://github.com/William12556/solax-modbus/releases/latest/download/install.sh | bash
```

### 3.1. Verify Update

```bash
sudo journalctl -u solax-monitor -f
```

Expected: Service restarts and telemetry resumes.

[Return to Table of Contents](<#table of contents>)

## 4. Service Operations

### 4.1. Control

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

### 4.2. Logs

**Real-time:**
```bash
sudo journalctl -u solax-monitor -f
```

**Recent entries:**
```bash
sudo journalctl -u solax-monitor -n 100
```

**Time-based:**
```bash
sudo journalctl -u solax-monitor --since "1 hour ago"
sudo journalctl -u solax-monitor --since "2026-01-09 10:00"
```

**Remote monitoring from Mac:**
```bash
# Stream logs
ssh pi@<hostname> 'sudo journalctl -u solax-monitor -f'

# Stream and save
ssh pi@<hostname> 'sudo journalctl -u solax-monitor -f' | tee solax-monitor.log
```

### 4.3. Configuration

Files:
- Service: `/etc/systemd/system/solax-monitor.service`
- Installation: `/opt/solax-monitor/`
- Virtual environment: `/opt/solax-monitor/venv/`

[Return to Table of Contents](<#table of contents>)

## 5. Uninstallation

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
ls /opt/solax-monitor/  # "No such file or directory"
python3 -c "import solax_modbus"  # ModuleNotFoundError
```

[Return to Table of Contents](<#table of contents>)

## 6. Testing

### 6.1. Development Tests (Mac)

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

### 6.2. Hardware Validation (Pi)

**CLI test:**
```bash
/opt/solax-monitor/venv/bin/solax-monitor --ip <INVERTER-IP> --interval 5
```

Expected output:
- Connection established
- System status
- Grid metrics (3-phase voltage, current, power)
- PV generation (per-string and total)
- Battery metrics (voltage, current, SOC, temperature)
- Continuous updates

Press Ctrl+C to stop.

**Service test:**
```bash
# Verify startup
sudo systemctl status solax-monitor
sudo journalctl -u solax-monitor -n 50

# Monitor for 5 minutes
sudo journalctl -u solax-monitor -f
```

Expected: Stable operation, no errors.

**Connection test:**
```bash
ping <INVERTER-IP>
nc -zv <INVERTER-IP> 502
```

Expected: Ping succeeds, port 502 open.

**Restart test:**
```bash
sudo systemctl restart solax-monitor
sudo journalctl -u solax-monitor -f
```

Expected: Clean restart, telemetry resumes.

**Boot persistence test:**
```bash
sudo reboot
# After reboot
sudo systemctl status solax-monitor
```

Expected: Service starts automatically.

### 6.3. Validation Checklist

- [ ] Package installs without errors
- [ ] Service active and running
- [ ] Modbus connection established
- [ ] Telemetry displays at configured interval
- [ ] All metrics present (grid, PV, battery)
- [ ] Stable operation (5+ minutes)
- [ ] Service restart maintains operation
- [ ] Boot auto-start functions

[Return to Table of Contents](<#table of contents>)

## 7. Troubleshooting

### 7.1. Build Script Failures

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

### 7.2. Install Script Failures

**Virtual environment missing:**

Error indicates first-time installation. Follow [Initial Installation](<#2 initial installation>) procedures.

**Version mismatch:**

Script verifies installed version matches wheel. If mismatch occurs:
```bash
sudo /opt/solax-monitor/venv/bin/pip install --force-reinstall /tmp/solax_modbus-*.whl
```

### 7.3. Service Won't Start

**Check status:**
```bash
sudo systemctl status solax-monitor
sudo journalctl -u solax-monitor -n 50
```

**Common causes:**
- Python < 3.9: `python3 --version`
- Package not installed: `/opt/solax-monitor/venv/bin/pip list | grep solax-modbus`
- Invalid inverter IP in service file
- Network issues: `ping <INVERTER-IP>`
- Port blocked: `nc -zv <INVERTER-IP> 502`

### 7.4. Connection Failures

**Verify network:**
```bash
ping <INVERTER-IP>
nc -zv <INVERTER-IP> 502
sudo iptables -L  # Check firewall
```

**Common causes:**
- Inverter powered off or rebooting
- WiFi dongle not configured
- Wrong subnet
- Firewall blocking port 502
- Incorrect IP in service configuration

### 7.5. Data Display Issues

**Check logs:**
```bash
sudo journalctl -u solax-monitor | grep -i "error\|exception"
```

**Common causes:**
- Register read failures (verify inverter model compatibility)
- Scaling errors (check register mappings match documentation)
- Type conversion errors (signed/unsigned handling)

### 7.6. Log Analysis

**Find errors:**
```bash
sudo journalctl -u solax-monitor | grep -i "error\|exception\|traceback"
```

**Connection attempts:**
```bash
sudo journalctl -u solax-monitor | grep "connect"
```

**Data readings:**
```bash
sudo journalctl -u solax-monitor | grep "Grid\|PV\|Battery"
```

[Return to Table of Contents](<#table of contents>)

## 8. Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-01-09 | Initial deployment guide |
| 1.1 | 2026-01-09 | Added scripted deployment workflow |
| 2.0 | 2026-01-21 | Simplified to script-based workflow only, removed redundant manual procedures |
| 2.1 | 2026-03-19 | Added GitHub release workflow; three install modes (GitHub download, SCP, pipe-to-bash); release.sh; manual systemd registration |

---

Copyright (c) 2025 William Watson. This work is licensed under the MIT License.
