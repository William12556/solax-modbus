# Prompt: Annual Rollup Tier (daily_rollup, /api/history/12mo, Dashboard Toggle)

Created: 2026 July 17

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
  id: "prompt-b1c2d3e4"
  task_type: "code_generation"
  source_ref: "change-b1c2d3e4"
  target_profile: "claude_code"
  date: "2026-07-17"
  iteration: 1
  coupled_docs:
    change_ref: "change-b1c2d3e4"
    change_iteration: 1
```

[Return to Table of Contents](<#table of contents>)

---

## Context

```yaml
context:
  purpose: >
    Add a third TimeSeriesStore tier (daily_rollup: 1-day buckets, avg/min/max,
    retained a rolling trailing 365 days) and a new /api/history/12mo JSON
    endpoint, and add a toggle to the existing dashboard cards to switch each
    card's sparkline between the existing 30-day view and the new 12-month
    view. Extends the SQLite history baseline established by change-a2d5f7c9;
    does not modify the existing raw or 15-min rollup tiers.
  integration: >
    storage.py (existing TimeSeriesStore) gains daily_rollup schema,
    rollup_daily(), prune_daily(), and query_history_12mo(). main.py tracks a
    second elapsed-time horizon and invokes rollup_daily()/prune_daily() once
    per day, inline in the existing poll loop, alongside the existing 15-min
    rollup/prune check; no new thread. server.py adds a GET /api/history/12mo
    route reusing the same store reference and the same source-IP allowlist
    check as /api/history. dashboard.html adds a per-card toggle control that
    switches the sparkline data source between the already-fetched 30-day
    series and a lazily-fetched 12-month series (fetched only once the
    operator switches a card to the 12-month view, then cached client-side and
    refreshed on a low-frequency interval).
  knowledge_references:
    - "ai/workspace/design/design-b7c8d9e0-component_data_storage.md"
    - "ai/workspace/design/design-9e4b2c3d-domain_data.md"
    - "ai/workspace/design/design-9b7e2c4a-component_presentation_server.md"
    - "ai/workspace/design/design-af5c3d4e-domain_presentation.md"
    - "ai/workspace/design/design-solax-modbus-name_registry-master.md"
    - "ai/workspace/requirements/requirements-solax-modbus-master.md"
    - "ai/workspace/change/change-b1c2d3e4-annual-rollup-tier.md"
    - "ai/workspace/issues/issue-b1c2d3e4-annual-rollup-tier.md"
    - "ai/workspace/change/change-a2d5f7c9-offgrid-ui-sqlite-history.md"
  constraints:
    - "Standard library only. No new external dependency."
    - "Do NOT modify the existing raw or rollup (15-min/30-day) tables, their schema, or their rollup()/prune()/query_history() behaviour. This prompt is additive only."
    - "daily_rollup is aggregated from the rollup table, not from raw, per design-b7c8d9e0 section 6.1.1. Do not aggregate daily buckets directly from raw."
    - "daily_rollup stores the same four primitives as rollup: pv_power, battery_power, battery_soc, grid_power_total. Do NOT add a house_load column or metric."
    - "The 12-month window is a rolling trailing window (now minus 365 days), not fixed calendar-year buckets. Do not align bucket boundaries to Jan 1 or any calendar year."
    - "rollup_daily() must run at least once per day, before prune() removes rollup rows older than 30 days, or daily_rollup develops a gap for the unrolled day. Schedule rollup_daily()/prune_daily() to run in the same poll-loop pass as, and before, the existing rollup()/prune() call within a given iteration."
    - "Existing /api/telemetry and /api/history contracts, field names, and behaviour are unchanged. This prompt does not touch Modbus polling or the register map."
    - "Existing tests must remain green. Do not alter public behaviour of SolaxInverterClient, TimeSeriesStore.rollup/prune/query_history, or the /api/history route."
    - "No new dashboard card. The 12-month view is a toggle/expand on each of the four existing cards, per operator decision."
    - "Names must match the name registry exactly (rollup_daily, prune_daily, query_history_12mo, daily_rollup)."
```

[Return to Table of Contents](<#table of contents>)

---

## Specification

```yaml
specification:
  description: |
    Modify src/solax_modbus/data/storage.py to add the daily_rollup table and
    three new TimeSeriesStore methods. Modify presentation/server.py to add a
    GET /api/history/12mo route. Modify main.py to schedule the daily
    rollup/prune inline in the poll loop and pass through unchanged otherwise.
    Modify presentation/templates/dashboard.html to add a toggle per card.
    Full component detail is in design-b7c8d9e0 section 6.0/6.1.1/8.0 and
    design-9b7e2c4a Routes/Interfaces; this prompt specifies the essentials.
  requirements:
    functional:
      - "init_schema() additionally issues CREATE TABLE IF NOT EXISTS for daily_rollup(bucket_ts, metric, avg, min, max) with PRIMARY KEY (bucket_ts, metric) and an index on bucket_ts, per design-b7c8d9e0 section 5.0. Idempotent; existing raw/rollup schema statements unchanged."
      - "rollup_daily() -> int aggregates rows from the rollup table (not raw) since the last daily-rollup horizon into 1-day buckets (bucket_ts equals the source bucket_ts minus bucket_ts modulo 86400), computing avg of avg, min of min, max of max per metric per design-b7c8d9e0 section 6.1.1, and upserts into daily_rollup. Returns the number of bucket-metric rows written or updated."
      - "prune_daily() -> int deletes daily_rollup rows older than a rolling trailing 365 days (now minus 31536000 seconds) per design-b7c8d9e0 section 6.2. Returns rows deleted."
      - "query_history_12mo(metric: str) -> list of dict validates metric is one of the four stored metrics, raising ValueError otherwise; returns daily_rollup rows within the trailing 365-day window as bucket_ts, avg, min, max dictionaries ordered oldest to newest. Structurally identical to query_history() but sourced from daily_rollup with a fixed 365-day window (no window_seconds parameter)."
      - "TelemetryRequestHandler.do_GET adds route /api/history/12mo: if store is None, return an empty list per metric with HTTP 200; otherwise for each of the four metrics call store.query_history_12mo(metric), assemble a JSON object keyed by the four metric names, respond 200 application/json. Subject to the same source-IP allowlist check as the other routes, unchanged."
      - "main.py tracks elapsed time since the last daily rollup separately from the existing 15-min rollup horizon. Roughly once per day (elapsed >= 86400s), within the same poll-loop pass, call store.rollup_daily() followed by store.prune_daily(), after the existing store.rollup()/store.prune() call for that iteration. No new thread."
      - "dashboard.html: each of the four existing cards gains a small toggle control (for example a '30d / 12mo' switch) next to its sparkline. Default state is 30d (existing behaviour, unchanged). Switching a card to 12mo lazily fetches /api/history/12mo (once, cached client-side across all four cards since the response covers all metrics) and re-renders that card's sparkline from the daily series; switching back to 30d re-renders from the already-fetched 30-day series without a new fetch. While in 12mo view, the card refreshes from the cached /api/history/12mo response on a low-frequency interval (for example every 10 minutes), separate from the existing /api/telemetry and /api/history polling intervals. House load for the 12mo view is derived client-side using the same formula and function already used for the 30d view, applied to the daily series points."
    technical:
      language: "Python"
      version: "3.13"
      standards:
        - "Thread-safe store access via the existing single lock (no new lock)"
        - "Comprehensive error handling; store faults never crash the poll loop"
        - "Debug logging with traceback via the existing logger"
        - "Professional docstrings"
        - "PEP 8 compliant"
  performance:
    - target: "Daily rollup/prune does not measurably delay polling"
      metric: "rollup_daily()/prune_daily() run within the existing poll iteration without added inverter I/O"
    - target: "Bounded local storage"
      metric: "daily_rollup adds an estimated ~1,460 rows steady-state (4 metrics x 365 days); total file size remains well under 1 GB (NFR-008)"
```

[Return to Table of Contents](<#table of contents>)

---

## Design

```yaml
design:
  architecture: "Additive third tier on the existing single-writer local persistence model. The poll loop remains the sole writer (adds rollup_daily/prune_daily calls alongside the existing rollup/prune calls); HTTP handler threads remain read-only via the new query_history_12mo(). The existing lock in TimeSeriesStore serializes all access, including the new methods; no new lock or thread."
  components:
    - name: "TimeSeriesStore (modified)"
      type: "class"
      purpose: "Gains a daily_rollup table and three methods; existing raw/rollup behaviour unchanged."
      interface:
        inputs: []
        outputs:
          type: "varies"
          description: "See rollup_daily, prune_daily, query_history_12mo in Specification"
        raises:
          - "ValueError (query_history_12mo with an unknown metric)"
      logic:
        - "init_schema additionally creates daily_rollup and its index if absent, per design-b7c8d9e0 section 5.0"
        - "rollup_daily groups rollup rows by 86400-second bucket per metric (avg of avg, min of min, max of max) and upserts into daily_rollup, under the existing lock"
        - "prune_daily deletes daily_rollup rows older than 31536000 seconds, under the existing lock"
        - "query_history_12mo selects from daily_rollup filtered by metric over the trailing 365-day window, ordered ascending, under the existing lock"
    - name: "TelemetryRequestHandler (modified)"
      type: "class"
      purpose: "Adds the /api/history/12mo route."
      interface:
        inputs:
          - name: "(HTTP GET request)"
            type: "n/a"
            description: "Standard handler invocation"
        outputs:
          type: "HTTP response"
          description: "JSON daily-rollup object, or existing responses for other routes"
        raises: []
      logic:
        - "do_GET keeps the existing allowlist check and existing routes (including /api/history) unchanged; adds /api/history/12mo returning the per-metric JSON described in Specification; responds 200 application/json"
    - name: "dashboard.html (modified)"
      type: "module"
      purpose: "Adds a per-card 30d/12mo toggle; no new card."
      interface:
        inputs: []
        outputs:
          type: "n/a"
          description: "Client-side rendering only"
        raises: []
      logic:
        - "Each card's existing sparkline-rendering function is parameterised by data source (30-day series already held in memory, or lazily-fetched 12-month series)"
        - "A single shared client-side fetch of /api/history/12mo is triggered on first toggle to 12mo (by any card), cached, and reused by all four cards; not fetched before any card is toggled"
        - "House-load derivation function is reused unchanged for daily-series points"
  dependencies:
    internal:
      - "Existing TimeSeriesStore instance and lock (no new instance)"
      - "Existing house-load derivation logic in dashboard.html (reused, not duplicated)"
    external: []
```

[Return to Table of Contents](<#table of contents>)

---

## Data Schema

```yaml
data_schema:
  entities:
    - name: "daily_rollup"
      attributes:
        - name: "bucket_ts"
          type: "INTEGER"
          constraints: "epoch seconds, 1-day bucket start, not null"
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
        - "Schema-identical to rollup; distinguished only by bucket width (86400s vs 900s) and source table (rollup vs raw)"
```

[Return to Table of Contents](<#table of contents>)

---

## Error Handling

```yaml
error_handling:
  strategy: "Daily-tier faults are isolated from the poll loop and from the HTTP server, exactly as the existing rollup/prune and /api/history isolate faults."
  exceptions:
    - exception: "sqlite3.OperationalError"
      condition: "Database locked (concurrent access) or disk full during daily rollup/prune"
      handling: "Log with traceback; rollup_daily/prune_daily return 0; polling and serving continue"
    - exception: "ValueError"
      condition: "query_history_12mo called with an unrecognised metric"
      handling: "Raise; do_GET catches and responds with an empty series for that metric plus a logged WARNING, consistent with the existing /api/history handling"
  logging:
    level: "INFO for daily-rollup summary; WARNING for lock retries; ERROR for failures, consistent with existing storage.py logging"
    format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
```

[Return to Table of Contents](<#table of contents>)

---

## Testing

```yaml
testing:
  unit_tests:
    - scenario: "rollup_daily over synthetic rollup rows spanning two daily buckets"
      expected: "Two daily_rollup rows per metric with avg-of-avg, min-of-min, max-of-max correctly computed"
    - scenario: "prune_daily with daily_rollup rows older than 365 days"
      expected: "Old rows removed; rows within the trailing window retained"
    - scenario: "query_history_12mo for an unknown metric"
      expected: "ValueError raised"
    - scenario: "GET /api/history/12mo from an allowlisted IP"
      expected: "200 application/json with four metric keys, each a list of bucket_ts, avg, min, max objects"
    - scenario: "GET /api/history/12mo from a non-allowlisted IP"
      expected: "403, unchanged allowlist behaviour"
    - scenario: "GET /api/history/12mo when store is None"
      expected: "200 with empty lists per metric, no exception"
    - scenario: "Existing rollup()/prune()/query_history() behaviour unaffected by the new tier"
      expected: "Existing tests for the 15-min/30-day tier continue to pass unchanged"
  edge_cases:
    - "rollup_daily called before any rollup rows exist: returns 0, no error"
    - "query_history_12mo window larger than available history (e.g. fresh deployment) returns fewer buckets, no error"
    - "Concurrent rollup_daily and query_history_12mo: existing lock serializes, no corruption"
    - "Deployment gap exceeding ~30 days between poll-loop runs: documented known limitation (design-b7c8d9e0 section 6.1.1), not required to be corrected by this prompt"
  validation:
    - "Existing test suite (SolaxInverterClient, TelemetryServer /api/telemetry and /api/history, allowlist) passes unchanged"
    - "No new external dependency introduced"
    - "No house_load column or metric value appears anywhere in the daily_rollup schema"
  note: "Formal P06 test documents and pytest are a separate phase after review, per project convention."
```

[Return to Table of Contents](<#table of contents>)

---

## Deliverable

```yaml
deliverable:
  format_requirements:
    - "Modify files in place; do not create new modules for this prompt"
    - "Implement interfaces exactly as named in the Element Registry"
    - "Consult design-b7c8d9e0 and design-9b7e2c4a for any detail not restated here"
    - "Do not modify DataValidator/DataBuffer (already retired) or reintroduce them"
  files:
    - path: "src/solax_modbus/data/storage.py"
      content: |
        Add the daily_rollup table to init_schema(). Add rollup_daily(),
        prune_daily(), query_history_12mo() to TimeSeriesStore per the Design
        and Element Registry sections. Existing raw/rollup schema, rollup(),
        prune(), query_history() unchanged. Standard library only.
    - path: "src/solax_modbus/presentation/server.py"
      content: |
        Add the /api/history/12mo route to TelemetryRequestHandler.do_GET per
        the Specification. Preserve all existing routes (including
        /api/history) and the allowlist check unchanged.
    - path: "src/solax_modbus/presentation/templates/dashboard.html"
      content: |
        Add a 30d/12mo toggle to each of the four existing cards. On first
        toggle to 12mo, fetch /api/history/12mo once, cache client-side, and
        render that card's sparkline from the daily series using the existing
        sparkline-rendering and house-load-derivation functions. Toggling back
        to 30d re-renders from the already-held 30-day series. While any card
        is in 12mo view, refresh the cached 12mo data on a low-frequency
        interval (e.g. every 10 minutes). No new card, no external assets or
        frameworks; inline CSS and JS only.
    - path: "src/solax_modbus/main.py"
      content: |
        Track a second elapsed-time horizon for the daily tier, separate from
        the existing 15-min rollup horizon. Once per day (elapsed >= 86400s),
        within the same poll-loop iteration, call store.rollup_daily() then
        store.prune_daily(), after the existing store.rollup()/store.prune()
        call for that iteration. No new thread. Preserve all existing
        behaviour, flags, and the ordered shutdown sequence.
```

[Return to Table of Contents](<#table of contents>)

---

## Success Criteria

```yaml
success_criteria:
  - "TimeSeriesStore creates daily_rollup alongside the unchanged raw and rollup tables, and rolls rollup rows up into 1-day buckets with avg, min, max for pv_power, battery_power, battery_soc, and grid_power_total only."
  - "No house_load column or metric exists anywhere in the daily_rollup schema or stored data."
  - "daily_rollup rows older than a rolling trailing 365 days are pruned; the window is not aligned to calendar-year boundaries."
  - "GET /api/history/12mo from an allowlisted IP returns 200 JSON with the four metric series (daily buckets); a non-allowlisted IP receives 403."
  - "GET /api/history (30-day) and GET /api/telemetry behaviour and payload shape are byte-for-byte unchanged from before this prompt."
  - "Each of the four existing dashboard cards has a working 30d/12mo toggle; no new card is added; /api/history/12mo is not fetched until a card is first toggled to 12mo."
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
      - name: "TelemetryRequestHandler"
        module: "solax_modbus.presentation.server"
    functions:
      - name: "rollup_daily"
        module: "solax_modbus.data.storage"
        signature: "rollup_daily(self) -> int"
      - name: "prune_daily"
        module: "solax_modbus.data.storage"
        signature: "prune_daily(self) -> int"
      - name: "query_history_12mo"
        module: "solax_modbus.data.storage"
        signature: "query_history_12mo(self, metric: str) -> List[Dict[str, Any]]"
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
  Profile: claude_code (manual, single-pass). tactical_brief and AEL
  orchestrator fields do not apply and are omitted.
  coupled_docs.change_ref is change-b1c2d3e4 (formal T02/T03 path,
  consistent with change-a2d5f7c9's precedent for this project).
  Correctness dependency: rollup_daily() must observe rollup rows before
  they age out of the 30-day rollup window via prune(). Both the 15-min and
  daily horizons run inline in the same poll loop, so this holds under
  normal operation; an outage exceeding ~30 days would leave a gap in
  daily_rollup for the unrolled span (see design-b7c8d9e0 section 6.1.1,
  "Correctness dependency" note). This is a known, accepted limitation, not
  something to be engineered around in this prompt.
  The "12mo" naming (endpoint, table, methods) is deliberate, replacing the
  informal "annual" language used during scoping, to avoid implying fixed
  calendar-year semantics for what is a rolling trailing window.
  Scope is confined to design-b7c8d9e0 (daily_rollup tier) and
  design-9b7e2c4a (/api/history/12mo route) plus the main.py scheduling and
  dashboard.html toggle described above. No functionality beyond the
  approved design is to be added.
```

[Return to Table of Contents](<#table of contents>)

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-07-17 | Initial prompt. Implement daily_rollup tier (rollup_daily, prune_daily, query_history_12mo), /api/history/12mo route, per-card dashboard toggle, and main.py scheduling integration, per design-b7c8d9e0 and design-9b7e2c4a (change-b1c2d3e4). Authored for the Claude Code profile. |
| 1.1 | 2026-07-17 | Closed. Implemented by Claude Code and committed/pushed; P08 review by Claude (Strategic Domain) passed with one non-blocking naming note (source constant DAILY_ROLLUP_RETENTION_SECONDS vs. DAILY_RETENTION_SECONDS as informally referenced during scoping). Existing pytest suite not executed by Claude; operator confirmation pending. |

---

Copyright (c) 2026 William Watson. This work is licensed under the MIT License.
