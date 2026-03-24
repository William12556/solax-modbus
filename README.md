# Solax Modbus Monitoring System

Real-time monitoring system for Solax X3 Hybrid 6.0-D solar inverters using Modbus TCP protocol.

## Table of Contents

- [Features](<#features>)
- [Publish](<#publish>)
- [Install — Raspberry Pi Linux](<#install--raspberry-pi-linux>)
- [Install — Apple macOS](<#install--apple-macos>)
- [Configure Service](<#configure-service>)
- [Verify](<#verify>)
- [Updates](<#updates>)
- [Documentation](<#documentation>)
- [Architecture](<#architecture>)
- [Development](<#development>)
- [Project Status](<#project-status>)
- [License](<#license>)

---

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

[Return to Table of Contents](<#table-of-contents>)

---

## Publish

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

[Return to Table of Contents](<#table-of-contents>)

---

## Install — Raspberry Pi Linux

Installs to `/opt/solax-monitor/`.

### Primary — GitHub release

```bash
curl -fsSL https://github.com/William12556/solax-modbus/releases/latest/download/install.sh -o install.sh
chmod +x install.sh && ./install.sh
```

To install a specific version:

```bash
./install.sh 0.1.5
```

### Developer — SCP from Mac

For development or pre-release testing. Build on Mac first, then transfer and install:

```bash
# Mac
scp dist/solax_modbus-*.whl install.sh pi@<hostname>:/tmp/

# Pi
chmod +x /tmp/install.sh && /tmp/install.sh /tmp/solax_modbus-*.whl
```

[Return to Table of Contents](<#table-of-contents>)

---

## Install — Apple macOS

Installs to `~/.local/opt/solax-monitor/`. No `sudo` required. Manual start only — no service registration.

### Primary — GitHub release

```bash
curl -fsSL https://github.com/William12556/solax-modbus/releases/latest/download/install.sh -o install.sh
chmod +x install.sh && ./install.sh
```

To install a specific version:

```bash
./install.sh 0.1.5
```

### Developer — local wheel

After running `build.sh` locally:

```bash
chmod +x install.sh && ./install.sh dist/solax_modbus-*.whl
```

[Return to Table of Contents](<#table-of-contents>)

---

## Configure Service

Raspberry Pi only. After installation, register `solax-monitor` as a systemd service:

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

sudo systemctl daemon-reload
sudo systemctl enable solax-monitor
sudo systemctl start solax-monitor
```

Replace `<INVERTER-IP>` with the inverter's IP address.

[Return to Table of Contents](<#table-of-contents>)

---

## Verify

```bash
sudo systemctl status solax-monitor
sudo journalctl -u solax-monitor -f
```

[Return to Table of Contents](<#table-of-contents>)

---

## Updates

Increment `version` in `pyproject.toml`, then repeat the same workflow used for initial installation.

**Publish and deploy via GitHub release:**

```bash
# Mac
./release.sh

# Pi or macOS
./install.sh
```

**Developer SCP (Pi only):**

```bash
# Mac
./build.sh
scp dist/solax_modbus-*.whl install.sh pi@<hostname>:/tmp/

# Pi
/tmp/install.sh /tmp/solax_modbus-*.whl
```

[Return to Table of Contents](<#table-of-contents>)

---

## Documentation

- [Deployment Guide](docs/deployment-guide.md) — Comprehensive installation and configuration
- [Design Documents](workspace/design/) — System architecture and component specifications
- [Test Documentation](workspace/test/) — Test plans and results

[Return to Table of Contents](<#table-of-contents>)

---

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

**System Requirements:**

| Platform | Requirement |
|---|---|
| Raspberry Pi 4 | Debian 12 (Bookworm), 100MB disk, network to inverter |
| macOS | Python 3.9+, Git |

[Return to Table of Contents](<#table-of-contents>)

---

## Development

**Run tests:**

```bash
cd /path/to/solax-modbus
source venv/bin/activate
pytest
pytest --cov=src --cov-report=html
```

**Development with emulator:**

The emulator runs on macOS and Linux. Port 502 requires elevated privileges on both platforms.

```bash
# Terminal 1: Start emulator (requires sudo for port 502 — macOS and Linux)
sudo python -m solax_modbus.emulator

# Terminal 2: Connect client
solax-monitor --ip 127.0.0.1 --interval 2
```

[Return to Table of Contents](<#table-of-contents>)

---

## Project Status

**Current Implementation:**
- Single-inverter monitoring (read-only)
- Validated with Solax X3 Hybrid 6.0-D
- Debian 12 deployment on Raspberry Pi 4
- macOS manual execution
- Scripted build and installation workflow

**Development Focus:**
This project serves as a practical implementation of LLM Orchestration Framework governance, AI-assisted embedded systems development, and systematic documentation and traceability practices.

**Important Notice:**
Experimental software in active development. Read-only operation ensures safe monitoring without inverter control risks. Fitness for production use not guaranteed.

[Return to Table of Contents](<#table-of-contents>)

---

## License

MIT License — see [LICENSE](<LICENSE>) file.

---

## Version History

| Version | Date | Description |
|---|---|---|
| 1.0 | 2026-03-19 | Initial README |
| 1.1 | 2026-03-24 | Restructured installation: added Publish section; separated Raspberry Pi Linux and Apple macOS install sections; added developer SCP path for each platform |
| 1.2 | 2026-03-24 | Corrected emulator platform constraint: emulator runs on macOS and Linux (not Pi only); sudo required on both for port 502 |

---

Copyright (c) 2025 William Watson. This work is licensed under the MIT License.
