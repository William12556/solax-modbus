```yaml
# T03 Issue Document
# Off-Grid UI Simplification and SQLite History

issue_info:
  id: "issue-a2d5f7c9"
  title: "Off-Grid UI Simplification and SQLite History"
  date: "2026-07-16"
  reporter: "William Watson"
  status: "closed"
  severity: "medium"
  type: "requirement_change"
  iteration: 1
  coupled_docs:
    change_ref: "change-a2d5f7c9"
    change_iteration: 1

source:
  origin: "requirement_change"
  test_ref: ""
  description: >
    Operator requests simplification of the web UI for an island (off-grid)
    solar installation with no utility connection. Primary metrics of interest:
    total solar production, battery state of charge and charge/discharge level,
    and house load. A historical overview is requested, stored in a compact
    round-robin-style local database. These requirements deviate from the
    established InfluxDB-based Data domain baseline, which was designed for a
    grid-tied, remote time-series database model.

affected_scope:
  components:
    - name: "TimeSeriesStore"
      file_path: "src/solax_modbus/data/storage.py"
    - name: "DataValidator"
      file_path: "src/solax_modbus/data/validator.py"
    - name: "DataBuffer"
      file_path: "src/solax_modbus/data/buffer.py"
    - name: "TelemetryServer"
      file_path: "src/solax_modbus/presentation/server.py"
    - name: "dashboard"
      file_path: "src/solax_modbus/presentation/templates/dashboard.html"
  designs:
    - design_ref: "design-b7c8d9e0-component_data_storage"
    - design_ref: "design-a6b7c8d9-component_data_validator"
    - design_ref: "design-c8d9e0f1-component_data_buffer"
    - design_ref: "design-9e4b2c3d-domain_data"
    - design_ref: "design-af5c3d4e-domain_presentation"
    - design_ref: "design-9b7e2c4a-component_presentation_server"
    - design_ref: "design-solax-modbus-master"
    - design_ref: "requirements-solax-modbus-master"
  version: "0.1.4"

reproduction:
  prerequisites: "Not applicable - requirement change, not a defect."
  steps:
    - "Not applicable."
  frequency: "n/a"
  reproducibility_conditions: "n/a"
  preconditions: ""
  test_data: ""
  error_output: ""

behavior:
  expected: >
    A simplified dashboard presenting four primary metrics (solar production,
    battery SOC and flow, house load, system status) with inline historical
    sparklines, backed by a compact local persistence layer suited to a
    standalone off-grid deployment.
  actual: >
    Current dashboard exposes grid-tied telemetry (three-phase grid breakdown,
    per-string PV voltage/current, feed-in, temperatures) with no historical
    view. The persistence baseline (FR-010 through FR-012, Data domain) targets
    InfluxDB with network-outage buffering and multi-tier retention.
  impact: >
    UI presents grid-oriented detail not meaningful for an off-grid island
    system; no historical trend is available; the persistence baseline mandates
    an external database dependency inconsistent with the standard-library
    discipline of the deployed system.
  workaround: "None."

environment:
  python_version: "3.13"
  os: "Debian 13 (trixie), macOS (development)"
  dependencies:
    - library: "pymodbus"
      version: ">=3.11.0,<4.0.0"
  domain: "Data, Presentation"

analysis:
  root_cause: >
    The Data domain baseline was designed for a grid-tied deployment with a
    remote InfluxDB time-series store, network-outage buffering, and data
    quality scoring. The actual deployment is a single, headless, off-grid unit
    where a local SQLite store with periodic downsampling satisfies the
    historical requirement without external dependencies, and where network
    outage buffering and quality scoring are not warranted.
  technical_notes: >
    Decisions agreed with operator:
    (1) Persistence engine: SQLite (stdlib sqlite3) with a raw table and a
        downsampled rollup table.
    (2) Retention: raw 1-min/24h; rollup 15-min/30d; each rollup bucket stores
        avg, min, and max.
    (3) History served as JSON via a new /api/history route; sparklines rendered
        client-side in dashboard.html (consistent with /api/telemetry).
    (4) TimeSeriesStore superseded in place (InfluxDB -> SQLite); minimal range
        validation folded into the store write path.
    (5) DataValidator and DataBuffer retired; FR-011 (buffering) retired;
        FR-009 (validation) narrowed to the folded range check.
    (6) Store PRIMITIVES only (pv_power, battery_power, battery_soc,
        grid_power_total). house_load is derived at display time
        (house_load = pv_power - battery_power + grid_power_total), not stored.
    Falsification note: the grid-port registers (0x006A) and feed_in_power
    (0x0046) are the only AC-side power reads in the register map. On a true
    off-grid island the grid port may read near zero and house consumption is
    served via an EPS/backup output not in the current register map. The
    house_load derivation is provisional and must be validated against emulator
    and live data before the history is relied upon.
  related_issues:
    - issue_ref: ""
      relationship: ""

resolution:
  assigned_to: "Strategic Domain"
  target_date: ""
  approach: >
    Author change-a2d5f7c9 and revise the requirements and design baseline.
    Source implementation delivered via prompt-a2d5f7c9 (T04) for Claude Code.
  change_ref: "change-a2d5f7c9"
  resolved_date: "2026-07-16"
  resolved_by: "Claude Code (Tactical Domain)"
  fix_description: >
    SQLite TimeSeriesStore (raw + rollup, primitives only), /api/history
    endpoint, four-card dashboard with client-side house_load derivation, and
    main.py integration implemented per prompt-a2d5f7c9 and committed by
    Claude Code. P08 reviewed against design-b7c8d9e0 and design-9b7e2c4a: pass.

verification:
  verified_date: "2026-07-16"
  verified_by: "Claude (Strategic Domain, P08 review)"
  test_results: >
    P08 code review against design-b7c8d9e0 and design-9b7e2c4a: storage.py
    (primitives-only schema, retention, folded validation), server.py
    (/api/history under existing allowlist), main.py integration (--db-path,
    inline rollup/prune, ordered shutdown), dashboard.html (four cards,
    client-side house_load derivation with provisional-formula comment) all
    conform. validator.py and buffer.py confirmed absent. Existing pytest
    suite not executed by Claude; operator to confirm green.
  closure_notes: >
    Requirements and design baseline revised; source implemented via
    prompt-a2d5f7c9 and committed/pushed by Claude Code. Issue closed.

prevention:
  preventive_measures: >
    Confirm deployment topology (grid-tied vs off-grid) and persistence
    constraints during requirements elicitation before committing a persistence
    engine to the baseline.
  process_improvements: ""

verification_enhanced:
  verification_steps:
    - "Requirements FR-010, FR-012, NFR-008, AR-002 reflect SQLite."
    - "FR-011 retired; FR-009 narrowed; FR-019 added for /api/history."
    - "Design set consistent across master, data domain, storage, presentation domain, server."
    - "DataValidator and DataBuffer retired in designs and name registry."
    - "Store persists primitives; house_load derived at display."
  verification_results: >
    All steps confirmed by P08 review of the implemented source (storage.py,
    server.py, main.py, dashboard.html) against the revised design and
    requirements baseline.

traceability:
  design_refs:
    - "design-b7c8d9e0-component_data_storage"
    - "design-9e4b2c3d-domain_data"
    - "design-9b7e2c4a-component_presentation_server"
  change_refs:
    - "change-a2d5f7c9"
  test_refs: []

notes: >
  Baseline deviation raised at operator request. Full P02 design plus T02 change
  documentation elected over the primer 7.0 initial-implementation forward path.
  Source code implementation delivered via a T04 prompt (prompt-a2d5f7c9) for the
  Claude Code tactical profile.

loop_context:
  was_loop_execution: false
  blocked_at_iteration: 0
  failure_mode: ""
  last_review_feedback: ""

version_history:
  - version: "1.0"
    date: "2026-07-16"
    author: "William Watson"
    changes:
      - "Initial issue documenting off-grid UI simplification and SQLite history baseline deviation"
  - version: "1.1"
    date: "2026-07-16"
    author: "William Watson"
    changes:
      - "Recorded primitives-storage decision and provisional house_load derivation (grid-port registers may not represent off-grid house consumption)"
  - version: "1.2"
    date: "2026-07-16"
    author: "William Watson"
    changes:
      - "Closed following P08 review of implemented source (prompt-a2d5f7c9). Status open -> closed."

metadata:
  copyright: "Copyright (c) 2026 William Watson. MIT License."
  template_version: "1.0"
  schema_type: "t03_issue"
```
