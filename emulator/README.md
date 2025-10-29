Created: 2025 October 29

# Solax Inverter Modbus TCP Emulator

## Overview

Self-contained Modbus TCP server emulating a Solax X3 Hybrid 6.0-D inverter for testing and development without physical hardware access.

## Features

- **Modbus TCP Server** on port 502
- **Input Registers** (telemetry - read-only)
- **Holding Registers** (configuration - read/write)
- **Dynamic Simulation**: PV power varies by time of day, battery SOC changes
- **Realistic Values**: Grid voltage, PV generation, battery charge/discharge
- **Simple Configuration**: Hardcoded constants at file start

## Requirements

```bash
pip install pymodbus
```

## Usage

### Start Emulator

```bash
sudo python3 solax_emulator.py
```

**Note**: Port 502 requires root/admin privileges. To use unprivileged port:

```python
# Edit solax_emulator.py
MODBUS_PORT = 5020  # Change from 502
```

### Test Connection

```python
from pymodbus.client import ModbusTcpClient

client = ModbusTcpClient('localhost', port=502)
client.connect()

# Read grid voltage (register 0x0000)
result = client.read_input_registers(0x0000, 1, slave=1)
voltage = result.registers[0] / 10.0  # Scale: 0.1V
print(f"Grid voltage: {voltage}V")

# Read battery SOC (register 0x001D)
result = client.read_input_registers(0x001D, 1, slave=1)
soc = result.registers[0]
print(f"Battery SOC: {soc}%")

client.close()
```

## Configuration

Edit constants at the beginning of `solax_emulator.py`:

```python
# Network
MODBUS_PORT = 502

# Specifications
PV1_MAX_POWER = 3300  # Watts
BATTERY_CAPACITY = 10000  # Watt-hours
BATTERY_VOLTAGE = 51.2  # Volts

# Initial State
INITIAL_BATTERY_SOC = 75  # Percent
INITIAL_RUN_MODE = 2  # Normal operation

# Simulation
UPDATE_INTERVAL = 1.0  # Seconds
BATTERY_CHARGE_RATE = 500  # Watts
```

## Register Map

### Input Registers (Read-Only)

| Address | Field | Scale | Unit |
|---------|-------|-------|------|
| 0x0000 | Grid Voltage Phase R | 0.1 | V |
| 0x0001 | Grid Voltage Phase S | 0.1 | V |
| 0x0002 | Grid Voltage Phase T | 0.1 | V |
| 0x0009 | PV1 Voltage | 0.1 | V |
| 0x000A | PV2 Voltage | 0.1 | V |
| 0x000B | PV1 Current | 0.1 | A |
| 0x000C | PV2 Current | 0.1 | A |
| 0x0014 | Battery Voltage | 0.1 | V |
| 0x0015 | Battery Current | 0.1 | A |
| 0x0016 | Battery Power | 1 | W |
| 0x001C | Battery Temperature | 1 | Â°C |
| 0x001D | Battery SOC | 1 | % |
| 0x0020 | Feedin Power | 1 | W |
| 0x0047 | Run Mode | 1 | enum |

### Holding Registers (Read/Write)

| Address | Field | Unit |
|---------|-------|------|
| 0x001F | Operating Mode | enum |
| 0x0020 | Charge Start Hour | hour |
| 0x0021 | Charge Start Minute | minute |
| 0x0028 | Charge Power Limit | W |
| 0x0029 | Discharge Power Limit | W |

## Dynamic Behavior

- **PV Power**: Sine curve based on hour (peak at noon, zero at night)
- **Battery Charging**: When PV > 1000W and SOC < 100%
- **Battery Discharging**: When PV < 500W and SOC > 10%
- **Temperature**: Increases with high PV power and battery activity

## Simulation Logic

```
6:00 AM  → PV starts generating
12:00 PM → Peak PV generation
6:00 PM  → PV generation stops
Night    → Battery may discharge if needed
```

## Troubleshooting

**Permission denied (port 502)**:
- Run with `sudo` or change `MODBUS_PORT` to >1024

**Connection refused**:
- Check firewall: `sudo ufw allow 502/tcp`
- Verify emulator is running: `netstat -an | grep 502`

**No data updates**:
- Check logs for errors
- Verify `UPDATE_INTERVAL` is set
- Ensure state update thread is running

## Architecture

```
┌─────────────────────────────┐
│  Modbus TCP Server (502)   │
└──────────┬──────────────────┘
           │
           ├─► Input Registers (Telemetry)
           │   └─► Dynamic updates (1s interval)
           │
           └─► Holding Registers (Config)
               └─► Read/Write support
```

---

**Copyright**: Copyright (c) 2025 William Watson. This work is licensed under the MIT License.
