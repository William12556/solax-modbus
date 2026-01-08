# Change Document
# Update SolaxEmulator Design Documentation

**Change ID:** change-f3a4b5c6-update-protocol-emulator-design  
**Date:** 2026-01-08  
**Status:** Proposed

---

## Table of Contents

- [Change Information](<#change information>)
- [Source](<#source>)
- [Scope](<#scope>)
- [Rationale](<#rationale>)
- [Technical Details](<#technical details>)
- [Testing Requirements](<#testing requirements>)
- [Implementation](<#implementation>)
- [Traceability](<#traceability>)
- [Version History](<#version history>)

---

## Change Information

```yaml
change_info:
  id: "change-f3a4b5c6"
  title: "Update SolaxEmulator Design Documentation"
  date: "2026-01-08"
  author: "Claude (Domain 1)"
  status: "proposed"
  priority: "high"
  iteration: 1
  coupled_docs:
    issue_ref: "issue-f3a4b5c6"
    issue_iteration: 1
```

---

## Source

```yaml
source:
  type: "issue"
  reference: "issue-f3a4b5c6-protocol-emulator-design-incomplete"
  description: "Design document lacks state machine, PV algorithm, battery logic, temperature modeling, and threading architecture details"
```

---

## Scope

```yaml
scope:
  summary: "Update design-c2b3c4d5-component_protocol_emulator.md with complete emulator specification including simulation algorithms, threading design, and register generation"
  affected_components:
    - name: "design-c2b3c4d5-component_protocol_emulator.md"
      file_path: "workspace/design/design-c2b3c4d5-component_protocol_emulator.md"
      change_type: "modify"
  affected_designs:
    - design_ref: "design-c2b3c4d5-component_protocol_emulator.md"
      sections:
        - "Component Overview"
        - "Class Architecture"
        - "State Machine"
        - "PV Simulation"
        - "Battery Simulation"
        - "Temperature Modeling"
        - "Threading Design"
        - "Register Generation"
```

---

## Rationale

```yaml
rational:
  problem_statement: "Design document high-level only while implementation includes sophisticated time-based PV curves, battery state machine, thermal modeling, background threading, and custom Modbus data block"
  proposed_solution: "Document complete emulator architecture with state machine diagram, algorithm specifications, threading model, and register mapping mechanism"
  benefits:
    - "Accurate test infrastructure documentation"
    - "Foundation for emulator enhancements"
    - "Reference for alternative protocol emulators"
```

---

## Technical Details

**Content to Document:**

1. **Class Architecture:**
   - DynamicModbusDataBlock: Custom BaseModbusDataBlock extension
   - SolaxEmulatorState: Simulation state management
   - Background thread: state_update_loop with 1-second interval

2. **PV Simulation:**
   - Sine curve: Peak at noon (hour=12), zero outside 6-18 hour window
   - Formula: factor = sin((hour-6)/12 * π)
   - Random variation: ±10%
   - Per-string power: PV1_MAX=3300W, PV2_MAX=3300W

3. **Battery State Machine:**
   - Charge: PV>1000W AND SOC<100% → +500W
   - Discharge: PV<500W AND SOC>10% → -300W
   - Idle: Otherwise

4. **Temperature Modeling:**
   - Inverter: Increases with PV>2000W (max 45°C), cools to 25°C
   - Battery: Increases with SOC>90% (max 30°C), cools to 20°C

5. **Register Generation:**
   - get_input_registers(): 128 registers (0x00-0x7F) telemetry
   - get_holding_registers(): 128 registers configuration
   - Dynamic updates via setValues() every 1 second

---

## Testing Requirements

```yaml
testing_requirements:
  test_approach: "No testing - documentation only"
  validation_criteria:
    - "State machine documented with diagram"
    - "All simulation algorithms specified"
    - "Threading architecture described"
```

---

## Implementation

```yaml
implementation:
  effort_estimate: "1.5 hours"
  implementation_steps:
    - step: "Analyze src/emulator/solax_emulator.py"
      owner: "Claude (Domain 1)"
    - step: "Create state machine diagram"
      owner: "Claude (Domain 1)"
    - step: "Document simulation algorithms"
      owner: "Claude (Domain 1)"
  rollback_procedure: "Git revert"
```

---

## Traceability

```yaml
traceability:
  design_updates:
    - design_ref: "design-c2b3c4d5-component_protocol_emulator.md"
      sections_updated:
        - "All sections"
  related_issues:
    - issue_ref: "issue-f3a4b5c6"
      relationship: "resolves"
```

---

## Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-01-08 | Claude (Domain 1) | Initial change proposal from issue-f3a4b5c6 |

---

Copyright (c) 2025 William Watson. This work is licensed under the MIT License.
