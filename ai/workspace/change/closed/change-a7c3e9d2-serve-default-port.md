```yaml
# T02 Change Document
# Web UI Serve-by-Default and Port Default 8181

change_info:
  id: "change-a7c3e9d2"
  title: "Web UI Serve-by-Default and Port Default 8181"
  date: "2026-07-07"
  author: "William Watson"
  status: "implemented"
  priority: "low"
  iteration: 1
  coupled_docs:
    issue_ref: "issue-a7c3e9d2"
    issue_iteration: 1

source:
  type: "issue"
  reference: "ai/workspace/issues/issue-a7c3e9d2-serve-default-port.md"
  description: >
    Make the HTTP telemetry server serve by default, disabled with --no-serve,
    and change the default HTTP port from 8080 to 8181 via a single module
    constant.

scope:
  summary: >
    Introduce DEFAULT_HTTP_PORT = 8181 in the presentation server module and
    reference it from both the TelemetryServer constructor default and the
    main.py --http-port argparse default. Invert the serve flag: replace
    --serve (store_true, default off) with --no-serve (store_false into the
    same 'serve' destination; default serve=True). Update the main.py epilog
    examples and the affected unit tests. Update design-9b7e2c4a,
    design-bf6d4e5f, and the name registry.
  affected_components:
    - name: "server.py"
      file_path: "src/solax_modbus/presentation/server.py"
      change_type: "modify"
    - name: "main.py"
      file_path: "src/solax_modbus/main.py"
      change_type: "modify"
    - name: "test_solax_poll.py"
      file_path: "tests/test_solax_poll.py"
      change_type: "modify"
  affected_designs:
    - design_ref: "design-9b7e2c4a"
      sections:
        - "Purpose"
        - "Class Design (Constructor)"
        - "Configuration"
    - design_ref: "design-bf6d4e5f"
      sections:
        - "Components (main :: CLI Arguments)"
    - design_ref: "design-solax-modbus-name_registry-master"
      sections:
        - "Element Registry (constants)"
  out_of_scope:
    - "Removing the --serve flag name with no replacement (a disable path is retained as --no-serve)"
    - "Authentication or TLS for the HTTP server"
    - "Changes to the allowlist model or DEFAULT_ALLOWED_NETWORKS"
    - "bin/install.sh, README.md, docs/guide.md — updated directly as tooling/docs, outside this protocol"

rational:
  problem_statement: >
    Serving requires an explicit --serve flag, and the default port 8080 is
    commonly occupied. The default declaration is duplicated across main.py
    and server.py.
  proposed_solution: >
    Serve by default; disable with --no-serve. Default port 8181, declared
    once as DEFAULT_HTTP_PORT in server.py and imported by main.py.
  alternatives_considered:
    - option: "Drop --serve entirely with no disable flag"
      reason_rejected: "Removes operator control; --no-serve retains an off switch at negligible cost."
    - option: "Auto-serve only in the systemd unit (install.sh injects --serve); leave the CLI default off"
      reason_rejected: "CLI and service would disagree on the default; less coherent and does not simplify manual runs."
    - option: "Change the port default in main.py only, leaving server.py at 8080"
      reason_rejected: "Leaves two competing defaults; a direct TelemetryServer caller would bind 8080."
  benefits:
    - "Common path needs no flag; Web UI is available by default"
    - "8181 reduces port-collision likelihood versus 8080"
    - "Single source of truth for the default port (DEFAULT_HTTP_PORT)"
  risks:
    - risk: "Serving by default binds a network port that was previously opt-in"
      mitigation: "The existing RFC1918 source-IP allowlist still applies; --no-serve disables binding entirely; deployment remains on a trusted network (NFR-006)."
    - risk: "Inverting the serve contract breaks tests asserting the old opt-in behaviour"
      mitigation: "Update tests/test_solax_poll.py in the same change; supersede the opt-in contract in prompt-c4d8e1f6 (annotated)."

technical_details:
  current_behavior: >
    main.py: --serve is store_true (default off); --http-port default 8080;
    the server is constructed and started only under 'if args.serve'.
    server.py: TelemetryServer.__init__ declares port: int = 8080.
  proposed_behavior: >
    main.py: serving defaults on; --no-serve sets serve=False; --http-port
    default is DEFAULT_HTTP_PORT (8181). The existing 'if args.serve' guards
    are unchanged in logic. server.py: port default is DEFAULT_HTTP_PORT.
  implementation_approach: >
    1. server.py: add module constant DEFAULT_HTTP_PORT = 8181 (near
       DEFAULT_ALLOWED_NETWORKS); set the constructor default to
       port: int = DEFAULT_HTTP_PORT; update the docstring's numeric mention.
    2. main.py: import DEFAULT_HTTP_PORT; replace the --serve argument with
       --no-serve (dest='serve', action='store_false') and
       parser.set_defaults(serve=True); set --http-port default to
       DEFAULT_HTTP_PORT and update its help text; update the three epilog
       examples to reflect default-on serving and --no-serve.
    3. tests/test_solax_poll.py: set the expected http_port to 8181; invert
       the serve-absent expectation (absent -> server starts) and add a
       --no-serve case (server not started).
  code_changes:
    - component: "server.py"
      file: "src/solax_modbus/presentation/server.py"
      change_summary: "Add DEFAULT_HTTP_PORT = 8181; constructor default port: int = DEFAULT_HTTP_PORT; docstring update."
      functions_affected:
        - "TelemetryServer.__init__"
      classes_affected:
        - "TelemetryServer"
    - component: "main.py"
      file: "src/solax_modbus/main.py"
      change_summary: "Import DEFAULT_HTTP_PORT; --serve -> --no-serve (store_false, default serve=True); --http-port default DEFAULT_HTTP_PORT; epilog examples."
      functions_affected:
        - "main"
      classes_affected: []
    - component: "test_solax_poll.py"
      file: "tests/test_solax_poll.py"
      change_summary: "http_port expectation 8181; invert serve-absent assertion; add --no-serve case."
      functions_affected: []
      classes_affected: []
  data_changes: []
  interface_changes:
    - interface: "solax-monitor CLI"
      change_type: "contract"
      details: "--serve removed; --no-serve added. Default behaviour now serves. --http-port default 8080 -> 8181."
      backward_compatible: "no"

dependencies:
  internal:
    - component: "main.py -> server.py"
      impact: "main.py imports DEFAULT_HTTP_PORT from the presentation server module."
  external: []
  required_changes: []

testing_requirements:
  test_approach: "pytest on the development machine; manual confirmation on the Pi."
  test_cases:
    - scenario: "solax-monitor <ip> (no flag)"
      expected_result: "Server starts; binds 8181; dashboard served."
    - scenario: "solax-monitor <ip> --no-serve"
      expected_result: "Poll loop runs; no port bound."
    - scenario: "solax-monitor <ip> --http-port 9000"
      expected_result: "Server binds 9000."
  regression_scope:
    - "Poll loop, shutdown ordering, and allowlist behaviour unchanged"
    - "Existing --http-port and --allow parsing unchanged"
  validation_criteria:
    - "pytest passes"
    - "DEFAULT_HTTP_PORT is the sole literal declaration of the default port"

implementation:
  effort_estimate: ""
  implementation_steps:
    - step: "server.py: DEFAULT_HTTP_PORT and constructor default"
      owner: "Tactical Domain (Claude Code)"
    - step: "main.py: import, --no-serve, --http-port default, epilog"
      owner: "Tactical Domain (Claude Code)"
    - step: "tests: update contract"
      owner: "Tactical Domain (Claude Code)"
    - step: "Code review (P08) and test (P06)"
      owner: "Strategic Domain"
  rollback_procedure: "Restore the three source files from git history."
  deployment_notes: >
    A systemd unit generated without --http-port now serves on 8181. README.md,
    docs/guide.md, and bin/install.sh are updated directly (outside this
    protocol) to match.

verification:
  implemented_date: "2026-07-07"
  implemented_by: "Claude Code"
  verification_date: "2026-07-07"
  verified_by: "William Watson"
  test_results: "pytest: 24 passed, 0 failed"
  issues_found: []

traceability:
  design_updates:
    - design_ref: "design-9b7e2c4a"
      sections_updated:
        - "Purpose"
        - "Constructor"
        - "Configuration"
      update_date: "2026-07-07"
    - design_ref: "design-bf6d4e5f"
      sections_updated:
        - "CLI Arguments"
      update_date: "2026-07-07"
    - design_ref: "design-solax-modbus-name_registry-master"
      sections_updated:
        - "Element Registry"
      update_date: "2026-07-07"
  related_changes: []
  related_issues:
    - issue_ref: "issue-a7c3e9d2"
      relationship: "source"

notes: >
  Human decisions (2026-07-07): serve by default with --no-serve; port 8181;
  DEFAULT_HTTP_PORT constant as single source of truth; server.py aligned to
  8181; designs updated concurrently; install.sh edited directly as tooling;
  README/guide drafted in parallel; prompt-c4d8e1f6 annotated (superseded
  opt-in contract).

version_history:
  - version: "1.0"
    date: "2026-07-07"
    author: "William Watson"
    changes:
      - "Initial change document"
  - version: "1.1"
    date: "2026-07-07"
    author: "William Watson"
    changes:
      - "Status implemented; verified via pytest (24 passed); closed"

metadata:
  copyright: "Copyright (c) 2025 William Watson. This work is licensed under the MIT License."
  template_version: "1.0"
  schema_type: "t02_change"
```
