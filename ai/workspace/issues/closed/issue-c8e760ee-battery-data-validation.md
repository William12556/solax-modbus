Created: 2026 September 29

```yaml
issue_info:
  id: "issue-c8e760ee"
  title: "_process_battery_data does not validate its register list"
  date: "2026-09-29"
  reporter: "William Watson"
  status: "closed"
  severity: "medium"
  type: "defect"
  iteration: 1
  coupled_docs:
    change_ref: "change-c8e760ee"
    change_iteration: 1

source:
  origin: "audit"
  test_ref: ""
  description: >
    Tactical audit audit-3e4f5a6b (ai/workspace/audit/audit-3e4f5a6b-report.md,
    SolaxInverterClient._process_battery_data, medium, error-handling): no
    validation of the regs parameter; a short list or None raises IndexError
    or TypeError. Selected as the first live engine run in this project after
    the AI-G&O layout migration (AI-G&O change-5bcd46ad pilot).

affected_scope:
  components:
    - name: "SolaxInverterClient._process_battery_data"
      file_path: "src/solax_modbus/main.py"
  designs:
    - design_ref: "design-c1a2b3d4-component_protocol_client"
  version: "current main"

reproduction:
  prerequisites: "Development install (pip install -e .[dev])"
  steps:
    - "Call SolaxInverterClient._process_battery_data with a list of fewer than 9 registers, or with None"
  frequency: "always"
  reproducibility_conditions: "Malformed or truncated register read"
  preconditions: ""
  test_data: "regs = [2705, 124, 3354, 0, 24]"
  error_output: "IndexError: list index out of range"

behavior:
  expected: >
    An incomplete register list is logged as a warning and yields no battery
    metrics, in the same way a failed register read does today.
  actual: "IndexError or TypeError propagates from poll_inverter()."
  impact: "One malformed battery read aborts the whole poll cycle."
  workaround: "None"

environment:
  python_version: "3.9+"
  os: "Raspberry Pi / Debian Linux; macOS for development"
  dependencies: ["pymodbus>=3.11,<4"]
  domain: "protocol"

analysis:
  root_cause: "_process_battery_data indexes regs[0..8] without checking length or None."
  technical_notes: >
    poll_inverter() only calls the method when read_registers() returned a
    truthy list, so the risk is a short list rather than None; the guard
    covers both. The expected count is REGISTER_MAPPINGS['battery_data']['count'] (9).
  related_issues: []

resolution:
  assigned_to: "engine (worker/reviewer loop)"
  target_date: "2026-09-29"
  approach: "Guard clause: warn and return {} when regs is None or shorter than the mapped count; add two unit tests."
  change_ref: "change-c8e760ee"
  resolved_date: "2026-09-29"
  resolved_by: "engine (Devstral 8-bit worker), accepted by operator"
  fix_description: "Guard clause in _process_battery_data returns {} and logs a warning for None or fewer than REGISTER_MAPPINGS['battery_data']['count'] registers; tests test_process_battery_data_short and test_process_battery_data_none added."

verification:
  verified_date: "2026-09-29"
  verified_by: "Strategic Domain code review; operator acceptance"
  test_results: "pytest tests: 26 passed (operator, solax-modbus venv, 2026-09-29)"
  closure_notes: "Closed with change-c8e760ee."

loop_context:
  was_loop_execution: true
  blocked_at_iteration: 3
  failure_mode: "Reviewer false REVISE: stall BLOCK after three identical objections although the implementation was complete and gates passed"
  last_review_feedback: "Guard and tests reported missing; both present in src/solax_modbus/main.py and tests/test_solax_poll.py"

version_history:
  - version: "1.0"
    date: "2026-09-29"
    author: "William Watson"
    changes:
      - "Initial issue from audit-3e4f5a6b"
  - version: "1.1"
    date: "2026-09-29"
    author: "William Watson"
    changes:
      - "Resolved and closed; loop context recorded"

metadata:
  copyright: "Copyright (c) 2026 William Watson. MIT License."
  template_version: "1.0"
  schema_type: "t06_issue"
```

---

Copyright (c) 2026 William Watson. MIT License.
