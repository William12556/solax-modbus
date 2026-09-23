Created: 2026 June 17

# Project Context

---

## 1.0 Project

**Name:** solax-modbus
**Description:** Read-only Modbus TCP monitor for Solax X3 Hybrid 6.0-D inverters, with a console display, a web UI and SQLite history.

**Technology stack:** Python 3.9+ | pymodbus (>=3.11, <4); standard library `http.server`, `sqlite3`, `threading`
**Target platform:** Raspberry Pi / Debian Linux (installed to `/opt/solax-monitor/`, optional systemd service); macOS for development against the emulator

---

## 2.0 Commands

| Action | Command |
|---|---|
| Install (dev) | `pip install -e .[dev]` |
| Install (Pi) | `sudo ./bin/install.sh [version] [--ip <INVERTER-IP>]` |
| Test | `pytest tests/` |
| Lint | n/a (none configured) |
| Run | `solax-monitor <INVERTER-IP>` (web UI on port 8181; `--no-serve` disables it) |
| Emulator | `python3 src/tools/emulator/solax_emulator.py --port 5020`, then `solax-monitor 127.0.0.1 --port 5020` |
| Build | `./bin/build.sh` |
| Release | `./bin/release.sh` (requires authenticated `gh` CLI) |

---

## 3.0 Code Style

- PEP 8
- Read-only Modbus access; no register writes to the inverter
- Offline operation; no cloud dependencies
- Packages under `src/solax_modbus/`: `data` (SQLite storage), `presentation` (HTTP server, `templates/`), `main.py` (CLI)

---

## 4.0 Repository Conventions

**Branches:** `main` only; no feature branches in use.
**Commits:** conventional commits with optional scope (`feat(data):`, `fix(config):`, `docs:`, `chore:`); cycle closures cite the change UUID.

---

## 5.0 Governance

| Artifact | Location |
|---|---|
| Governance | `ai/governance.md` |
| Designs | `ai/workspace/design/` |
| Changes | `ai/workspace/change/` |
| Prompts | `ai/workspace/prompt/` |
| Issues | `ai/workspace/issues/` |
| Reports | `ai/workspace/report/` |

---

## Version History

| Version | Date | Description |
|---|---|---|
| 0.1 | 2026-06-17 | Initial template |
| 1.0 | 2026-09-23 | Project context filled in (solax-modbus) |

---

Copyright (c) 2026 William Watson. MIT License.
