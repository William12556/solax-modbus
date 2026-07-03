 # Solax Modbus Monitoring System

Real-time monitoring system for Solax X3 Hybrid 6.0-D solar inverters using Modbus TCP protocol.

## Table of Contents

- [1.0 Features](<#1.0-features>)
- [2.0 Install — Raspberry Pi Linux](<#2.0-install--raspberry-pi-linux>)
- [3.0 Verify](<#3.0-verify>)
- [4.0 Web UI](<#4.0-web-ui>)
- [5.0 Updates](<#5.0-updates>)
- [6.0 Documentation](<#6.0-documentation>)
- [7.0 License](<#7.0-license>)

---

## 1.0 Features

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

## 2.0 Install — Raspberry Pi Linux

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

## 3.0 Verify

Register `solax-monitor` as a systemd service before verifying; see the [Guide](docs/guide.md) for service configuration.

```bash
sudo systemctl status solax-monitor
sudo journalctl -u solax-monitor -f
```

[Return to Table of Contents](<#table-of-contents>)

---

## 4.0 Web UI

Optional HTTP interface providing live telemetry in a browser, alongside the console display.

**Enable:**

```bash
solax-monitor <INVERTER-IP> --serve
```

**Optional flags:**

| Flag | Purpose | Default |
|---|---|---|
| `--http-port <N>` | HTTP server port | 8080 |
| `--allow <CIDR>` | Restrict access to a network (repeatable) | RFC 1918 private ranges + link-local |

**Access:**

```
http://<pi-host-or-ip>:8080/
```

Dashboard refreshes automatically every 5 seconds. Raw telemetry is available at `/api/telemetry` (JSON).

Source-IP filtering restricts by network address; it is not authentication. Keep the port off the public internet.

[Return to Table of Contents](<#table-of-contents>)

---

## 5.0 Updates

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

## 6.0 Documentation

This README covers installation and basic operation. For service configuration, build and release, local development, testing, architecture, and troubleshooting, see the [Guide](docs/guide.md).

- [Guide](docs/guide.md) — Installation, configuration, development, and troubleshooting
- [Design Documents](ai/workspace/design/) — System architecture and component specifications
- [Test Documentation](ai/workspace/test/) — Test plans and results

[Return to Table of Contents](<#table-of-contents>)

---

## 7.0 License

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
| 1.5 | 2026-06-25 | Removed macOS as installation target: deleted Apple macOS install section and TOC entry, macOS system-requirements row, and macOS manual-execution status line. Deployment target is Raspberry Pi / Linux only. |
| 1.6 | 2026-07-02 | Added section numbering (1.0–10.0) to all headings and TOC. Added Web UI section (5.0): --serve, --http-port, --allow usage. |
| 1.7 | 2026-07-03 | Simplified to exclusively user-facing content. Removed Configure Service (3.0), Architecture (8.0), and Project Status (9.0); migrated to docs/guide.md §10–§11. Renumbered remaining sections (1.0–7.0). Expanded Documentation section note pointing to Guide for developer and extended reference content. |

---

Copyright (c) 2025 William Watson. This work is licensed under the MIT License.
