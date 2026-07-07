```yaml
# T04 Prompt Document
# Web UI Serve-by-Default and Port Default 8181

prompt_info:
  id: "prompt-a7c3e9d2"
  task_type: "code_generation"
  source_ref: "change-a7c3e9d2"
  target_profile: "claude_code"
  date: "2026-07-07"
  iteration: 1
  coupled_docs:
    change_ref: "change-a7c3e9d2"
    change_iteration: 1

context:
  purpose: >
    Make the HTTP telemetry server serve by default (disabled with --no-serve)
    and change the default port from 8080 to 8181 via a single shared constant.
  integration: >
    Modifies src/solax_modbus/main.py, src/solax_modbus/presentation/server.py,
    and tests/test_solax_poll.py only. The poll loop, shutdown ordering,
    allowlist model, and DEFAULT_ALLOWED_NETWORKS are unchanged.
  knowledge_references: []
  constraints:
    - "Introduce DEFAULT_HTTP_PORT once in server.py; do not hard-code 8181 elsewhere."
    - "Preserve the existing 'if args.serve' guard logic in main.py; only the flag definition and default change."
    - "--no-serve must write to dest 'serve' (store_false) with default serve=True, so downstream code keeps reading args.serve."
    - "Do not remove --http-port or --allow. Do not add authentication."

specification:
  description: >
    Edit server.py to declare DEFAULT_HTTP_PORT = 8181 and use it as the
    constructor default. Edit main.py to import the constant, invert the serve
    flag to --no-serve, default --http-port to the constant, and refresh the
    epilog examples. Update the affected unit tests.
  requirements:
    functional:
      - "server.py: add module-level DEFAULT_HTTP_PORT = 8181 near DEFAULT_ALLOWED_NETWORKS."
      - "server.py: TelemetryServer.__init__ default becomes port: int = DEFAULT_HTTP_PORT; update the docstring numeric reference to 8181."
      - "main.py: import DEFAULT_HTTP_PORT from solax_modbus.presentation.server."
      - "main.py: replace the --serve argument with --no-serve (action='store_false', dest='serve', help='Disable the HTTP telemetry server (enabled by default)'); add parser.set_defaults(serve=True)."
      - "main.py: --http-port default becomes DEFAULT_HTTP_PORT; help text 'HTTP server port (default: 8181)'."
      - "main.py: update the three epilog examples — remove the --serve example, add a --no-serve example, and keep --http-port/--allow examples with default-on serving."
      - "tests/test_solax_poll.py: change the expected http_port from 8080 to 8181; invert any assertion that the server is absent without --serve (absent flag now starts the server); add a case asserting --no-serve does not start the server."
    technical:
      language: "Python"
      version: "3.13"
      standards:
        - "Preserve professional docstrings"
        - "No change to logging configuration"
        - "No new external dependencies"

design:
  architecture: >
    A single shared constant declares the default port; the CLI inverts one
    flag. No structural change to the server or poll loop.
  components:
    - name: "DEFAULT_HTTP_PORT (server.py)"
      type: "module"
      purpose: "Single source of truth for the default HTTP port."
      interface:
        inputs: []
        outputs:
          type: "constant"
          description: "int = 8181"
        raises: []
      logic:
        - "Declare DEFAULT_HTTP_PORT = 8181 at module scope"
        - "Reference it as the TelemetryServer.__init__ port default"
    - name: "main (main.py)"
      type: "function"
      purpose: "Serve by default; disable with --no-serve; default port 8181."
      interface:
        inputs:
          - name: "--no-serve"
            type: "flag"
            description: "store_false into dest 'serve'; default serve=True"
          - name: "--http-port"
            type: "int"
            description: "default DEFAULT_HTTP_PORT"
        outputs:
          type: "side effect"
          description: "Server started unless --no-serve"
        raises: []
      logic:
        - "Import DEFAULT_HTTP_PORT"
        - "Define --no-serve (store_false, dest=serve); set_defaults(serve=True)"
        - "Set --http-port default to DEFAULT_HTTP_PORT"
        - "Leave the 'if args.serve' construction/startup guard intact"
        - "Refresh epilog examples"
  dependencies:
    internal:
      - "main.py imports DEFAULT_HTTP_PORT from solax_modbus.presentation.server"
    external: []

data_schema:
  entities: []

error_handling:
  strategy: "Unchanged. Port-bind failure is still logged and the poll loop continues."
  exceptions:
    - exception: "OSError"
      condition: "http-port already in use"
      handling: "Logged in server.start(); server disabled; poll loop continues"
  logging:
    level: "INFO"
    format: "unchanged"

testing:
  unit_tests:
    - scenario: "args with serve defaulting True, no --no-serve"
      expected: "TelemetryServer constructed and started"
    - scenario: "args with --no-serve"
      expected: "TelemetryServer not constructed"
    - scenario: "default http_port"
      expected: "8181"
  edge_cases:
    - "--no-serve with --http-port supplied: no server bound; no error"
  validation:
    - "pytest passes"
    - "grep shows 8181 only via DEFAULT_HTTP_PORT; no residual 8080 default in main.py or server.py"

deliverable:
  format_requirements:
    - "Modify files in place; do not rewrite unrelated sections"
  files:
    - path: "src/solax_modbus/presentation/server.py"
      content: "Add DEFAULT_HTTP_PORT = 8181; constructor default uses it; docstring updated"
    - path: "src/solax_modbus/main.py"
      content: "Import constant; --serve -> --no-serve (store_false, default serve=True); --http-port default DEFAULT_HTTP_PORT; epilog examples"
    - path: "tests/test_solax_poll.py"
      content: "http_port 8181; invert serve-absent assertion; add --no-serve case"

success_criteria:
  - "solax-monitor <ip> serves on 8181 with no flag"
  - "solax-monitor <ip> --no-serve binds no port"
  - "solax-monitor <ip> --http-port 9000 serves on 9000"
  - "DEFAULT_HTTP_PORT is the only literal for the default port"
  - "pytest passes"

element_registry:
  source: "ai/workspace/design/design-solax-modbus-name_registry-master.md"
  entries:
    modules:
      - name: "solax_modbus.presentation.server"
        path: "src/solax_modbus/presentation/server.py"
    classes:
      - name: "TelemetryServer"
        module: "solax_modbus.presentation.server"
    functions:
      - name: "main"
        module: "solax_modbus.main"
        signature: "main() -> None"
    constants:
      - name: "DEFAULT_HTTP_PORT"
        module: "solax_modbus.presentation.server"
        type: "int"
      - name: "DEFAULT_ALLOWED_NETWORKS"
        module: "solax_modbus.presentation.server"
        type: "list"

notes: >
  Human decisions (2026-07-07): serve by default with --no-serve; port 8181;
  DEFAULT_HTTP_PORT as single source of truth; server.py aligned. Do not remove
  --http-port/--allow; do not touch the allowlist model. bin/install.sh,
  README.md, and docs/guide.md are handled outside this prompt.
```
