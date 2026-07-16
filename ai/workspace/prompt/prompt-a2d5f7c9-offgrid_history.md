# Prompt: Implement SQLite History (TimeSeriesStore, /api/history, Dashboard)

Created: 2026 July 16

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
  id: "prompt-a2d5f7c9"
  task_type: "code_generation"
  source_ref: "change-a2d5f7c9"
  target_profile: "claude_code"
  date: "2026-07-16"
  iteration: 1
  coupled_docs:
    change_ref: "change-a2d5f7c9"
    change_iteration: 1
```

[Return to Table of Contents](<#table of contents>)

---

## Context

```yaml
context:
  purpose: >
    Add a local SQLite time-series history (raw + rollup) and a /api/history
    JSON endpoint, and rework the dashboard to four primary off-grid metrics
    (solar production, battery, house load, status) with inline client-side
    sparklines. Supersedes the InfluxDB persistence baseline; retires
    DataValidator and DataBuffer.
  integration: >
    New Data-domain package src/solax_modbus/data/ (storage.py only; validator.py
    and buffer.py are retired and must NOT be created). main.py instantiates
    TimeSeriesStore, writes a sample each poll iteration, schedules periodic
    rollup and prune, passes the store into TelemetryServer, and performs
    ordered shutdown (stop server, close store, disconnect client).
    TelemetryServer gains a read-only store reference and a new /api/history
    route. dashboard.html is reworked to four cards with sparklines fed by
    /api/history, secondary detail collapsed but still sourced from the
    unchanged /api/telemetry.
  knowledge_references:
    - "ai/workspace/design/design-b7c8d9e0-component_data_storage.md"
    - "ai/workspace/design/design-9e4b2c3d-domain_data.md"
    - "ai/workspace/design/design-9b7e2c4a-component_presentation_server.md"
    - "ai/workspace/design/design-af5c3d4e-domain_presentation.md"
    - "ai/workspace/design/design-solax-modbus-name_registry-master.md"
    - "ai/workspace/requirements/requirements-solax-modbus-master.md"
    - "ai/workspace/change/change-a2d5f7c9-offgrid-ui-sqlite-history.md"
    - "ai/workspace/issues/issue-a2d5f7c9-offgrid-ui-sqlite-history.md"
  constraints:
    - "Standard library only for storage: sqlite3, time, threading, logging, typing. No new external dependency."
    - "Do NOT create validator.py or buffer.py (retired, change-a2d5f7c9). Do not reintroduce DataValidator, DataBuffer, or ValidationResult."
    - "TimeSeriesStore persists PRIMITIVES ONLY: pv_power, battery_power, battery_soc, grid_power_total. Do NOT add a house_load column to either table."
    - "house_load is derived client-side in dashboard.html as pv_power minus battery_power plus grid_power_total. Do not compute or store it server-side."
    - "Existing /api/telemetry contract, field names, and register-read logic are unchanged. This prompt does not touch main.py Modbus polling or the register map."
    - "Existing tests must remain green. Do not alter public behaviour of SolaxInverterClient."
    - "Writes must not block or measurably delay the poll loop."
    - "Names must match the name registry exactly."
    - "Mark the house_load formula with a source code comment noting it is provisional pending validation against live and emulator data (see issue-a2d5f7c9 analysis: the grid-port registers may read near zero on a true off-grid island whose loads are served via an EPS or backup output outside the current register map)."
```

[Return to Table of Contents](<#table of contents>)

---

## Specification

```yaml
specification:
  description: |
    Create src/solax_modbus/data/__init__.py and src/solax_modbus/data/storage.py
    implementing TimeSeriesStore (SQLite, raw + rollup tables, primitives only).
    Modify presentation/server.py to accept an optional TimeSeriesStore and add
    a GET /api/history route. Modify main.py to own the store lifecycle and
    argparse. Rewrite presentation/templates/dashboard.html to four primary
    cards with client-side SVG sparklines and a collapsed detail section. Full
    component detail is in design-b7c8d9e0 and design-9b7e2c4a; this prompt
    specifies the essentials.
  requirements:
    functional:
      - "TimeSeriesStore(db_path='solax_history.db') opens or creates the SQLite file with check_same_thread=False, a threading.Lock guarding access, and WAL journal mode."
      - "init_schema() issues CREATE TABLE IF NOT EXISTS for raw(ts, pv_power, battery_power, battery_soc, grid_power_total) and rollup(bucket_ts, metric, avg, min, max) with the indexes specified in design-b7c8d9e0 section 5.0. Idempotent."
      - "write_sample(data: dict) -> bool derives pv_power as pv1_power plus pv2_power; battery_power and battery_soc read directly; grid_power_total as the sum of grid_power_r, grid_power_s, grid_power_t (missing individual phases treated as 0 in the sum, but if all three are absent leave grid_power_total NULL). Apply the range checks in design-b7c8d9e0 section 7.0: a breach logs WARNING and stores NULL for that field, the row is kept. Insert one raw row at the current epoch second. Return True on success, False and a logged ERROR on failure; never raise out of this method."
      - "rollup() -> int aggregates raw rows since the last rollup horizon into 15-minute buckets (bucket_ts equals ts minus ts modulo 900) computing avg, min, max per metric, and upserts into rollup per design-b7c8d9e0 section 6.1. Returns the number of bucket-metric rows written or updated."
      - "prune() -> int deletes raw rows older than 24 hours and rollup rows older than 30 days per design-b7c8d9e0 section 6.2. Returns total rows deleted."
      - "query_history(metric: str, window_seconds: int) -> list of dict validates metric is one of the four stored metrics, raising ValueError otherwise; returns rollup rows within the trailing window as bucket_ts, avg, min, max dictionaries ordered oldest to newest."
      - "close() -> None is idempotent; flushes and closes the connection."
      - "TelemetryServer.__init__ gains an optional store parameter (TimeSeriesStore or None, default None); the reference is stored for the handler."
      - "TelemetryRequestHandler.do_GET adds route /api/history: if store is None, return an empty list per metric with HTTP 200; otherwise for each of the four metrics call store.query_history(metric, 30 times 24 times 3600), assemble a JSON object keyed by the four metric names, respond 200 application/json. Subject to the same source-IP allowlist check as the other routes, unchanged."
      - "main.py adds --db-path (str, default solax_history.db); instantiates TimeSeriesStore(args.db_path) and calls init_schema() at startup unconditionally (not gated on --serve); each poll iteration, after state.set(data), calls store.write_sample(data); tracks elapsed time since the last rollup and calls store.rollup() plus store.prune() roughly every 15 minutes inline in the existing poll loop, without adding a new thread; passes store=store when constructing TelemetryServer; in the ordered shutdown sequence calls store.close() after server.stop() and before client.disconnect()."
      - "dashboard.html presents four primary cards: Solar Production, Battery, House Load, Status. Each shows a current value from /api/telemetry and an inline SVG sparkline built from the corresponding /api/history series. The House Load card computes its headline number client-side from the current telemetry snapshot as pv_power minus battery_power plus grid_power_total, and derives the same formula per point for its sparkline from the history series. Secondary detail (per-string PV voltage and current, phase breakdown, temperatures) moves into a collapsed details element sourced from /api/telemetry as before. Poll /api/telemetry on the existing interval; poll /api/history on a longer interval, for example every 60 seconds."
    technical:
      language: "Python"
      version: "3.13"
      standards:
        - "Thread-safe store access via a single lock"
        - "Comprehensive error handling; store faults never crash the poll loop"
        - "Debug logging with traceback via the existing logger"
        - "Professional docstrings"
        - "PEP 8 compliant"
  performance:
    - target: "Write path does not measurably delay polling"
      metric: "write_sample() returns well under the poll interval; no added inverter I/O"
    - target: "Bounded local storage"
      metric: "Steady-state db_path file size stays well under 1 GB at the defined retention (NFR-008)"
```

[Return to Table of Contents](<#table of contents>)

---

## Design

```yaml
design:
  architecture: "Single-writer local persistence. The poll loop is the sole writer (write_sample, periodic rollup and prune); HTTP handler threads are read-only via query_history(). A lock in TimeSeriesStore serializes access; store failures are isolated from polling."
  components:
    - name: "TimeSeriesStore"
      type: "class"
      purpose: "Local SQLite store: raw samples, downsampled rollup, retention, and history query."
      interface:
        inputs:
          - name: "db_path"
            type: "str"
            description: "Path to the SQLite database file"
        outputs:
          type: "varies"
          description: "See write_sample, rollup, prune, query_history, close in Specification"
        raises:
          - "ValueError (query_history with an unknown metric)"
      logic:
        - "__init__ opens the connection with check_same_thread=False, sets PRAGMA journal_mode=WAL, creates a threading.Lock, calls init_schema()"
        - "init_schema creates raw and rollup tables and indexes if absent, per design-b7c8d9e0 section 5.0"
        - "write_sample derives the four primitives from the telemetry dict, range-checks each per section 7.0, inserts one raw row under lock"
        - "rollup groups by 900-second bucket per metric and upserts into rollup, under lock"
        - "prune deletes raw rows older than 86400 seconds and rollup rows older than 2592000 seconds, under lock"
        - "query_history selects from rollup filtered by metric and bucket_ts, ordered ascending, under lock"
        - "close closes the connection if open and is safe to call more than once"
    - name: "TelemetryServer (modified)"
      type: "class"
      purpose: "Gains a read-only TimeSeriesStore reference for /api/history."
      interface:
        inputs:
          - name: "store"
            type: "TimeSeriesStore or None"
            description: "Optional history source; None yields empty /api/history series"
        outputs:
          type: "None"
          description: "Constructor stores the reference; behaviour otherwise unchanged"
        raises: []
      logic:
        - "__init__ accepts and stores the new store parameter alongside the existing state parameter; both are attached to the httpd instance in start() for handler access, as state already is"
    - name: "TelemetryRequestHandler (modified)"
      type: "class"
      purpose: "Adds the /api/history route."
      interface:
        inputs:
          - name: "(HTTP GET request)"
            type: "n/a"
            description: "Standard handler invocation"
        outputs:
          type: "HTTP response"
          description: "JSON history object, or existing responses for other routes"
        raises: []
      logic:
        - "do_GET keeps the existing allowlist check and existing routes unchanged; adds /api/history returning the per-metric JSON described in Specification; responds 200 application/json"
  dependencies:
    internal:
      - "TimeSeriesStore instance provided by main.py"
      - "Telemetry dict shape from SolaxInverterClient.poll_inverter() (Protocol domain, unchanged)"
    external: []
```

[Return to Table of Contents](<#table of contents>)

---

## Data Schema

```yaml
data_schema:
  entities:
    - name: "raw"
      attributes:
        - name: "ts"
          type: "INTEGER"
          constraints: "epoch seconds, not null"
        - name: "pv_power"
          type: "INTEGER"
          constraints: "nullable; 0 to 15000 or NULL on breach"
        - name: "battery_power"
          type: "INTEGER"
          constraints: "nullable; signed, -15000 to 15000 or NULL on breach"
        - name: "battery_soc"
          type: "INTEGER"
          constraints: "nullable; 0 to 100 or NULL on breach"
        - name: "grid_power_total"
          type: "INTEGER"
          constraints: "nullable; signed, -15000 to 15000 or NULL on breach"
      validation:
        - "One row per write_sample() call; out-of-range fields are NULL, not row rejection"
    - name: "rollup"
      attributes:
        - name: "bucket_ts"
          type: "INTEGER"
          constraints: "epoch seconds, 15-minute bucket start, not null"
        - name: "metric"
          type: "TEXT"
          constraints: "one of pv_power, battery_power, battery_soc, grid_power_total"
        - name: "avg"
          type: "REAL"
          constraints: "nullable"
        - name: "min"
          type: "REAL"
          constraints: "nullable"
        - name: "max"
          type: "REAL"
          constraints: "nullable"
      validation:
        - "PRIMARY KEY (bucket_ts, metric); upsert on conflict"
        - "house_load is never a column or a metric value in this table"
```

[Return to Table of Contents](<#table of contents>)

---

## Error Handling

```yaml
error_handling:
  strategy: "Store faults are isolated from the poll loop and from the HTTP server, exactly as the existing TelemetryServer isolates server faults."
  exceptions:
    - exception: "sqlite3.OperationalError"
      condition: "Database locked (concurrent access) or disk full"
      handling: "Log with traceback; write_sample, rollup, prune return False or 0; polling and serving continue"
    - exception: "sqlite3.DatabaseError"
      condition: "Corrupt database file"
      handling: "Log ERROR at open time; do not auto-recreate; a clear startup log message is required (operator intervention expected)"
    - exception: "ValueError"
      condition: "query_history called with an unrecognised metric"
      handling: "Raise; do_GET catches and responds with an empty series for that metric plus a logged WARNING"
  logging:
    level: "INFO for schema init and periodic rollup summary; WARNING for out-of-range fields and lock retries; ERROR for write or open failures"
    format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
```

[Return to Table of Contents](<#table of contents>)

---

## Testing

```yaml
testing:
  unit_tests:
    - scenario: "write_sample with all four primitives in range"
      expected: "One raw row inserted with all fields populated"
    - scenario: "write_sample with pv_power out of range"
      expected: "Row inserted with pv_power NULL; other fields populated; WARNING logged"
    - scenario: "rollup over synthetic raw rows spanning two 15-minute buckets"
      expected: "Two rollup rows per metric with correct avg, min, max"
    - scenario: "prune with raw rows older than 24 hours and rollup rows older than 30 days"
      expected: "Old rows removed; recent rows retained"
    - scenario: "query_history for an unknown metric"
      expected: "ValueError raised"
    - scenario: "GET /api/history from an allowlisted IP"
      expected: "200 application/json with four metric keys, each a list of bucket_ts, avg, min, max objects"
    - scenario: "GET /api/history from a non-allowlisted IP"
      expected: "403, unchanged allowlist behaviour"
    - scenario: "GET /api/history when store is None"
      expected: "200 with empty lists per metric, no exception"
  edge_cases:
    - "query_history window larger than available history returns fewer buckets, no error"
    - "write_sample before any rollup has run: raw accumulates; /api/history returns empty until the first rollup"
    - "Concurrent write_sample and query_history: lock serializes, no corruption"
    - "--db-path directory not writable: log ERROR at startup; do not crash silently"
  validation:
    - "Existing test suite (SolaxInverterClient, TelemetryServer /api/telemetry, allowlist) passes unchanged"
    - "No new external dependency introduced (sqlite3 is standard library)"
    - "No house_load column or metric value appears anywhere in the SQLite schema"
  note: "Formal P06 test documents and pytest are a separate phase after review, per project convention."
```

[Return to Table of Contents](<#table of contents>)

---

## Deliverable

```yaml
deliverable:
  format_requirements:
    - "Save generated code directly to the specified paths"
    - "Implement interfaces exactly as named in the Element Registry"
    - "Consult design-b7c8d9e0 and design-9b7e2c4a for any detail not restated here"
    - "Do not create src/solax_modbus/data/validator.py or src/solax_modbus/data/buffer.py"
  files:
    - path: "src/solax_modbus/data/__init__.py"
      content: "Package marker (may be empty)."
    - path: "src/solax_modbus/data/storage.py"
      content: |
        Implement TimeSeriesStore per the Design and Element Registry sections.
        Standard library only: sqlite3, time, threading, logging, typing.
    - path: "src/solax_modbus/presentation/server.py"
      content: |
        Modify TelemetryServer.__init__ to accept an optional store parameter
        (TimeSeriesStore or None, default None); attach it to the httpd instance
        in start() alongside state. Add the /api/history route to
        TelemetryRequestHandler.do_GET per the Specification. Preserve all
        existing routes and the allowlist check.
    - path: "src/solax_modbus/presentation/templates/dashboard.html"
      content: |
        Rework to four primary cards (Solar Production, Battery, House Load,
        Status), each with a current-value readout and an inline SVG sparkline
        rendered client-side from fetch('/api/history'). House Load is computed
        client-side as pv_power minus battery_power plus grid_power_total
        (comment it as provisional, see Context constraints). Move per-string PV,
        phase breakdown, and temperature detail into a collapsed details element
        fed by the existing fetch('/api/telemetry'). No external assets or
        frameworks; inline CSS and JS only.
    - path: "src/solax_modbus/main.py"
      content: |
        Add --db-path (default solax_history.db). Instantiate TimeSeriesStore and
        call init_schema() at startup, unconditional, not gated on --serve. Each
        poll iteration, after state.set(data), call store.write_sample(data).
        Track elapsed time since the last rollup and prune and invoke
        store.rollup() and store.prune() roughly every 15 minutes from within the
        existing poll loop, no new thread. Pass store=store to TelemetryServer. In
        the ordered shutdown sequence, call store.close() after server.stop() and
        before client.disconnect(). Preserve all existing behaviour and flags.
```

[Return to Table of Contents](<#table of contents>)

---

## Success Criteria

```yaml
success_criteria:
  - "TimeSeriesStore creates or opens db_path, writes a raw sample each poll, and rolls up into 15-minute buckets with avg, min, max for pv_power, battery_power, battery_soc, and grid_power_total only."
  - "No house_load column or metric exists anywhere in the SQLite schema or in stored data."
  - "Raw rows older than 24 hours and rollup rows older than 30 days are pruned."
  - "GET /api/history from an allowlisted IP returns 200 JSON with the four metric series; a non-allowlisted IP receives 403 as before."
  - "The dashboard shows four primary cards with sparklines; House Load is computed and displayed client-side from the three stored primitives."
  - "GET /api/telemetry contract and existing dashboard detail, moved to a collapsed section, are unchanged in content."
  - "src/solax_modbus/data/validator.py and src/solax_modbus/data/buffer.py do not exist after this change."
  - "Only standard-library modules are imported by storage.py."
  - "The existing test suite passes unchanged."
  - "Ctrl+C shuts down cleanly with the store open: no hang, database closed."
```

[Return to Table of Contents](<#table of contents>)

---

## Element Registry

```yaml
element_registry:
  source: "ai/workspace/design/design-solax-modbus-name_registry-master.md"
  entries:
    modules:
      - name: "solax_modbus.data.storage"
        path: "src/solax_modbus/data/storage.py"
      - name: "solax_modbus.presentation.server"
        path: "src/solax_modbus/presentation/server.py"
    classes:
      - name: "TimeSeriesStore"
        module: "solax_modbus.data.storage"
      - name: "TelemetryServer"
        module: "solax_modbus.presentation.server"
      - name: "TelemetryRequestHandler"
        module: "solax_modbus.presentation.server"
    functions:
      - name: "init_schema"
        module: "solax_modbus.data.storage"
        signature: "init_schema(self) -> None"
      - name: "write_sample"
        module: "solax_modbus.data.storage"
        signature: "write_sample(self, data: Dict[str, Any]) -> bool"
      - name: "rollup"
        module: "solax_modbus.data.storage"
        signature: "rollup(self) -> int"
      - name: "prune"
        module: "solax_modbus.data.storage"
        signature: "prune(self) -> int"
      - name: "query_history"
        module: "solax_modbus.data.storage"
        signature: "query_history(self, metric: str, window_seconds: int) -> List[Dict[str, Any]]"
      - name: "close"
        module: "solax_modbus.data.storage"
        signature: "close(self) -> None"
      - name: "do_GET"
        module: "solax_modbus.presentation.server"
        signature: "do_GET(self) -> None"
    constants: []
```

[Return to Table of Contents](<#table of contents>)

---

## Notes

```yaml
notes: |
  Profile: claude_code (manual, single-pass). tactical_brief and AEL orchestrator
  fields do not apply and are omitted.
  coupled_docs.change_ref is change-a2d5f7c9 (formal T02/T03 path elected by the
  operator over the primer 7.0 initial-implementation forward path).
  The house_load formula (pv_power minus battery_power plus grid_power_total) is
  provisional: it assumes conservation of energy across PV, battery, and the
  instrumented grid port. On a true off-grid island the grid port may read near
  zero if house loads are served via an EPS or backup output not present in the
  current register map (see issue-a2d5f7c9 analysis and main.py existing register
  map at 0x006A and 0x0046). Storing primitives rather than a derived house_load
  value is deliberate so this formula can be corrected later without losing
  history. Do not add new Modbus registers or change register-read logic in this
  prompt; that is a separate, not-yet-scoped change.
  Scope is confined to design-b7c8d9e0 (SQLite store) and design-9b7e2c4a
  (/api/history route) plus the main.py and dashboard.html integration described
  above. No functionality beyond the approved design is to be added.
```

[Return to Table of Contents](<#table of contents>)

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-07-16 | Initial prompt. Implement TimeSeriesStore (SQLite, primitives-only schema), /api/history route, four-card dashboard with client-side house_load derivation and sparklines, and main.py integration, per design-b7c8d9e0 and design-9b7e2c4a (change-a2d5f7c9). Authored for the Claude Code profile. |
| 1.1 | 2026-07-16 | Closed. Implemented by Claude Code and committed/pushed; P08 review by Claude (Strategic Domain) passed with two non-blocking notes (rollup() full-table re-aggregation; avg-only house_load sparkline). Existing pytest suite not executed by Claude; operator confirmation pending. |

---

Copyright (c) 2026 William Watson. This work is licensed under the MIT License.
