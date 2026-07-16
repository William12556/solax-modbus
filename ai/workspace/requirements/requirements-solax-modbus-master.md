# Requirements Document
# Solax X3 Hybrid Inverter Monitoring System

Created: 2026 January 08

**Document Type:** Requirements Specification  
**Document ID:** requirements-solax-modbus-master  
**Status:** Active  

---

## Table of Contents

- [Project Information](<#project information>)
- [System Overview](<#system overview>)
- [Functional Requirements](<#functional requirements>)
- [Non-Functional Requirements](<#non-functional requirements>)
- [Architectural Requirements](<#architectural requirements>)
- [Traceability](<#traceability>)
- [Validation](<#validation>)
- [Glossary](<#glossary>)
- [Version History](<#version history>)

---

## Project Information

```yaml
project_info:
  name: "solax-modbus"
  version: "0.1.0"
  date: "2026-01-08"
  author: "William Watson"
  status: "active"
  description: "Real-time monitoring system for Solax X3 Hybrid 6.0-D solar inverters using Modbus TCP protocol"
```

[Return to Table of Contents](<#table of contents>)

---

## System Overview

### Purpose

Provide direct, local monitoring of Solax X3 Hybrid 6.0-D solar inverters without cloud service dependencies. System eliminates latency, ensures data ownership, operates independent of internet connectivity, and enables industrial automation integration.

### Scope

**In Scope:**
- Modbus TCP communication with Solax inverters
- Real-time telemetry acquisition and display
- Data validation and quality checks
- Time-series data persistence
- Threshold-based alerting
- Configuration write operations
- Development emulator
- Embedded HTTP server for live telemetry (single inverter, read-only)

**Out of Scope:**
- Multi-inverter fleet coordination
- Hardware procurement
- Network infrastructure
- Cloud integration
- Direct BMS interface

### Stakeholders

| Stakeholder | Interest |
|-------------|----------|
| End User | Reliable monitoring, data ownership, minimal maintenance |
| System Integrator | Industrial automation compatibility, API access |
| Developer | Clear architecture, testability, maintainability |
| Operations | Deployment simplicity, observability, recovery procedures |

[Return to Table of Contents](<#table of contents>)

---

## Functional Requirements

### FR-001: Data Acquisition

```yaml
- id: "a1b2c3d4"
  type: "functional"
  description: "System SHALL poll inverter telemetry via Modbus TCP at configurable intervals (minimum 1 second per protocol specification)"
  acceptance_criteria:
    - "Poll interval configurable from command line"
    - "Minimum interval enforced at 1 second"
    - "Actual poll interval logged for verification"
  source: "Solax Protocol V3.21 timing constraints"
  rationale: "1-second minimum prevents protocol violations and inverter lockup"
  dependencies: []
```

### FR-002: Grid Telemetry

```yaml
- id: "b2c3d4e5"
  type: "functional"
  description: "System SHALL read three-phase grid electrical parameters: voltage, current, power, frequency"
  acceptance_criteria:
    - "Phase R, S, T voltage readings (Volts)"
    - "Phase R, S, T current readings (Amperes)"
    - "Phase R, S, T power readings (Watts)"
    - "Grid frequency (Hertz)"
    - "All values scaled from raw registers per specification"
  source: "Industrial solar monitoring requirements"
  rationale: "Three-phase monitoring essential for grid interaction visibility"
  dependencies: ["a1b2c3d4"]
```

### FR-003: PV Generation Telemetry

```yaml
- id: "c3d4e5f6"
  type: "functional"
  description: "System SHALL read dual MPPT solar generation metrics: voltage, current, power per string"
  acceptance_criteria:
    - "PV1 voltage, current, power (per string)"
    - "PV2 voltage, current, power (per string)"
    - "Total PV power calculated (sum of strings)"
    - "Values updated per polling interval"
  source: "Solar generation monitoring requirements"
  rationale: "Per-string monitoring enables imbalance detection and production optimization"
  dependencies: ["a1b2c3d4"]
```

### FR-004: Battery System Telemetry

```yaml
- id: "d4e5f6a7"
  type: "functional"
  description: "System SHALL read battery system state: voltage, current, power, SOC, temperature"
  acceptance_criteria:
    - "Battery voltage (Volts)"
    - "Battery current (Amperes, signed for charge/discharge direction)"
    - "Battery power (Watts, signed for charge/discharge direction)"
    - "State of Charge (percentage 0-100)"
    - "Battery temperature (Celsius)"
  source: "Energy storage monitoring requirements"
  rationale: "Battery state visibility critical for system health and energy management"
  dependencies: ["a1b2c3d4"]
```

### FR-005: System Status

```yaml
- id: "e5f6a7b8"
  type: "functional"
  description: "System SHALL read inverter operational status: run mode, temperature, error states"
  acceptance_criteria:
    - "Run mode decoded to human-readable state (waiting, normal, fault, etc.)"
    - "Inverter temperature (Celsius)"
    - "Grid import/export power (feed-in)"
    - "Daily and cumulative energy totals"
  source: "System health monitoring requirements"
  rationale: "Operational status enables fault detection and performance tracking"
  dependencies: ["a1b2c3d4"]
```

### FR-006: Data Type Conversion

```yaml
- id: "f6a7b8c9"
  type: "functional"
  description: "System SHALL correctly handle signed and unsigned 16-bit and 32-bit register values with appropriate scaling"
  acceptance_criteria:
    - "Unsigned 16-bit values (0 to 65535)"
    - "Signed 16-bit values (-32768 to +32767) via two's complement"
    - "Unsigned 32-bit values from register pairs"
    - "Signed 32-bit values from register pairs"
    - "Scaling factors applied per register definition"
  source: "Modbus protocol specification, Solax register map"
  rationale: "Correct type handling prevents data corruption and calculation errors"
  dependencies: ["a1b2c3d4"]
```

### FR-007: Console Display

```yaml
- id: "a7b8c9d0"
  type: "functional"
  description: "System SHALL format and display telemetry to console in structured sections"
  acceptance_criteria:
    - "System status section with run mode"
    - "Grid metrics section (three-phase)"
    - "Solar generation section (per-string and total)"
    - "Battery system section (all parameters)"
    - "Power flow section (import/export indication)"
    - "Energy totals section (daily and cumulative)"
    - "Inverter temperature section"
  source: "Operational visibility requirements"
  rationale: "Structured display enables rapid system assessment"
  dependencies: ["b2c3d4e5", "c3d4e5f6", "d4e5f6a7", "e5f6a7b8"]
```

### FR-008: Connection Management

```yaml
- id: "b8c9d0e1"
  type: "functional"
  description: "System SHALL manage TCP connection lifecycle with automatic reconnection on failure"
  acceptance_criteria:
    - "Initial connection established with retry (exponential backoff)"
    - "Connection state monitored continuously"
    - "Automatic reconnection on disconnection"
    - "Maximum 3 connection attempts before reporting failure"
    - "Retry delays: 1s, 2s, 4s"
  source: "Reliability requirements"
  rationale: "Network transients and inverter reboots require automatic recovery"
  dependencies: []
```

### FR-009: Data Validation

```yaml
- id: "c9d0e1f2"
  type: "functional"
  description: "System SHALL apply range validation to telemetry values on the persistence write path"
  acceptance_criteria:
    - "Grid voltage range: 180-260V"
    - "Grid frequency range: 45-55Hz"
    - "PV voltage range: 0-600V"
    - "PV current range: 0-20A"
    - "Battery voltage range: 40-60V"
    - "Battery current range: -100 to +100A"
    - "Battery SOC range: 0-100%"
    - "Temperature range: -20 to +80°C"
    - "Out-of-range values logged and rejected before storage"
  source: "Physical system constraints, data quality requirements"
  rationale: "Range validation detects sensor failures and prevents invalid data from being persisted"
  dependencies: ["a1b2c3d4"]
  notes: "Change: change-a2d5f7c9. Narrowed from a standalone DataValidator (with quality scoring) to a minimal range check folded into the SQLite store write path."
```

### FR-010: Time-Series Storage

```yaml
- id: "d0e1f2a3"
  type: "functional"
  description: "System SHALL persist validated telemetry to InfluxDB time-series database"
  acceptance_criteria:
    - "Measurements stored with nanosecond timestamp precision"
    - "Data tagged with inverter_id and location"
    - "Write operations non-blocking to polling loop"
    - "Database connection failures trigger buffering"
    - "Successful flush of buffered data on reconnection"
  source: "Historical analysis and trending requirements"
  rationale: "Time-series storage enables performance analysis and fault diagnosis"
  dependencies: ["c9d0e1f2"]
```

### FR-011: Data Buffering (Retired)

```yaml
- id: "e1f2a3b4"
  type: "functional"
  status: "retired"
  description: "RETIRED. System SHALL buffer measurements in memory during database outages (maximum 1 hour)"
  retirement:
    date: "2026-07-16"
    change_ref: "change-a2d5f7c9"
    reason: >
      Outage buffering addressed a remote InfluxDB network dependency. The
      persistence store is now a local SQLite file (FR-010); a network-outage
      buffer is no longer applicable. The DataBuffer component is retired.
  dependencies: ["d0e1f2a3"]
```

### FR-012: Retention Policies

```yaml
- id: "f2a3b4c5"
  type: "functional"
  description: "System SHALL enforce time-based retention on the SQLite store"
  acceptance_criteria:
    - "Raw table: 1-minute resolution retained for 24 hours"
    - "Rollup table: 15-minute resolution retained for 30 days"
    - "Each rollup bucket stores average, minimum, and maximum per metric"
    - "Raw samples older than the raw window pruned"
    - "Rollup buckets older than the rollup window pruned"
  source: "Storage management requirements (off-grid deployment)"
  rationale: "Bounded raw and rollup windows keep the local database file small while preserving a 30-day trend"
  dependencies: ["d0e1f2a3"]
  notes: "Change: change-a2d5f7c9. Replaces the InfluxDB three-tier retention model."
```

### FR-013: Threshold Alerting

```yaml
- id: "a3b4c5d6"
  type: "functional"
  description: "System SHALL monitor telemetry against configurable thresholds and generate alerts"
  acceptance_criteria:
    - "Communication failure alert (>5 consecutive timeouts)"
    - "Battery low alert (SOC <10%)"
    - "Battery critical alert (SOC <5%)"
    - "Battery over-temperature alert (>50°C)"
    - "Grid fault alert (run_mode = 3)"
    - "Inverter over-temperature alert (>75°C)"
    - "Alerts include timestamp, severity, and triggering value"
  source: "Operational monitoring requirements"
  rationale: "Proactive alerting enables rapid response to system anomalies"
  dependencies: ["c9d0e1f2"]
```

### FR-014: Alert Notifications

```yaml
- id: "b4c5d6e7"
  type: "functional"
  description: "System SHALL dispatch alert notifications via multiple channels"
  acceptance_criteria:
    - "Email notification via SMTP"
    - "SMS notification via Twilio API"
    - "Webhook notification via HTTP POST"
    - "Local syslog logging"
    - "Notification retry on transient failure"
    - "Rate limiting to prevent notification storms"
  source: "Alert delivery requirements"
  rationale: "Multiple channels ensure alert delivery despite single-channel failures"
  dependencies: ["a3b4c5d6"]
```

### FR-015: Configuration Write

```yaml
- id: "c5d6e7f8"
  type: "functional"
  description: "System SHALL support write operations to inverter holding registers"
  acceptance_criteria:
    - "Operating mode selection (self-use, feed-in, backup, manual)"
    - "Charge time window configuration (start/end hour:minute)"
    - "Discharge time window configuration (start/end hour:minute)"
    - "Charge power limit (Watts)"
    - "Discharge power limit (Watts)"
    - "Values validated before transmission"
    - "Write result confirmed via readback"
  source: "Energy management requirements"
  rationale: "Configuration control enables automated energy optimization"
  dependencies: ["a1b2c3d4", "b8c9d0e1"]
```

### FR-016: Configuration Audit

```yaml
- id: "d6e7f8a9"
  type: "functional"
  description: "System SHALL maintain audit log of all configuration changes"
  acceptance_criteria:
    - "Timestamp of change"
    - "User or process identifier"
    - "Register address and previous value"
    - "Register address and new value"
    - "Operation result (success/failure)"
    - "Rollback capability for failed operations"
  source: "Operational accountability requirements"
  rationale: "Audit trail essential for troubleshooting and compliance"
  dependencies: ["c5d6e7f8"]
```

### FR-017: Development Emulator

```yaml
- id: "f8a9b0c1"
  type: "functional"
  description: "System SHALL provide Modbus TCP emulator for offline development and testing"
  acceptance_criteria:
    - "Emulates Solax X3 Hybrid register map"
    - "Dynamic state simulation (time-based PV power curve)"
    - "Battery charge/discharge modeling"
    - "Realistic value ranges and behaviors"
    - "Supports read and write operations"
  source: "Development workflow requirements"
  rationale: "Emulator enables testing without physical hardware"
  dependencies: []
```

### FR-018: HTTP Telemetry Server

```yaml
- id: "1a2b3c4d"
  type: "functional"
  description: "System SHALL optionally serve live single-inverter telemetry over HTTP to LAN clients"
  acceptance_criteria:
    - "Server activated via opt-in command-line flag; default behaviour unchanged"
    - "Server reads most recent polled telemetry from shared state; does not poll inverter directly"
    - "JSON endpoint returns current telemetry"
    - "Static HTML dashboard served to browser clients"
    - "Bind address all-interfaces; port configurable, non-privileged default"
    - "Requests from non-permitted source IP ranges rejected (HTTP 403)"
    - "Permitted source ranges configurable; default RFC 1918 plus link-local (169.254.0.0/16)"
    - "IPv4 only"
  source: "Headless deployment monitoring requirements"
  rationale: "Headless devices require remote access to live telemetry without a local console"
  dependencies: ["a1b2c3d4", "a7b8c9d0"]
```

### FR-019: Historical Telemetry Endpoint

```yaml
- id: "2e5f8a1b"
  type: "functional"
  description: "System SHALL serve downsampled historical telemetry over HTTP for trend visualisation"
  acceptance_criteria:
    - "JSON endpoint (/api/history) returns rollup series from the SQLite store"
    - "Stored series are the primitives: pv_power, battery_power, battery_soc, grid_power_total"
    - "Each rollup point exposes average, minimum, and maximum for the bucket"
    - "House load is derived client-side (house_load = pv_power - battery_power + grid_power_total), not stored"
    - "Endpoint governed by the same source-IP allowlist as /api/telemetry (HTTP 403 for non-permitted sources)"
    - "Dashboard renders inline sparklines client-side from the returned series"
  source: "Off-grid historical overview requirements"
  rationale: "A local historical trend lets an operator assess production and battery behaviour over time without an external tool"
  dependencies: ["d0e1f2a3", "1a2b3c4d"]
  notes: "Change: change-a2d5f7c9."
```

[Return to Table of Contents](<#table of contents>)

---

## Non-Functional Requirements

### NFR-001: Polling Performance

```yaml
- id: "a9b0c1d2"
  type: "non_functional"
  category: "performance"
  description: "System SHALL process Modbus requests within specified latency thresholds"
  acceptance_criteria:
    - "99.9% of requests complete within 1 second under normal conditions"
    - "Network latency up to 500ms tolerated without data loss"
    - "CPU utilization <10% on Raspberry Pi 4 class hardware"
  target_metric: "P99 latency <1000ms"
  source: "Real-time monitoring requirements"
  rationale: "Responsive monitoring requires predictable low latency"
  dependencies: []
```

### NFR-002: Memory Efficiency

```yaml
- id: "b0c1d2e3"
  type: "non_functional"
  category: "performance"
  description: "System SHALL operate within embedded hardware memory constraints"
  acceptance_criteria:
    - "Resident memory footprint ≤256MB for single-inverter deployment"
    - "Memory usage stable over 30-day runtime"
    - "No memory leaks detected in 72-hour stress test"
  target_metric: "RSS ≤256MB"
  source: "Raspberry Pi 4 deployment constraint"
  rationale: "Embedded deployment requires efficient memory usage"
  dependencies: []
```

### NFR-003: System Reliability

```yaml
- id: "c1d2e3f4"
  type: "non_functional"
  category: "reliability"
  description: "System SHALL achieve high availability with graceful degradation"
  acceptance_criteria:
    - "99.5% uptime over 30-day periods"
    - "Mean Time Between Failures (MTBF) >720 hours"
    - "Mean Time To Recovery (MTTR) <5 minutes"
    - "Automatic restart after crash"
    - "No data loss for buffered measurements (up to 1 hour)"
  target_metric: "Availability 99.5%"
  source: "Industrial monitoring requirements"
  rationale: "Continuous monitoring critical for operational awareness"
  dependencies: []
```

### NFR-004: Error Recovery

```yaml
- id: "d2e3f4a5"
  type: "non_functional"
  category: "reliability"
  description: "System SHALL recover gracefully from transient failures"
  acceptance_criteria:
    - "Network transients tolerated with automatic reconnection"
    - "Database outages handled via buffering (max 1 hour)"
    - "Partial data availability (e.g., PV available but battery unavailable)"
    - "Error states logged with context for diagnosis"
  target_metric: "MTTR <5 minutes"
  source: "Operational resilience requirements"
  rationale: "External system failures should not require manual intervention"
  dependencies: []
```

### NFR-005: Code Maintainability

```yaml
- id: "e3f4a5b6"
  type: "non_functional"
  category: "maintainability"
  description: "System SHALL be maintainable by developers with reasonable Python experience"
  acceptance_criteria:
    - "Cyclomatic complexity <15 per function"
    - "Test coverage >80% for core modules"
    - "Public interfaces documented with docstrings"
    - "Configuration externalized (no hardcoded values)"
    - "Hot-reload of configuration without restart"
  target_metric: "Code coverage >80%"
  source: "Long-term maintenance requirements"
  rationale: "Maintainability reduces total cost of ownership"
  dependencies: []
```

### NFR-006: Network Security

```yaml
- id: "f4a5b6c7"
  type: "non_functional"
  category: "security"
  description: "System SHALL implement defense-in-depth network security"
  acceptance_criteria:
    - "Modbus traffic isolated to dedicated VLAN or VPN"
    - "Firewall rules restrict access to required ports only"
    - "No direct internet exposure of Modbus endpoints"
    - "HTTP telemetry server governed by the same network isolation as Modbus; no direct internet exposure"
    - "HTTP telemetry server enforces a source-IP allowlist as a secondary control (defense-in-depth, not authentication)"
    - "TLS 1.3 for API endpoints (future)"
  target_metric: "Zero unauthorized network access"
  source: "Industrial security best practices"
  rationale: "Unsecured Modbus protocol requires network-level protection"
  dependencies: []
```

### NFR-007: Data Protection

```yaml
- id: "a5b6c7d8"
  type: "non_functional"
  category: "security"
  description: "System SHALL protect sensitive configuration data"
  acceptance_criteria:
    - "Configuration write operations require authentication"
    - "Passwords stored encrypted at rest"
    - "API keys stored in environment variables or secrets manager"
    - "Audit log of all security-relevant events"
  target_metric: "Zero plaintext credential exposure"
  source: "Security compliance requirements"
  rationale: "Unauthorized configuration changes pose safety and financial risks"
  dependencies: []
```

### NFR-008: Storage Efficiency

```yaml
- id: "b6c7d8e9"
  type: "non_functional"
  category: "efficiency"
  description: "System SHALL manage storage growth through retention policies"
  acceptance_criteria:
    - "SQLite file size bounded by the raw (24h) and rollup (30d) retention windows"
    - "Downsampling to the rollup table reduces long-term storage requirements"
    - "Steady-state file size is bounded and does not grow without limit"
  target_metric: "Bounded SQLite file size (well under 1 GB at the defined retention)"
  source: "Long-term operational sustainability"
  rationale: "Embedded systems have limited storage capacity"
  dependencies: []
  notes: "Change: change-a2d5f7c9. Bounds restated for the SQLite store."
```

### NFR-009: Installation Simplicity

```yaml
- id: "c7d8e9f0"
  type: "non_functional"
  category: "usability"
  description: "System SHALL be deployable with minimal technical knowledge on all supported platforms"
  acceptance_criteria:
    - "Installation requires <10 manual steps"
    - "Configuration via human-readable YAML"
    - "Automated dependency installation via pyproject.toml"
    - "Linux: systemd service for automatic startup"
    - "Health check endpoint for monitoring tools"
  target_metric: "Time-to-production <30 minutes"
  source: "Deployment efficiency requirements"
  rationale: "Complex installation increases operational risk and cost"
  dependencies: []
  notes: "Change: change-b4e7f1a9"
```

### NFR-010: Diagnostic Capability

```yaml
- id: "d8e9f0a1"
  type: "non_functional"
  category: "usability"
  description: "System SHALL provide comprehensive observability for troubleshooting"
  acceptance_criteria:
    - "Structured logging with configurable levels (DEBUG, INFO, WARNING, ERROR)"
    - "Error messages include actionable diagnostic information"
    - "Metrics exported for Prometheus/Grafana (future)"
    - "Register-level logging available in debug mode"
  target_metric: "Mean time to diagnose <15 minutes"
  source: "Operational support requirements"
  rationale: "Rapid diagnosis reduces downtime and support cost"
  dependencies: []
```

[Return to Table of Contents](<#table of contents>)

---

## Architectural Requirements

### AR-001: Modular Design

```yaml
- id: "e9f0a1b2"
  type: "architectural"
  description: "System SHALL implement modular architecture with clear domain separation"
  acceptance_criteria:
    - "Protocol domain encapsulates Modbus communication"
    - "Data domain encapsulates validation and persistence"
    - "Presentation domain encapsulates display formatting"
    - "Application domain encapsulates business logic"
    - "Domain interfaces well-defined and minimal"
  constraints:
    - "Domains communicate via interfaces only (no direct coupling)"
    - "Domain internal implementation details hidden"
  source: "Software architecture best practices"
  rationale: "Modularity enables independent evolution and testing of components"
  dependencies: []
```

### AR-002: Technology Stack

```yaml
- id: "f0a1b2c3"
  type: "architectural"
  description: "System SHALL use specified technology stack for implementation"
  acceptance_criteria:
    - "Python 3.9+ runtime"
    - "pymodbus 3.5.0+ for Modbus TCP"
    - "sqlite3 (Python standard library) for time-series storage"
    - "pyyaml for configuration"
    - "pytest for testing"
  constraints:
    - "No dependencies on proprietary libraries"
    - "All dependencies available via pip"
  source: "Technology selection decision"
  rationale: "Consistent technology stack reduces complexity and improves maintainability"
  dependencies: []
```

### AR-003: Target Platform

```yaml
- id: "a1b2c3d4"
  type: "architectural"
  description: "System SHALL operate on all supported target platforms"
  acceptance_criteria:
    - "Linux target: Debian 12 (Bookworm) on ARM64 (Raspberry Pi 4)"
    - "Development platform: macOS (primary), Linux"
    - "Cross-platform compatibility via standard Python"
    - "install.sh installs to /opt/solax-monitor with a symlink in /usr/local/bin"
  constraints:
    - "No platform-specific extensions without abstraction"
    - "Linux deployment via systemd service"
    - "Linux install path: /opt/solax-monitor"
  source: "Deployment platform decision; change-b4e7f1a9 (added macOS); reversed 2026-06-25 (Linux-only deployment)"
  rationale: "Deployment target is Raspberry Pi / Debian Linux; macOS is retained as development platform only"
  dependencies: []
```

### AR-004: Error Handling Strategy

```yaml
- id: "b2c3d4e5"
  type: "architectural"
  description: "System SHALL implement consistent error handling across all components"
  acceptance_criteria:
    - "Exceptions logged with full traceback"
    - "Transient errors handled via retry with exponential backoff"
    - "Critical errors trigger graceful shutdown"
    - "Partial failure tolerated (continue with available data)"
  constraints:
    - "No silent failures (all errors logged)"
    - "Error context preserved for diagnosis"
  source: "Reliability requirements"
  rationale: "Consistent error handling improves debuggability and operational resilience"
  dependencies: []
```

### AR-005: Testing Strategy

```yaml
- id: "c3d4e5f6"
  type: "architectural"
  description: "System SHALL employ comprehensive testing at multiple levels"
  acceptance_criteria:
    - "Unit tests for individual functions and classes"
    - "Integration tests for component interactions"
    - "System tests for end-to-end workflows"
    - "Test coverage >80% for core modules"
    - "Continuous integration via pytest"
  constraints:
    - "Tests executable without physical hardware (use emulator)"
    - "Test isolation via mocking and temporary environments"
  source: "Quality assurance requirements"
  rationale: "Comprehensive testing prevents regressions and validates requirements"
  dependencies: []
```

### AR-006: Configuration Management

```yaml
- id: "d4e5f6a7"
  type: "architectural"
  description: "System SHALL externalize all configuration via files and environment variables"
  acceptance_criteria:
    - "Configuration via YAML files"
    - "Sensitive values via environment variables"
    - "Configuration schema validation"
    - "Hot-reload of non-structural configuration"
    - "Configuration documentation via examples"
  constraints:
    - "No hardcoded IP addresses, credentials, or thresholds"
    - "Configuration changes logged to audit trail"
  source: "Operational flexibility requirements"
  rationale: "Externalized configuration enables deployment customization without code changes"
  dependencies: []
```

### AR-007: Data Model

```yaml
- id: "e5f6a7b8"
  type: "architectural"
  description: "System SHALL define explicit data models for all domain entities"
  acceptance_criteria:
    - "Python dataclasses for structured data"
    - "Type hints for all attributes"
    - "Validation rules documented"
    - "Serialization/deserialization methods"
  constraints:
    - "Immutable data models where feasible"
    - "Schema versioning for database compatibility"
  source: "Data integrity requirements"
  rationale: "Explicit data models prevent type confusion and enable validation"
  dependencies: []
```

### AR-008: Extensibility

```yaml
- id: "f6a7b8c9"
  type: "architectural"
  description: "System SHALL support future extension via plugin architecture"
  acceptance_criteria:
    - "Notification channel plugins"
    - "Data store adapters (beyond the default SQLite store)"
    - "Plugin discovery and loading mechanism"
  constraints:
    - "Core system functionality independent of plugins"
    - "Plugin API stability guaranteed"
  source: "Future enhancement requirements"
  rationale: "Plugin architecture enables customization without forking codebase"
  dependencies: []
```

[Return to Table of Contents](<#table of contents>)

---

## Traceability

### Design References

| Requirement ID | Design Document | Design Section |
|----------------|-----------------|----------------|
| a1b2c3d4 | design-solax-modbus-master.md | System Overview |
| a1b2c3d4 | design-8f3a1b2c-domain_protocol.md | Protocol Domain |
| a1b2c3d4 | design-c1a2b3d4-component_protocol_client.md | SolaxInverterClient |
| b2c3d4e5 | design-solax-modbus-master.md | Data Design |
| c3d4e5f6 | design-solax-modbus-master.md | Data Design |
| d4e5f6a7 | design-solax-modbus-master.md | Data Design |
| e5f6a7b8 | design-solax-modbus-master.md | Data Design |
| f6a7b8c9 | design-8f3a1b2c-domain_protocol.md | Data Type Conversion |
| a7b8c9d0 | design-af5c3d4e-domain_presentation.md | Presentation Domain |
| a7b8c9d0 | design-d3c4d5e6-component_presentation_console.md | InverterDisplay |
| b8c9d0e1 | design-c1a2b3d4-component_protocol_client.md | Connection Management |
| c9d0e1f2 | design-9e4b2c3d-domain_data.md | Data Validation |
| c9d0e1f2 | design-b7c8d9e0-component_data_storage.md | Write-path validation |
| d0e1f2a3 | design-9e4b2c3d-domain_data.md | Time-Series Storage |
| d0e1f2a3 | design-b7c8d9e0-component_data_storage.md | TimeSeriesStore |
| f2a3b4c5 | design-b7c8d9e0-component_data_storage.md | Retention Policies |
| 2e5f8a1b | design-9b7e2c4a-component_presentation_server.md | Routes (/api/history) |
| 2e5f8a1b | design-b7c8d9e0-component_data_storage.md | History query |
| a3b4c5d6 | design-bf6d4e5f-domain_application.md | Application Domain |
| a3b4c5d6 | design-e0f1a2b3-component_application_alerting.md | AlertManager |
| b4c5d6e7 | design-e0f1a2b3-component_application_alerting.md | Notification Dispatch |
| c5d6e7f8 | design-f5e6f7a8-component_protocol_controller.md | InverterController |
| d6e7f8a9 | design-f5e6f7a8-component_protocol_controller.md | Audit Logging |
| f8a9b0c1 | design-c2b3c4d5-component_protocol_emulator.md | SolaxEmulator |
| 1a2b3c4d | design-af5c3d4e-domain_presentation.md | Presentation Domain |
| 1a2b3c4d | design-9b7e2c4a-component_presentation_server.md | TelemetryServer |

Retired references (change-a2d5f7c9): e1f2a3b4 -> design-c8d9e0f1 (DataBuffer) and the standalone c9d0e1f2 -> design-a6b7c8d9 (DataValidator) mapping are withdrawn.

### Test References

*To be populated during test documentation phase (P06)*

### Code References

| Requirement ID | Component | File Path |
|----------------|-----------|-----------|
| a1b2c3d4 | SolaxInverterClient | src/solax_modbus/main.py |
| b2c3d4e5 | SolaxInverterClient | src/solax_modbus/main.py |
| c3d4e5f6 | SolaxInverterClient | src/solax_modbus/main.py |
| d4e5f6a7 | SolaxInverterClient | src/solax_modbus/main.py |
| e5f6a7b8 | SolaxInverterClient | src/solax_modbus/main.py |
| f6a7b8c9 | SolaxInverterClient | src/solax_modbus/main.py |
| a7b8c9d0 | InverterDisplay | src/solax_modbus/main.py |
| b8c9d0e1 | SolaxInverterClient | src/solax_modbus/main.py |
| f8a9b0c1 | SolaxEmulator | src/tools/emulator/solax_emulator.py |
| 1a2b3c4d | TelemetryServer | src/solax_modbus/presentation/server.py |
| 2e5f8a1b | TelemetryServer / TimeSeriesStore | src/solax_modbus/presentation/server.py, src/solax_modbus/data/storage.py |

[Return to Table of Contents](<#table of contents>)

---

## Validation

### Completeness Check

✓ **Complete**: All functional, non-functional, and architectural requirements captured from design documents and deprecated SDS.

**Coverage:**
- Data acquisition and display: FR-001 through FR-007
- Connection management: FR-008
- Data quality and persistence: FR-009, FR-010, FR-012 (FR-011 retired)
- Historical telemetry endpoint: FR-019
- Monitoring and alerting: FR-013 through FR-014
- Configuration control: FR-015 through FR-016
- Development infrastructure: FR-017
- Performance constraints: NFR-001 through NFR-002
- Reliability: NFR-003 through NFR-004
- Maintainability: NFR-005
- Security: NFR-006 through NFR-007
- Scalability: NFR-008
- Usability: NFR-009 through NFR-010
- Architecture: AR-001 through AR-008

### Clarity Check

✓ **Clear**: All requirements state specific, measurable acceptance criteria using SHALL language and avoiding ambiguity.

**Verification:**
- Requirements use SHALL (mandatory), SHOULD (recommended), MAY (optional)
- Acceptance criteria provide objective pass/fail conditions
- Technical terms defined in Glossary
- Numeric thresholds explicitly stated

### Testability Check

✓ **Testable**: All requirements include acceptance criteria enabling verification via unit, integration, or system testing.

**Verification:**
- Functional requirements testable via automated tests against emulator and hardware
- Non-functional requirements testable via performance benchmarks and stress tests
- Architectural requirements testable via code inspection and structure analysis

### Conflicts Identified

**None**: No conflicting requirements identified during validation.

[Return to Table of Contents](<#table of contents>)

---

## Glossary

| Term | Definition |
|------|------------|
| Modbus TCP | Ethernet-based variant of Modbus protocol using TCP/IP transport |
| Register | 16-bit data storage location in Modbus device address space |
| Input Register | Read-only register accessed via function code 0x04 |
| Holding Register | Read-write register accessed via function codes 0x03/0x06 |
| MPPT | Maximum Power Point Tracking - solar charge controller optimization |
| SOC | State of Charge - battery capacity as percentage of full charge |
| Unit ID | Modbus device identifier (slave address), typically 1 for single inverter |
| Feed-in | Export of excess solar generation to electrical grid |
| Scaling Factor | Multiplier applied to raw register value to obtain engineering units |
| Two's Complement | Binary representation method for signed integers |
| RFC 1918 | IETF specification defining private IPv4 address ranges not routable on the public internet (10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16) |
| Source-IP Allowlist | Access control admitting requests only from configured source address ranges; a network-address filter, not user authentication |
| Link-local Address | IPv4 address in 169.254.0.0/16, valid only on a single network segment; used by the USB-gadget direct-connection path |
| SQLite | Embedded, serverless relational database provided by the Python standard library (sqlite3); the local time-series store |
| Rollup | Downsampled aggregate table holding average, minimum, and maximum per time bucket |
| Retention Policy | Rules governing data aging and deletion in the local store |
| Downsampling | Aggregation of fine-grained data to coarser time resolution |
| Exponential Backoff | Retry strategy with geometrically increasing delays |
| Circuit Breaker | Fault tolerance pattern preventing cascading failures |

[Return to Table of Contents](<#table of contents>)

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-01-08 | Initial requirements document reverse-engineered from design documents and deprecated SDS |
| 1.1 | 2026-01-08 | Removed FR-017 Multi-Inverter Coordination. Moved multi-inverter to out-of-scope. Updated NFR-002 for single-inverter (256MB). Replaced NFR-008 Scalability with Storage Efficiency. Updated AR-008 Extensibility. Removed traceability entries. |
| 1.2 | 2026-03-14 | AR-003: added macOS as supported target platform (x86_64 and ARM64). NFR-009: added macOS manual-start acceptance criterion; systemd criterion scoped to Linux only. Change: change-b4e7f1a9. |
| 1.3 | 2026-06-25 | Removed macOS as deployment target (reverses 1.2). AR-003: dropped macOS target, macOS constraints, and OS-detection criterion; retained macOS as development platform. NFR-009: dropped macOS manual-start criterion. |
| 1.4 | 2026-06-26 | Brought web UI in-scope (embedded HTTP telemetry server). Added FR-018 HTTP Telemetry Server. Amended NFR-006 with HTTP isolation and source-IP allowlist criteria. Added traceability rows and glossary terms (RFC 1918, source-IP allowlist, link-local). |
| 1.5 | 2026-07-03 | Updated SolaxEmulator source path: src/solax_modbus/emulator/solax_emulator.py → src/tools/emulator/solax_emulator.py (see design-c2b3c4d5 1.5). |
| 1.6 | 2026-07-16 | Off-grid UI / SQLite history (change-a2d5f7c9). FR-010 persistence retargeted InfluxDB → local SQLite. FR-012 retention retargeted to raw 1-min/24h + rollup 15-min/30d (avg/min/max). FR-011 (buffering) retired. FR-009 narrowed to write-path range validation. Added FR-019 (/api/history). NFR-008 restated for SQLite. AR-002 dropped influxdb-client (added sqlite3). AR-008 generalised store-adapter wording. Updated traceability (withdrew DataValidator/DataBuffer standalone rows; added FR-019 rows) and glossary (replaced InfluxDB with SQLite/Rollup). |

---

Copyright (c) 2025 William Watson. This work is licensed under the MIT License.
