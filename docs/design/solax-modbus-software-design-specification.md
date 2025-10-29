# Software Design Specification
## Solax X3 Hybrid Inverter Monitoring System

**Document Type:** Software Design Specification  
**Version:** 1.0  
**Date:** October 25, 2025  
**Classification:** Technical Specification  
**Status:** Draft

---

## 1. Introduction

### 1.1 Purpose

This document specifies the software design for a real-time monitoring and control system for Solax X3 Hybrid 6.0-D solar inverters. The system employs Modbus TCP protocol for direct device communication, eliminating dependencies on cloud services or proprietary APIs.

### 1.2 Scope

The specification covers:
- Data acquisition subsystem
- Protocol interface layer
- Data storage and persistence
- Monitoring and alerting capabilities
- Control and configuration management
- Multi-inverter support architecture

Out of scope:
- Hardware selection and procurement
- Physical network infrastructure design
- User interface implementation details
- Cloud integration strategies

### 1.3 Target Audience

- Software engineers implementing the system
- System architects reviewing design decisions
- Quality assurance personnel developing test plans
- Operations staff deploying and maintaining the system

### 1.4 Document Conventions

- **SHALL**: Mandatory requirement
- **SHOULD**: Recommended requirement
- **MAY**: Optional requirement
- Register addresses use hexadecimal notation (0x prefix)
- Data types follow IEC 61131-3 conventions

---

## 2. System Overview

### 2.1 System Context

```
┌──────────────────────────────────────────────────────────────┐
│                     External Systems                          │
│  ┌───────────┐    ┌──────────────┐    ┌─────────────┐       │
│  │  Solax    │    │ Time-Series  │    │   Alert     │       │
│  │ Inverters │    │   Database   │    │  Services   │       │
│  └─────┬─────┘    └──────┬───────┘    └──────┬──────┘       │
└────────┼──────────────────┼──────────────────┼──────────────┘
         │                  │                  │
         │ Modbus TCP/502   │ HTTP/3000       │ SMTP/587
         │                  │                  │
    ┌────┴──────────────────┴──────────────────┴─────┐
    │      Solax Monitoring System (Core)             │
    │  ┌───────────────────────────────────────┐     │
    │  │  Protocol Interface Layer             │     │
    │  ├───────────────────────────────────────┤     │
    │  │  Data Processing Engine               │     │
    │  ├───────────────────────────────────────┤     │
    │  │  Control & Configuration Manager      │     │
    │  ├───────────────────────────────────────┤     │
    │  │  Monitoring & Alerting Subsystem      │     │
    │  └───────────────────────────────────────┘     │
    └─────────────────────────────────────────────────┘
```

### 2.2 High-Level Architecture

The system implements a modular architecture with clear separation of concerns:

**Layer 1: Protocol Interface**
- Modbus TCP client implementation
- Connection management and retry logic
- Register read/write operations
- Data type conversion and validation

**Layer 2: Data Processing**
- Register decoding and interpretation
- Unit conversion and scaling
- Data quality validation
- State machine management

**Layer 3: Business Logic**
- Energy calculations
- Statistical aggregation
- Threshold monitoring
- Schedule management

**Layer 4: Integration**
- Time-series database persistence
- Alert notification dispatch
- Configuration management
- Multi-inverter coordination

### 2.3 Design Principles

1. **Modularity**: Independent, replaceable components
2. **Fail-Safe**: Graceful degradation under fault conditions
3. **Observability**: Comprehensive logging and metrics
4. **Idempotency**: Repeatable operations without side effects
5. **Minimal Dependencies**: Reduce external library requirements

---

## 3. Functional Requirements

### 3.1 Data Acquisition

**REQ-DA-001**: The system SHALL poll inverter telemetry at configurable intervals (minimum 1 second).

**REQ-DA-002**: The system SHALL read the following data categories:
- Grid parameters (voltage, current, power, frequency per phase)
- Solar PV metrics (voltage, current, power per MPPT channel)
- Battery status (voltage, current, power, SOC, temperature)
- System status (run mode, temperature, error codes)
- Energy accounting (daily and cumulative statistics)

**REQ-DA-003**: The system SHALL validate all received data against expected ranges and flag anomalies.

**REQ-DA-004**: The system SHALL handle connection failures with exponential backoff retry (max 5 attempts).

**REQ-DA-005**: The system SHALL timeout Modbus operations after 1 second per protocol specification.

### 3.2 Data Processing

**REQ-DP-001**: The system SHALL convert raw register values to engineering units using documented scaling factors.

**REQ-DP-002**: The system SHALL handle signed and unsigned 16-bit integers per protocol specification.

**REQ-DP-003**: The system SHALL decode run mode enumeration values per Appendix B specification.

**REQ-DP-004**: The system SHALL calculate derived metrics:
- Total PV power (sum of MPPT channels)
- Net grid power (positive = export, negative = import)
- Battery charge/discharge rates
- System efficiency ratios

**REQ-DP-005**: The system SHALL maintain internal state for:
- Connection status
- Last successful poll timestamp
- Consecutive failure count
- Cumulative energy totals

### 3.3 Data Persistence

**REQ-PP-001**: The system SHALL store time-series data with timestamp resolution of 1 second.

**REQ-PP-002**: The system SHALL persist the following data types:
- Raw telemetry measurements
- Derived calculations
- System events and state transitions
- Configuration changes

**REQ-PP-003**: The system SHALL implement data retention policies:
- Raw data: 30 days at 1-second resolution
- Aggregated data: 1 year at 1-minute resolution
- Statistical summaries: 10 years at 1-hour resolution

**REQ-PP-004**: The system SHALL handle database connection failures gracefully with local buffering (max 1 hour).

### 3.4 Monitoring and Alerting

**REQ-MA-001**: The system SHALL detect and alert on the following conditions:
- Communication failure (>5 consecutive timeouts)
- Grid fault conditions
- Battery over-temperature (>50°C)
- Battery SOC critical (<10%)
- Inverter fault states
- Anomalous power readings

**REQ-MA-002**: The system SHALL support alert notification via:
- Email (SMTP)
- SMS (Twilio API)
- Webhook (HTTP POST)
- Local syslog

**REQ-MA-003**: The system SHALL implement alert rate limiting to prevent notification storms.

**REQ-MA-004**: The system SHALL maintain alert history with acknowledgment tracking.

### 3.5 Control and Configuration

**REQ-CC-001**: The system SHALL support read-only mode for initial deployment.

**REQ-CC-002**: The system SHALL support write operations to holding registers when enabled:
- Operating mode selection
- Charge/discharge time windows
- Battery power limits
- Grid export limits

**REQ-CC-003**: The system SHALL validate all write operations against inverter constraints before execution.

**REQ-CC-004**: The system SHALL maintain audit log of all configuration changes including:
- Timestamp
- User/process identifier
- Register address and value
- Operation result

**REQ-CC-005**: The system SHALL implement configuration rollback capability for failed operations.

### 3.6 Multi-Inverter Support

**REQ-MI-001**: The system SHALL support concurrent monitoring of multiple inverters (up to 100).

**REQ-MI-002**: Each inverter connection SHALL be managed independently with isolated failure domains.

**REQ-MI-003**: The system SHALL coordinate polling across inverters to prevent network congestion.

**REQ-MI-004**: The system SHALL aggregate data across inverters for:
- Total system generation
- Combined battery capacity
- Net grid interaction

---

## 4. Non-Functional Requirements

### 4.1 Performance

**REQ-NF-PERF-001**: The system SHALL process 99.9% of Modbus requests within 1 second under normal conditions.

**REQ-NF-PERF-002**: The system SHALL handle network latency up to 500ms without data loss.

**REQ-NF-PERF-003**: The system SHALL support polling intervals as low as 1 second per inverter.

**REQ-NF-PERF-004**: Memory footprint SHALL NOT exceed 512MB under typical operation (10 inverters).

**REQ-NF-PERF-005**: CPU utilization SHALL remain below 10% on Raspberry Pi 4 class hardware.

### 4.2 Reliability

**REQ-NF-REL-001**: The system SHALL achieve 99.5% uptime over 30-day periods.

**REQ-NF-REL-002**: Mean Time Between Failures (MTBF) SHALL exceed 720 hours.

**REQ-NF-REL-003**: Mean Time To Recovery (MTTR) SHALL be less than 5 minutes.

**REQ-NF-REL-004**: The system SHALL survive process crashes with automatic restart.

**REQ-NF-REL-005**: No data loss SHALL occur for buffered measurements (up to 1 hour).

### 4.3 Maintainability

**REQ-NF-MAINT-001**: Code SHALL maintain cyclomatic complexity below 15 per function.

**REQ-NF-MAINT-002**: Test coverage SHALL exceed 80% for core modules.

**REQ-NF-MAINT-003**: All public interfaces SHALL include docstring documentation.

**REQ-NF-MAINT-004**: Configuration SHALL be externalized via environment variables or config files.

**REQ-NF-MAINT-005**: The system SHALL support hot-reload of configuration without restart.

### 4.4 Security

**REQ-NF-SEC-001**: Modbus communication SHALL be isolated to dedicated VLAN or VPN.

**REQ-NF-SEC-002**: Configuration write operations SHALL require authentication.

**REQ-NF-SEC-003**: All passwords and API keys SHALL be stored encrypted at rest.

**REQ-NF-SEC-004**: The system SHALL log all security-relevant events.

**REQ-NF-SEC-005**: Network access SHALL be restricted via firewall rules (allow only required ports).

### 4.5 Scalability

**REQ-NF-SCALE-001**: The system SHALL scale linearly with number of inverters up to 100 units.

**REQ-NF-SCALE-002**: Database storage growth SHALL be predictable and bounded by retention policies.

**REQ-NF-SCALE-003**: The architecture SHALL support horizontal scaling via load balancing.

### 4.6 Usability

**REQ-NF-USE-001**: Installation SHALL require fewer than 10 manual steps.

**REQ-NF-USE-002**: Configuration SHALL use human-readable formats (YAML/TOML).

**REQ-NF-USE-003**: Error messages SHALL provide actionable diagnostic information.

**REQ-NF-USE-004**: The system SHALL provide health check endpoint for monitoring tools.

---

## 5. System Components

### 5.1 Protocol Interface Module

**Responsibilities:**
- Modbus TCP client connection management
- Register read/write operations
- Protocol-level error handling
- Connection pooling and lifecycle management

**Key Classes:**

```python
class ModbusClient:
    """
    Low-level Modbus TCP client wrapper.
    
    Encapsulates pymodbus library with retry logic and error handling.
    """
    
    def __init__(self, host: str, port: int, unit_id: int)
    def connect() -> bool
    def disconnect() -> None
    def read_input_registers(address: int, count: int) -> List[int]
    def read_holding_registers(address: int, count: int) -> List[int]
    def write_register(address: int, value: int) -> bool
    def is_connected() -> bool


class RegisterMap:
    """
    Defines Modbus register address space for Solax inverters.
    
    Provides type-safe access to register definitions including
    address, data type, scaling factor, and description.
    """
    
    def get_register_definition(name: str) -> RegisterDefinition
    def validate_address(address: int) -> bool
    def get_scaling_factor(address: int) -> float
```

**Configuration Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| host | string | required | Inverter IP address |
| port | integer | 502 | Modbus TCP port |
| unit_id | integer | 1 | Modbus unit identifier |
| timeout | float | 1.0 | Operation timeout (seconds) |
| retry_count | integer | 3 | Connection retry attempts |
| retry_delay | float | 2.0 | Delay between retries (seconds) |

### 5.2 Inverter Interface Module

**Responsibilities:**
- High-level inverter abstraction
- Data type conversion and scaling
- Register-to-field mapping
- State machine management

**Key Classes:**

```python
class SolaxInverter:
    """
    High-level interface to Solax X3 Hybrid inverter.
    
    Provides domain-specific methods for reading telemetry
    and controlling inverter operation.
    """
    
    def __init__(self, client: ModbusClient)
    def get_grid_metrics() -> GridMetrics
    def get_pv_metrics() -> PVMetrics
    def get_battery_metrics() -> BatteryMetrics
    def get_system_status() -> SystemStatus
    def get_energy_statistics() -> EnergyStats
    def set_operating_mode(mode: OperatingMode) -> bool
    def set_charge_window(start: time, end: time) -> bool


class InverterState:
    """
    Maintains current state of inverter.
    
    Tracks connection status, last update time, error conditions,
    and operational mode.
    """
    
    connection_status: ConnectionStatus
    last_update: datetime
    consecutive_failures: int
    current_mode: RunMode
    active_faults: List[FaultCode]
```

**Data Structures:**

```python
@dataclass
class GridMetrics:
    """Three-phase grid electrical parameters."""
    voltage_r: float  # Volts
    voltage_s: float  # Volts
    voltage_t: float  # Volts
    current_r: float  # Amperes
    current_s: float  # Amperes
    current_t: float  # Amperes
    power_r: float    # Watts
    power_s: float    # Watts
    power_t: float    # Watts
    frequency: float  # Hertz
    timestamp: datetime


@dataclass
class BatteryMetrics:
    """Battery system parameters."""
    voltage: float        # Volts
    current: float        # Amperes (positive = charge)
    power: int           # Watts (positive = charge)
    soc: int            # State of charge (%)
    temperature: int     # Celsius
    bms_status: bool    # BMS communication active
    capacity: int       # Watt-hours
    timestamp: datetime
```

### 5.3 Data Processing Module

**Responsibilities:**
- Raw data validation
- Derived metric calculation
- Unit conversion
- Data quality assessment

**Key Classes:**

```python
class DataValidator:
    """
    Validates telemetry data against expected ranges.
    
    Flags out-of-range values, detects sensor failures,
    and identifies implausible measurements.
    """
    
    def validate_metrics(metrics: Any) -> ValidationResult
    def check_range(value: float, min_val: float, max_val: float) -> bool
    def detect_anomalies(history: List[float], current: float) -> bool


class MetricsCalculator:
    """
    Computes derived metrics from raw telemetry.
    
    Calculates totals, averages, efficiency ratios,
    and energy flows.
    """
    
    def calculate_total_pv_power(pv_metrics: PVMetrics) -> float
    def calculate_net_grid_power(grid_import: float, grid_export: float) -> float
    def calculate_system_efficiency(input_power: float, output_power: float) -> float
    def calculate_daily_totals(measurements: List[Measurement]) -> DailyStats
```

### 5.4 Storage Module

**Responsibilities:**
- Time-series database interface
- Data buffering during outages
- Retention policy enforcement
- Query interface for historical data

**Key Classes:**

```python
class TimeSeriesStore:
    """
    Interface to time-series database.
    
    Abstracts database-specific operations and provides
    unified API for data persistence.
    """
    
    def __init__(self, connection_string: str)
    def write_measurement(measurement: Measurement) -> bool
    def write_batch(measurements: List[Measurement]) -> int
    def query(start: datetime, end: datetime, fields: List[str]) -> DataFrame
    def get_latest(inverter_id: str) -> Measurement
    

class DataBuffer:
    """
    In-memory buffer for measurements during database outages.
    
    Implements circular buffer with configurable size and
    automatic flush on reconnection.
    """
    
    def __init__(self, max_size: int, max_age: timedelta)
    def add(measurement: Measurement) -> None
    def flush() -> List[Measurement]
    def is_full() -> bool
```

**Database Schema (InfluxDB):**

```
measurement: inverter_telemetry
tags:
  - inverter_id: string
  - location: string
fields:
  - pv_power_total: float
  - pv1_voltage: float
  - pv1_current: float
  - pv2_voltage: float
  - pv2_current: float
  - battery_voltage: float
  - battery_current: float
  - battery_power: int
  - battery_soc: int
  - battery_temperature: int
  - grid_voltage_r: float
  - grid_current_r: float
  - grid_power_r: float
  - feedin_power: int
  - run_mode: int
timestamp: nanosecond precision
```

### 5.5 Monitoring Module

**Responsibilities:**
- Threshold-based alerting
- Anomaly detection
- Alert notification dispatch
- Alert rate limiting and deduplication

**Key Classes:**

```python
class AlertManager:
    """
    Manages alert conditions and notification dispatch.
    
    Evaluates thresholds, triggers notifications, and
    maintains alert state.
    """
    
    def __init__(self, config: AlertConfig)
    def evaluate_conditions(metrics: Measurement) -> List[Alert]
    def dispatch_alert(alert: Alert) -> bool
    def acknowledge_alert(alert_id: str) -> bool
    def get_active_alerts() -> List[Alert]


class NotificationDispatcher:
    """
    Sends alert notifications via multiple channels.
    
    Supports email, SMS, webhooks, and logging.
    """
    
    def send_email(alert: Alert, recipients: List[str]) -> bool
    def send_sms(alert: Alert, phone_numbers: List[str]) -> bool
    def send_webhook(alert: Alert, url: str) -> bool
    def log_alert(alert: Alert) -> None
```

**Alert Conditions:**

| Condition | Threshold | Severity | Action |
|-----------|-----------|----------|--------|
| Communication failure | 5 consecutive timeouts | Critical | Email + SMS |
| Battery low | SOC < 10% | Warning | Email |
| Battery critical | SOC < 5% | Critical | Email + SMS |
| Battery over-temp | Temperature > 50°C | Critical | Email + SMS |
| Grid fault | Run mode = Fault | Critical | Email + SMS |
| Inverter over-temp | Temperature > 75°C | Warning | Email |

### 5.6 Control Module

**Responsibilities:**
- Configuration write operations
- Operating mode management
- Schedule management
- Audit logging

**Key Classes:**

```python
class InverterController:
    """
    Manages write operations to inverter configuration.
    
    Validates requests, executes writes, and maintains
    audit trail.
    """
    
    def __init__(self, inverter: SolaxInverter, auditor: AuditLog)
    def set_operating_mode(mode: OperatingMode) -> ControlResult
    def set_charge_schedule(schedule: ChargeSchedule) -> ControlResult
    def set_power_limit(limit: int) -> ControlResult
    def rollback_last_change() -> bool


class ScheduleManager:
    """
    Manages time-of-use schedules for battery operation.
    
    Automatically applies schedule changes at configured times.
    """
    
    def __init__(self, schedule_config: ScheduleConfig)
    def add_schedule(schedule: Schedule) -> bool
    def remove_schedule(schedule_id: str) -> bool
    def get_current_schedule() -> Optional[Schedule]
    def execute_schedules() -> None
```

### 5.7 Multi-Inverter Coordinator

**Responsibilities:**
- Manage multiple inverter connections
- Coordinate polling to prevent network congestion
- Aggregate data across inverters
- Handle per-inverter failures independently

**Key Classes:**

```python
class InverterPool:
    """
    Manages collection of inverter instances.
    
    Provides concurrent polling with backpressure control
    and aggregated data access.
    """
    
    def __init__(self, inverter_configs: List[InverterConfig])
    def add_inverter(config: InverterConfig) -> str
    def remove_inverter(inverter_id: str) -> bool
    def poll_all() -> Dict[str, Measurement]
    def get_aggregate_metrics() -> AggregateMetrics


class PollingCoordinator:
    """
    Schedules and coordinates polling across inverters.
    
    Implements rate limiting and staggered polling to
    prevent network saturation.
    """
    
    def __init__(self, max_concurrent: int, poll_interval: timedelta)
    def schedule_poll(inverter_id: str) -> None
    def get_next_poll_time(inverter_id: str) -> datetime
```

---

## 6. Interface Specifications

### 6.1 Modbus Register Map

**Input Registers (Function Code 0x04):**

| Address | Field | Type | Scale | Unit | Access |
|---------|-------|------|-------|------|--------|
| 0x0000 | Grid Voltage Phase R | uint16 | 0.1 | V | R |
| 0x0001 | Grid Voltage Phase S | uint16 | 0.1 | V | R |
| 0x0002 | Grid Voltage Phase T | uint16 | 0.1 | V | R |
| 0x0003 | Grid Current Phase R | uint16 | 0.1 | A | R |
| 0x0004 | Grid Current Phase S | uint16 | 0.1 | A | R |
| 0x0005 | Grid Current Phase T | uint16 | 0.1 | A | R |
| 0x0006 | Grid Power Phase R | int16 | 1 | W | R |
| 0x0007 | Grid Power Phase S | int16 | 1 | W | R |
| 0x0008 | Grid Power Phase T | int16 | 1 | W | R |
| 0x0009 | PV1 Voltage | uint16 | 0.1 | V | R |
| 0x000A | PV2 Voltage | uint16 | 0.1 | V | R |
| 0x000B | PV1 Current | uint16 | 0.1 | A | R |
| 0x000C | PV2 Current | uint16 | 0.1 | A | R |
| 0x0014 | Battery Voltage | uint16 | 0.1 | V | R |
| 0x0015 | Battery Current | int16 | 0.1 | A | R |
| 0x0016 | Battery Power | int16 | 1 | W | R |
| 0x001C | Battery Temperature | int16 | 1 | °C | R |
| 0x001D | Battery SOC | uint16 | 1 | % | R |
| 0x0020 | Feedin Power | int16 | 1 | W | R |
| 0x0047 | Run Mode | uint16 | 1 | enum | R |

**Holding Registers (Function Code 0x03):**

| Address | Field | Type | Scale | Unit | Access |
|---------|-------|------|-------|------|--------|
| 0x001F | Operating Mode | uint16 | 1 | enum | RW |
| 0x0020 | Charge Start Hour | uint16 | 1 | hour | RW |
| 0x0021 | Charge Start Minute | uint16 | 1 | minute | RW |
| 0x0022 | Charge End Hour | uint16 | 1 | hour | RW |
| 0x0023 | Charge End Minute | uint16 | 1 | minute | RW |
| 0x0024 | Discharge Start Hour | uint16 | 1 | hour | RW |
| 0x0025 | Discharge Start Minute | uint16 | 1 | minute | RW |
| 0x0026 | Discharge End Hour | uint16 | 1 | hour | RW |
| 0x0027 | Discharge End Minute | uint16 | 1 | minute | RW |
| 0x0028 | Charge Power Limit | uint16 | 1 | W | RW |
| 0x0029 | Discharge Power Limit | uint16 | 1 | W | RW |

**Enumeration Values:**

*Operating Mode (0x001F):*
- 0: Self-use mode
- 1: Feed-in priority
- 2: Backup mode
- 3: Manual mode

*Run Mode (0x0047):*
- 0: Waiting
- 1: Checking
- 2: Normal
- 3: Fault
- 4: Permanent fault
- 5: Update mode
- 6: Off-grid waiting
- 7: Off-grid
- 8: Self-testing
- 9: Idle
- 10: Standby

### 6.2 REST API Specification

**Base URL:** `http://localhost:8080/api/v1`

**Authentication:** Bearer token (JWT)

**Endpoints:**

```
GET /inverters
    - Returns list of configured inverters
    - Response: 200 OK, JSON array of inverter objects

GET /inverters/{inverter_id}/telemetry
    - Returns current telemetry for specified inverter
    - Parameters:
        - inverter_id: string (path)
    - Response: 200 OK, JSON telemetry object

GET /inverters/{inverter_id}/history
    - Returns historical telemetry data
    - Parameters:
        - inverter_id: string (path)
        - start: ISO8601 datetime (query)
        - end: ISO8601 datetime (query)
        - fields: comma-separated list (query)
    - Response: 200 OK, JSON array of measurements

POST /inverters/{inverter_id}/control
    - Execute control command
    - Parameters:
        - inverter_id: string (path)
    - Request body:
        {
            "command": "set_mode",
            "parameters": {
                "mode": "self_use"
            }
        }
    - Response: 200 OK, JSON result object

GET /alerts
    - Returns active alerts
    - Response: 200 OK, JSON array of alert objects

POST /alerts/{alert_id}/acknowledge
    - Acknowledge an alert
    - Parameters:
        - alert_id: string (path)
    - Response: 200 OK

GET /health
    - System health check
    - Response: 200 OK
        {
            "status": "healthy",
            "database": "connected",
            "inverters": {
                "total": 2,
                "connected": 2,
                "disconnected": 0
            }
        }
```

### 6.3 Configuration File Format

**Format:** YAML

**Location:** `/etc/solax-monitor/config.yaml`

**Schema:**

```yaml
# System configuration
system:
  log_level: INFO
  log_file: /var/log/solax-monitor/app.log
  pid_file: /var/run/solax-monitor.pid
  
# Database configuration
database:
  type: influxdb
  host: localhost
  port: 8086
  database: solar_monitoring
  username: admin
  password: ${INFLUX_PASSWORD}
  retention_policy:
    raw_data: 30d
    aggregated_1m: 365d
    aggregated_1h: 3650d

# Inverter configuration
inverters:
  - id: inv001
    name: "Main Inverter"
    host: 192.168.1.100
    port: 502
    unit_id: 1
    location: "Building A"
    poll_interval: 5
    enabled: true
    
  - id: inv002
    name: "Secondary Inverter"
    host: 192.168.1.101
    port: 502
    unit_id: 1
    location: "Building B"
    poll_interval: 5
    enabled: true

# Alert configuration
alerts:
  enabled: true
  channels:
    - type: email
      smtp_host: smtp.gmail.com
      smtp_port: 587
      smtp_user: alerts@example.com
      smtp_password: ${SMTP_PASSWORD}
      recipients:
        - admin@example.com
        
    - type: sms
      provider: twilio
      account_sid: ${TWILIO_SID}
      auth_token: ${TWILIO_TOKEN}
      from_number: "+1234567890"
      to_numbers:
        - "+0987654321"
        
  conditions:
    - name: communication_failure
      severity: critical
      threshold: 5
      channels: [email, sms]
      
    - name: battery_low
      severity: warning
      threshold: 10
      channels: [email]

# Control configuration  
control:
  enabled: false
  require_authentication: true
  audit_log: /var/log/solax-monitor/audit.log
```

---

## 7. Data Flow Diagrams

### 7.1 Telemetry Acquisition Flow

```
┌──────────┐
│  Timer   │
│ Trigger  │
└────┬─────┘
     │
     ▼
┌────────────────────┐
│ Polling            │
│ Coordinator        │
└────┬───────────────┘
     │
     ▼
┌────────────────────┐     ┌──────────────┐
│ Modbus Client      │────►│  Inverter    │
│ Read Registers     │◄────│  (Modbus)    │
└────┬───────────────┘     └──────────────┘
     │
     ▼
┌────────────────────┐
│ Register Decoder   │
│ - Type conversion  │
│ - Scaling          │
│ - Validation       │
└────┬───────────────┘
     │
     ▼
┌────────────────────┐
│ Data Processor     │
│ - Calculations     │
│ - Aggregations     │
└────┬───────────────┘
     │
     ├──────────────────┬──────────────────┐
     ▼                  ▼                  ▼
┌─────────────┐   ┌─────────────┐   ┌─────────────┐
│  Database   │   │   Alert     │   │   API       │
│  Storage    │   │  Manager    │   │  Endpoint   │
└─────────────┘   └─────────────┘   └─────────────┘
```

### 7.2 Control Command Flow

```
┌──────────┐
│   API    │
│ Request  │
└────┬─────┘
     │
     ▼
┌────────────────────┐
│ Authentication     │
│ & Authorization    │
└────┬───────────────┘
     │
     ▼
┌────────────────────┐
│ Command Validator  │
│ - Range checks     │
│ - Constraint verify│
└────┬───────────────┘
     │
     ▼
┌────────────────────┐
│ Audit Logger       │
│ - Log command      │
│ - Log user         │
└────┬───────────────┘
     │
     ▼
┌────────────────────┐     ┌──────────────┐
│ Modbus Client      │────►│  Inverter    │
│ Write Register     │◄────│  (Modbus)    │
└────┬───────────────┘     └──────────────┘
     │
     ▼
┌────────────────────┐
│ Result Processor   │
│ - Verify write     │
│ - Update state     │
└────┬───────────────┘
     │
     ├──────────────────┬──────────────────┐
     ▼                  ▼                  ▼
┌─────────────┐   ┌─────────────┐   ┌─────────────┐
│  Audit      │   │   Alert     │   │   API       │
│  Database   │   │  Manager    │   │  Response   │
└─────────────┘   └─────────────┘   └─────────────┘
```

---

## 8. Security Architecture

### 8.1 Network Security

**Network Segmentation:**

```
┌─────────────────────────────────────────────────┐
│                 Management VLAN                  │
│              192.168.10.0/24                     │
│  ┌──────────────────────────────────────┐       │
│  │  Monitoring Server                    │       │
│  │  - Management access only             │       │
│  └──────────────────────────────────────┘       │
└─────────────────────┬───────────────────────────┘
                      │ Firewall
                      │ Rules: Port 502 only
┌─────────────────────┴───────────────────────────┐
│              Automation VLAN                     │
│              192.168.20.0/24                     │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐      │
│  │Inverter 1│  │Inverter 2│  │Inverter 3│      │
│  └──────────┘  └──────────┘  └──────────┘      │
└─────────────────────────────────────────────────┘
```

**Firewall Rules:**

| Source | Destination | Port | Protocol | Action |
|--------|-------------|------|----------|--------|
| Monitoring Server | Inverters | 502 | TCP | ALLOW |
| Inverters | Monitoring Server | * | * | DENY |
| Management VLAN | Monitoring Server | 22, 8080 | TCP | ALLOW |
| Internet | Monitoring Server | * | * | DENY |

### 8.2 Authentication and Authorization

**Authentication Methods:**

1. **API Access**: JWT tokens with 1-hour expiration
2. **SSH Access**: Public key authentication only
3. **Database Access**: Username/password over encrypted connection

**Authorization Levels:**

| Role | Permissions |
|------|-------------|
| Administrator | Full read/write access, configuration changes, control operations |
| Operator | Read access, limited control operations (mode changes only) |
| Viewer | Read-only access to telemetry and alerts |

### 8.3 Data Protection

**Encryption:**

- **At Rest**: Database encryption enabled
- **In Transit**: TLS 1.3 for API endpoints
- **Credentials**: Environment variables or secrets manager

**Sensitive Data Handling:**

- Passwords stored using bcrypt (cost factor 12)
- API keys rotated every 90 days
- Audit logs retain 2 years, then archived encrypted

### 8.4 Security Monitoring

**Log Events:**

- All authentication attempts (success/failure)
- All control commands
- Configuration changes
- Security policy violations
- Unusual access patterns

**Intrusion Detection:**

- Rate limiting on API endpoints (100 requests/minute per IP)
- Failed authentication lockout (5 attempts = 15-minute block)
- Anomalous network traffic detection

---

## 9. Deployment Architecture

### 9.1 Physical Deployment

**Hardware Requirements:**

| Component | Specification |
|-----------|---------------|
| CPU | ARM Cortex-A72 (quad-core) @ 1.5GHz or equivalent |
| RAM | 4GB minimum, 8GB recommended |
| Storage | 64GB microSD/eMMC minimum |
| Network | Gigabit Ethernet (required) |
| Power | 5V/3A power supply with surge protection |

**Recommended Platforms:**

- Raspberry Pi 4 Model B (4GB/8GB)
- ASUS Tinker Board 2S
- Hardkernel ODROID-N2+
- Industrial PC (for production deployments)

### 9.2 Software Stack

```
┌─────────────────────────────────────────────┐
│          Application Layer                   │
│  ┌────────────────────────────────────┐     │
│  │  Solax Monitoring System           │     │
│  │  (Python 3.11)                     │     │
│  └────────────────────────────────────┘     │
├─────────────────────────────────────────────┤
│          Service Layer                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │ systemd  │  │  nginx   │  │ InfluxDB │  │
│  │ (process)│  │ (reverse)│  │ (tsdb)   │  │
│  └──────────┘  └──────────┘  └──────────┘  │
├─────────────────────────────────────────────┤
│          Operating System                    │
│  ┌────────────────────────────────────┐     │
│  │  Ubuntu Server 24.04 LTS (ARM64)   │     │
│  └────────────────────────────────────┘     │
├─────────────────────────────────────────────┤
│          Hardware                            │
│  ┌────────────────────────────────────┐     │
│  │  Raspberry Pi 4 / Industrial PC    │     │
│  └────────────────────────────────────┘     │
└─────────────────────────────────────────────┘
```

**Dependencies:**

| Package | Version | Purpose |
|---------|---------|---------|
| Python | 3.11+ | Runtime environment |
| pymodbus | 3.5.0+ | Modbus protocol implementation |
| influxdb-client | 1.38.0+ | Time-series database client |
| pyyaml | 6.0+ | Configuration file parsing |
| requests | 2.31.0+ | HTTP client for API |
| pytest | 7.4.0+ | Testing framework |

### 9.3 Installation Procedure

**Step 1: System Preparation**

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y python3.11 python3-pip git nginx influxdb

# Create application user
sudo useradd -r -s /bin/false solax-monitor
```

**Step 2: Application Installation**

```bash
# Clone repository
git clone https://github.com/example/solax-monitor.git
cd solax-monitor

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Install application
sudo python setup.py install
```

**Step 3: Configuration**

```bash
# Copy configuration template
sudo mkdir -p /etc/solax-monitor
sudo cp config.yaml.example /etc/solax-monitor/config.yaml

# Edit configuration
sudo nano /etc/solax-monitor/config.yaml

# Set permissions
sudo chown -R solax-monitor:solax-monitor /etc/solax-monitor
```

**Step 4: Database Setup**

```bash
# Initialize InfluxDB
influx setup \
  --username admin \
  --password $INFLUX_PASSWORD \
  --org solax \
  --bucket solar_monitoring \
  --retention 30d

# Create retention policies
influx bucket create \
  --name solar_monitoring_1m \
  --retention 365d

influx bucket create \
  --name solar_monitoring_1h \
  --retention 3650d
```

**Step 5: Service Deployment**

```bash
# Install systemd service
sudo cp systemd/solax-monitor.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable solax-monitor
sudo systemctl start solax-monitor

# Verify service status
sudo systemctl status solax-monitor
```

**Step 6: Verification**

```bash
# Check application logs
sudo journalctl -u solax-monitor -f

# Verify database connectivity
influx query 'from(bucket:"solar_monitoring") |> range(start: -5m)'

# Test API endpoint
curl http://localhost:8080/api/v1/health
```

### 9.4 High Availability Configuration

**Active-Passive Setup:**

```
┌──────────────────┐      ┌──────────────────┐
│   Primary Node   │      │  Secondary Node  │
│  (Active)        │◄────►│  (Standby)       │
│  - Monitoring    │      │  - Monitoring    │
│  - Database      │      │  - Database      │
└────────┬─────────┘      └────────┬─────────┘
         │                         │
         │   Shared VIP            │
         │   192.168.10.100        │
         └─────────┬───────────────┘
                   │
                   ▼
         ┌─────────────────┐
         │   Inverters     │
         └─────────────────┘
```

**Failover Mechanism:**

- Keepalived for VIP management
- Heartbeat interval: 1 second
- Failover time: <5 seconds
- Database replication: InfluxDB clustering

---

## 10. Testing Strategy

### 10.1 Unit Testing

**Scope:**

- Individual functions and methods
- Data type conversions
- Register decoding logic
- Calculation algorithms
- Validation routines

**Framework:** pytest

**Coverage Target:** >80%

**Example Test Cases:**

```python
def test_register_scaling():
    """Verify correct scaling of register values."""
    raw_value = 2305  # 230.5V
    scaled = scale_voltage(raw_value)
    assert scaled == 230.5

def test_signed_conversion():
    """Verify signed integer conversion."""
    raw_value = 0xFFFE  # -2 in two's complement
    converted = convert_signed_int16(raw_value)
    assert converted == -2

def test_battery_power_calculation():
    """Verify battery power calculation."""
    voltage = 51.2  # V
    current = -10.0  # A (negative = discharge)
    power = calculate_battery_power(voltage, current)
    assert power == -512  # W
```

### 10.2 Integration Testing

**Scope:**

- Modbus communication with test harness
- Database read/write operations
- Alert notification delivery
- API endpoint functionality
- Multi-component interactions

**Test Environment:**

- Modbus simulator (pymodbus server)
- Test database instance
- Mock notification services

**Example Test Cases:**

```python
def test_modbus_connection():
    """Verify successful connection to Modbus device."""
    client = ModbusClient("localhost", 5020, 1)
    assert client.connect() is True

def test_data_persistence():
    """Verify measurement storage and retrieval."""
    measurement = create_test_measurement()
    store.write_measurement(measurement)
    retrieved = store.get_latest("test_inverter")
    assert retrieved.pv_power_total == measurement.pv_power_total

def test_alert_dispatch():
    """Verify alert notification delivery."""
    alert = create_test_alert(severity="critical")
    result = alert_manager.dispatch_alert(alert)
    assert result is True
    assert len(mock_email_service.sent_messages) == 1
```

### 10.3 System Testing

**Scope:**

- End-to-end functionality
- Performance under load
- Error recovery
- Configuration management
- Multi-inverter coordination

**Test Scenarios:**

| Scenario | Description | Expected Result |
|----------|-------------|-----------------|
| ST-001 | Normal operation with single inverter | Data acquired, stored, accessible via API |
| ST-002 | Network interruption (30 seconds) | System recovers, buffers data, no loss |
| ST-003 | Database unavailability (5 minutes) | Data buffered in memory, flushed on reconnect |
| ST-004 | Inverter fault condition | Alert generated, notification delivered |
| ST-005 | Configuration hot-reload | New config applied without restart |
| ST-006 | Multi-inverter load (10 devices) | <10% CPU, <512MB RAM, no dropped polls |

### 10.4 Acceptance Testing

**Scope:**

- User requirements validation
- Real-world deployment simulation
- Documentation completeness
- Operational procedures

**Acceptance Criteria:**

| ID | Criterion | Verification Method |
|----|-----------|---------------------|
| AC-001 | Data latency <1 second | Timestamp analysis |
| AC-002 | 99.5% uptime over 30 days | Availability monitoring |
| AC-003 | Alert delivery <30 seconds | Alert timestamp correlation |
| AC-004 | Installation time <30 minutes | Timed installation procedure |
| AC-005 | CPU utilization <10% | System monitoring |
| AC-006 | Memory footprint <512MB | Resource monitoring |

---

## 11. Maintenance and Operations

### 11.1 Logging Strategy

**Log Levels:**

- **DEBUG**: Detailed diagnostic information
- **INFO**: Normal operational messages
- **WARNING**: Potential issues, degraded performance
- **ERROR**: Error conditions, recoverable failures
- **CRITICAL**: Critical failures requiring immediate attention

**Log Structure:**

```json
{
  "timestamp": "2025-10-25T10:30:45.123Z",
  "level": "INFO",
  "module": "modbus_client",
  "inverter_id": "inv001",
  "message": "Successfully read 32 registers",
  "duration_ms": 87,
  "context": {
    "address": "0x0000",
    "count": 32
  }
}
```

**Log Rotation:**

- Maximum file size: 100MB
- Retention: 30 days
- Compression: gzip
- Location: `/var/log/solax-monitor/`

### 11.2 Monitoring and Metrics

**System Metrics:**

| Metric | Type | Description | Alert Threshold |
|--------|------|-------------|-----------------|
| modbus_requests_total | Counter | Total Modbus requests | N/A |
| modbus_requests_failed | Counter | Failed Modbus requests | >5/min |
| modbus_request_duration | Histogram | Request latency | P95 >1s |
| database_writes_total | Counter | Database write operations | N/A |
| database_writes_failed | Counter | Failed database writes | >1/min |
| buffer_size | Gauge | Buffered measurements | >1000 |
| inverter_connected | Gauge | Inverter connection status | 0 |
| memory_usage_bytes | Gauge | Memory consumption | >512MB |
| cpu_usage_percent | Gauge | CPU utilization | >10% |

**Health Checks:**

```python
def health_check() -> HealthStatus:
    """Perform comprehensive health check."""
    status = HealthStatus()
    
    # Check database connectivity
    status.database = check_database_connection()
    
    # Check inverter connections
    status.inverters = check_inverter_connections()
    
    # Check buffer status
    status.buffer_utilization = get_buffer_utilization()
    
    # Check alert system
    status.alerts = check_alert_system()
    
    return status
```

### 11.3 Backup and Recovery

**Backup Strategy:**

| Component | Frequency | Retention | Method |
|-----------|-----------|-----------|--------|
| Configuration | Daily | 30 days | File backup |
| Database (full) | Weekly | 4 weeks | InfluxDB backup |
| Database (incremental) | Daily | 7 days | InfluxDB backup |
| Audit logs | Daily | 90 days | File backup |
| Application code | On change | Git repository | Version control |

**Recovery Procedures:**

**Scenario 1: Configuration Corruption**

```bash
# Restore configuration from backup
sudo cp /backup/config.yaml.2025-10-24 /etc/solax-monitor/config.yaml
sudo systemctl restart solax-monitor
```

**Scenario 2: Database Failure**

```bash
# Stop services
sudo systemctl stop solax-monitor influxdb

# Restore database from backup
influxd restore -portable /backup/influxdb/2025-10-24

# Start services
sudo systemctl start influxdb solax-monitor
```

**Scenario 3: Complete System Failure**

```bash
# Prepare new system
sudo apt update && sudo apt install -y python3.11 influxdb

# Restore application
cd /opt
sudo tar -xzf /backup/solax-monitor-app.tar.gz

# Restore configuration
sudo cp /backup/config.yaml /etc/solax-monitor/

# Restore database
influxd restore -portable /backup/influxdb/latest

# Start services
sudo systemctl enable --now solax-monitor
```

### 11.4 Update Procedures

**Application Updates:**

```bash
# Pull latest code
cd /opt/solax-monitor
git pull origin main

# Install dependencies
source venv/bin/activate
pip install -r requirements.txt

# Run database migrations
python migrate.py

# Restart service
sudo systemctl restart solax-monitor

# Verify operation
sudo systemctl status solax-monitor
curl http://localhost:8080/api/v1/health
```

**Firmware Updates (Inverter):**

1. Schedule maintenance window
2. Enable audit logging
3. Backup current configuration
4. Perform firmware update per manufacturer instructions
5. Verify Modbus connectivity
6. Validate register mappings
7. Resume normal operation

---

## 12. Error Handling and Recovery

### 12.1 Error Classification

| Category | Severity | Response | Example |
|----------|----------|----------|---------|
| Transient | Low | Retry with backoff | Network timeout |
| Degraded | Medium | Continue with reduced capability | Single inverter offline |
| Critical | High | Alert and failover | Database unavailable |
| Fatal | Critical | Shutdown and alert | Configuration corruption |

### 12.2 Retry Logic

**Exponential Backoff:**

```python
def exponential_backoff(attempt: int, base_delay: float = 1.0, max_delay: float = 60.0) -> float:
    """
    Calculate exponential backoff delay.
    
    Args:
        attempt: Retry attempt number (0-indexed)
        base_delay: Base delay in seconds
        max_delay: Maximum delay in seconds
        
    Returns:
        Delay in seconds before next retry
    """
    delay = min(base_delay * (2 ** attempt), max_delay)
    jitter = random.uniform(0, 0.1 * delay)
    return delay + jitter
```

**Retry Policy:**

| Operation | Max Attempts | Base Delay | Max Delay |
|-----------|--------------|------------|-----------|
| Modbus read | 3 | 1s | 5s |
| Modbus write | 5 | 2s | 10s |
| Database write | 5 | 1s | 30s |
| Alert dispatch | 3 | 5s | 60s |

### 12.3 Circuit Breaker Pattern

```python
class CircuitBreaker:
    """
    Implements circuit breaker pattern for fault tolerance.
    
    States:
        - CLOSED: Normal operation, requests allowed
        - OPEN: Fault detected, requests blocked
        - HALF_OPEN: Testing if fault resolved
    """
    
    def __init__(
        self,
        failure_threshold: int = 5,
        success_threshold: int = 2,
        timeout: float = 60.0
    ):
        self.failure_threshold = failure_threshold
        self.success_threshold = success_threshold
        self.timeout = timeout
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function through circuit breaker."""
        if self.state == CircuitState.OPEN:
            if time.time() - self.last_failure_time > self.timeout:
                self.state = CircuitState.HALF_OPEN
            else:
                raise CircuitBreakerOpenError()
        
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise e
```

---

## 13. Performance Optimization

### 13.1 Optimization Strategies

**1. Register Batch Reading**

Read contiguous registers in single operation:

```python
# Inefficient: Multiple reads
voltage = read_register(0x0000)
current = read_register(0x0001)
power = read_register(0x0002)

# Optimized: Batch read
registers = read_registers(0x0000, 3)
voltage, current, power = registers
```

**2. Connection Pooling**

Maintain persistent connections to inverters:

```python
class ConnectionPool:
    """Manage pool of Modbus connections."""
    
    def __init__(self, max_connections: int = 10):
        self.pool = Queue(maxsize=max_connections)
        self.active_connections = {}
    
    def acquire(self, inverter_id: str) -> ModbusClient:
        """Get connection from pool."""
        if inverter_id in self.active_connections:
            return self.active_connections[inverter_id]
        
        try:
            client = self.pool.get_nowait()
        except Empty:
            client = self._create_connection()
        
        self.active_connections[inverter_id] = client
        return client
```

**3. Asynchronous I/O**

Use async/await for concurrent operations:

```python
async def poll_inverter(inverter: SolaxInverter) -> Measurement:
    """Asynchronously poll inverter telemetry."""
    tasks = [
        inverter.get_grid_metrics(),
        inverter.get_pv_metrics(),
        inverter.get_battery_metrics(),
        inverter.get_system_status()
    ]
    results = await asyncio.gather(*tasks)
    return Measurement(*results)
```

**4. Data Compression**

Compress historical data in database:

```python
# Use downsampling for long-term storage
CREATE CONTINUOUS QUERY "cq_1m" ON "solar_monitoring"
BEGIN
  SELECT mean("pv_power_total") AS "pv_power_total",
         mean("battery_soc") AS "battery_soc"
  INTO "solar_monitoring_1m"."autogen"."inverter_telemetry"
  FROM "inverter_telemetry"
  GROUP BY time(1m), "inverter_id"
END
```

### 13.2 Performance Targets

| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| Poll interval | ≤1s | Timestamp delta analysis |
| Modbus latency | <100ms (P95) | Request duration histogram |
| Database write latency | <50ms (P95) | Write duration histogram |
| Memory footprint | <512MB | RSS monitoring |
| CPU utilization | <10% | System monitoring |
| Startup time | <10s | Systemd service metrics |

---

## 14. Extensibility and Future Enhancements

### 14.1 Plugin Architecture

**Plugin Interface:**

```python
class InverterPlugin(ABC):
    """Base class for inverter protocol plugins."""
    
    @abstractmethod
    def connect(self, config: dict) -> bool:
        """Establish connection to inverter."""
        pass
    
    @abstractmethod
    def read_telemetry(self) -> Measurement:
        """Read current telemetry data."""
        pass
    
    @abstractmethod
    def write_configuration(self, config: dict) -> bool:
        """Write configuration to inverter."""
        pass
```

**Example Plugin:**

```python
class SunGrowPlugin(InverterPlugin):
    """Plugin for SunGrow inverters."""
    
    def connect(self, config: dict) -> bool:
        # SunGrow-specific connection logic
        pass
    
    def read_telemetry(self) -> Measurement:
        # SunGrow-specific register mapping
        pass
```

### 14.2 Planned Features

**Phase 2: Advanced Analytics**

- Machine learning for predictive maintenance
- Anomaly detection using statistical methods
- Performance benchmarking against similar systems
- Degradation analysis and forecasting

**Phase 3: Optimization Engine**

- Dynamic charge/discharge scheduling
- Time-of-use rate optimization
- Weather forecast integration
- Load prediction and management

**Phase 4: Grid Services**

- Frequency response participation
- Voltage support
- Demand response integration
- Virtual power plant capabilities

---

## 15. Dependencies and Constraints

### 15.1 External Dependencies

| Dependency | Version | License | Purpose |
|------------|---------|---------|---------|
| Python | ≥3.11 | PSF | Runtime environment |
| pymodbus | ≥3.5.0 | BSD | Modbus protocol |
| InfluxDB | ≥2.7 | MIT | Time-series database |
| pyyaml | ≥6.0 | MIT | Configuration parsing |
| requests | ≥2.31.0 | Apache 2.0 | HTTP client |
| systemd | - | LGPL | Service management |

### 15.2 Hardware Constraints

| Constraint | Limit | Impact |
|------------|-------|--------|
| Modbus poll rate | ≥1s | Minimum polling interval |
| Network bandwidth | 100 Mbps minimum | Multi-inverter support |
| Memory | 4GB minimum | Number of buffered measurements |
| Storage I/O | 10 MB/s minimum | Database write performance |
| CPU | Quad-core minimum | Concurrent inverter polling |

### 15.3 Protocol Constraints

**Modbus TCP Limitations:**

- No native authentication or encryption
- Single master per slave (no concurrent access)
- 16-bit register size (extended data requires multiple registers)
- Limited error information
- Vendor-specific register mappings

**Mitigation Strategies:**

- Network isolation and VPN tunneling
- Connection multiplexer for multi-client access
- 32-bit value reconstruction from paired registers
- Enhanced error logging and diagnostics
- Standardized vendor abstraction layer

### 15.4 Assumptions

1. **Network Stability**: Local network provides <100ms latency and <1% packet loss
2. **Inverter Availability**: Inverters online and accessible 24/7
3. **Hardware Reliability**: Monitoring hardware MTBF >10,000 hours
4. **Protocol Stability**: Solax Modbus protocol remains backward-compatible
5. **Resource Availability**: Sufficient storage for retention policies

---

## 16. Compliance and Standards

### 16.1 Applicable Standards

| Standard | Title | Relevance |
|----------|-------|-----------|
| IEC 61850 | Communication networks and systems for power utility automation | Grid communication protocols |
| IEEE 1547 | Interconnection and interoperability of distributed energy resources | Grid connection requirements |
| IEC 62109 | Safety of power converters for use in photovoltaic power systems | Inverter safety requirements |
| Modbus Application Protocol V1.1b3 | Modbus messaging specification | Protocol implementation |

### 16.2 Data Privacy

**GDPR Compliance:**

- No personally identifiable information collected
- System telemetry only (energy metrics, device status)
- Data retention policies documented and enforced
- Right to deletion supported (data purge procedures)

### 16.3 Safety Considerations

**Electrical Safety:**

- No direct modification of inverter operation without user authorization
- All control commands subject to inverter's built-in safety limits
- Emergency shutdown procedures documented
- Fail-safe defaults (read-only mode)

**Operational Safety:**

- Alert escalation for critical conditions
- Redundancy for critical monitoring functions
- Comprehensive audit logging
- Change management procedures

---

## 17. Glossary

| Term | Definition |
|------|------------|
| BMS | Battery Management System - Controller for battery pack |
| EPS | Emergency Power Supply - Off-grid backup mode |
| Feed-in | Export of excess solar generation to grid |
| Holding Register | Modbus register type for configuration data (read/write) |
| Input Register | Modbus register type for telemetry data (read-only) |
| MPPT | Maximum Power Point Tracking - Solar charge controller |
| Modbus RTU | Serial variant of Modbus protocol |
| Modbus TCP | Ethernet variant of Modbus protocol |
| Register | 16-bit data storage location in Modbus device |
| SCADA | Supervisory Control and Data Acquisition |
| SOC | State of Charge - Battery capacity percentage |
| TOU | Time of Use - Variable electricity pricing by time |
| Unit ID | Modbus device identifier (slave address) |

---

## 18. References

### 18.1 Protocol Documentation

1. Solax Modbus TCP/RTU Protocol V3.21 - `Hybrid-X1X3-G4-ModbusTCPRTU-V3.21-English_0622-public-version.pdf`
2. Modbus Application Protocol Specification V1.1b3 - Modbus Organization
3. Modbus Messaging on TCP/IP Implementation Guide V1.0b - Modbus Organization

### 18.2 Software Libraries

1. pymodbus Documentation - https://pymodbus.readthedocs.io/
2. InfluxDB Python Client - https://influxdb-client.readthedocs.io/
3. Python Standard Library - https://docs.python.org/3/library/

### 18.3 Standards

1. IEC 61850 - Communication networks and systems for power utility automation
2. IEEE 1547 - Standard for Interconnecting Distributed Resources with Electric Power Systems
3. IEC 62109 - Safety of power converters for use in photovoltaic power systems

---

## Appendix A: Register Reference Tables

### A.1 Complete Input Register Map

[Detailed register map would be included here with all addresses, data types, scaling factors, units, and descriptions]

### A.2 Complete Holding Register Map

[Detailed holding register map would be included here with all configuration parameters]

---

## Appendix B: Configuration Examples

### B.1 Single Inverter Configuration

```yaml
system:
  log_level: INFO
  
database:
  type: influxdb
  host: localhost
  port: 8086
  database: solar_monitoring
  
inverters:
  - id: inv001
    name: "Home Inverter"
    host: 192.168.1.100
    port: 502
    unit_id: 1
    poll_interval: 5
    enabled: true
    
alerts:
  enabled: true
  channels:
    - type: email
      smtp_host: smtp.gmail.com
      smtp_port: 587
      smtp_user: alerts@example.com
      recipients:
        - homeowner@example.com
```

### B.2 Multi-Inverter Configuration

```yaml
inverters:
  - id: inv001
    name: "Building A - Roof 1"
    host: 192.168.1.100
    location: "Building A"
    
  - id: inv002
    name: "Building A - Roof 2"
    host: 192.168.1.101
    location: "Building A"
    
  - id: inv003
    name: "Building B - Main"
    host: 192.168.1.102
    location: "Building B"
    
  - id: inv004
    name: "Carport"
    host: 192.168.1.103
    location: "Parking"
```

---

## Appendix C: API Examples

### C.1 Retrieve Current Telemetry

**Request:**

```http
GET /api/v1/inverters/inv001/telemetry HTTP/1.1
Host: localhost:8080
Authorization: Bearer eyJhbGc...
```

**Response:**

```json
{
  "inverter_id": "inv001",
  "timestamp": "2025-10-25T14:30:45Z",
  "grid": {
    "voltage_r": 230.1,
    "voltage_s": 229.8,
    "voltage_t": 230.3,
    "current_r": 5.2,
    "current_s": 5.1,
    "current_t": 5.3,
    "power_total": 3580,
    "frequency": 50.02
  },
  "pv": {
    "pv1_voltage": 385.2,
    "pv1_current": 8.5,
    "pv1_power": 3274,
    "pv2_voltage": 380.1,
    "pv2_current": 0.0,
    "pv2_power": 0,
    "power_total": 3274
  },
  "battery": {
    "voltage": 51.2,
    "current": -10.5,
    "power": -538,
    "soc": 75,
    "temperature": 22
  },
  "system": {
    "run_mode": "normal",
    "inverter_temperature": 35,
    "feedin_power": -244
  }
}
```

### C.2 Set Operating Mode

**Request:**

```http
POST /api/v1/inverters/inv001/control HTTP/1.1
Host: localhost:8080
Authorization: Bearer eyJhbGc...
Content-Type: application/json

{
  "command": "set_mode",
  "parameters": {
    "mode": "self_use"
  }
}
```

**Response:**

```json
{
  "success": true,
  "message": "Operating mode changed to self_use",
  "audit_id": "ctrl-20251025-143045-001"
}
```

---

## Appendix D: Troubleshooting Decision Tree

```
Connection Issue?
├─ YES → Can ping inverter IP?
│        ├─ YES → Port 502 open?
│        │        ├─ YES → Check Modbus unit ID
│        │        └─ NO → Check firewall rules
│        └─ NO → Verify network configuration
│
├─ Data Quality Issue?
│  ├─ Register value out of range?
│  │    └─ Verify register address against protocol doc
│  └─ Intermittent data?
│       └─ Check polling interval (must be ≥1s)
│
└─ Performance Issue?
   ├─ High latency?
   │    └─ Check network congestion
   └─ High resource usage?
        └─ Check number of concurrent inverters
```

---

## Document Control

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-10-25 | System Architect | Initial release |

**Approval:**

| Role | Name | Signature | Date |
|------|------|-----------|------|
| Technical Lead | | | |
| Security Architect | | | |
| QA Manager | | | |
| Operations Manager | | | |

---

**END OF DOCUMENT**