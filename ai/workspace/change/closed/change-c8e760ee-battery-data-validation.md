Created: 2026 September 29

```yaml
change_info:
  id: "change-c8e760ee"
  title: "Validate the register list in _process_battery_data"
  date: "2026-09-29"
  author: "William Watson"
  status: "verified"
  priority: "medium"
  iteration: 1
  coupled_docs:
    issue_ref: "issue-c8e760ee"
    issue_iteration: 1

source:
  type: "issue"
  reference: "issue-c8e760ee"
  description: "Audit finding: missing input validation in _process_battery_data."

scope:
  summary: "Add a guard clause to SolaxInverterClient._process_battery_data and two unit tests."
  affected_components:
    - name: "SolaxInverterClient._process_battery_data"
      file_path: "src/solax_modbus/main.py"
      change_type: "modify"
    - name: "battery data tests"
      file_path: "tests/test_solax_poll.py"
      change_type: "modify"
  affected_designs: []
  out_of_scope:
    - "_process_grid_data and _process_pv_data (same finding type; separate changes)"
    - "Any change to poll_inverter, read_registers or REGISTER_MAPPINGS"
    - "Any other file"

rational:
  problem_statement: "A register list shorter than 9 entries, or None, raises and aborts the poll cycle."
  proposed_solution: >
    At the start of _process_battery_data, compute
    expected = self.REGISTER_MAPPINGS['battery_data']['count']. If regs is
    None or len(regs) < expected, log a warning naming the expected and
    received counts and return an empty dict. Otherwise behave exactly as now.
  alternatives_considered:
    - option: "Raise ValueError"
      reason_rejected: "poll_inverter would need new handling; returning {} matches the existing failed-read path"
  benefits:
    - "A malformed battery read no longer aborts the whole poll"
  risks:
    - risk: "Silent loss of battery metrics"
      mitigation: "Warning is logged on every occurrence"

technical_details:
  current_behavior: "IndexError or TypeError on short or None input."
  proposed_behavior: "Warning logged; {} returned; valid input unchanged."
  implementation_approach: "Guard clause at the top of the method; two new tests next to test_process_battery_data."
  code_changes:
    - component: "SolaxInverterClient"
      file: "src/solax_modbus/main.py"
      change_summary: "Guard clause in _process_battery_data"
      functions_affected:
        - "_process_battery_data"
      classes_affected: []
  data_changes: []
  interface_changes: []

dependencies:
  internal: []
  external: []
  required_changes: []

testing_requirements:
  test_approach: "pytest tests/test_solax_poll.py"
  test_cases:
    - scenario: "Five registers"
      expected_result: "{} returned; warning logged"
    - scenario: "None"
      expected_result: "{} returned; warning logged"
    - scenario: "Nine registers (existing test_process_battery_data)"
      expected_result: "Unchanged results"
  regression_scope:
    - "tests/test_solax_poll.py (all tests)"
  validation_criteria:
    - "All tests in tests/test_solax_poll.py pass"

implementation:
  effort_estimate: "under 1 hour"
  implementation_steps:
    - step: "Engine run on prompt-c8e760ee (live pilot of the AI-G&O engine layout)"
      owner: "engine"
  rollback_procedure: "git revert of the implementing commit"
  deployment_notes: "None"

verification:
  implemented_date: "2026-09-29"
  implemented_by: "engine: Devstral Small 2 8-bit worker, Magistral Small 2509 8-bit reviewer (run engine_20260929-131551)"
  verification_date: "2026-09-29"
  verified_by: "Strategic Domain code review of the diff; operator acceptance overriding the reviewer's BLOCKED"
  test_results: >
    Worker implemented the change in loop iteration 1; syntax gate and
    pytest gate PASS in iterations 1-3. Reviewer returned REVISE claiming
    the guard was missing (false negative), then repeated it without
    re-reading the code; stall BLOCK at iteration 3. Diff limited to
    src/solax_modbus/main.py and tests/test_solax_poll.py, matching the
    prompt. Operator pytest tests: 26 passed. An earlier run
    (engine_20260929-131033) crashed on an endpoint response without
    choices before any change (AI-G&O backlog §3.0 item 5).
  issues_found: []

traceability:
  design_updates: []
  related_changes: []
  related_issues:
    - issue_ref: "issue-c8e760ee"
      relationship: "resolves"

notes: "First live engine run after the AI-G&O layout migration (pilot for AI-G&O change-5bcd46ad). The logger.warning line exceeds 79 characters; accepted as is by the operator."

version_history:
  - version: "1.0"
    date: "2026-09-29"
    author: "William Watson"
    changes:
      - "Initial change document"
  - version: "1.1"
    date: "2026-09-29"
    author: "William Watson"
    changes:
      - "Implemented by the engine; verified by review and pytest; accepted over reviewer BLOCKED; closed"

metadata:
  copyright: "Copyright (c) 2026 William Watson. MIT License."
  template_version: "1.0"
  schema_type: "t07_change"
```

---

Copyright (c) 2026 William Watson. MIT License.
