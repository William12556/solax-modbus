Created: 2026 January 09

# Solax-Modbus Deployment Guide

## Table of Contents

- [1. Quick Start](<#1 quick start>)
- [2. Build and Deploy](<#2 build and deploy>)
- [3. Service Operations](<#3 service operations>)
- [4. Uninstallation](<#4 uninstallation>)
- [5. Testing](<#5 testing>)
- [6. Troubleshooting](<#6 troubleshooting>)
- [7. Version History](<#7 version history>)

[Return to Table of Contents](<#table of contents>)

## 1. Quick Start

### 1.1. Prerequisites Check

**On development Mac:**
```bash
# Verify you're in project root
pwd  # Should show: /Users/<user_name>/Documents/GitHub/solax-modbus

# Verify build tools available
python3 --version  # Should be 3.9+
python3 -m pip show build  # Should show package info
```

**On Raspberry Pi:**
```bash
# Verify Python version
python3 --version  # Should be 3.9+

# Verify network connectivity to inverter
ping <inverter-ip>
```

### 1.2. Build Package

**Working directory: Project root on Mac**
```bash
cd /Users/<user_name>/Documents/GitHub/solax-modbus

# Clean previous builds
rm -rf dist/ build/ *.egg-info/

# Build distribution
python3 -m build

# Verify output
ls -lh dist/  # Should show: solax_modbus-0.1.0-py3-none-any.whl
```

### 1.3. Deploy to Pi

**Working directory: Project root on Mac**
```bash
# Transfer package
scp dist/solax_modbus-*.whl pi@<hostname>:/tmp/

# Connect to Pi
ssh pi@<hostname>
```

**Working directory: Any directory on Pi**
```bash
# Create installation directory
sudo mkdir -p /opt/solax-monitor
cd /opt/solax-monitor

# Create virtual environment
sudo python3 -m venv venv

# Install package into venv
sudo ./venv/bin/pip install /tmp/solax_modbus-*.whl

# Verify installation
./venv/bin/python -c "import solax_modbus; print(solax_modbus.__version__)"
```

### 1.4. Configure Service

Create systemd service file:

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

[Install]
WantedBy=multi-user.target
EOF
```

**Replace `<INVERTER-IP>` with your inverter's IP address.**

Enable and start service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable solax-monitor
sudo systemctl start solax-monitor
```

### 1.5. Verify Installation

```bash
# Check service status
sudo systemctl status solax-monitor

# Monitor logs
sudo journalctl -u solax-monitor -f
```

Service logs should show successful Modbus connection and telemetry display.

[Return to Table of Contents](<#table of contents>)

## 2. Build and Deploy

### 2.1. Prerequisites

**Development machine:**
- Python 3.9+
- Build tools: `pip install build`
- Git repository clone
- Working directory: Project root (`/Users/<user_name>/Documents/GitHub/solax-modbus`)

**Raspberry Pi:**
- Debian-based OS (tested on Debian 12)
- Python 3.9+
- Network connectivity to inverter
- Root/sudo access
- Sufficient disk space (100MB minimum)

### 2.2. Build Distribution

**Working directory: Project root on Mac**
```bash
# Navigate to project root
cd /Users/<user_name>/Documents/GitHub/solax-modbus

# Verify location
pwd  # Should output: /Users/<user_name>/Documents/GitHub/solax-modbus

# Install build tools (one-time)
pip install build

# Use build script
chmod +x build.sh
./build.sh

# Or build manually:
rm -rf dist/ build/ *.egg-info/
python3 -m build

# Verify output
ls -lh dist/  # Should show: solax_modbus-0.1.0-py3-none-any.whl
```

### 2.3. Transfer to Pi

**Working directory: Project root on Mac**
```bash
# Transfer package (adjust hostname as needed)
scp dist/solax_modbus-*.whl pi@raspberrypi:/tmp/

# Verify transfer
ssh pi@raspberrypi 'ls -lh /tmp/solax_modbus-*.whl'
```

### 2.4. Install on Pi

**Working directory: Any directory on Pi**
```bash
# Connect to Pi
ssh pi@raspberrypi

# Create installation directory
sudo mkdir -p /opt/solax-monitor
cd /opt/solax-monitor

# Create virtual environment
sudo python3 -m venv venv

# Verify venv creation
ls -la venv/  # Should show bin/, lib/, etc.

# Install package into venv
sudo ./venv/bin/pip install /tmp/solax_modbus-*.whl

# Verify installation
./venv/bin/python -c "import solax_modbus; print(solax_modbus.__version__)"

# Test CLI
./venv/bin/solax-monitor --help
```

### 2.5. Configure Systemd Service

Create service file with your inverter IP:

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

**Configuration parameters:**
- `--ip <INVERTER-IP>`: Inverter IP address (required)
- `--port 502`: Modbus TCP port (default: 502)
- `--interval 5`: Polling interval in seconds (minimum: 1)
- `--unit-id 1`: Modbus unit ID (default: 1)

Reload and enable:

```bash
sudo systemctl daemon-reload
sudo systemctl enable solax-monitor
sudo systemctl start solax-monitor
```

**Verify service:**
```bash
# Check service status
sudo systemctl status solax-monitor

# Check service file created
ls -l /etc/systemd/system/solax-monitor.service

# Monitor initial logs
sudo journalctl -u solax-monitor -n 50
```

Service starts automatically. Successful installation shows:
- `Active: active (running)` in status
- Modbus connection established in logs
- Telemetry data displayed in logs
- No error messages in journalctl output

### 2.6. Update Deployment

**Working directory: Project root on Mac**
```bash
# Build new version
cd /Users/<user_name>/Documents/GitHub/solax-modbus
./build.sh

# Transfer to Pi
scp dist/solax_modbus-*.whl pi@raspberrypi:/tmp/
```

**Working directory: Any directory on Pi**
```bash
# Connect to Pi
ssh pi@raspberrypi

# Use install script (preferred)
chmod +x install.sh
./install.sh solax_modbus-X.Y.Z-py3-none-any.whl

# Or manually:
sudo systemctl stop solax-monitor
sudo /opt/solax-monitor/venv/bin/pip install --upgrade /tmp/solax_modbus-*.whl
sudo systemctl start solax-monitor

# Verify upgrade
sudo journalctl -u solax-monitor -n 50
```

[Return to Table of Contents](<#table of contents>)

## 3. Service Operations

### 3.1. Control Commands

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

### 3.2. Log Access

**Real-time monitoring:**
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

**Stream to Mac:**
```bash
# Direct streaming (persistent connection)
ssh pi@raspberrypi 'sudo journalctl -u solax-monitor -f' > ~/solax-logs/stream.log

# Stream and view simultaneously
ssh pi@raspberrypi 'sudo journalctl -u solax-monitor -f' | tee ~/solax-logs/stream.log
```

**Collect logs:**
```bash
# On Pi
ssh pi@raspberrypi 'sudo journalctl -u solax-monitor --no-pager' > solax-monitor.log

# Transfer to Mac
scp pi@raspberrypi:~/solax-monitor.log ./
```

### 3.3. Configuration Locations

- Service file: `/etc/systemd/system/solax-monitor.service`
- Installation directory: `/opt/solax-monitor/`
- Virtual environment: `/opt/solax-monitor/venv/`

[Return to Table of Contents](<#table of contents>)

## 4. Uninstallation

### 4.1. Prerequisites Check

**Working directory: Any directory on Pi**
```bash
# Verify installation exists
sudo systemctl status solax-monitor  # Check if service exists
ls -la /opt/solax-monitor/  # Check if venv exists
```

### 4.2. Complete Removal

**Working directory: Any directory on Pi**
```bash
# Stop and disable service
sudo systemctl stop solax-monitor
sudo systemctl disable solax-monitor

# Remove systemd service file
sudo rm -f /etc/systemd/system/solax-monitor.service
sudo systemctl daemon-reload

# Remove entire installation directory
sudo rm -rf /opt/solax-monitor
```

### 4.3. Verification

**Working directory: Any directory on Pi**
```bash
# Confirm service removed
sudo systemctl status solax-monitor  # Should show "Unit solax-monitor.service could not be found"

# Confirm service file removed
ls /etc/systemd/system/solax-monitor.service  # Should show "No such file or directory"

# Confirm installation removed
ls /opt/solax-monitor/  # Should show "No such file or directory"

# Confirm package not importable
python3 -c "import solax_modbus"  # Should fail with ModuleNotFoundError
```

[Return to Table of Contents](<#table of contents>)

## 5. Testing

### 5.1. Development Tests (Mac)

**Working directory: Project root on Mac**
```bash
# Navigate to project root
cd /Users/<user_name>/Documents/GitHub/solax-modbus

# Verify location
pwd  # Should output: /Users/<user_name>/Documents/GitHub/solax-modbus
```

**Setup (one-time):**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -e ".[dev]"
deactivate
```

**Run tests (activate venv each new terminal session):**
```bash
source venv/bin/activate

# Run tests
pytest

# With coverage
pytest --cov=src --cov-report=html
open htmlcov/index.html

# Deactivate when done
deactivate
```

### 5.2. Hardware Validation (Pi)

**Prerequisites: Package deployed per [Build and Deploy](<#2 build and deploy>)**

**Working directory: Any directory on Pi**

**Manual CLI testing:**

```bash
# Test direct CLI (not as service)
/opt/solax-monitor/venv/bin/solax-monitor --ip <INVERTER-IP> --interval 5

# Expected output:
# - Connection established
# - System status displayed
# - Grid metrics (3-phase voltage, current, power)
# - PV generation (per-string and total)
# - Battery system (voltage, current, SOC, temperature)
# - Continuous updates every 5 seconds

# Press Ctrl+C to stop
```

**Service validation:**

After deployment, verify service operation:

```bash
# Check service startup
sudo systemctl status solax-monitor
sudo journalctl -u solax-monitor -n 50

# Monitor for 5 minutes - should remain stable
sudo journalctl -u solax-monitor -f
```

Expected logs:
1. Connection established to inverter
2. Continuous telemetry updates at configured interval
3. No connection errors or exceptions

**Connection validation:**

```bash
# Verify network connectivity
ping <INVERTER-IP>

# Verify Modbus port accessible
nc -zv <INVERTER-IP> 502
```

Expected: Ping succeeds, port 502 open

**Service restart:**
```bash
sudo systemctl restart solax-monitor
sudo journalctl -u solax-monitor -f
```

Expected: Service restarts cleanly, resumes telemetry display

**Boot persistence:**
```bash
sudo reboot
# After reboot
sudo systemctl status solax-monitor
```

Expected: Service starts automatically, telemetry display resumes

### 5.3. Validation Checklist

**Installation:**
- [ ] Package installs without errors
- [ ] Systemd service created and enabled
- [ ] Service active and running

**Data Acquisition:**
- [ ] Modbus connection established
- [ ] Telemetry displayed at configured interval
- [ ] Grid metrics present (voltage, current, power)
- [ ] PV metrics present (per-string voltage, current, power)
- [ ] Battery metrics present (voltage, current, SOC, temperature)
- [ ] No data corruption or scaling errors

**Service Operation:**
- [ ] Stable operation (5+ minutes)
- [ ] Service restart maintains operation
- [ ] Boot auto-start functions
- [ ] Logs accessible via journalctl

[Return to Table of Contents](<#table of contents>)

## 6. Troubleshooting

### 6.1. Service Won't Start

**Check status:**
```bash
sudo systemctl status solax-monitor
sudo journalctl -u solax-monitor -n 50
```

**Common causes:**
- Python < 3.9: `python3 --version`
- Package not installed: `pip list | grep solax-modbus`
- Invalid inverter IP in service file
- Network connectivity: `ping <INVERTER-IP>`
- Port 502 blocked: `nc -zv <INVERTER-IP> 502`

### 6.2. Connection Failures

**Verify network path:**
```bash
# Check inverter reachable
ping <INVERTER-IP>

# Check Modbus port open
nc -zv <INVERTER-IP> 502

# Check firewall rules (if applicable)
sudo iptables -L
```

**Common causes:**
- Inverter powered off or rebooting
- WiFi dongle not configured
- Inverter on different subnet
- Firewall blocking port 502
- Wrong IP address in service configuration

### 6.3. Data Display Issues

**Check logs:**
```bash
sudo journalctl -u solax-monitor | grep -i "error\|exception"
```

**Common causes:**
- Register read failures (check inverter compatibility)
- Scaling errors (verify register mappings)
- Type conversion errors (check signed/unsigned handling)

### 6.4. Import Errors After Install

**Verify installation:**
```bash
/opt/solax-monitor/venv/bin/pip list | grep solax-modbus
/opt/solax-monitor/venv/bin/python -c "import solax_modbus; print(solax_modbus.__version__)"
```

**Reinstall if needed:**
```bash
sudo /opt/solax-monitor/venv/bin/pip install --force-reinstall /tmp/solax_modbus-0.1.0-py3-none-any.whl
```

### 6.5. Log Analysis Patterns

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

## 7. Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-01-09 | Initial deployment guide |

---

Copyright (c) 2025 William Watson. This work is licensed under the MIT License.