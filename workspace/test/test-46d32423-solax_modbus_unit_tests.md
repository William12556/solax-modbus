Created: 2026 March 13

---

# Test Document: Solax Modbus Unit Tests

`test-46d32423-solax_modbus_unit_tests`

---

## Table of Contents

- [1.0 Test Information](<#1.0 test information>)
- [2.0 Source](<#2.0 source>)
- [3.0 Scope](<#3.0 scope>)
- [4.0 Test Environment](<#4.0 test environment>)
- [5.0 Test Cases](<#5.0 test cases>)
  - [5.1 TestSolaxInverterClient](<#5.1 testsolaxinverterclient>)
  - [5.2 TestInverterDisplay](<#5.2 testinverterdisplay>)
  - [5.3 TestMainExecution](<#5.3 testmainexecution>)
- [6.0 Coverage](<#6.0 coverage>)
- [7.0 Test Execution Summary](<#7.0 test execution summary>)
- [8.0 Defect Summary](<#8.0 defect summary>)
- [9.0 Verification](<#9.0 verification>)
- [10.0 Traceability](<#10.0 traceability>)
- [11.0 Notes](<#11.0 notes>)
- [Version History](<#version history>)

---

## 1.0 Test Information

```yaml
test_info:
  id: "test-46d32423"
  title: "Solax Modbus Unit Tests"
  date: "2026-03-13"
  author: "William Watson"
  status: "planned"
  type: "unit"
  priority: "high"
  iteration: 1
  coupled_docs:
    prompt_ref: "prompt-46d32423"
    prompt_iteration: 1
    result_ref: ""
```

> **Note:** This test document formalises an existing test suite created prior to full P06 governance coupling. The `prompt_ref` references the nearest prior prompt document (`prompt-46d32423-pymodbus_api_fix.md`). The test suite covers the complete `SolaxInverterClient` and `InverterDisplay` implementations, not solely the pymodbus API fix.

[Return to Table of Contents](<#table of contents>)

---

## 2.0 Source

```yaml
source:
  test_target: "src/solax_modbus/main.py — SolaxInverterClient, InverterDisplay, main()"
  design_refs:
    - "workspace/design/design-c1a2b3d4-component_protocol_client.md"
    - "workspace/design/design-d3c4d5e6-component_presentation_console.md"
    - "workspace/design/design-e4d5e6f7-component_application_main.md"
    - "workspace/design/design-solax-modbus-master.md"
  change_refs:
    - "workspace/prompt/closed/prompt-46d32423-pymodbus_api_fix.md"
  requirement_refs: []
```

[Return to Table of Contents](<#table of contents>)

---

## 3.0 Scope

```yaml
scope:
  description: >
    Unit tests for the solax-modbus monitoring application. Covers Modbus TCP
    client lifecycle, register read/decode operations, data processing for grid,
    PV, and battery subsystems, console display logic, and main execution loop
    error handling. All Modbus TCP communication is mocked.
  test_objectives:
    - "Verify SolaxInverterClient initialises with correct default parameters"
    - "Verify connection lifecycle: connect, retry with exponential backoff, disconnect"
    - "Verify register read operations: success, Modbus error, exception paths"
    - "Verify data processing: grid (three-phase), PV (dual MPPT), battery"
    - "Verify complete poll cycle returns correctly structured data"
    - "Verify InverterDisplay output: no data, complete data, power flow states"
    - "Verify main() loop handles KeyboardInterrupt and performs cleanup"
  in_scope:
    - "SolaxInverterClient class — all public and helper methods"
    - "InverterDisplay class — display_statistics method"
    - "main() function — argument parsing, loop control, graceful exit"
  out_scope:
    - "Modbus TCP emulator (src/solax_modbus/emulator/)"
    - "Integration tests against live or emulated Modbus TCP endpoints"
    - "System tests on Raspberry Pi target hardware"
    - "Build and packaging scripts (build.sh, install.sh)"
  dependencies:
    - "pytest >= 7.0.0"
    - "pymodbus >= 3.11.0"
    - "unittest.mock (stdlib)"
```

[Return to Table of Contents](<#table of contents>)

---

## 4.0 Test Environment

```yaml
test_environment:
  python_version: "3.11"
  os: "macOS (development); Debian 12 Bookworm (target validation)"
  libraries:
    - name: "pytest"
      version: ">=7.0.0"
    - name: "pymodbus"
      version: ">=3.11.0"
    - name: "pytest-cov"
      version: ">=4.0.0"
  test_framework: "pytest"
  test_data_location: "tests/test_solax_poll.py"
```

[Return to Table of Contents](<#table of contents>)

---

## 5.0 Test Cases

### 5.1 TestSolaxInverterClient

#### TC-001: Client Initialisation

```yaml
- case_id: "TC-001"
  description: "Verify SolaxInverterClient initialises with correct parameter defaults"
  category: "positive"
  preconditions:
    - "No Modbus connection established"
  test_steps:
    - step: "1"
      action: "Instantiate SolaxInverterClient('192.168.1.100', port=502, unit_id=1)"
    - step: "2"
      action: "Assert attribute values"
  inputs:
    - parameter: "ip"
      value: "192.168.1.100"
      type: "str"
    - parameter: "port"
      value: "502"
      type: "int"
    - parameter: "unit_id"
      value: "1"
      type: "int"
  expected_outputs:
    - field: "client.ip"
      expected_value: "'192.168.1.100'"
      validation: "assertEqual"
    - field: "client.port"
      expected_value: "502"
      validation: "assertEqual"
    - field: "client.unit_id"
      expected_value: "1"
      validation: "assertEqual"
    - field: "client.client"
      expected_value: "None"
      validation: "assertIsNone"
    - field: "client.max_retries"
      expected_value: "3"
      validation: "assertEqual"
    - field: "client.retry_delay"
      expected_value: "1"
      validation: "assertEqual"
  postconditions:
    - "No side effects"
  execution:
    status: "not_run"
    pass_fail_criteria: "All assertions pass"
```

#### TC-002: Connect Success

```yaml
- case_id: "TC-002"
  description: "Verify connect() succeeds on first attempt and assigns internal client"
  category: "positive"
  preconditions:
    - "ModbusTcpClient patched to return mock that reports connect() = True"
  test_steps:
    - step: "1"
      action: "Call client.connect()"
    - step: "2"
      action: "Assert return value and internal state"
  inputs:
    - parameter: "mock_modbus.connect.return_value"
      value: "True"
      type: "bool"
  expected_outputs:
    - field: "return value"
      expected_value: "True"
      validation: "assertTrue"
    - field: "client.client"
      expected_value: "mock_modbus instance"
      validation: "assertEqual"
    - field: "ModbusTcpClient call args"
      expected_value: "('192.168.1.100', port=502)"
      validation: "assert_called_once_with"
  postconditions:
    - "client.client is assigned"
  execution:
    status: "not_run"
    pass_fail_criteria: "All assertions pass"
```

#### TC-003: Connect With Retry (Exponential Backoff)

```yaml
- case_id: "TC-003"
  description: "Verify connect() retries on failure with exponential backoff delays"
  category: "negative"
  preconditions:
    - "mock_modbus.connect() returns False, False, True (succeed on attempt 3)"
    - "time.sleep patched"
  test_steps:
    - step: "1"
      action: "Call client.connect()"
    - step: "2"
      action: "Assert retry count and sleep call sequence"
  inputs:
    - parameter: "mock_modbus.connect.side_effect"
      value: "[False, False, True]"
      type: "list"
  expected_outputs:
    - field: "return value"
      expected_value: "True"
      validation: "assertTrue"
    - field: "connect call count"
      expected_value: "3"
      validation: "assertEqual"
    - field: "sleep call args"
      expected_value: "[call(1), call(2)]"
      validation: "assertEqual"
  postconditions:
    - "client.client is assigned"
  execution:
    status: "not_run"
    pass_fail_criteria: "All assertions pass"
```

#### TC-004: Connect Failure After Max Retries

```yaml
- case_id: "TC-004"
  description: "Verify connect() returns False after exhausting max_retries"
  category: "negative"
  preconditions:
    - "mock_modbus.connect() always returns False"
    - "time.sleep patched"
  test_steps:
    - step: "1"
      action: "Call client.connect()"
    - step: "2"
      action: "Assert return value and attempt count"
  inputs:
    - parameter: "mock_modbus.connect.return_value"
      value: "False"
      type: "bool"
  expected_outputs:
    - field: "return value"
      expected_value: "False"
      validation: "assertFalse"
    - field: "connect call count"
      expected_value: "3"
      validation: "assertEqual"
    - field: "sleep call count"
      expected_value: "2"
      validation: "assertEqual"
  postconditions:
    - "client.client may be assigned to failed mock"
  execution:
    status: "not_run"
    pass_fail_criteria: "All assertions pass"
```

#### TC-005: Disconnect Normal

```yaml
- case_id: "TC-005"
  description: "Verify disconnect() calls close() on the internal Modbus client"
  category: "positive"
  preconditions:
    - "client.client assigned to mock"
  test_steps:
    - step: "1"
      action: "Call client.disconnect()"
    - step: "2"
      action: "Assert mock_client.close called once"
  inputs: []
  expected_outputs:
    - field: "mock_client.close call count"
      expected_value: "1"
      validation: "assert_called_once"
  postconditions:
    - "No exception raised"
  execution:
    status: "not_run"
    pass_fail_criteria: "assert_called_once passes; no exception raised"
```

#### TC-006: Disconnect With Error

```yaml
- case_id: "TC-006"
  description: "Verify disconnect() swallows exceptions from close()"
  category: "negative"
  preconditions:
    - "mock_client.close() raises Exception('Connection error')"
  test_steps:
    - step: "1"
      action: "Call client.disconnect()"
    - step: "2"
      action: "Verify no exception propagates"
  inputs:
    - parameter: "mock_client.close.side_effect"
      value: "Exception('Connection error')"
      type: "Exception"
  expected_outputs:
    - field: "exception raised"
      expected_value: "None"
      validation: "no exception"
  postconditions:
    - "close() was called"
  execution:
    status: "not_run"
    pass_fail_criteria: "No exception propagates to caller"
```

#### TC-007 to TC-011: Numeric Conversion Helpers

```yaml
- case_id: "TC-007"
  description: "_to_signed(): positive values pass through unchanged"
  category: "boundary"
  inputs:
    - parameter: "value"
      value: "100"
      type: "int"
    - parameter: "value"
      value: "32767"
      type: "int"
  expected_outputs:
    - field: "_to_signed(100)"
      expected_value: "100"
      validation: "assertEqual"
    - field: "_to_signed(32767)"
      expected_value: "32767"
      validation: "assertEqual"
  execution:
    status: "not_run"
    pass_fail_criteria: "All assertions pass"

- case_id: "TC-008"
  description: "_to_signed(): values >= 32768 are converted to negative (two's complement)"
  category: "boundary"
  inputs:
    - parameter: "value"
      value: "32768"
      type: "int"
    - parameter: "value"
      value: "65535"
      type: "int"
  expected_outputs:
    - field: "_to_signed(32768)"
      expected_value: "-32768"
      validation: "assertEqual"
    - field: "_to_signed(65535)"
      expected_value: "-1"
      validation: "assertEqual"
  execution:
    status: "not_run"
    pass_fail_criteria: "All assertions pass"

- case_id: "TC-009"
  description: "_to_signed_32(): positive 32-bit signed conversion"
  category: "positive"
  inputs:
    - parameter: "low"
      value: "0x1234"
      type: "int"
    - parameter: "high"
      value: "0x0001"
      type: "int"
  expected_outputs:
    - field: "result"
      expected_value: "0x00011234"
      validation: "assertEqual"
  execution:
    status: "not_run"
    pass_fail_criteria: "assertEqual passes"

- case_id: "TC-010"
  description: "_to_signed_32(): negative 32-bit signed conversion (all 0xFFFF)"
  category: "boundary"
  inputs:
    - parameter: "low"
      value: "0xFFFF"
      type: "int"
    - parameter: "high"
      value: "0xFFFF"
      type: "int"
  expected_outputs:
    - field: "result"
      expected_value: "-1"
      validation: "assertEqual"
  execution:
    status: "not_run"
    pass_fail_criteria: "assertEqual passes"

- case_id: "TC-011"
  description: "_to_unsigned_32(): 32-bit unsigned combination of two 16-bit registers"
  category: "positive"
  inputs:
    - parameter: "low"
      value: "0x1234"
      type: "int"
    - parameter: "high"
      value: "0x5678"
      type: "int"
  expected_outputs:
    - field: "result"
      expected_value: "0x56781234"
      validation: "assertEqual"
  execution:
    status: "not_run"
    pass_fail_criteria: "assertEqual passes"
```

#### TC-012 to TC-014: Register Read Operations

```yaml
- case_id: "TC-012"
  description: "read_registers(): returns register list on success"
  category: "positive"
  preconditions:
    - "mock Modbus client assigned; read_input_registers returns non-error result with registers=[100,200,300]"
  test_steps:
    - step: "1"
      action: "Call client.read_registers(0x0003, 3, 'test registers')"
    - step: "2"
      action: "Assert return value and call arguments"
  inputs:
    - parameter: "address"
      value: "0x0003"
      type: "int"
    - parameter: "count"
      value: "3"
      type: "int"
    - parameter: "description"
      value: "'test registers'"
      type: "str"
  expected_outputs:
    - field: "return value"
      expected_value: "[100, 200, 300]"
      validation: "assertEqual"
    - field: "read_input_registers call args"
      expected_value: "address=0x0003, count=3, device_id=1"
      validation: "assert_called_once_with"
  execution:
    status: "not_run"
    pass_fail_criteria: "All assertions pass"

- case_id: "TC-013"
  description: "read_registers(): returns None when response.isError() is True"
  category: "negative"
  preconditions:
    - "mock_result.isError() returns True"
  inputs:
    - parameter: "address"
      value: "0x0003"
      type: "int"
    - parameter: "count"
      value: "3"
      type: "int"
  expected_outputs:
    - field: "return value"
      expected_value: "None"
      validation: "assertIsNone"
  execution:
    status: "not_run"
    pass_fail_criteria: "assertIsNone passes"

- case_id: "TC-014"
  description: "read_registers(): returns None when ModbusException raised"
  category: "negative"
  preconditions:
    - "mock_modbus.read_input_registers raises ModbusException"
  inputs:
    - parameter: "side_effect"
      value: "ModbusException('Test error')"
      type: "exception"
  expected_outputs:
    - field: "return value"
      expected_value: "None"
      validation: "assertIsNone"
  execution:
    status: "not_run"
    pass_fail_criteria: "assertIsNone passes; no exception propagates"
```

#### TC-015 to TC-017: Data Processing

```yaml
- case_id: "TC-015"
  description: "_process_grid_data(): correctly decodes three-phase grid register block"
  category: "positive"
  preconditions:
    - "12-register input representing R/S/T phase data"
  inputs:
    - parameter: "regs"
      value: "[2302, 42, 966, 5001, 2298, 38, 873, 5002, 2311, 45, 1040, 5003]"
      type: "list[int]"
  expected_outputs:
    - field: "grid_voltage_r"
      expected_value: "230.2 (±0.01)"
      validation: "pytest.approx"
    - field: "grid_current_r"
      expected_value: "4.2 (±0.01)"
      validation: "pytest.approx"
    - field: "grid_power_r"
      expected_value: "966"
      validation: "assertEqual"
    - field: "grid_frequency_r"
      expected_value: "50.01 (±0.001)"
      validation: "pytest.approx"
  execution:
    status: "not_run"
    pass_fail_criteria: "All assertions pass"

- case_id: "TC-016"
  description: "_process_pv_data(): correctly decodes dual-MPPT PV register blocks"
  category: "positive"
  inputs:
    - parameter: "vc_regs"
      value: "[3854, 3821, 82, 78]"
      type: "list[int]"
    - parameter: "power_regs"
      value: "[3160, 2980]"
      type: "list[int]"
  expected_outputs:
    - field: "pv1_voltage"
      expected_value: "385.4 (±0.01)"
      validation: "pytest.approx"
    - field: "pv2_voltage"
      expected_value: "382.1 (±0.01)"
      validation: "pytest.approx"
    - field: "pv1_current"
      expected_value: "8.2 (±0.01)"
      validation: "pytest.approx"
    - field: "pv2_current"
      expected_value: "7.8 (±0.01)"
      validation: "pytest.approx"
    - field: "pv1_power"
      expected_value: "3160"
      validation: "assertEqual"
    - field: "pv2_power"
      expected_value: "2980"
      validation: "assertEqual"
  execution:
    status: "not_run"
    pass_fail_criteria: "All assertions pass"

- case_id: "TC-017"
  description: "_process_battery_data(): correctly decodes battery register block"
  category: "positive"
  inputs:
    - parameter: "regs"
      value: "[2705, 124, 3354, 0, 24, 0, 0, 0, 78]"
      type: "list[int]"
  expected_outputs:
    - field: "battery_voltage"
      expected_value: "270.5 (±0.01)"
      validation: "pytest.approx"
    - field: "battery_current"
      expected_value: "12.4 (±0.01)"
      validation: "pytest.approx"
    - field: "battery_power"
      expected_value: "3354"
      validation: "assertEqual"
    - field: "battery_temperature"
      expected_value: "24"
      validation: "assertEqual"
    - field: "battery_soc"
      expected_value: "78"
      validation: "assertEqual"
  execution:
    status: "not_run"
    pass_fail_criteria: "All assertions pass"
```

#### TC-018: Complete Poll Cycle

```yaml
- case_id: "TC-018"
  description: "poll_inverter(): full polling cycle returns correctly structured data dict"
  category: "positive"
  preconditions:
    - "read_registers patched via patch.object to return fixture data per (address, count) key"
  inputs:
    - parameter: "register_map"
      value: >
        {(0x006A,12): grid_regs, (0x0003,4): pv_vc_regs, (0x000A,2): pv_power_regs,
        (0x0014,9): battery_regs, (0x0046,2): feed_in_regs, (0x0050,1): energy_today_regs,
        (0x0052,2): energy_total_regs, (0x0008,2): status_regs}
      type: "dict"
  expected_outputs:
    - field: "timestamp present"
      expected_value: "True"
      validation: "assertIn"
    - field: "grid_voltage_r"
      expected_value: "230.2 (±0.01)"
      validation: "pytest.approx"
    - field: "pv1_power"
      expected_value: "3160"
      validation: "assertEqual"
    - field: "battery_soc"
      expected_value: "78"
      validation: "assertEqual"
    - field: "energy_today"
      expected_value: "28.4 (±0.01)"
      validation: "pytest.approx"
    - field: "run_mode"
      expected_value: "'Normal'"
      validation: "assertEqual"
  execution:
    status: "not_run"
    pass_fail_criteria: "All assertions pass"
```

[Return to Table of Contents](<#table of contents>)

---

### 5.2 TestInverterDisplay

#### TC-019: Display With No Data

```yaml
- case_id: "TC-019"
  description: "display_statistics(): outputs 'No data available' when passed empty dict"
  category: "edge"
  preconditions:
    - "capsys fixture active"
  inputs:
    - parameter: "data"
      value: "{}"
      type: "dict"
  expected_outputs:
    - field: "stdout"
      expected_value: "contains 'No data available'"
      validation: "assertIn"
  execution:
    status: "not_run"
    pass_fail_criteria: "assertIn passes"
```

#### TC-020: Display With Complete Data

```yaml
- case_id: "TC-020"
  description: "display_statistics(): renders all major sections with complete data set"
  category: "positive"
  preconditions:
    - "capsys fixture active"
    - "Full 25-field data dict provided"
  inputs:
    - parameter: "data"
      value: "complete 25-field inverter data dict (see test file)"
      type: "dict"
  expected_outputs:
    - field: "stdout contains header"
      expected_value: "'Solax X3 Hybrid 6.0-D Inverter Statistics'"
      validation: "assertIn"
    - field: "stdout contains status"
      expected_value: "'System Status: Normal'"
      validation: "assertIn"
    - field: "stdout contains grid section"
      expected_value: "'Grid (Three-Phase AC)'"
      validation: "assertIn"
    - field: "stdout contains PV section"
      expected_value: "'Solar PV Generation'"
      validation: "assertIn"
    - field: "stdout contains battery section"
      expected_value: "'Battery System'"
      validation: "assertIn"
    - field: "stdout contains SOC"
      expected_value: "'State of Charge: 78%'"
      validation: "assertIn"
    - field: "stdout contains energy today"
      expected_value: "'Solar Generation Today: 28.4kWh'"
      validation: "assertIn"
  execution:
    status: "not_run"
    pass_fail_criteria: "All assertIn checks pass"
```

#### TC-021: Power Flow — Exporting

```yaml
- case_id: "TC-021"
  description: "display_statistics(): shows EXPORTING when feed_in_power > 0"
  category: "positive"
  inputs:
    - parameter: "data"
      value: "{'feed_in_power': 1500}"
      type: "dict"
  expected_outputs:
    - field: "stdout"
      expected_value: "contains 'EXPORTING 1500W'"
      validation: "assertIn"
  execution:
    status: "not_run"
    pass_fail_criteria: "assertIn passes"
```

#### TC-022: Power Flow — Importing

```yaml
- case_id: "TC-022"
  description: "display_statistics(): shows IMPORTING when feed_in_power < 0"
  category: "positive"
  inputs:
    - parameter: "data"
      value: "{'feed_in_power': -800}"
      type: "dict"
  expected_outputs:
    - field: "stdout"
      expected_value: "contains 'IMPORTING 800W'"
      validation: "assertIn"
  execution:
    status: "not_run"
    pass_fail_criteria: "assertIn passes"
```

[Return to Table of Contents](<#table of contents>)

---

### 5.3 TestMainExecution

#### TC-023: Main Loop KeyboardInterrupt Handling

```yaml
- case_id: "TC-023"
  description: "main(): handles KeyboardInterrupt; calls disconnect() before exit"
  category: "edge"
  preconditions:
    - "argparse, SolaxInverterClient, InverterDisplay, time.sleep all patched"
    - "mock_sleep.side_effect = KeyboardInterrupt() to interrupt after first poll"
    - "mock_client.connect() returns True"
    - "mock_client.poll_inverter() returns {'test': 'data'}"
  test_steps:
    - step: "1"
      action: "Call main(); catch SystemExit if raised"
    - step: "2"
      action: "Assert mock_client.disconnect called once"
  inputs:
    - parameter: "mock_args.ip"
      value: "'192.168.1.100'"
      type: "str"
    - parameter: "mock_args.interval"
      value: "5"
      type: "int"
    - parameter: "mock_args.debug"
      value: "False"
      type: "bool"
  expected_outputs:
    - field: "exception propagated"
      expected_value: "None (or SystemExit only)"
      validation: "no unhandled exception"
    - field: "disconnect call count"
      expected_value: "1"
      validation: "assert_called_once"
  execution:
    status: "not_run"
    pass_fail_criteria: "No unhandled exception; disconnect_called_once passes"
```

[Return to Table of Contents](<#table of contents>)

---

## 6.0 Coverage

```yaml
coverage:
  requirements_covered: []
  code_coverage:
    target: "80%"
    achieved: ""
  untested_areas:
    - component: "src/solax_modbus/emulator/"
      reason: "Out of scope for this test document; emulator is a development utility"
    - component: "error recovery paths in poll_inverter() when read_registers returns None for individual groups"
      reason: "Not currently covered; candidate for future test expansion"
    - component: "argparse validation edge cases"
      reason: "Argument parser boundary testing not implemented"
    - component: "logging output assertions"
      reason: "Log output not asserted; functional correctness only"
```

[Return to Table of Contents](<#table of contents>)

---

## 7.0 Test Execution Summary

```yaml
test_execution_summary:
  total_cases: 23
  passed: 0
  failed: 0
  blocked: 0
  skipped: 0
  pass_rate: ""
  execution_time: ""
  test_cycle: "Initial"
```

[Return to Table of Contents](<#table of contents>)

---

## 8.0 Defect Summary

```yaml
defect_summary:
  total_defects: 0
  critical: 0
  high: 0
  medium: 0
  low: 0
  issues: []
```

[Return to Table of Contents](<#table of contents>)

---

## 9.0 Verification

```yaml
verification:
  verified_date: ""
  verified_by: ""
  verification_notes: ""
  sign_off: ""
```

[Return to Table of Contents](<#table of contents>)

---

## 10.0 Traceability

```yaml
traceability:
  requirements: []
  designs:
    - design_ref: "design-c1a2b3d4-component_protocol_client.md"
      test_cases:
        - "TC-001"
        - "TC-002"
        - "TC-003"
        - "TC-004"
        - "TC-005"
        - "TC-006"
        - "TC-007"
        - "TC-008"
        - "TC-009"
        - "TC-010"
        - "TC-011"
        - "TC-012"
        - "TC-013"
        - "TC-014"
        - "TC-015"
        - "TC-016"
        - "TC-017"
        - "TC-018"
    - design_ref: "design-d3c4d5e6-component_presentation_console.md"
      test_cases:
        - "TC-019"
        - "TC-020"
        - "TC-021"
        - "TC-022"
    - design_ref: "design-e4d5e6f7-component_application_main.md"
      test_cases:
        - "TC-023"
  changes:
    - change_ref: "prompt-46d32423"
      test_cases:
        - "TC-012"
        - "TC-013"
        - "TC-014"
```

[Return to Table of Contents](<#table of contents>)

---

## 11.0 Notes

The test suite was created prior to full P06 governance formalisation. `prompt_ref` is set to `prompt-46d32423` (pymodbus API fix) as the nearest traceable prior prompt. The suite covers the full application implementation, not solely the API fix.

Three areas are identified as candidates for future test expansion:

1. `poll_inverter()` partial-failure paths (individual register groups returning `None`)
2. Argument parser boundary and invalid-input cases
3. Log output verification

[Return to Table of Contents](<#table of contents>)

---

## Version History

| Version | Date       | Author          | Changes                          |
| ------- | ---------- | --------------- | -------------------------------- |
| 1.0     | 2026-03-13 | William Watson  | Initial formalisation of existing test suite per P06 |

---

Copyright (c) 2025 William Watson. This work is licensed under the MIT License.
