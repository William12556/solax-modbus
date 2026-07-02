# Prompt: Implement TelemetryServer (HTTP Telemetry Server)

Created: 2026 July 01

---

## Table of Contents

- [Prompt Information](<#prompt information>)
- [Context](<#context>)
- [Specification](<#specification>)
- [Design](<#design>)
- [Data Schema](<#data schema>)
- [Error Handling](<#error handling>)
- [Testing](<#testing>)
- [Deliverable](<#deliverable>)
- [Success Criteria](<#success criteria>)
- [Element Registry](<#element registry>)
- [Notes](<#notes>)
- [Version History](<#version history>)

---

## Prompt Information

```yaml
prompt_info:
  id: "prompt-c4d8e1f6"
  task_type: "code_generation"
  source_ref: "design-9b7e2c4a"        # Tier 3 component design (authoritative)
  date: "2026-07-01"
  iteration: 1
  coupled_docs:
    change_ref: "N/A"                   # initial implementation; no change document (primer §7.0)
    change_iteration: 1
  profile: "claude"                     # Claude Code (manual, single-pass)
```

[Return to Table of Contents](<#table of contents>)

---

## Context

```yaml
context:
  purpose: "Add an opt-in embedded HTTP server that serves live single-inverter telemetry (JSON endpoint plus a static dashboard) to LAN clients, reading from shared state populated by the existing poll loop."
  integration: "New Presentation-domain package src/solax_modbus/presentation/. The Application entry point (main.py) instantiates shared state, writes each poll snapshot to it, and starts/stops the server thread. The server never contacts the inverter."
  knowledge_references:
    - "ai/workspace/design/design-9b7e2c4a-component_presentation_server.md"
    - "ai/workspace/design/design-af5c3d4e-domain_presentation.md"
    - "ai/workspace/design/design-bf6d4e5f-domain_application.md"
    - "ai/workspace/design/design-solax-modbus-name_registry-master.md"
    - "ai/workspace/requirements/requirements-solax-modbus-master.md"   # FR-018, NFR-006
  constraints:
    - "Standard library only: http.server, json, ipaddress, threading, pathlib. No new external dependencies."
    - "Read-only: the server reads shared state; it never calls the inverter or SolaxInverterClient."
    - "Default behaviour unchanged when --serve is absent."
    - "Existing tests must remain green. Do not alter the public behaviour of SolaxInverterClient or InverterDisplay."
    - "IPv4 only."
    - "Use --http-port for the server. --port remains the Modbus TCP port."
    - "Names must match the name registry exactly."
```

[Return to Table of Contents](<#table of contents>)

---

## Specification

```yaml
specification:
  description: |
    Create the Presentation-domain package implementing StateHolder, TelemetryServer, and
    TelemetryRequestHandler, plus a static dashboard asset. Refactor main.py to own a
    StateHolder instance, write each poll snapshot to it, and (when --serve is set) start the
    server before the poll loop and stop it during ordered shutdown. Full component detail is in
    design-9b7e2c4a; this prompt specifies the essentials.
  requirements:
    functional:
      - "StateHolder: thread-safe holder of the latest telemetry dict; get() returns a copy under lock; set(data) replaces the snapshot under lock."
      - "TelemetryServer: background ThreadingHTTPServer on its own thread; start() and stop() lifecycle; constructor (state, bind_host='0.0.0.0', port=8080, allowed_networks=None)."
      - "TelemetryRequestHandler.do_GET: reject non-allowlisted source IPs with 403; route '/' to the dashboard (text/html); route '/api/telemetry' to StateHolder.get() serialized as JSON (application/json); all other paths 404."
      - "DEFAULT_ALLOWED_NETWORKS: 10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16, 169.254.0.0/16 (as ipaddress networks)."
      - "main.py: add --serve (flag), --http-port (int, default 8080), --allow (repeatable str, CIDR); instantiate StateHolder; call state.set(data) each poll iteration; when --serve, start server before loop and stop it in ordered shutdown (stop loop -> server.stop() -> client.disconnect())."
      - "When --allow is absent, use DEFAULT_ALLOWED_NETWORKS; when present, parse each value as an ipaddress network."
    technical:
      language: "Python"
      version: "3.13"
      standards:
        - "Thread-safe shared state via a single lock"
        - "Comprehensive error handling"
        - "Debug logging with traceback via the existing logger"
        - "Professional docstrings"
        - "PEP 8 compliant"
  performance:
    - target: "No added inverter I/O; server reads in-memory snapshot only"
      metric: "Poll cadence unaffected by HTTP request volume"
```

[Return to Table of Contents](<#table of contents>)

---

## Design

```yaml
design:
  architecture: "Background-poll-and-serve. One producer (poll loop) writes a lock-guarded snapshot; N consumer HTTP handler threads read it. Server runs on its own thread; server failure must not stop polling."
  components:
    - name: "StateHolder"
      type: "class"
      purpose: "Thread-safe latest-snapshot holder, owned (instantiated) by the Application entry point."
      interface:
        inputs:
          - name: "data"
            type: "dict"
            description: "Telemetry dict from poll_inverter() (set)"
        outputs:
          type: "dict"
          description: "Copy of the latest snapshot (get)"
        raises: []
      logic:
        - "__init__: create threading.Lock and empty snapshot dict"
        - "get(): acquire lock; return a shallow copy of the snapshot"
        - "set(data): acquire lock; replace snapshot with a copy of data"
    - name: "TelemetryServer"
      type: "class"
      purpose: "Own the ThreadingHTTPServer lifecycle on a background thread."
      interface:
        inputs:
          - name: "state"
            type: "StateHolder"
            description: "Shared snapshot holder (read-only use)"
          - name: "bind_host"
            type: "str"
            description: "Interface to bind (default '0.0.0.0')"
          - name: "port"
            type: "int"
            description: "TCP port (default 8080)"
          - name: "allowed_networks"
            type: "list | None"
            description: "Permitted source networks; None -> DEFAULT_ALLOWED_NETWORKS"
        outputs:
          type: "None"
          description: "start()/stop() have no return"
        raises:
          - "OSError (bind failure in start(); log and do not crash the poll loop)"
      logic:
        - "__init__: store state, bind_host, port, allowed_networks (or DEFAULT_ALLOWED_NETWORKS), resolve dashboard template path; httpd/thread None"
        - "start(): create ThreadingHTTPServer((bind_host, port), TelemetryRequestHandler); attach state, allowed_networks, and template to the httpd instance for handler access; start a daemon thread running serve_forever()"
        - "stop(): if running, call httpd.shutdown() then httpd.server_close(); join the thread with a timeout; idempotent"
    - name: "TelemetryRequestHandler"
      type: "class"
      purpose: "Per-request GET handler; base BaseHTTPRequestHandler."
      interface:
        inputs:
          - name: "(HTTP GET request)"
            type: "n/a"
            description: "Standard handler invocation"
        outputs:
          type: "HTTP response"
          description: "HTML, JSON, 403, or 404"
        raises: []
      logic:
        - "do_GET: if client_address[0] not in any allowed network -> 403"
        - "route '/' -> read dashboard template, respond 200 text/html"
        - "route '/api/telemetry' -> json.dumps(server.state.get()), respond 200 application/json"
        - "else -> 404"
        - "override log_message to route through the module logger (avoid stderr noise)"
  dependencies:
    internal:
      - "StateHolder instance provided by main.py"
    external: []
```

[Return to Table of Contents](<#table of contents>)

---

## Data Schema

```yaml
data_schema:
  entities:
    - name: "TelemetrySnapshot"
      attributes:
        - name: "(telemetry keys)"
          type: "dict"
          constraints: "Exactly the dict returned by SolaxInverterClient.poll_inverter(); includes 'timestamp'. Serialized verbatim to JSON."
      validation:
        - "When the snapshot is empty (no poll completed), /api/telemetry returns an empty object; the endpoint does not error."
```

[Return to Table of Contents](<#table of contents>)

---

## Error Handling

```yaml
error_handling:
  strategy: "Server faults are isolated from the poll loop."
  exceptions:
    - exception: "OSError"
      condition: "Port unavailable at bind"
      handling: "Log with traceback; server does not start; poll loop continues"
    - exception: "Exception"
      condition: "Unhandled error in a request handler"
      handling: "Respond 500; log with traceback; server continues"
    - exception: "ValueError"
      condition: "Invalid --allow CIDR value at startup"
      handling: "Log and exit before starting the loop"
  logging:
    level: "INFO default; DEBUG for request detail; ERROR for faults"
    format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
```

[Return to Table of Contents](<#table of contents>)

---

## Testing

```yaml
testing:
  unit_tests:
    - scenario: "StateHolder.set then get"
      expected: "get() returns an equal but distinct dict (copy, not reference)"
    - scenario: "Allowlisted source IP requests /api/telemetry"
      expected: "200 application/json with current snapshot"
    - scenario: "Non-allowlisted source IP requests any path"
      expected: "403"
    - scenario: "GET unknown path from allowlisted IP"
      expected: "404"
    - scenario: "main without --serve"
      expected: "Console behaviour unchanged; no port bound"
  edge_cases:
    - "Request before first poll completes (empty snapshot)"
    - "Ctrl+C while server running (clean, prompt shutdown; no hang)"
    - "--http-port already in use (logged; poll loop still runs)"
  validation:
    - "Existing test suite passes unchanged"
    - "No new external dependency introduced"
  note: "Formal P06 test documents and pytest are a separate phase after review."
```

[Return to Table of Contents](<#table of contents>)

---

## Deliverable

```yaml
deliverable:
  format_requirements:
    - "Save generated code directly to the specified paths"
    - "Implement interfaces exactly as named in the Element Registry"
    - "Consult design-9b7e2c4a for any detail not restated here"
  files:
    - path: "src/solax_modbus/presentation/__init__.py"
      content: "Package marker (may be empty)."
    - path: "src/solax_modbus/presentation/server.py"
      content: |
        Implement DEFAULT_ALLOWED_NETWORKS, StateHolder, TelemetryRequestHandler,
        and TelemetryServer per the Design and Element Registry sections.
        Standard library only.
    - path: "src/solax_modbus/presentation/templates/dashboard.html"
      content: |
        Minimal static page. On load and on an interval, fetch('/api/telemetry'),
        then render the returned fields (timestamp, run_mode, grid, PV, battery,
        feed-in, energy). No external assets or frameworks. Inline CSS/JS only.
    - path: "src/solax_modbus/main.py"
      content: |
        Add --serve, --http-port (default 8080), --allow (repeatable CIDR) to argparse.
        Instantiate StateHolder. Call state.set(data) each poll iteration.
        When --serve: parse --allow (or use default), construct and start TelemetryServer
        before the loop; in the finally block perform ordered shutdown
        (server.stop() before client.disconnect()). Preserve all existing behaviour.
```

[Return to Table of Contents](<#table of contents>)

---

## Success Criteria

```yaml
success_criteria:
  - "Without --serve, application behaviour is identical to the current version; no port is bound."
  - "With --serve, GET /api/telemetry from an allowlisted IP returns the current telemetry as JSON."
  - "With --serve, GET / returns the dashboard, which displays live values by polling the JSON endpoint."
  - "A request from a non-allowlisted source IP receives 403; an unknown path receives 404."
  - "Ctrl+C shuts down cleanly with the server running (no hang, socket released)."
  - "Only standard-library modules are imported by server.py."
  - "The existing test suite passes unchanged."
```

[Return to Table of Contents](<#table of contents>)

---

## Element Registry

```yaml
element_registry:
  source: "ai/workspace/design/design-solax-modbus-name_registry-master.md"
  entries:
    modules:
      - name: "solax_modbus.presentation.server"
        path: "src/solax_modbus/presentation/server.py"
    classes:
      - name: "StateHolder"
        module: "solax_modbus.presentation.server"
      - name: "TelemetryServer"
        module: "solax_modbus.presentation.server"
      - name: "TelemetryRequestHandler"
        module: "solax_modbus.presentation.server"
    functions:
      - name: "get"
        module: "solax_modbus.presentation.server"
        signature: "get(self) -> Dict[str, Any]"
      - name: "set"
        module: "solax_modbus.presentation.server"
        signature: "set(self, data: Dict[str, Any]) -> None"
      - name: "start"
        module: "solax_modbus.presentation.server"
        signature: "start(self) -> None"
      - name: "stop"
        module: "solax_modbus.presentation.server"
        signature: "stop(self) -> None"
      - name: "do_GET"
        module: "solax_modbus.presentation.server"
        signature: "do_GET(self) -> None"
    constants:
      - name: "DEFAULT_ALLOWED_NETWORKS"
        module: "solax_modbus.presentation.server"
        type: "list"
```

[Return to Table of Contents](<#table of contents>)

---

## Notes

```yaml
notes: |
  Profile: Claude Code (manual, single-pass). Claude Code reads this full document; the
  tactical_brief and AEL orchestrator fields do not apply and are omitted.
  coupled_docs.change_ref is N/A: this is initial implementation from an approved design,
  which does not require issue or change documents (primer §7.0). The T03 -> T02 corrective
  loop applies only on a later test failure.
  Scope is confined to design-9b7e2c4a and the associated main.py integration. No functionality
  beyond the approved design is to be added.
```

[Return to Table of Contents](<#table of contents>)

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-07-01 | Initial prompt. Implement TelemetryServer, StateHolder, TelemetryRequestHandler, dashboard asset, and main.py integration per design-9b7e2c4a. Authored for the Claude Code profile. |

---

Copyright (c) 2025 William Watson. This work is licensed under the MIT License.
