```yaml
# T02 Change Document
# Off-Grid UI Simplification and SQLite History

change_info:
  id: "change-a2d5f7c9"
  title: "Off-Grid UI Simplification and SQLite History"
  date: "2026-07-16"
  author: "William Watson"
  status: "implemented"
  priority: "medium"
  iteration: 1
  coupled_docs:
    issue_ref: "issue-a2d5f7c9"
    issue_iteration: 1

source:
  type: "issue"
  reference: "ai/workspace/issues/issue-a2d5f7c9-offgrid-ui-sqlite-history.md"
  description: >
    Simplify the web UI for an off-grid island installation and add a local
    historical overview. Replace the InfluxDB persistence baseline with a
    standard-library SQLite store using a raw table and a downsampled rollup
    table. Treated as a baseline deviation requiring formal change documentation.

scope:
  summary: >
    Revise the requirements and design baseline to consolidate the dashboard to
    four primary metrics with inline client-rendered sparklines, replace the
    InfluxDB TimeSeriesStore with a SQLite store (raw + rollup) that persists
    primitives only, retire DataValidator and DataBuffer (folding a minimal range
    check into the store), and add a /api/history endpoint. Source implementation
    is delivered via prompt-a2d5f7c9 (T04, Claude Code).
  affected_components:
    - name: "TimeSeriesStore"
      file_path: "src/solax_modbus/data/storage.py"
      change_type: "refactor"
    - name: "DataValidator"
      file_path: "src/solax_modbus/data/validator.py"
      change_type: "delete"
    - name: "DataBuffer"
      file_path: "src/solax_modbus/data/buffer.py"
      change_type: "delete"
    - name: "TelemetryServer"
      file_path: "src/solax_modbus/presentation/server.py"
      change_type: "modify"
    - name: "dashboard"
      file_path: "src/solax_modbus/presentation/templates/dashboard.html"
      change_type: "modify"
  affected_designs:
    - design_ref: "requirements-solax-modbus-master"
      sections: ["FR-009", "FR-010", "FR-011", "FR-012", "FR-019 (new)", "NFR-008", "AR-002", "AR-008", "Traceability", "Glossary"]
    - design_ref: "design-solax-modbus-master"
      sections: ["Scope", "System Overview", "Data Design", "Cross-References"]
    - design_ref: "design-9e4b2c3d-domain_data"
      sections: ["Technology Stack", "Components", "Retention"]
    - design_ref: "design-b7c8d9e0-component_data_storage"
      sections: ["Supersession to SQLite; primitives schema"]
    - design_ref: "design-a6b7c8d9-component_data_validator"
      sections: ["Status -> Retired"]
    - design_ref: "design-c8d9e0f1-component_data_buffer"
      sections: ["Status -> Retired"]
    - design_ref: "design-af5c3d4e-domain_presentation"
      sections: ["Component status", "History responsibility"]
    - design_ref: "design-9b7e2c4a-component_presentation_server"
      sections: ["Routes (/api/history)", "Interfaces"]
    - design_ref: "design-solax-modbus-name_registry-master"
      sections: ["DataValidator, DataBuffer, ValidationResult -> retired"]
  out_of_scope:
    - "Modbus register map changes (no new EPS/backup registers added)"
    - "Rename of the TimeSeriesStore element"
    - "Server-side sparkline rendering"

rational:
  problem_statement: >
    The deployment is a standalone off-grid island unit, but the UI presents
    grid-tied detail and the persistence baseline mandates an external InfluxDB
    dependency with network-outage buffering and quality scoring. No historical
    trend view exists.
  proposed_solution: >
    Simplify the UI to four primary metrics with client-rendered sparklines;
    present house load; replace InfluxDB with a local SQLite store (raw
    1-min/24h, rollup 15-min/30d, avg+min+max per bucket) persisting primitives
    (pv_power, battery_power, battery_soc, grid_power_total); derive house_load
    at display; retire buffering and standalone validation; add /api/history.
  alternatives_considered:
    - option: "rrdtool for round-robin history"
      reason_rejected: "External C library / apt dependency; contradicts stdlib discipline."
    - option: "Flat CSV/append-only log"
      reason_rejected: "Unbounded growth; needs separate pruning/downsampling that SQLite provides via SQL."
    - option: "Retain InfluxDB TimeSeriesStore as designed"
      reason_rejected: "External DB and remote-outage semantics unwarranted for a single local off-grid unit."
    - option: "Store house_load as a derived column"
      reason_rejected: >
        Grid-port registers may not represent house consumption off-grid; baking an
        unverified derivation into pruned history is irreversible. Storing primitives
        keeps the derivation correctable retroactively.
  benefits:
    - "No external database dependency; standard library only (sqlite3)."
    - "Historical trend on the primary dashboard."
    - "History correctable if the house_load derivation is later revised."
    - "Reduced component count (DataValidator, DataBuffer retired)."
  risks:
    - risk: "SQLite write contention with the polling loop thread."
      mitigation: "Single writer; WAL journal mode; lock-guarded access."
    - risk: "house_load derivation invalid for the actual wiring."
      mitigation: "Primitives stored, not the derived value; validate formula against emulator and live data."

technical_details:
  current_behavior: >
    Dashboard shows three-phase grid, per-string PV V/I, battery detail, feed-in,
    energy, and temperatures, polling /api/telemetry every 5s. No persistence is
    implemented. The baseline (FR-010..FR-012) targets InfluxDB with buffering.
  proposed_behavior: >
    Dashboard shows four primary cards - Solar Production, Battery (SOC and
    charge/discharge), House Load, System Status - each with an inline SVG
    sparkline fed by /api/history. Secondary detail is demoted to a collapsed
    section but retained in /api/telemetry. A SQLite store records primitive
    samples (1-min/24h) and a rollup (15-min/30d, avg+min+max) and serves history
    as JSON. House load is derived client-side
    (house_load = pv_power - battery_power + grid_power_total).
  implementation_approach: >
    Source implementation via prompt-a2d5f7c9 (T04, Claude Code). Documentation
    (this change plus requirements and design revisions) precedes it.
  code_changes:
    - component: "TimeSeriesStore"
      file: "src/solax_modbus/data/storage.py"
      change_summary: "New sqlite3 store: raw + rollup tables of primitives; write_sample, rollup, prune, query_history; folded range validation."
      functions_affected: ["init_schema", "write_sample", "rollup", "prune", "query_history"]
      classes_affected: ["TimeSeriesStore"]
    - component: "TelemetryServer"
      file: "src/solax_modbus/presentation/server.py"
      change_summary: "Add /api/history route returning rollup JSON; accept a TimeSeriesStore reference."
      functions_affected: ["do_GET"]
      classes_affected: ["TelemetryRequestHandler", "TelemetryServer"]
    - component: "dashboard"
      file: "src/solax_modbus/presentation/templates/dashboard.html"
      change_summary: "Four primary cards; present house load; client-side SVG sparklines fed by /api/history; collapse secondary detail."
      functions_affected: []
      classes_affected: []
    - component: "main"
      file: "src/solax_modbus/main.py"
      change_summary: "Instantiate the store; write a sample each poll; schedule rollup/prune; pass the store to TelemetryServer; add --db-path."
      functions_affected: ["main"]
      classes_affected: []
  data_changes:
    - entity: "SQLite schema"
      change_type: "schema"
      details: >
        raw(ts, pv_power, battery_power, battery_soc, grid_power_total);
        rollup(bucket_ts, metric, avg, min, max). Store primitives only; house_load
        derived at display (pv_power - battery_power + grid_power_total), not
        persisted. Schema fixed in design-b7c8d9e0 2.1.
    - entity: "Measurement"
      change_type: "validation"
      details: "Minimal range check folded into the store write path; quality scoring dropped."
  interface_changes:
    - interface: "HTTP /api/history"
      change_type: "contract"
      details: "New GET route returning JSON rollup series (primitives)."
      backward_compatible: "yes"
    - interface: "TimeSeriesStore constructor"
      change_type: "signature"
      details: "SQLite file path replaces InfluxDB connection parameters."
      backward_compatible: "n/a"
    - interface: "TelemetryServer constructor"
      change_type: "signature"
      details: "Accepts an optional TimeSeriesStore for /api/history."
      backward_compatible: "yes"

dependencies:
  internal:
    - component: "TelemetryServer"
      impact: "Read dependency on TimeSeriesStore for /api/history."
    - component: "main (Application)"
      impact: "Owns store lifecycle, write cadence, rollup/prune scheduling."
  external:
    - library: "influxdb-client"
      version_change: "removed"
      impact: "Dropped from the technology stack."
    - library: "sqlite3"
      version_change: "standard library"
      impact: "No new pip dependency."
  required_changes: []

testing_requirements:
  test_approach: "P06. Unit tests over synthetic time series for rollup, retention, validation; route tests for /api/history."
  test_cases:
    - scenario: "Rollup bucket computes avg/min/max per metric."
      expected_result: "Aggregates match reference computation."
    - scenario: "Raw retention prunes samples older than 24h."
      expected_result: "No raw rows older than the window remain."
    - scenario: "Rollup retention prunes buckets older than 30d."
      expected_result: "No rollup rows older than the window remain."
    - scenario: "/api/history for a permitted source IP."
      expected_result: "HTTP 200 with rollup series; 403 for disallowed source."
    - scenario: "Out-of-range field stored NULL, sample retained."
      expected_result: "Row inserted with offending field NULL; warning logged."
  regression_scope:
    - "/api/telemetry route unchanged."
    - "Existing IP allowlist behaviour unchanged."
  validation_criteria:
    - "Requirements and design baseline internally consistent post-revision."
    - "No residual active reference to InfluxDB persistence."
    - "house_load not persisted; derivable from stored primitives."

implementation:
  effort_estimate: ""
  implementation_steps:
    - step: "Author T03 issue and T02 change."
      owner: "Strategic Domain"
    - step: "Revise requirements and design baseline."
      owner: "Strategic Domain"
    - step: "Author prompt-a2d5f7c9 (T04) and hand to Claude Code."
      owner: "Strategic Domain"
    - step: "Implement source per T04; P08 review; P06 tests."
      owner: "Tactical Domain (Claude Code)"
  rollback_procedure: >
    Documentation reverts via git. Source reverts by removing the storage module,
    the /api/history route, and the dashboard changes; no data migration required.
  deployment_notes: >
    New SQLite file created on first run at --db-path. No external service. Ensure
    the monitor user can write the database directory on the Pi.

verification:
  implemented_date: "2026-07-16"
  implemented_by: "Claude Code (Tactical Domain)"
  verification_date: "2026-07-16"
  verified_by: "Claude (Strategic Domain, P08 review)"
  test_results: >
    P08 review pass. storage.py, server.py, main.py, dashboard.html each
    conform to prompt-a2d5f7c9 and to design-b7c8d9e0 / design-9b7e2c4a.
    validator.py and buffer.py confirmed absent; storage.py imports standard
    library only. Two non-blocking notes recorded: rollup() aggregates the
    full raw table each call rather than a since-cursor (harmless given the
    24h-bounded table); house_load sparkline renders avg-only, consistent
    with all other sparklines in this dashboard. Existing pytest suite not
    executed by Claude; operator to confirm green.
  issues_found:
    - issue_ref: "issue-a2d5f7c9"

traceability:
  design_updates:
    - design_ref: "requirements-solax-modbus-master"
      sections_updated: ["FR-009, FR-010, FR-011, FR-012, FR-019, NFR-008, AR-002, AR-008, Traceability, Glossary"]
      update_date: "2026-07-16"
    - design_ref: "design-b7c8d9e0-component_data_storage"
      sections_updated: ["Supersession to SQLite; primitives schema (2.1)"]
      update_date: "2026-07-16"
    - design_ref: "design-9e4b2c3d-domain_data"
      sections_updated: ["Technology Stack, Components, retention"]
      update_date: "2026-07-16"
    - design_ref: "design-a6b7c8d9-component_data_validator"
      sections_updated: ["Status -> Retired"]
      update_date: "2026-07-16"
    - design_ref: "design-c8d9e0f1-component_data_buffer"
      sections_updated: ["Status -> Retired"]
      update_date: "2026-07-16"
    - design_ref: "design-9b7e2c4a-component_presentation_server"
      sections_updated: ["Routes, Interfaces (/api/history)"]
      update_date: "2026-07-16"
    - design_ref: "design-af5c3d4e-domain_presentation"
      sections_updated: ["Component status, history responsibility"]
      update_date: "2026-07-16"
    - design_ref: "design-solax-modbus-master"
      sections_updated: ["Scope, System Overview, Data Design, Cross-References"]
      update_date: "2026-07-16"
    - design_ref: "design-solax-modbus-name_registry-master"
      sections_updated: ["DataValidator, DataBuffer, ValidationResult retired"]
      update_date: "2026-07-16"
  related_changes:
    - change_ref: "change-a7c3e9d2"
      relationship: "related (prior TelemetryServer change)"
  related_issues:
    - issue_ref: "issue-a2d5f7c9"
      relationship: "source"

notes: >
  House load is derived, not persisted: house_load = pv_power - battery_power +
  grid_power_total. The grid-port registers may not represent house consumption on
  a true off-grid island (EPS/backup output is not in the register map); storing
  primitives keeps the derivation correctable. Sparklines are rendered client-side
  from /api/history JSON, consistent with the /api/telemetry pattern.

version_history:
  - version: "1.0"
    date: "2026-07-16"
    author: "William Watson"
    changes:
      - "Initial change document for off-grid UI simplification and SQLite history"
  - version: "1.1"
    date: "2026-07-16"
    author: "William Watson"
    changes:
      - "Store primitives; house_load derived at display, not persisted (grid-port registers may not represent off-grid house consumption). Updated data_changes schema and design references."
  - version: "1.2"
    date: "2026-07-16"
    author: "William Watson"
    changes:
      - "Implemented via prompt-a2d5f7c9 by Claude Code; P08 reviewed and passed. Status proposed -> implemented."

metadata:
  copyright: "Copyright (c) 2026 William Watson. MIT License."
  template_version: "1.0"
  schema_type: "t02_change"
```
