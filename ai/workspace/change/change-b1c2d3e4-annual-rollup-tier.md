```yaml
# T02 Change Document
# Annual Rollup Tier for 12-Month History Graph

change_info:
  id: "change-b1c2d3e4"
  title: "Annual Rollup Tier for 12-Month History Graph"
  date: "2026-07-17"
  author: "William Watson"
  status: "proposed"
  priority: "low"
  iteration: 1
  coupled_docs:
    issue_ref: "issue-b1c2d3e4"
    issue_iteration: 1

source:
  type: "issue"
  reference: "ai/workspace/issues/issue-b1c2d3e4-annual-rollup-tier.md"
  description: >
    Add a rolling trailing 12-month history graph alongside the existing 30-day
    view. Requires a new, coarser rollup tier; the existing 15-min rollup is
    unsuited to a 12-month query window.

scope:
  summary: >
    Add a third TimeSeriesStore tier: daily-bucket rollup (avg/min/max),
    retained 12 months on a rolling trailing-window basis, in a new table.
    Add a new /api/history/12mo endpoint serving the daily series. Existing
    raw (24h) and 15-min rollup (30-day) tiers unchanged. Dashboard gains a
    toggle/expand on existing cards to display the 12-month view; no new card.
    Source implementation delivered via a T04 prompt (Claude Code).
  affected_components:
    - name: "TimeSeriesStore"
      file_path: "src/solax_modbus/data/storage.py"
      change_type: "modify"
    - name: "TelemetryServer"
      file_path: "src/solax_modbus/presentation/server.py"
      change_type: "modify"
    - name: "dashboard"
      file_path: "src/solax_modbus/presentation/templates/dashboard.html"
      change_type: "modify"
    - name: "main"
      file_path: "src/solax_modbus/main.py"
      change_type: "modify"
  affected_designs:
    - design_ref: "requirements-solax-modbus-master"
      sections: ["FR-012", "Traceability"]
    - design_ref: "design-solax-modbus-master"
      sections: ["Data Design", "Component Status"]
    - design_ref: "design-b7c8d9e0-component_data_storage"
      sections: ["6.0 Retention and Rollup", "Database Schema", "Interfaces"]
    - design_ref: "design-9b7e2c4a-component_presentation_server"
      sections: ["Routes", "Interfaces"]
    - design_ref: "design-af5c3d4e-domain_presentation"
      sections: ["History responsibility"]
    - design_ref: "design-9e4b2c3d-domain_data"
      sections: ["Retention"]
  out_of_scope:
    - "Changes to the existing 15-min / 30-day rollup tier"
    - "Calendar-year-aligned reporting (fixed Jan-Dec buckets)"
    - "New dashboard card (toggle/expand on existing cards only)"
    - "Server-side chart rendering (client-side SVG, consistent with existing sparklines)"

rational:
  problem_statement: >
    FR-012's rollup tier (15-min buckets, 30-day retention) was sized for an
    operational view. A 12-month query at that resolution returns approximately
    35,040 points per metric, producing an oversized /api/history payload and
    an illegible sparkline, with repeated serialization cost on a Pi Zero 2W.
  proposed_solution: >
    Add a daily-bucket rollup tier (avg/min/max) in a separate table, retained
    12 months on a rolling trailing-window basis. Serve it via a new
    /api/history/12mo endpoint. Compute inline in the existing poll loop via
    an elapsed-time check, matching the existing 15-min rollup pattern.
  alternatives_considered:
    - option: "Extend the existing 15-min rollup retention to 12 months"
      reason_rejected: "Resolution mismatch; payload and rendering unsuited to a 12-month span (see problem_statement)."
    - option: "Client-side downsampling of the existing rollup for the long view"
      reason_rejected: "Still requires transferring and holding ~35,040 points per metric per request; does not reduce server or transfer load."
    - option: "Fixed calendar-year buckets"
      reason_rejected: "Operator explicitly requested a rolling trailing 12 months, not discrete calendar years."
    - option: "New dashboard card for the 12-month view"
      reason_rejected: "Operator preference: toggle/expand on existing cards."
  benefits:
    - "Readable, appropriately-sized 12-month trend view."
    - "No change to existing 30-day tier behaviour or retention."
    - "Reuses the established inline elapsed-time rollup/prune pattern; no new thread or scheduler."
  risks:
    - risk: "Additional SQLite table and write path increases store complexity."
      mitigation: "Daily tier is structurally identical to the existing rollup tier (avg/min/max per bucket); no new dependency."
    - risk: "Naming ambiguity if 'annual' is read as calendar-year."
      mitigation: "Use '12mo' consistently in table, constant, method, and endpoint names."

technical_details:
  current_behavior: >
    TimeSeriesStore maintains raw (1-min, 24h) and rollup (15-min, 30-day)
    tables. /api/history serves the rollup tier only, queried over a fixed
    30-day window.
  proposed_behavior: >
    TimeSeriesStore gains a third table (e.g. daily_rollup: bucket_ts, metric,
    avg, min, max), populated by aggregating the existing 15-min rollup (or raw,
    per implementation approach below) into daily buckets, retained 365 days on
    a rolling trailing-window basis (DAILY_RETENTION_SECONDS = 31536000). A new
    query_history_12mo(metric) method returns the trailing 365-day daily series.
    TelemetryServer adds a GET /api/history/12mo route returning this series as
    JSON, under the existing source-IP allowlist. main.py tracks elapsed time
    since the last daily rollup and triggers rollup + prune for the daily tier
    when elapsed >= 86400s, inline in the existing poll loop, alongside the
    existing 15-min rollup/prune check. dashboard.html adds a toggle/expand
    control on each existing card to switch its sparkline between the 30-day
    and 12-month series.
  implementation_approach: >
    Source implementation via a new T04 prompt (Claude Code), following
    documentation revision (this change plus requirements and design updates).
    Daily bucket source (aggregate from 15-min rollup vs. from raw) to be fixed
    in the T04 prompt; aggregating from the 15-min rollup is expected to be
    the lower-cost approach given the 30-day rollup is always a superset of
    the most recent portion of the 12-month window.
  code_changes:
    - component: "TimeSeriesStore"
      file: "src/solax_modbus/data/storage.py"
      change_summary: "New daily_rollup table; DAILY_RETENTION_SECONDS constant; daily rollup/prune methods; query_history_12mo method."
      functions_affected: ["init_schema", "rollup_daily", "prune_daily", "query_history_12mo"]
      classes_affected: ["TimeSeriesStore"]
    - component: "TelemetryServer"
      file: "src/solax_modbus/presentation/server.py"
      change_summary: "Add /api/history/12mo route returning the daily series JSON."
      functions_affected: ["do_GET"]
      classes_affected: ["TelemetryRequestHandler"]
    - component: "dashboard"
      file: "src/solax_modbus/presentation/templates/dashboard.html"
      change_summary: "Add toggle/expand control per card switching between 30-day and 12-month sparkline series; fetch /api/history/12mo on a low-frequency interval."
      functions_affected: []
      classes_affected: []
    - component: "main"
      file: "src/solax_modbus/main.py"
      change_summary: "Track elapsed time since last daily rollup; trigger rollup_daily/prune_daily inline in the poll loop when elapsed >= 86400s."
      functions_affected: ["main"]
      classes_affected: []
  data_changes:
    - entity: "SQLite schema"
      change_type: "schema"
      details: >
        New table daily_rollup(bucket_ts, metric, avg, min, max), structurally
        identical to the existing rollup table. No change to raw or rollup
        (15-min) tables.
    - entity: "Retention policy"
      change_type: "schema"
      details: "New constant DAILY_RETENTION_SECONDS = 31536000 (365 days), rolling trailing-window prune."
  interface_changes:
    - interface: "HTTP /api/history/12mo"
      change_type: "contract"
      details: "New GET route returning JSON daily series (primitives) for the trailing 365 days."
      backward_compatible: "yes"
    - interface: "TimeSeriesStore.query_history_12mo"
      change_type: "signature"
      details: "New method, analogous to the existing query_history(metric, window_seconds)."
      backward_compatible: "yes"

dependencies:
  internal:
    - component: "TelemetryServer"
      impact: "Additional read dependency on TimeSeriesStore for /api/history/12mo."
    - component: "main (Application)"
      impact: "Additional elapsed-time check and rollup/prune call in the poll loop."
  external: []
  required_changes:
    - change_ref: "change-a2d5f7c9"
      relationship: "blocked_by"

testing_requirements:
  test_approach: >
    P06. Unit tests over synthetic time series for daily rollup aggregation and
    12-month retention pruning; route tests for /api/history/12mo.
  test_cases:
    - scenario: "Daily rollup bucket computes avg/min/max per metric."
      expected_result: "Aggregates match reference computation."
    - scenario: "Daily retention prunes buckets older than 365 days."
      expected_result: "No daily_rollup rows older than the trailing window remain."
    - scenario: "/api/history/12mo for a permitted source IP."
      expected_result: "HTTP 200 with daily series; 403 for disallowed source."
    - scenario: "/api/history/12mo before any daily rollup has run."
      expected_result: "Empty series returned, no error."
  regression_scope:
    - "/api/history (30-day) route and existing rollup tier unchanged."
    - "/api/telemetry route unchanged."
  validation_criteria:
    - "Requirements and design baseline internally consistent post-revision."
    - "Existing 30-day tier behaviour unchanged by this addition."
    - "daily_rollup pruning bounded at 365 days trailing, not calendar-year."

implementation:
  effort_estimate: ""
  implementation_steps:
    - step: "Revise requirements (FR-012 extension) and design baseline."
      owner: "Strategic Domain"
    - step: "Author T04 prompt and hand to Claude Code."
      owner: "Strategic Domain"
    - step: "Implement source per T04; P08 review; P06 tests."
      owner: "Tactical Domain (Claude Code)"
  rollback_procedure: >
    Documentation reverts via git. Source reverts by removing the daily_rollup
    table/methods, the /api/history/12mo route, and the dashboard toggle; no
    migration required for existing raw/rollup data.
  deployment_notes: >
    daily_rollup table created in the existing SQLite file on first run
    following deployment; no new file or external service.

verification:
  implemented_date: ""
  implemented_by: ""
  verification_date: ""
  verified_by: ""
  test_results: ""
  issues_found: []

traceability:
  design_updates:
    - design_ref: "requirements-solax-modbus-master"
      sections_updated: ["FR-012", "FR-020 (new)", "Traceability", "Glossary"]
      update_date: "2026-07-17"
    - design_ref: "design-b7c8d9e0-component_data_storage"
      sections_updated: ["6.0 Retention and Rollup", "Database Schema", "Interfaces"]
      update_date: "2026-07-17"
    - design_ref: "design-9b7e2c4a-component_presentation_server"
      sections_updated: ["Routes", "Interfaces"]
      update_date: "2026-07-17"
    - design_ref: "design-af5c3d4e-domain_presentation"
      sections_updated: ["History responsibility"]
      update_date: "2026-07-17"
    - design_ref: "design-9e4b2c3d-domain_data"
      sections_updated: ["Retention"]
      update_date: "2026-07-17"
    - design_ref: "design-solax-modbus-master"
      sections_updated: ["Data Design", "Component Status"]
      update_date: "2026-07-17"
    - design_ref: "trace-traceability-matrix-master"
      sections_updated: ["Functional Requirements", "Component Mapping", "Design Document Cross-Reference", "Bidirectional Navigation"]
      update_date: "2026-07-17"
    - design_ref: "design-solax-modbus-name_registry-master"
      sections_updated: ["TimeSeriesStore class diagram"]
      update_date: "2026-07-17"
  related_changes:
    - change_ref: "change-a2d5f7c9"
      relationship: "related (established the existing rollup tier this extends)"
  related_issues:
    - issue_ref: "issue-b1c2d3e4"
      relationship: "source"

notes: >
  Naming convention "12mo" used throughout (table, constant, method, endpoint)
  in place of "annual" to avoid implying fixed calendar-year semantics; the
  tier is a rolling trailing 365-day window. Daily bucket source fixed at
  prompt authoring: aggregated from the 15-min rollup table, not raw (see
  design-b7c8d9e0 section 6.1.1). Source implementation specified in
  prompt-b1c2d3e4 (T04, Claude Code profile), not yet executed.

version_history:
  - version: "1.0"
    date: "2026-07-17"
    author: "William Watson"
    changes:
      - "Initial change document for the annual (12-month, trailing) rollup tier"
  - version: "1.1"
    date: "2026-07-17"
    author: "William Watson"
    changes:
      - "Requirements and design baseline revised (FR-012 extended, FR-020 added; design-b7c8d9e0, design-9b7e2c4a, design-af5c3d4e, design-9e4b2c3d, design-solax-modbus-master updated; traceability matrix and name registry updated). Source implementation (T04 prompt) not yet authored."
  - version: "1.2"
    date: "2026-07-17"
    author: "William Watson"
    changes:
      - "Authored prompt-b1c2d3e4 (T04, Claude Code profile) specifying source implementation. Not yet executed."

metadata:
  copyright: "Copyright (c) 2026 William Watson. MIT License."
  template_version: "1.0"
  schema_type: "t02_change"
```
