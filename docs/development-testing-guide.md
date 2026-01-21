# Development Testing Guide

Created: 2025 January 21

---

## Table of Contents

- [Overview](<#overview>)
- [Requirements](<#requirements>)
- [Raspberry Pi Deployment](<#raspberry pi deployment>)
  - [Installation](<#installation>)
  - [Starting the Emulator](<#starting the emulator>)
  - [Verification](<#verification>)
- [Testing Workflow](<#testing workflow>)
  - [Basic Testing](<#basic testing>)
  - [Extended Testing](<#extended testing>)
- [Emulator Behavior](<#emulator behavior>)
- [Troubleshooting](<#troubleshooting>)
- [Version History](<#version history>)

---

## Overview

The solax-modbus emulator enables development and testing without physical inverter hardware. It simulates a Solax X3 Hybrid 6.0-D inverter with dynamic PV generation and battery state changes.

[Return to Table of Contents](<#table of contents>)

---

## Requirements

- Raspberry Pi with Debian 12 (Bookworm)
- Python 3.9 or higher
- Root privileges (port 502 requires sudo)

[Return to Table of Contents](<#table of contents>)

---

## Raspberry Pi Deployment

### Installation

Deploy emulator to Raspberry Pi:

```bash
# On development machine:
scp /path/to/solax-modbus/src/solax_modbus/emulator/solax_emulator.py admin@<pi-ip>:/tmp/
```

```bash
# On Raspberry Pi:
sudo mkdir -p /opt/solax_emulator
sudo mv /tmp/solax_emulator.py /opt/solax_emulator/
sudo chown -R admin:admin /opt/solax_emulator
cd /opt/solax_emulator
python3 -m venv venv
source venv/bin/activate
pip install pymodbus
```

[Return to Table of Contents](<#table of contents>)

### Starting the Emulator

```bash
cd /opt/solax_emulator
sudo venv/bin/python solax_emulator.py
```

Expected output:

```
============================================================
Solax X3 Hybrid Inverter Modbus TCP Emulator
============================================================
Host: 0.0.0.0
Port: 502
Unit ID: 1
PV Capacity: 6600W
Battery: 10000Wh @ 51.2V
Initial SOC: 75%
============================================================
State update thread started
Starting Modbus TCP server...
Press Ctrl+C to stop
```

[Return to Table of Contents](<#table of contents>)

### Verification

Verify emulator is running:

```bash
# Check if port 502 is listening
sudo netstat -an | grep 502

# Expected output:
tcp4       0      0  *.502                  *.*                    LISTEN
```

[Return to Table of Contents](<#table of contents>)

---

## Testing Workflow

### Basic Testing

1. **Start Emulator**:
   ```bash
   cd /opt/solax_emulator
   sudo venv/bin/python solax_emulator.py
   ```

2. **Run Monitor** (separate SSH session):
   ```bash
   solax-monitor --host 127.0.0.1 --port 502 --interval 5
   ```

3. **Observe Output**:
   - PV power varies based on simulated time of day
   - Battery SOC changes based on PV generation
   - Temperature values adjust dynamically

4. **Stop Testing**:
   - Press `Ctrl+C` in both sessions

[Return to Table of Contents](<#table of contents>)

### Extended Testing

Test longer scenarios to observe state transitions:

```bash
# Run for 1 hour with 10-second updates
solax-monitor --host 127.0.0.1 --interval 10 --duration 3600
```

Observe:
- Battery charging during high PV periods (simulated midday)
- Battery discharging during low PV periods (simulated night)
- Temperature increases with high PV generation

[Return to Table of Contents](<#table of contents>)

---

## Emulator Behavior

### PV Generation Pattern

- **06:00-18:00**: Sinusoidal power curve (peak at 12:00)
- **Peak Power**: 3300W per string (6600W total)
- **Variation**: ±10% random fluctuation
- **Night (18:00-06:00)**: Zero generation

### Battery Simulation

- **Capacity**: 10000Wh @ 51.2V
- **Initial SOC**: 75%
- **Charge Rate**: 500W when PV > 1000W and SOC < 100%
- **Discharge Rate**: 300W when PV < 500W and SOC > 10%
- **Temperature**: Increases to 30°C when SOC > 90%

### Grid Interaction

- **Voltage**: 230V per phase (nominal)
- **Frequency**: 50Hz
- **Power Flow**: Simplified export/import model
- **Feed-in**: Calculated from PV surplus

### Update Cycle

State updates every 1.0 seconds with:
- PV power recalculation
- Battery SOC adjustment
- Temperature modeling
- Register value refresh

[Return to Table of Contents](<#table of contents>)

---

## Troubleshooting

### Emulator Won't Start

**Problem**: Port 502 already in use

**Solution**:
```bash
# Find process using port 502
sudo lsof -i :502

# Kill the process
sudo kill -9 <PID>
```

**Problem**: Permission denied on port 502

**Solution**: Ensure using sudo when launching emulator (ports < 1024 require root)

### Monitor Connection Failed

**Problem**: "Connection refused" error

**Verification**:
```bash
# Verify emulator is running
sudo netstat -an | grep 502
```

**Solution**:
- Ensure emulator started successfully with sudo
- Verify host/port parameters match emulator configuration

### Unexpected Values

**Problem**: PV power always zero

**Cause**: Emulator uses system time for PV simulation

**Solution**: 
- Run during daylight hours (06:00-18:00 local time)
- Or modify emulator time calculations for testing

[Return to Table of Contents](<#table of contents>)

---

## Version History

| Version | Date | Description |
|---------|------|-------------|
| 1.0 | 2025-01-21 | Initial creation |
| 1.1 | 2025-01-21 | Added Raspberry Pi standalone deployment |
| 1.2 | 2025-01-21 | Removed local development deployment |

---

## Copyright

Copyright (c) 2025 William Watson. This work is licensed under the MIT License.

---

[Return to Table of Contents](<#table of contents>)
