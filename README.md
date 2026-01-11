# Solax Modbus Monitoring System

Real-time monitoring system for Solax X3 Hybrid 6.0-D solar inverters using Modbus TCP protocol.

## Features

- Direct Modbus TCP communication (offline operation, no cloud dependencies)
- Read-only monitoring (safe, non-intrusive)
- Comprehensive telemetry display:
  - Three-phase grid metrics (voltage, current, power)
  - Dual MPPT PV generation (per-string and total)
  - Battery system status (voltage, current, SOC, temperature)
  - Energy accounting (grid import/export, load consumption)
- Console-based real-time display with power flow visualization
- Configurable polling intervals
- Modbus TCP emulator for offline development

## Quick Start

### Prerequisites

**Development Machine (Mac):**
- Python 3.9+
- Build tools: `pip install build`
- Git repository clone

**Raspberry Pi:**
- Debian 12 (tested platform)
- Python 3.9+
- Network access to Solax inverter (Modbus TCP port 502)

### Installation

#### Build on Mac

```bash
cd /path/to/solax-modbus

# Use build script
chmod +x build.sh
./build.sh
```

#### Deploy to Raspberry Pi

```bash
# Transfer wheel
scp dist/solax_modbus-*.whl pi@raspberrypi:/tmp/

# Connect to Pi
ssh pi@raspberrypi

# Initial setup
sudo mkdir -p /opt/solax-monitor
cd /opt/solax-monitor
sudo python3 -m venv venv
sudo ./venv/bin/pip install /tmp/solax_modbus-*.whl
```

### Configure Service

```bash
# Create systemd service
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

# Enable and start
sudo systemctl daemon-reload
sudo systemctl enable solax-monitor
sudo systemctl start solax-monitor
```

**Replace `<INVERTER-IP>` with your inverter's IP address.**

### Verify

```bash
# Check service status
sudo systemctl status solax-monitor

# Monitor logs
sudo journalctl -u solax-monitor -f
```

### Updates

```bash
# Build on Mac
cd /path/to/solax-modbus
./build.sh
scp dist/solax_modbus-*.whl pi@raspberrypi:/tmp/

# Install on Pi using install script
ssh pi@raspberrypi
./install.sh solax_modbus-X.Y.Z-py3-none-any.whl
```

## Documentation

- [Deployment Guide](docs/deployment-guide.md) - Comprehensive installation and configuration
- [Design Documents](workspace/design/) - System architecture and component specifications
- [Test Documentation](workspace/test/) - Test plans and results

## Architecture

```
Raspberry Pi ──Modbus TCP (port 502)──> Solax X3 Hybrid Inverter
     │
     └──> Console Display (journalctl logs)
```

**Components:**
- `SolaxInverterClient`: Modbus TCP communication with exponential backoff
- `InverterDisplay`: Formatted telemetry output with power flow visualization
- `SolaxEmulator`: Offline development emulator

## System Requirements

**Raspberry Pi:**
- Raspberry Pi 4 (tested)
- Debian 12 (Bookworm)
- 100MB disk space
- Network connectivity to inverter

**Development:**
- macOS or Linux
- Python 3.9+
- Git

## Development

**Run tests:**
```bash
cd /path/to/solax-modbus
source venv/bin/activate
pytest
pytest --cov=src --cov-report=html
```

**Development with emulator:**
```bash
# Terminal 1: Start emulator
python -m solax_modbus.emulator

# Terminal 2: Connect client
solax-monitor --ip 127.0.0.1 --interval 2
```

## Project Status

**Current Implementation:**
- Single-inverter monitoring (read-only)
- Validated with Solax X3 Hybrid 6.0-D
- Debian 12 deployment on Raspberry Pi 4
- Scripted build and installation workflow

**Development Focus:**
This project serves as a practical implementation of:
- LLM Orchestration Framework governance
- AI-assisted embedded systems development
- Systematic documentation and traceability practices

**Important Notice:**
Experimental software in active development. Read-only operation ensures safe monitoring without inverter control risks. Fitness for production use not guaranteed.
## License

MIT License - see [LICENSE](<LICENSE>) file.

---

Copyright (c) 2025 William Watson. This work is licensed under the MIT License.
