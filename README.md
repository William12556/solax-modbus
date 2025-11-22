# Solax Modbus Monitoring System

Real-time monitoring and control system for Solax X3 Hybrid 6.0-D solar inverters using Modbus TCP protocol.

## Features

- Direct Modbus TCP communication (no cloud dependencies)
- Multi-inverter support (up to 100 units)
- Time-series data storage (InfluxDB)
- Configurable alerting (email, SMS, webhook)
- REST API for integration
- Battery management and scheduling
- Real-time telemetry acquisition

## Quick Start

### Prerequisites

- Python 3.11+
- InfluxDB 2.7+
- Debian 12 (Bookworm) or later (recommended)
- Network access to Solax inverters (Modbus TCP port 502)

### Installation

#### Option 1: Git Clone

```bash
# Clone repository
git clone https://github.com/username/solax-modbus.git
cd solax-modbus

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

#### Option 2: Manual Installation (No Git Required)

```bash
# Download and extract release archive
wget https://github.com/username/solax-modbus/archive/refs/tags/v1.0.0.tar.gz
tar -xzf v1.0.0.tar.gz
cd solax-modbus-1.0.0

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies manually
pip install pymodbus>=3.5.0
pip install influxdb-client>=1.38.0
pip install pyyaml>=6.0
pip install requests>=2.31.0
pip install pytest>=7.4.0
```

**Alternative: Direct File Transfer**

If internet access is limited:

```bash
# On source machine with internet:
# Download dependencies
pip download -r requirements.txt -d ./packages

# Transfer entire directory to target machine via USB/SCP
# Then on target machine:
cd solax-modbus
python3 -m venv venv
source venv/bin/activate
pip install --no-index --find-links=./packages -r requirements.txt
```

### Configuration

```bash
# Copy configuration template
cp config.yaml.example config.yaml

# Edit configuration (set inverter IP, database credentials)
nano config.yaml
```

Minimum configuration:

```yaml
database:
  host: localhost
  port: 8086
  database: solar_monitoring

inverters:
  - id: inv001
    host: 192.168.1.100
    port: 502
    unit_id: 1
    poll_interval: 5
```

### Run

```bash
# Development
python src/main.py

# Production (systemd)
sudo systemctl enable solax-monitor
sudo systemctl start solax-monitor
```

### Verify

```bash
# Check health
curl http://localhost:8080/api/v1/health

# View telemetry
curl http://localhost:8080/api/v1/inverters/inv001/telemetry
```

## Documentation

- [Software Design Specification](<docs/specifications/solax-modbus-software-design-specification.md>)
- [API Reference](<docs/api/README.md>)
- [Architecture](<docs/architecture/README.md>)

## Architecture

```
Monitoring Server ──Modbus TCP──> Solax Inverters
       │
       ├──> InfluxDB (time-series data)
       ├──> Alert Services (email/SMS)
       └──> REST API (port 8080)
```

## System Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| CPU | Quad-core ARM | Quad-core x86_64 |
| RAM | 4GB | 8GB |
| Storage | 64GB | 128GB SSD |
| Network | 100 Mbps | 1 Gbps |

## Support

- Issues: https://github.com/username/solax-modbus/issues
- Documentation: `docs/` directory

## Important Notice
This software is currently very unproven and in early development stages. The implementation is experimental in nature, serving as a learning exercise in AI-assisted development workflows, protocol-driven project management, and cross-platform embedded systems development. **Actual fitness for purpose is not guaranteed.**
## License

MIT License - see [LICENSE](<LICENSE>) file.

---

Copyright (c) 2025 William Watson. This work is licensed under the MIT License.
