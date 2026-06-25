 # Solax Modbus Monitoring System

Real-time monitoring system for Solax X3 Hybrid 6.0-D solar inverters using Modbus TCP protocol.

## Table of Contents

- [Features](<#features>)
- [Install — Raspberry Pi Linux](<#install--raspberry-pi-linux>)
- [Install — Apple macOS](<#install--apple-macos>)
- [Configure Service](<#configure-service>)
- [Verify](<#verify>)
- [Updates](<#updates>)
- [Documentation](<#documentation>)
- [Architecture](<#architecture>)
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

## Install — Raspberry Pi Linux

Installs to `/opt/solax-monitor/`. A symlink is created at `/usr/local/bin/solax-monitor` so the command is available without a full path. The symlink is verified on each install and corrected if stale.

```bash
curl -fsSL https://github.com/William12556/solax-modbus/releases/latest/download/install.sh -o install.sh
chmod +x install.sh && ./install.sh
```

To install a specific version:

```bash
./install.sh 0.1.5
```

[Return to Table of Contents](<#table-of-contents>)

---

## Install — Apple macOS

Installs to `~/.local/opt/solax-monitor/`. No `sudo` required. Manual start only — no service registration.

The installer adds `~/.local/opt/solax-monitor/venv/bin` to `PATH` in your shell profile (`~/.zshrc` or `~/.bash_profile`). Open a new terminal after installation for the change to take effect.

```bash
curl -fsSL https://github.com/William12556/solax-modbus/releases/latest/download/install.sh -o install.sh
chmod +x install.sh && ./install.sh
```

To install a specific version:

```bash
./install.sh 0.1.5
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

Re-run the installer to update to the latest release:

```bash
./install.sh
```

To update to a specific version:

```bash
./install.sh 0.1.5
```

[Return to Table of Contents](<#table-of-contents>)

---

## Documentation

- [Deployment Guide](docs/deployment-guide.md) — Comprehensive installation and configuration
- [Development Guide](docs/development.md) — Build, release, and developer workflows
- [Design Documents](ai/workspace/design/) — System architecture and component specifications
- [Test Documentation](ai/workspace/test/) — Test plans and results

[Return to Table of Contents](<#table-of-contents>)

---

## Architecture

```
Raspberry Pi ──Modbus TCP (port 502)──> Solax X3 Hybrid Inverter
     │
     └──> Console Display (journalctl logs)
```

**System Requirements:**

| Platform | Requirement |
|---|---|
| Raspberry Pi 4 | Debian 12 (Bookworm), 100MB disk, network to inverter |
| macOS | Python 3.9+, Git |

[Return to Table of Contents](<#table-of-contents>)

---

## Project Status

**Current Implementation:**
- Single-inverter monitoring (read-only)
- Validated with Solax X3 Hybrid 6.0-D
- Debian 12 deployment on Raspberry Pi 4
- macOS manual execution
- Scripted build and installation workflow

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
| 1.3 | 2026-03-24 | Updated PATH configuration: Linux symlink to /usr/local/bin/; macOS PATH added to shell profile; updated emulator development commands |
| 1.4 | 2026-06-25 | Separated user and developer content: moved Publish, Development, and developer install/update paths to docs/development.md; simplified Architecture and Project Status; added development.md to Documentation |

---

Copyright (c) 2025 William Watson. This work is licensed under the MIT License.
