```yaml
# T03 Issue Document
# Web UI Serve-by-Default and Port Default 8181

issue_info:
  id: "issue-a7c3e9d2"
  title: "Web UI Serve-by-Default and Port Default 8181"
  date: "2026-07-07"
  reporter: "William Watson"
  status: "open"
  severity: "low"
  type: "enhancement"
  iteration: 1
  coupled_docs:
    change_ref: "change-a7c3e9d2"
    change_iteration: 1

source:
  origin: "user_report"
  test_ref: ""
  description: >
    Simplify operation of the Web UI. Currently the HTTP telemetry server is
    opt-in (--serve) and defaults to port 8080. The request is to serve by
    default (disable via --no-serve) and to change the default port to 8181,
    which is less commonly occupied than 8080.

affected_scope:
  components:
    - name: "main.py"
      file_path: "src/solax_modbus/main.py"
    - name: "server.py"
      file_path: "src/solax_modbus/presentation/server.py"
    - name: "test_solax_poll.py"
      file_path: "tests/test_solax_poll.py"
  designs:
    - design_ref: "design-9b7e2c4a"
    - design_ref: "design-bf6d4e5f"
    - design_ref: "design-solax-modbus-name_registry-master"
  version: "0.1.12"

reproduction:
  prerequisites: ""
  steps:
    - "solax-monitor <ip>            # current: no Web UI"
    - "solax-monitor <ip> --serve    # current: Web UI on 8080"
  frequency: "always"
  reproducibility_conditions: ""
  preconditions: ""
  test_data: ""
  error_output: ""

behavior:
  expected: >
    solax-monitor <ip> serves the Web UI by default on port 8181. --no-serve
    disables the server. --http-port overrides the port.
  actual: >
    solax-monitor <ip> does not serve. --serve is required to enable the Web
    UI, which binds port 8080 by default.
  impact: "Operational only. The common deployment path requires an extra flag; 8080 is prone to port collision."
  workaround: "Pass --serve and --http-port 8181 explicitly."

environment:
  python_version: "3.13"
  os: "Debian 13 (trixie), Raspberry Pi Zero 2W"
  dependencies:
    - library: "pymodbus"
      version: "3.11.4"
  domain: "domain_1"

analysis:
  root_cause: >
    Design decision, not a fault. main.py defines --serve as store_true
    (default off) and --http-port default 8080. server.py repeats the 8080
    default in the TelemetryServer constructor. The behaviour is being changed
    by request.
  technical_notes: >
    server.py's constructor default (port: int = 8080) is not exercised via
    the CLI, which always passes an explicit port=args.http_port; it is a
    second, independent declaration of the default. A single module constant
    DEFAULT_HTTP_PORT removes the duplication.
  related_issues:
    - issue_ref: "issue-c4d8e1f6"
      relationship: "supersedes the opt-in serve contract established for the telemetry server"

resolution:
  assigned_to: "William Watson"
  target_date: ""
  approach: >
    See change-a7c3e9d2. Introduce DEFAULT_HTTP_PORT = 8181 in server.py; use
    it as both the constructor default and the main.py --http-port default.
    Replace --serve (store_true) with --no-serve (dest=serve, store_false;
    set_defaults serve=True). Update the epilog examples and the affected
    tests. Update design-9b7e2c4a, design-bf6d4e5f, and the name registry.
  change_ref: "change-a7c3e9d2"
  resolved_date: ""
  resolved_by: ""
  fix_description: ""

verification:
  verified_date: ""
  verified_by: ""
  test_results: ""
  closure_notes: ""

prevention:
  preventive_measures: "Declare shared defaults once as a named constant."
  process_improvements: ""

verification_enhanced:
  verification_steps:
    - "solax-monitor <ip> binds 8181 and serves the dashboard without any flag"
    - "solax-monitor <ip> --no-serve runs the poll loop and binds no port"
    - "solax-monitor <ip> --http-port 9000 serves on 9000"
    - "pytest passes with the inverted serve contract"
  verification_results: ""

traceability:
  design_refs:
    - "design-9b7e2c4a"
    - "design-bf6d4e5f"
    - "design-solax-modbus-name_registry-master"
  change_refs:
    - "change-a7c3e9d2"
  test_refs: []

notes: >
  Documentation (README.md, docs/guide.md) and the installer (bin/install.sh)
  are updated directly outside the source-change protocol, per human decision
  (2026-07-07).

loop_context:
  was_loop_execution: false
  blocked_at_iteration: 0
  failure_mode: ""
  last_review_feedback: ""

version_history:
  - version: "1.0"
    date: "2026-07-07"
    author: "William Watson"
    changes:
      - "Initial issue document"

metadata:
  copyright: "Copyright (c) 2025 William Watson. This work is licensed under the MIT License."
  template_version: "1.0"
  schema_type: "t03_issue"
```
