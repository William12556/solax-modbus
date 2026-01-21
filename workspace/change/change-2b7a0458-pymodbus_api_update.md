# Change: Update Pymodbus API - Replace 'slave' with 'unit' Parameter

Created: 2025-01-21

---

## Table of Contents

- [Change Information](<#change information>)
- [Source](<#source>)
- [Scope](<#scope>)
- [Rationale](<#rationale>)
- [Technical Details](<#technical details>)
- [Dependencies](<#dependencies>)
- [Testing Requirements](<#testing requirements>)
- [Implementation](<#implementation>)
- [Verification](<#verification>)
- [Traceability](<#traceability>)
- [Version History](<#version history>)

---

## Change Information

```yaml
change_info:
  id: "change-2b7a0458"
  title: "Update Pymodbus API - Replace 'slave' with 'unit' Parameter"
  date: "2025-01-21"
  author: "William Watson"
  status: "proposed"
  priority: "critical"
  iteration: 1
  coupled_docs:
    issue_ref: "issue-f2a39d1c"
    issue_iteration: 1
```

[Return to Table of Contents](<#table of contents>)

---

## Source

```yaml
source:
  type: "issue"
  reference: "issue-f2a39d1c"
  description: "Fix pymodbus API incompatibility causing TypeError in all register read operations"
```

[Return to Table of Contents](<#table of contents>)

---

## Scope

```yaml
scope:
  summary: "Update all Modbus register read operations to use pymodbus 3.x compatible 'unit' parameter instead of deprecated 'slave' parameter"
  affected_components:
    - name: "SolaxInverterClient"
      file_path: "src/solax_modbus/main.py"
      change_type: "modify"
  affected_designs:
    - design_ref: "design-<uuid>-component_modbus_client"
      sections:
        - "Modbus Communication Interface"
  out_of_scope:
    - "Modbus write operations (read-only system)"
    - "Protocol specification changes"
    - "Register address modifications"
```

[Return to Table of Contents](<#table of contents>)

---

## Rationale

```yaml
rational:
  problem_statement: "Application fails completely with TypeError when attempting to read Modbus registers due to using deprecated 'slave' parameter from pymodbus 2.x API in environment running pymodbus 3.x"
  proposed_solution: "Update all read_input_registers and read_holding_registers calls to use 'unit' parameter instead of 'slave' parameter, maintaining backward compatibility with pymodbus 3.x API"
  alternatives_considered:
    - option: "Downgrade to pymodbus 2.x"
      reason_rejected: "Not sustainable - pymodbus 2.x is deprecated, lacks security updates, and prevents future library updates"
    - option: "Version detection with conditional parameter naming"
      reason_rejected: "Unnecessary complexity - standardize on pymodbus 3.x which is current stable version"
  benefits:
    - "Restores full application functionality"
    - "Aligns with current pymodbus stable API"
    - "Enables future library updates without breaking changes"
    - "Improves code maintainability"
  risks:
    - risk: "May reveal additional API incompatibilities"
      mitigation: "Comprehensive testing of all Modbus operations after fix"
```

[Return to Table of Contents](<#table of contents>)

---

## Technical Details

```yaml
technical_details:
  current_behavior: "Code calls self.client.read_input_registers(address=..., count=..., slave=self.unit_id) which raises TypeError with pymodbus 3.x"
  proposed_behavior: "Code calls self.client.read_input_registers(address=..., count=..., unit=self.unit_id) compatible with pymodbus 3.x API"
  implementation_approach: |
    1. Locate all Modbus read operation calls in SolaxInverterClient class
    2. Replace 'slave=self.unit_id' with 'unit=self.unit_id' in each call
    3. Verify pyproject.toml constraints allow pymodbus 3.x
    4. Review error handling for any version-specific error types
  code_changes:
    - component: "SolaxInverterClient"
      file: "src/solax_modbus/main.py"
      change_summary: "Replace 'slave' parameter with 'unit' in all read_input_registers and read_holding_registers calls"
      functions_affected:
        - "read_registers"
      classes_affected:
        - "SolaxInverterClient"
  data_changes: []
  interface_changes:
    - interface: "Modbus read operations"
      change_type: "protocol"
      details: "Internal parameter naming only - no external interface changes"
      backward_compatible: "yes"
```

[Return to Table of Contents](<#table of contents>)

---

## Dependencies

```yaml
dependencies:
  internal:
    - component: "None"
      impact: "Isolated change within SolaxInverterClient"
  external:
    - library: "pymodbus"
      version_change: "Requires pymodbus >= 3.0.0"
      impact: "Must verify pyproject.toml allows pymodbus 3.x"
  required_changes: []
```

[Return to Table of Contents](<#table of contents>)

---

## Testing Requirements

```yaml
testing_requirements:
  test_approach: "Progressive validation: targeted fix verification, then full regression"
  test_cases:
    - scenario: "Read input registers with valid address"
      expected_result: "Successfully returns register data without TypeError"
    - scenario: "Read holding registers with valid address"
      expected_result: "Successfully returns register data without TypeError"
    - scenario: "Connection timeout handling"
      expected_result: "Proper timeout exception, not TypeError"
    - scenario: "Invalid register address"
      expected_result: "Proper Modbus exception, not TypeError"
  regression_scope:
    - "All existing unit tests for SolaxInverterClient"
    - "Integration test with Modbus emulator"
    - "Full application smoke test"
  validation_criteria:
    - "No TypeError exceptions during register reads"
    - "Successful data retrieval from all register types"
    - "All existing tests pass"
```

[Return to Table of Contents](<#table of contents>)

---

## Implementation

```yaml
implementation:
  effort_estimate: "1 hour"
  implementation_steps:
    - step: "Review all read_input_registers calls in main.py"
      owner: "Claude Code"
    - step: "Review all read_holding_registers calls in main.py"
      owner: "Claude Code"
    - step: "Replace slave=self.unit_id with unit=self.unit_id"
      owner: "Claude Code"
    - step: "Verify pyproject.toml pymodbus version constraint"
      owner: "Claude Code"
    - step: "Update component design document if needed"
      owner: "Claude Desktop"
  rollback_procedure: "Git revert commit if testing reveals issues. No data migration required."
  deployment_notes: |
    - Verify deployment environment has pymodbus >= 3.0.0
    - No configuration changes required
    - No database migrations required
    - Restart service after deployment
```

[Return to Table of Contents](<#table of contents>)

---

## Verification

```yaml
verification:
  implemented_date: ""
  implemented_by: ""
  verification_date: ""
  verified_by: ""
  test_results: ""
  issues_found: []
```

[Return to Table of Contents](<#table of contents>)

---

## Traceability

```yaml
traceability:
  design_updates:
    - design_ref: "design-<uuid>-component_modbus_client"
      sections_updated:
        - "Modbus Communication Interface"
      update_date: ""
  related_changes: []
  related_issues:
    - issue_ref: "issue-f2a39d1c"
      relationship: "resolves"
```

[Return to Table of Contents](<#table of contents>)

---

## Version History

| Version | Date       | Author          | Changes                    |
| ------- | ---------- | --------------- | -------------------------- |
| 1.0     | 2025-01-21 | William Watson  | Initial change proposal    |

---

Copyright (c) 2025 William Watson. This work is licensed under the MIT License.
