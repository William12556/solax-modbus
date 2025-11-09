# Master Design Document
# Solax X3 Hybrid Inverter Monitoring System

**MASTER DESIGN DOCUMENT** - This is the authoritative master design from which all design elements are derived.

---

```yaml
# T01 Design Template v1.0 - YAML Format
# Master Design Document

project_info:
  name: "Solax Modbus Monitoring System"
  version: "1.0"
  date: "2025-11-09"
  author: "System Architect"

scope:
  purpose: "Real-time monitoring and control system for Solax X3 Hybrid 6.0-D solar inverters using Modbus TCP protocol, eliminating cloud service dependencies and proprietary API requirements"
  in_scope:
    - "Data acquisition via Modbus TCP protocol"
    - "Protocol interface layer implementation"
    - "Time-series data storage and persistence"
    - "Monitoring and alerting capabilities"
    - "Control and configuration management"
    - "Multi-inverter support architecture"
    - "Local data ownership and offline operation"
  out_scope:
    - "Hardware selection and procurement"
    - "Physical network infrastructure design"
    - "User interface implementation details"
    - "Cloud integration strategies"
    - "Battery Management System (BMS) direct interface"
  terminology:
    - term: "MPPT"
      definition: "Maximum Power Point Tracking - Solar charge controller optimization algorithm"
    - term: "SOC"
      definition: "State of Charge - Battery capacity percentage remaining"
    - term: "Modbus TCP"
      definition: "Ethernet variant of Modbus protocol using TCP/IP transport"
    - term: "Register"
      definition: "16-bit data storage location in Modbus device memory map"
    - term: "Unit ID"
      definition: "Modbus device identifier (slave address)"
    - term: "Feed-in"
      definition: "Export of excess solar generation to electrical grid"

system_overview:
  description: "Modular architecture implementing direct Modbus TCP communication with Solax inverters, processing telemetry data, storing in time-series database, and providing monitoring/control capabilities"
  context_flow: "Inverters (Modbus TCP) → Protocol Interface → Data Processing → Storage/Monitoring/Control → External Systems (Database/Alerts)"
  primary_functions:
    - "Acquire real-time telemetry from inverters at 1-5 second intervals"
    - "Process and validate inverter data with unit conversions and scaling"
    - "Store time-series data with configurable retention policies"
    - "Monitor thresholds and dispatch alerts via multiple channels"
    - "Execute control commands with audit logging"
    - "Coordinate multiple inverter instances with isolated failure domains"

design_constraints:
  technical:
    - "Modbus TCP protocol mandatory for inverter communication"
    - "Minimum 1 second polling interval per Modbus specification"
    - "Network latency tolerance up to 500ms"
    - "No authentication/encryption at Modbus protocol layer"
    - "16-bit register architecture requires multi-register reconstruction for 32-bit values"
  implementation:
    language: "Python"
    framework: "asyncio for concurrent operations"
    libraries:
      - "pymodbus 3.5.0+ (Modbus protocol implementation)"
      - "influxdb-client 1.38.0+ (time-series database)"
      - "pyyaml 6.0+ (configuration management)"
      - "pytest 7.4.0+ (testing framework)"
    standards:
      - "IEC 61131-3 data type conventions"
      - "Modbus Application Protocol V1.1b3"
      - "PEP 8 Python style guide"
  performance_targets:
    - metric: "Request latency"
      value: "99.9% within 1 second"
    - metric: "Memory footprint"
      value: "≤512MB (10 inverters)"
    - metric: "CPU utilization"
      value: "≤10% on Raspberry Pi 4"

architecture:
  pattern: "Layered architecture with modular separation of concerns"
  component_relationships: "Protocol Interface → Inverter Interface → Data Processing → (Storage | Monitoring | Control)"
  technology_stack:
    language: "Python 3.11+"
    framework: "asyncio with concurrent.futures"
    libraries:
      - "pymodbus (Modbus TCP/IP client)"
      - "influxdb-client (time-series persistence)"
      - "pyyaml (configuration)"
      - "pytest (testing)"
    data_store: "InfluxDB 2.7+ (time-series database)"
  directory_structure:
    - "governance/ - Operational rules and framework"
    - "workspace/design/ - Design documents"
    - "workspace/change/ - Change management"
    - "workspace/issues/ - Issue tracking"
    - "workspace/trace/ - Prompt documents"
    - "workspace/test/ - Test plans and results"
    - "docs/ - Technical documentation"
    - "src/ - Source code modules"
    - "deprecated/ - Archived materials"

components:
  - name: "Protocol Interface Module"
    purpose: "Encapsulates low-level Modbus TCP communication with connection management and error handling"
    responsibilities:
      - "Establish and maintain TCP connections to inverters"
      - "Execute Modbus read/write operations with timeout handling"
      - "Implement exponential backoff retry logic"
      - "Manage connection pooling and lifecycle"
    inputs:
      - field: "host"
        type: "string"
        description: "Inverter IP address"
      - field: "port"
        type: "integer"
        description: "Modbus TCP port (default 502)"
      - field: "unit_id"
        type: "integer"
        description: "Modbus device identifier"
    outputs:
      - field: "register_values"
        type: "List[int]"
        description: "Raw 16-bit register values"
      - field: "connection_status"
        type: "bool"
        description: "Connection state indicator"
    key_elements:
      - name: "ModbusClient"
        type: "class"
        purpose: "Low-level Modbus TCP client wrapper with retry logic"
      - name: "RegisterMap"
        type: "class"
        purpose: "Type-safe register address definitions with metadata"
    dependencies:
      internal: []
      external:
        - "pymodbus.client.tcp.ModbusTcpClient"
    processing_logic:
      - "Initialize TCP connection with configurable timeout"
      - "Read input registers (function code 0x04) for telemetry"
      - "Read holding registers (function code 0x03) for configuration"
      - "Write holding registers (function code 0x06/0x10) for control"
      - "Handle connection failures with exponential backoff (max 5 attempts)"
    error_conditions:
      - condition: "Connection timeout"
        handling: "Exponential backoff retry, log failure, raise ModbusConnectionError after max attempts"
      - condition: "Invalid register address"
        handling: "Validate against RegisterMap, raise ModbusAddressError"
      - condition: "Malformed response"
        handling: "Log error details, raise ModbusProtocolError"

  - name: "Inverter Interface Module"
    purpose: "High-level abstraction layer mapping registers to domain objects with type conversion and scaling"
    responsibilities:
      - "Map Modbus registers to structured domain objects"
      - "Apply scaling factors (e.g., 0.1 for voltage)"
      - "Handle signed/unsigned integer conversions"
      - "Maintain inverter state machine"
    inputs:
      - field: "raw_registers"
        type: "List[int]"
        description: "Unscaled register values from Modbus client"
    outputs:
      - field: "telemetry_data"
        type: "Measurement"
        description: "Structured telemetry with engineering units"
      - field: "inverter_state"
        type: "InverterState"
        description: "Current operational state"
    key_elements:
      - name: "SolaxInverter"
        type: "class"
        purpose: "High-level interface providing domain methods"
      - name: "InverterState"
        type: "class"
        purpose: "State machine tracking connection and operation status"
    dependencies:
      internal:
        - "Protocol Interface Module (ModbusClient)"
      external: []
    processing_logic:
      - "Read grid metrics: voltage (0x006A-0x006C), current (0x006D-0x006F), power (0x0070-0x0072), frequency (0x0074-0x0075)"
      - "Read PV metrics: PV1/PV2 voltage (0x000A-0x000B), current (0x000C-0x000D)"
      - "Read battery metrics: voltage (0x0014), current (0x0015), power (0x0016), SOC (0x001D), temperature (0x001C)"
      - "Read system status: run mode (0x0047), feed-in power (0x0020)"
      - "Apply scaling: voltage ×0.1, current ×0.1, power ×1, temperature ×1"
      - "Convert signed integers using two's complement for negative values"
    error_conditions:
      - condition: "Out-of-range values"
        handling: "Flag data quality issue, log warning, optionally discard measurement"
      - condition: "Register read failure"
        handling: "Propagate ModbusError, update consecutive_failures counter"

  - name: "Data Processing Module"
    purpose: "Validates telemetry data, calculates derived metrics, and performs quality assessment"
    responsibilities:
      - "Validate measurements against expected ranges"
      - "Calculate derived metrics (total PV power, net grid power, efficiency)"
      - "Detect anomalies and sensor failures"
      - "Perform unit conversions where required"
    inputs:
      - field: "raw_measurement"
        type: "Measurement"
        description: "Unvalidated telemetry data"
    outputs:
      - field: "validated_measurement"
        type: "Measurement"
        description: "Quality-assessed data with derived metrics"
      - field: "validation_result"
        type: "ValidationResult"
        description: "Data quality indicators and flags"
    key_elements:
      - name: "DataValidator"
        type: "class"
        purpose: "Range checking and anomaly detection"
      - name: "MetricsCalculator"
        type: "class"
        purpose: "Derived metric computation"
    dependencies:
      internal:
        - "Inverter Interface Module"
      external: []
    processing_logic:
      - "Validate voltage: 180-260V (grid), 0-600V (PV), 40-60V (battery)"
      - "Validate current: 0-50A (grid/PV), -100A to +100A (battery)"
      - "Validate temperature: -20°C to 80°C (inverter), 0°C to 60°C (battery)"
      - "Calculate total PV power: sum(PV1_power, PV2_power)"
      - "Calculate net grid power: feedin_power (positive=export, negative=import)"
      - "Detect anomalies: sudden value changes >50% of previous reading"
    error_conditions:
      - condition: "Value exceeds physical limits"
        handling: "Flag as invalid, log warning, exclude from aggregations"
      - condition: "Implausible reading sequence"
        handling: "Flag data quality issue, continue processing with warning"

  - name: "Storage Module"
    purpose: "Persist time-series data to InfluxDB with buffering during outages"
    responsibilities:
      - "Write measurements to time-series database"
      - "Buffer data during database unavailability"
      - "Enforce retention policies"
      - "Provide query interface for historical data"
    inputs:
      - field: "measurement"
        type: "Measurement"
        description: "Validated telemetry data"
    outputs:
      - field: "write_result"
        type: "bool"
        description: "Success/failure indicator"
    key_elements:
      - name: "TimeSeriesStore"
        type: "class"
        purpose: "InfluxDB interface abstraction"
      - name: "DataBuffer"
        type: "class"
        purpose: "Circular buffer for outage resilience"
    dependencies:
      internal: []
      external:
        - "influxdb_client.InfluxDBClient"
    processing_logic:
      - "Connect to InfluxDB using configuration credentials"
      - "Write measurement as point with nanosecond timestamp"
      - "Tag with inverter_id and location"
      - "Buffer in memory if database unreachable (max 1 hour)"
      - "Flush buffer on database reconnection"
      - "Apply retention policies: 30d raw, 365d 1min aggregates, 3650d 1hour aggregates"
    error_conditions:
      - condition: "Database connection failure"
        handling: "Buffer measurements in memory, retry connection, alert if buffer >80% full"
      - condition: "Write timeout"
        handling: "Retry write operation (max 3 attempts), buffer if persistent failure"

  - name: "Monitoring Module"
    purpose: "Evaluate alert conditions, dispatch notifications, and maintain alert state"
    responsibilities:
      - "Monitor thresholds (battery SOC, temperature, communication failures)"
      - "Dispatch notifications via multiple channels (email, SMS, webhook)"
      - "Implement rate limiting to prevent notification storms"
      - "Maintain alert history with acknowledgment tracking"
    inputs:
      - field: "measurement"
        type: "Measurement"
        description: "Current telemetry data"
      - field: "system_state"
        type: "SystemState"
        description: "Connection and operational status"
    outputs:
      - field: "alerts"
        type: "List[Alert]"
        description: "Triggered alert conditions"
    key_elements:
      - name: "AlertManager"
        type: "class"
        purpose: "Threshold evaluation and alert lifecycle management"
      - name: "NotificationDispatcher"
        type: "class"
        purpose: "Multi-channel notification delivery"
    dependencies:
      internal:
        - "Data Processing Module"
      external:
        - "smtplib (email)"
        - "requests (webhook)"
    processing_logic:
      - "Evaluate conditions: communication_failure (>5 timeouts), battery_low (<10%), battery_critical (<5%), battery_overtemp (>50°C), grid_fault (run_mode=3), inverter_overtemp (>75°C)"
      - "Check rate limits: max 1 notification per condition per 15 minutes"
      - "Dispatch via configured channels with severity-based routing"
      - "Log all alert events with timestamp and state"
    error_conditions:
      - condition: "Notification dispatch failure"
        handling: "Log error, retry alternate channel, escalate if all channels fail"
      - condition: "Rate limit exceeded"
        handling: "Queue alert, send summary notification after cooldown period"

  - name: "Control Module"
    purpose: "Execute write operations to inverter with validation and audit logging"
    responsibilities:
      - "Validate control commands against inverter constraints"
      - "Write to holding registers for configuration changes"
      - "Maintain comprehensive audit log"
      - "Implement rollback capability for failed operations"
    inputs:
      - field: "control_command"
        type: "ControlCommand"
        description: "Requested configuration change"
    outputs:
      - field: "control_result"
        type: "ControlResult"
        description: "Success/failure with audit reference"
    key_elements:
      - name: "InverterController"
        type: "class"
        purpose: "Control command validation and execution"
      - name: "AuditLog"
        type: "class"
        purpose: "Immutable audit trail storage"
    dependencies:
      internal:
        - "Protocol Interface Module"
      external: []
    processing_logic:
      - "Parse control command (operating mode, charge schedule, power limits)"
      - "Validate against inverter specifications"
      - "Write to holding registers: mode (0x001F), charge times (0x0020-0x0023), discharge times (0x0024-0x0027), power limits (0x0028-0x0029)"
      - "Verify write success by reading back register"
      - "Log audit entry: timestamp, user, operation, register, old/new values, result"
    error_conditions:
      - condition: "Invalid parameter value"
        handling: "Reject command, return validation error, do not write to inverter"
      - condition: "Write operation failure"
        handling: "Attempt rollback to previous value, log failure, raise ControlError"

  - name: "Multi-Inverter Coordinator"
    purpose: "Manage concurrent monitoring of multiple inverters with isolated failure domains"
    responsibilities:
      - "Instantiate and coordinate multiple inverter instances"
      - "Stagger polling to prevent network congestion"
      - "Aggregate data across inverter fleet"
      - "Handle per-inverter failures independently"
    inputs:
      - field: "inverter_configs"
        type: "List[InverterConfig]"
        description: "Configuration for each inverter instance"
    outputs:
      - field: "aggregate_metrics"
        type: "AggregateMetrics"
        description: "Fleet-wide totals and statistics"
    key_elements:
      - name: "InverterPool"
        type: "class"
        purpose: "Inverter instance lifecycle management"
      - name: "PollingCoordinator"
        type: "class"
        purpose: "Distributed polling scheduler with backpressure"
    dependencies:
      internal:
        - "Inverter Interface Module"
        - "Data Processing Module"
      external: []
    processing_logic:
      - "Initialize connection pool for up to 100 inverters"
      - "Schedule polls with staggered timing (offset by poll_interval/inverter_count)"
      - "Execute concurrent polls using asyncio.gather"
      - "Aggregate total generation, combined capacity, net grid interaction"
      - "Isolate failures: single inverter failure does not affect others"
    error_conditions:
      - condition: "Inverter communication failure"
        handling: "Continue polling other inverters, mark failed inverter as degraded, alert if >30% of fleet offline"
      - condition: "Network saturation"
        handling: "Implement backpressure: reduce polling frequency, prioritize critical telemetry"

data_design:
  entities:
    - name: "Measurement"
      purpose: "Structured telemetry snapshot from single inverter"
      attributes:
        - name: "timestamp"
          type: "datetime"
          constraints: "UTC timezone, nanosecond precision"
        - name: "inverter_id"
          type: "string"
          constraints: "Unique identifier per inverter"
        - name: "grid_voltage_r"
          type: "float"
          constraints: "180-260V"
        - name: "grid_current_r"
          type: "float"
          constraints: "0-50A"
        - name: "grid_power_r"
          type: "int"
          constraints: "-12000 to +12000W"
        - name: "pv1_voltage"
          type: "float"
          constraints: "0-600V"
        - name: "pv1_current"
          type: "float"
          constraints: "0-20A"
        - name: "battery_voltage"
          type: "float"
          constraints: "40-60V"
        - name: "battery_current"
          type: "float"
          constraints: "-100 to +100A (negative=discharge)"
        - name: "battery_soc"
          type: "int"
          constraints: "0-100%"
        - name: "battery_temperature"
          type: "int"
          constraints: "0-60°C"
        - name: "run_mode"
          type: "int"
          constraints: "0-10 enum (Waiting, Normal, Fault, etc.)"
      relationships: []
    - name: "InverterConfig"
      purpose: "Connection and operational parameters per inverter"
      attributes:
        - name: "id"
          type: "string"
          constraints: "Unique, alphanumeric"
        - name: "name"
          type: "string"
          constraints: "Human-readable label"
        - name: "host"
          type: "string"
          constraints: "Valid IPv4 address"
        - name: "port"
          type: "int"
          constraints: "1-65535, typically 502"
        - name: "unit_id"
          type: "int"
          constraints: "1-247"
        - name: "poll_interval"
          type: "int"
          constraints: "≥1 second"
        - name: "enabled"
          type: "bool"
          constraints: "true|false"
      relationships:
        - target: "Measurement"
          type: "one-to-many"
  storage:
    - name: "inverter_telemetry"
      fields:
        - name: "time"
          type: "timestamp"
          constraints: "Nanosecond precision, indexed"
        - name: "inverter_id"
          type: "tag"
          constraints: "Indexed for fast filtering"
        - name: "location"
          type: "tag"
          constraints: "Indexed"
        - name: "pv_power_total"
          type: "float"
          constraints: "Derived field"
        - name: "grid_voltage_r"
          type: "float"
          constraints: ""
        - name: "battery_soc"
          type: "integer"
          constraints: ""
      indexes:
        - "time (primary)"
        - "inverter_id (tag)"
        - "location (tag)"
  validation_rules:
    - "Grid voltage must be within ±10% of nominal (230V ±23V)"
    - "Battery SOC must be 0-100 inclusive"
    - "Temperature readings must be physically plausible (-20°C to +80°C)"
    - "Power values must balance: PV_power ≈ Grid_power + Battery_power (within 5% tolerance for losses)"

interfaces:
  internal:
    - name: "read_telemetry"
      purpose: "Retrieve current inverter measurements"
      signature: "async def read_telemetry(inverter: SolaxInverter) -> Measurement"
      parameters:
        - name: "inverter"
          type: "SolaxInverter"
          description: "Configured inverter interface instance"
      returns:
        type: "Measurement"
        description: "Structured telemetry data with timestamp"
      raises:
        - exception: "ModbusConnectionError"
          condition: "Unable to establish TCP connection"
        - exception: "ModbusTimeoutError"
          condition: "Read operation exceeds timeout threshold"
        - exception: "ModbusProtocolError"
          condition: "Malformed response from device"
    - name: "write_configuration"
      purpose: "Execute control command to inverter"
      signature: "async def write_configuration(inverter: SolaxInverter, command: ControlCommand) -> ControlResult"
      parameters:
        - name: "inverter"
          type: "SolaxInverter"
          description: "Target inverter instance"
        - name: "command"
          type: "ControlCommand"
          description: "Validated control parameters"
      returns:
        type: "ControlResult"
        description: "Execution outcome with audit reference"
      raises:
        - exception: "ValidationError"
          condition: "Command parameters outside allowable range"
        - exception: "ModbusWriteError"
          condition: "Register write operation failed"
    - name: "persist_measurement"
      purpose: "Store telemetry data to time-series database"
      signature: "async def persist_measurement(measurement: Measurement) -> bool"
      parameters:
        - name: "measurement"
          type: "Measurement"
          description: "Validated telemetry data"
      returns:
        type: "bool"
        description: "True if write successful, False if buffered"
      raises:
        - exception: "DatabaseConnectionError"
          condition: "Unable to reach InfluxDB instance"
  external:
    - name: "Modbus TCP"
      protocol: "Modbus TCP/IP over port 502"
      data_format: "Binary (register-based, big-endian)"
      specification: "Function codes 0x03 (read holding), 0x04 (read input), 0x06/0x10 (write)"
    - name: "InfluxDB Line Protocol"
      protocol: "HTTP POST to /api/v2/write"
      data_format: "Line protocol: measurement,tags fields timestamp"
      specification: "InfluxDB 2.x API specification"
    - name: "SMTP"
      protocol: "SMTP over TLS (port 587)"
      data_format: "MIME multipart/alternative (text + HTML)"
      specification: "RFC 5321 (SMTP), RFC 2045 (MIME)"

error_handling:
  exception_hierarchy:
    base: "SolaxMonitoringError"
    specific:
      - "ModbusConnectionError"
      - "ModbusTimeoutError"
      - "ModbusProtocolError"
      - "ModbusAddressError"
      - "ModbusWriteError"
      - "DatabaseConnectionError"
      - "DatabaseWriteError"
      - "ValidationError"
      - "ControlError"
  strategy:
    validation_errors: "Reject invalid input at boundary, return descriptive error to caller, do not propagate to lower layers"
    runtime_errors: "Log with full traceback, attempt recovery (retry/fallback), raise specific exception if unrecoverable"
    external_failures: "Implement circuit breaker pattern, exponential backoff, alert on persistent failures"
  logging:
    levels:
      - "DEBUG: Modbus request/response details"
      - "INFO: Connection state changes, successful operations"
      - "WARNING: Retries, data quality issues, approaching thresholds"
      - "ERROR: Operation failures, exceptions raised"
      - "CRITICAL: System-level failures, multiple component failures"
    required_info:
      - "Timestamp (ISO 8601 with timezone)"
      - "Module name and function"
      - "Inverter ID (if applicable)"
      - "Operation context"
      - "Exception traceback (for errors)"
    format: "JSON structured logging for machine parsing"

nonfunctional_requirements:
  performance:
    - metric: "Modbus request latency"
      target: "P95 <100ms, P99 <1s"
    - metric: "Database write latency"
      target: "P95 <50ms"
    - metric: "Memory footprint"
      target: "≤512MB for 10 inverters"
    - metric: "CPU utilization"
      target: "≤10% sustained on Raspberry Pi 4"
  security:
    authentication: "JWT tokens for API access, SSH public key authentication"
    authorization: "Role-based access control (Administrator, Operator, Viewer)"
    data_protection:
      - "TLS 1.3 for API endpoints"
      - "Database credentials via environment variables"
      - "Network isolation via VLAN or VPN"
      - "Audit logging of all privileged operations"
  reliability:
    error_recovery: "Automatic service restart on crash, connection retry with exponential backoff"
    fault_tolerance:
      - "Single inverter failure does not affect others"
      - "Database outage buffered for up to 1 hour"
      - "Alert delivery retry across multiple channels"
  maintainability:
    code_organization:
      - "Modular architecture with single responsibility principle"
      - "Dependency injection for testability"
      - "Type hints throughout codebase"
    documentation:
      - "Docstrings on all public interfaces"
      - "README with installation and configuration"
      - "Architecture decision records for key design choices"
    testing:
      coverage_target: "≥80% line coverage"
      approaches:
        - "Unit tests with mocked external dependencies"
        - "Integration tests with Modbus simulator"
        - "System tests with test inverter instance"

version_history:
  - version: "1.0"
    date: "2025-11-09"
    author: "System Architect"
    changes:
      - "Initial master design document created from reverse engineering of design-0001 and design-0002"
      - "Consolidated information into T01 template format per governance protocol P02"
      - "Designated as authoritative master design per P02 section 1.3.4"

metadata:
  copyright: "Copyright (c) 2025 William Watson. This work is licensed under the MIT License."
  template_version: "1.0"
  schema_type: "t01_design"
```

---

## Design Element Cross-References

This master design is decomposed into the following design element documents:

- [[design-0001-solax-modbus-software-design-specification]] - Comprehensive detailed specification
- [[design-0002-solax-modbus-poc]] - Proof of concept implementation and validation

---

## Return to Table of Contents

[Table of Contents](<#master design document>)

---

Copyright: Copyright (c) 2025 William Watson. This work is licensed under the MIT License.