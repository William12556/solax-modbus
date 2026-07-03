# Solax Inverter Modbus TCP Emulator

Standalone Modbus TCP server emulating a Solax X3 Hybrid 6.0-D
inverter for offline development and testing. Requires only
`pymodbus` — no project package install.

Full usage, register map, and behavior: see
[docs/guide.md §6.2](<../../../docs/guide.md#62-emulator>).

```bash
pip install pymodbus
python3 solax_emulator.py --port 5020
```

---

Copyright (c) 2025 William Watson. This work is licensed under the MIT License.
