```yaml
# T03 Issue Document
# Annual Rollup Tier for 12-Month History Graph

issue_info:
  id: "issue-b1c2d3e4"
  title: "Annual Rollup Tier for 12-Month History Graph"
  date: "2026-07-17"
  reporter: "William Watson"
  status: "open"
  severity: "low"
  type: "requirement_change"
  iteration: 1
  coupled_docs:
    change_ref: ""
    change_iteration: null

source:
  origin: "requirement_change"
  test_ref: ""
  description: >
    Operator requests a rolling trailing 12-month history graph in addition to
    the existing 30-day view (FR-012, TimeSeriesStore rollup tier). The
    existing 15-min rollup at 30-day retention is unsuited to a 12-month span:
    a 12-month query at 15-min resolution returns approximately 35,040 points
    per metric, producing an oversized /api/history payload and an illegible
    sparkline. A second, coarser rollup tier is required.

affected_scope:
  components:
    - name: "TimeSeriesStore"
      file_path: "src/solax_modbus/data/storage.py"
    - name: "TelemetryServer"
      file_path: "src/solax_modbus/presentation/server.py"
    - name: "dashboard"
      file_path: "src/solax_modbus/presentation/templates/dashboard.html"
  designs:
    - design_ref: "design-b7c8d9e0-component_data_storage"
    - design_ref: "design-9b7e2c4a-component_presentation_server"
    - design_ref: "design-af5c3d4e-domain_presentation"
    - design_ref: "design-9e4b2c3d-domain_data"
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
    A trailing 12-month history graph, toggled/expanded from an existing
    dashboard card, backed by a daily-bucket rollup tier retained 12 months.
  actual: >
    Only a 30-day, 15-min-resolution rollup exists (FR-012). No mechanism
    exists to serve a readable, reasonably-sized 12-month series.
  impact: >
    Operator cannot review longer-term production/battery/load trends without
    external tooling. Attempting to serve the existing rollup over a 12-month
    window would degrade dashboard responsiveness on the Pi Zero 2W.
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
    FR-012's rollup tier was sized for a 30-day operational view (change-a2d5f7c9)
    and was not designed to also serve a long-range trend graph. Resolution
    and retention are coupled in the existing single-tier design; extending
    retention alone without coarsening resolution produces an unusably large
    query result.
  technical_notes: >
    Decisions agreed with operator:
    (1) Existing raw (24h) and 15-min rollup (30-day) tiers unchanged.
    (2) New third tier: daily-bucket rollup (avg/min/max), retained 12 months
        on a rolling trailing-window basis (not calendar-year), in a separate
        table (e.g. daily_rollup).
    (3) New endpoint: /api/history/12mo, serving the daily series.
    (4) Naming convention: "12mo" used throughout (table, retention constant,
        endpoint, query method) to avoid calendar-year ambiguity implied by
        "annual".
    (5) Daily rollup computed inline in the existing poll loop via an
        elapsed-time check (>= 86400s since last daily rollup/prune), matching
        the existing 15-min rollup pattern. No new thread or fixed-time
        scheduler.
    (6) Dashboard: no new card; existing cards gain a toggle/expand to the
        12-month view.
  related_issues:
    - issue_ref: "issue-a2d5f7c9-offgrid-ui-sqlite-history"
      relationship: "related"

resolution:
  assigned_to: "Strategic Domain"
  target_date: ""
  approach: >
    Author change document and revise requirements/design baseline (FR-012
    extension). Source implementation delivered via a T04 prompt for
    Claude Code.
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
  preventive_measures: >
    When defining a rollup tier, confirm all intended query windows and
    resolutions during requirements elicitation rather than adding tiers
    reactively.
  process_improvements: ""

verification_enhanced:
  verification_steps:
    - ""
  verification_results: ""

traceability:
  design_refs:
    - "design-b7c8d9e0-component_data_storage"
    - "design-9b7e2c4a-component_presentation_server"
  change_refs: []
  test_refs: []

notes: >
  Scope and naming confirmed collaboratively with operator prior to issue
  authoring: second rollup tier (daily buckets, not calendar-year), 30-day
  tier retention unchanged, new endpoint /api/history/12mo, inline elapsed-time
  rollup cadence, dashboard toggle/expand placement (no new card).

loop_context:
  was_loop_execution: false
  blocked_at_iteration: 0
  failure_mode: ""
  last_review_feedback: ""

version_history:
  - version: "1.0"
    date: "2026-07-17"
    author: "William Watson"
    changes:
      - "Initial issue documenting the annual (12-month, trailing) rollup tier requirement"

metadata:
  copyright: "Copyright (c) 2026 William Watson. MIT License."
  template_version: "1.0"
  schema_type: "t03_issue"
```
