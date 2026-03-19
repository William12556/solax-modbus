```yaml
# T03 Issue Document
# Emulator --port argument ignored

issue_info:
  id: "issue-c3f7a2e1"
  title: "Emulator --port argument silently ignored"
  date: "2026-03-18"
  reporter: "William Watson"
  status: "open"
  severity: "high"
  type: "bug"
  iteration: 1
  coupled_docs:
    change_ref: ""
    change_iteration: null

source:
  origin: "user_report"
  test_ref: ""
  description: >
    During T2 test execution of change b4e7f1a9 (macOS platform support),
    the emulator was started with --port 5020 but logged Port: 502,
    causing the monitor to fail with Connection refused on port 5020.

affected_scope:
  components:
    - name: "solax_emulator.py"
      file_path: "src/solax_modbus/emulator/solax_emulator.py"
  designs:
    - design_ref: "workspace/design/design-c2b3c4d5-component_protocol_emulator.md"
  version: "0.1.4"

reproduction:
  prerequisites: "Package installed"
  steps:
    - "Run: python src/solax_modbus/emulator/solax_emulator.py --port 5020"
    - "Observe log output"
  frequency: "always"
  reproducibility_conditions: "Any invocation with --port argument"
  preconditions: ""
  test_data: ""
  error_output: "Port: 502  (expected Port: 5020)"

behavior:
  expected: "Emulator listens on the port supplied via --port argument"
  actual: >
    Emulator always listens on hardcoded MODBUS_PORT constant (502)
    regardless of --port argument. The argument is accepted by the
    shell but run_emulator() never calls argparse; it logs and uses
    the module-level constant directly.
  impact: >
    Emulator cannot be run on an unprivileged port for development.
    Port 502 requires root on Linux and macOS. Development testing
    against the emulator is blocked without sudo.
  workaround: "Edit MODBUS_PORT constant directly in source (not acceptable)."

environment:
  python_version: "3.11"
  os: "macOS"
  dependencies:
    - library: "pymodbus"
      version: "3.11.x"
  domain: "domain_1"

analysis:
  root_cause: >
    run_emulator() uses the module-level constant MODBUS_PORT throughout
    (logging, StartTcpServer address tuple). No argparse call exists in
    run_emulator() or at the __main__ entry point. The if __name__ == '__main__'
    block calls run_emulator() with no arguments and no argument parsing.
  technical_notes: >
    Fix requires: (1) add argparse block in __main__ with --host, --port,
    --unit-id arguments; (2) pass parsed values into run_emulator();
    (3) run_emulator() uses passed values instead of module constants.
    MODBUS_PORT constant may remain as the default value.
  related_issues: []

resolution:
  assigned_to: "William Watson"
  target_date: ""
  approach: "Add argparse to __main__ entry point; thread args through run_emulator()"
  change_ref: ""
  resolved_date: ""
  resolved_by: ""
  fix_description: ""

verification:
  verified_date: ""
  verified_by: ""
  test_results: ""
  closure_notes: ""

prevention:
  preventive_measures: "Test CLI argument handling as part of emulator unit tests."
  process_improvements: ""

verification_enhanced:
  verification_steps:
    - "Run emulator with --port 5020; confirm log shows Port: 5020"
    - "Run emulator with no arguments; confirm log shows Port: 502"
    - "Connect monitor to port 5020; confirm successful telemetry"
  verification_results: ""

traceability:
  design_refs:
    - "workspace/design/design-c2b3c4d5-component_protocol_emulator.md"
  change_refs: []
  test_refs: []

notes: "Discovered during T2 testing of change-b4e7f1a9 (macOS platform support)"

loop_context:
  was_loop_execution: false
  blocked_at_iteration: 0
  failure_mode: ""
  last_review_feedback: ""

version_history:
  - version: "1.0"
    date: "2026-03-18"
    author: "William Watson"
    changes:
      - "Initial issue document"

metadata:
  copyright: "Copyright (c) 2025 William Watson. This work is licensed under the MIT License."
  template_version: "1.0"
  schema_type: "t03_issue"
```
