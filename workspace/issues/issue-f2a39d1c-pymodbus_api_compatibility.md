# Issue: Pymodbus API Compatibility - Deprecated 'slave' Parameter

Created: 2025-01-21

---

## Table of Contents

- [Issue Information](<#issue information>)
- [Source](<#source>)
- [Affected Scope](<#affected scope>)
- [Reproduction](<#reproduction>)
- [Behavior](<#behavior>)
- [Environment](<#environment>)
- [Analysis](<#analysis>)
- [Resolution](<#resolution>)
- [Verification](<#verification>)
- [Prevention](<#prevention>)
- [Traceability](<#traceability>)
- [Version History](<#version history>)

---

## Issue Information

```yaml
issue_info:
  id: "issue-f2a39d1c"
  title: "Pymodbus API Compatibility - Deprecated 'slave' Parameter"
  date: "2025-01-21"
  reporter: "William Watson"
  status: "open"
  severity: "critical"
  type: "bug"
  iteration: 1
  coupled_docs:
    change_ref: "change-2b7a0458"
    change_iteration: 1
```

[Return to Table of Contents](<#table of contents>)

---

## Source

```yaml
source:
  origin: "user_report"
  test_ref: ""
  description: "Runtime TypeError when reading inverter registers due to pymodbus API incompatibility"
```

[Return to Table of Contents](<#table of contents>)

---

## Affected Scope

```yaml
affected_scope:
  components:
    - name: "SolaxInverterClient"
      file_path: "/opt/solax-monitor/venv/lib/python3.13/site-packages/solax_modbus/main.py"
  designs:
    - design_ref: ""
  version: "Current deployment"
```

[Return to Table of Contents](<#table of contents>)

---

## Reproduction

```yaml
reproduction:
  prerequisites: "Deployed solax-modbus application with pymodbus 3.x"
  steps:
    - "Start solax-modbus application"
    - "Application attempts to read input registers"
    - "TypeError raised at line 162"
  frequency: "always"
  reproducibility_conditions: "Occurs on every register read operation"
  preconditions: "Application running with pymodbus 3.x installed"
  test_data: "N/A - occurs during normal operation"
  error_output: |
    TypeError: ModbusClientMixin.read_input_registers() got an unexpected keyword argument 'slave'
    2026-01-21 13:12:29,159 - solax_modbus.main - ERROR - Unexpected error reading Inverter temperature and run mode: ModbusClientMixin.read_input_registers() got an unexpected keyword argument 'slave'
    Traceback (most recent call last):
      File "/opt/solax-monitor/venv/lib/python3.13/site-packages/solax_modbus/main.py", line 162, in read_registers
        result = self.client.read_input_registers(
            address=address,
            count=count,
            slave=self.unit_id
        )
    TypeError: ModbusClientMixin.read_input_registers() got an unexpected keyword argument 'slave'
```

[Return to Table of Contents](<#table of contents>)

---

## Behavior

```yaml
behavior:
  expected: "Application successfully reads input registers from Modbus device"
  actual: "Application crashes with TypeError on every register read attempt"
  impact: "Complete application failure - no monitoring data can be collected"
  workaround: "Downgrade to pymodbus 2.x (not recommended - temporary only)"
```

[Return to Table of Contents](<#table of contents>)

---

## Environment

```yaml
environment:
  python_version: "3.13"
  os: "Linux (Raspberry Pi deployment)"
  dependencies:
    - library: "pymodbus"
      version: "3.x (exact version TBD)"
  domain: "domain_1"
```

[Return to Table of Contents](<#table of contents>)

---

## Analysis

```yaml
analysis:
  root_cause: "Code written for pymodbus 2.x API which used 'slave' parameter. Pymodbus 3.x deprecated 'slave' in favor of 'unit' parameter. Deployed environment has pymodbus 3.x causing API mismatch."
  technical_notes: |
    The pymodbus library changed its API between major versions:
    - pymodbus 2.x: read_input_registers(..., slave=unit_id)
    - pymodbus 3.x: read_input_registers(..., unit=unit_id)
    
    Line 162 in main.py uses the deprecated parameter name, causing immediate failure.
    All Modbus read operations (read_input_registers, read_holding_registers) likely affected.
  related_issues:
    - issue_ref: ""
      relationship: ""
```

[Return to Table of Contents](<#table of contents>)

---

## Resolution

```yaml
resolution:
  assigned_to: "Claude Desktop + Claude Code"
  target_date: "2025-01-21"
  approach: |
    1. Update all Modbus read calls to use 'unit' instead of 'slave' parameter
    2. Verify pyproject.toml specifies pymodbus version constraint
    3. Review all read operations in SolaxInverterClient class
    4. Update error handling if needed
  change_ref: "change-2b7a0458"
  resolved_date: ""
  resolved_by: ""
  fix_description: ""
```

[Return to Table of Contents](<#table of contents>)

---

## Verification

```yaml
verification:
  verified_date: ""
  verified_by: ""
  test_results: ""
  closure_notes: ""
```

[Return to Table of Contents](<#table of contents>)

---

## Prevention

```yaml
prevention:
  preventive_measures: |
    - Enforce explicit pymodbus version constraint in pyproject.toml
    - Add API compatibility testing to test suite
    - Document pymodbus version requirements in deployment docs
  process_improvements: |
    - Add dependency version verification to deployment checklist
    - Include library version validation in test environment setup
```

[Return to Table of Contents](<#table of contents>)

---

## Traceability

```yaml
traceability:
  design_refs:
    - "design-<uuid>-component_modbus_client"
  change_refs:
    - "change-2b7a0458"
  test_refs:
    - ""
```

[Return to Table of Contents](<#table of contents>)

---

## Version History

| Version | Date       | Author          | Changes                    |
| ------- | ---------- | --------------- | -------------------------- |
| 1.0     | 2025-01-21 | William Watson  | Initial issue creation     |

---

Copyright (c) 2025 William Watson. This work is licensed under the MIT License.
