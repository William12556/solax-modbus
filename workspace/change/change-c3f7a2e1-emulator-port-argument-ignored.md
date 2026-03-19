```yaml
# T02 Change Document
# Emulator --port argument ignored

change_info:
  id: "change-c3f7a2e1"
  title: "Emulator --port argument silently ignored"
  date: "2026-03-18"
  author: "William Watson"
  status: "implemented"
  priority: "high"
  iteration: 1
  coupled_docs:
    issue_ref: "issue-c3f7a2e1"
    issue_iteration: 1

source:
  type: "bug"
  reference: "workspace/issues/issue-c3f7a2e1-emulator-port-argument-ignored.md"
  description: >
    Emulator ignores --port, --host, and --unit-id CLI arguments.
    run_emulator() uses hardcoded module-level constants throughout.
    No argparse call exists at the __main__ entry point.

scope:
  summary: >
    Add argparse to the __main__ entry point. Pass parsed host, port,
    and unit_id into run_emulator() as parameters. run_emulator() uses
    passed values instead of module-level constants.
  affected_components:
    - name: "solax_emulator.py"
      file_path: "src/solax_modbus/emulator/solax_emulator.py"
      change_type: "modify"
  affected_designs:
    - design_ref: "workspace/design/design-c2b3c4d5-component_protocol_emulator.md"
      sections:
        - "Entry Point"
  out_of_scope:
    - "Emulator simulation logic"
    - "Register values or data blocks"
    - "Logging configuration"

rational:
  problem_statement: >
    Emulator cannot be run on an unprivileged port for development.
    Port 502 requires root on Linux and macOS, blocking development
    testing without sudo.
  proposed_solution: >
    Add argparse at __main__ with --host, --port, --unit-id arguments
    defaulting to existing constant values. Pass args into run_emulator().
  alternatives_considered:
    - option: "Modify constants directly"
      reason_rejected: "Requires source edit for each invocation; not a fix"
  benefits:
    - "Emulator usable on unprivileged ports (e.g. 5020) without sudo"
    - "Host and unit ID also become configurable at runtime"
  risks:
    - risk: "None identified"
      mitigation: "n/a"

technical_details:
  current_behavior: >
    __main__ calls run_emulator() with no arguments. run_emulator()
    logs and passes MODBUS_HOST, MODBUS_PORT, MODBUS_UNIT_ID constants
    directly to StartTcpServer. CLI arguments are silently discarded.
  proposed_behavior: >
    __main__ parses --host, --port, --unit-id via argparse and passes
    values to run_emulator(host, port, unit_id). run_emulator() uses
    these parameters in logging and StartTcpServer address tuple.
  implementation_approach: >
    1. Added argparse block in __main__ with three arguments:
       --host (default MODBUS_HOST), --port (default MODBUS_PORT),
       --unit-id (default MODBUS_UNIT_ID).
    2. Changed run_emulator() signature to run_emulator(host, port, unit_id).
    3. Replaced MODBUS_HOST, MODBUS_PORT, MODBUS_UNIT_ID references inside
       run_emulator() with the passed parameters.
    4. ModbusServerContext device key uses unit_id parameter.
  code_changes:
    - component: "solax_emulator.py"
      file: "src/solax_modbus/emulator/solax_emulator.py"
      change_summary: >
        Added argparse import and __main__ argument parsing block;
        parameterised run_emulator(host, port, unit_id); replaced
        constant references with parameters inside run_emulator().
      functions_affected:
        - "run_emulator"
      classes_affected: []
  data_changes: []
  interface_changes:
    - interface: "run_emulator()"
      change_type: "signature"
      details: "run_emulator() → run_emulator(host, port, unit_id)"
      backward_compatible: "yes"

dependencies:
  internal: []
  external: []
  required_changes: []

testing_requirements:
  test_approach: "Manual CLI verification"
  test_cases:
    - scenario: "Run with --port 5020"
      expected_result: "Log shows Port: 5020; server listens on 5020"
    - scenario: "Run with no arguments"
      expected_result: "Log shows Port: 502; behaviour unchanged"
    - scenario: "Connect monitor to emulator on port 5020"
      expected_result: "Telemetry displayed; no connection errors"
  regression_scope:
    - "Default invocation (no args) behaviour unchanged"
  validation_criteria:
    - "Log Port: matches --port argument"
    - "Monitor connects successfully on specified port"

implementation:
  effort_estimate: ""
  implementation_steps:
    - step: "Modify solax_emulator.py per technical_details"
      owner: "Strategic Domain"
  rollback_procedure: "Restore from git history"
  deployment_notes: "Rebuild wheel and reinstall after source change"

verification:
  implemented_date: "2026-03-18"
  implemented_by: "Strategic Domain"
  verification_date: ""
  verified_by: ""
  test_results: "Pending manual verification"
  issues_found: []

traceability:
  design_updates:
    - design_ref: "workspace/design/design-c2b3c4d5-component_protocol_emulator.md"
      sections_updated:
        - "Entry Point"
      update_date: ""
  related_changes: []
  related_issues:
    - issue_ref: "issue-c3f7a2e1"
      relationship: "source"

notes: ""

version_history:
  - version: "1.0"
    date: "2026-03-18"
    author: "William Watson"
    changes:
      - "Initial change document"
  - version: "1.1"
    date: "2026-03-18"
    author: "William Watson"
    changes:
      - "Status updated to implemented"
      - "verification.implemented_date populated"

metadata:
  copyright: "Copyright (c) 2025 William Watson. This work is licensed under the MIT License."
  template_version: "1.0"
  schema_type: "t02_change"
```
