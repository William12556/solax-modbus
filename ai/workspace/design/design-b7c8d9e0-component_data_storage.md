# Component Design: TimeSeriesStore

Created: 2025 December 30

**Document Type:** Tier 3 Component Design  
**Document ID:** design-b7c8d9e0-component_data_storage  
**Parent:** [design-9e4b2c3d-domain_data.md](<design-9e4b2c3d-domain_data.md>)  
**Status:** Planned  

---

## Table of Contents

- [1.0 Component Information](<#1.0 component information>)
- [2.0 Purpose](<#2.0 purpose>)
- [3.0 Implementation](<#3.0 implementation>)
- [4.0 Class Design](<#4.0 class design>)
- [5.0 Database Schema](<#5.0 database schema>)
- [6.0 Retention and Rollup](<#6.0 retention and rollup>)
- [7.0 Write-Path Validation](<#7.0 write-path validation>)
- [8.0 Interfaces](<#8.0 interfaces>)
- [9.0 Error Handling](<#9.0 error handling>)
- [10.0 Design Element Cross-References](<#10.0 design element cross-references>)
- [Version History](<#version history>)

---

## 1.0 Component Information

```yaml
component_info:
  name: "TimeSeriesStore"
  domain: "Data"
  version: "2.0"
  date: "2026-07-16"
  status: "Planned"
  source_file: "src/solax_modbus/data/storage.py"
```

[Return to Table of Contents](<#table of contents>)

---

## 2.0 Purpose

Local SQLite store for telemetry history. Records raw samples and a downsampled
rollup, prunes both by age, and serves history for trend visualisation. Uses the
Python standard library `sqlite3`; no external database or network dependency.

### 2.1 Responsibilities

| Responsibility | Description |
|----------------|-------------|
| Persistence | Write telemetry samples to a raw table |
| Downsampling | Aggregate raw samples into rollup buckets (avg, min, max) |
| Retention | Prune raw and rollup rows past their age windows |
| Query | Return rollup series for the primary metrics |
| Write-path validation | Reject out-of-range values before insert |

### 2.2 Design Principles

| Principle | Implementation |
|-----------|----------------|
| Standard library only | `sqlite3`; no external dependency |
| Local file | Single database file on the deployment host |
| Non-blocking | Writes must not stall the polling loop |
| Bounded size | Age-based pruning keeps the file small |

[Return to Table of Contents](<#table of contents>)

---

## 3.0 Implementation

### 3.1 File Location

```
src/solax_modbus/data/storage.py (planned)
```

### 3.2 Dependencies

```yaml
dependencies:
  external: []
  internal:
    - "Telemetry dict from poll_inverter() (Protocol domain)"
  standard_library:
    - "sqlite3"
    - "time"
    - "logging"
    - "threading"
    - "typing"
```

[Return to Table of Contents](<#table of contents>)

---

## 4.0 Class Design

### 4.1 Class Diagram

```mermaid
classDiagram
    class TimeSeriesStore {
        +str db_path
        +Connection conn
        +Lock lock
        +__init__(db_path)
        +init_schema() None
        +write_sample(data: dict) bool
        +rollup() int
        +prune() int
        +query_history(metric, window) list
        +close() None
        -_validate(data: dict) dict
    }
```

### 4.2 Constructor

```python
def __init__(self, db_path: str = "solax_history.db"):
    """
    Open (or create) the SQLite store at db_path.

    Args:
        db_path: Path to the SQLite database file.

    Notes:
        Opens with check_same_thread=False and guards access with a lock,
        since the poll loop writes and HTTP handlers read. WAL journal mode
        is enabled for concurrent read during write.
    """
```

[Return to Table of Contents](<#table of contents>)

---

## 5.0 Database Schema

Two tables. `raw` holds recent full-resolution samples; `rollup` holds
downsampled aggregates. Timestamps are integer epoch seconds.

```sql
CREATE TABLE IF NOT EXISTS raw (
    ts            INTEGER NOT NULL,   -- epoch seconds
    pv_power      INTEGER,            -- total solar production (W)
    battery_soc   INTEGER,            -- state of charge (%)
    battery_power INTEGER,            -- signed: + charging, - discharging (W)
    house_load    INTEGER             -- AC output to house loads (W)
);
CREATE INDEX IF NOT EXISTS idx_raw_ts ON raw(ts);

CREATE TABLE IF NOT EXISTS rollup (
    bucket_ts  INTEGER NOT NULL,      -- epoch seconds, 15-min bucket start
    metric     TEXT    NOT NULL,      -- 'pv_power' | 'battery_soc' | 'battery_power' | 'house_load'
    avg        REAL,
    min        REAL,
    max        REAL,
    PRIMARY KEY (bucket_ts, metric)
);
CREATE INDEX IF NOT EXISTS idx_rollup_ts ON rollup(bucket_ts);
```

### 5.1 Metric Mapping

| Metric | Source field(s) in telemetry dict |
|--------|------------------------------------|
| `pv_power` | `pv1_power` + `pv2_power` |
| `battery_soc` | `battery_soc` |
| `battery_power` | `battery_power` (signed) |
| `house_load` | derived from grid-phase power fields (relabelled at display; stored as house load) |

House load is the AC output. Field names in `/api/telemetry` are unchanged;
the relabelling is a presentation concern (see the dashboard). The store
records the value under `house_load` for clarity of history.

[Return to Table of Contents](<#table of contents>)

---

## 6.0 Retention and Rollup

| Table | Resolution | Window | Aggregation |
|-------|------------|--------|-------------|
| raw | 1 minute | 24 hours | none (samples) |
| rollup | 15 minutes | 30 days | avg, min, max per metric |

### 6.1 Rollup Procedure

`rollup()` aggregates raw samples into 15-minute buckets per metric and upserts
into `rollup`. Bucket start is `ts - (ts % 900)`. Aggregation is deterministic
SQL:

```sql
INSERT INTO rollup (bucket_ts, metric, avg, min, max)
SELECT (ts - (ts % 900)) AS bucket_ts,
       'pv_power', AVG(pv_power), MIN(pv_power), MAX(pv_power)
FROM raw
WHERE ts >= :since
GROUP BY bucket_ts
ON CONFLICT(bucket_ts, metric) DO UPDATE SET
    avg = excluded.avg, min = excluded.min, max = excluded.max;
```

Repeated per metric. Invoked on an interval by the Application domain (for
example every 15 minutes), or opportunistically after writes.

### 6.2 Pruning

`prune()` deletes rows past the windows:

```sql
DELETE FROM raw    WHERE ts        < :now - 86400;      -- 24 hours
DELETE FROM rollup WHERE bucket_ts < :now - 2592000;    -- 30 days
```

### 6.3 Storage Estimate

| Table | Row rate | Rows retained | Approx size |
|-------|----------|---------------|-------------|
| raw | 1/min | ~1,440 | small (tens of KB) |
| rollup | 4/hr x 4 metrics | ~11,520 | small (hundreds of KB) |

The steady-state file is bounded well under 1 GB (NFR-008).

[Return to Table of Contents](<#table of contents>)

---

## 7.0 Write-Path Validation

Minimal range validation is folded into `write_sample()` via `_validate()`.
It replaces the retired standalone DataValidator (quality scoring and
stuck-sensor detection are not carried forward).

| Field | Min | Max | Action on breach |
|-------|-----|-----|------------------|
| pv_power | 0 | 15000 | log warning, drop field (store NULL) |
| battery_soc | 0 | 100 | log warning, drop field |
| battery_power | -15000 | 15000 | log warning, drop field |
| house_load | -15000 | 15000 | log warning, drop field |

Out-of-range fields are set NULL rather than discarding the whole sample.

[Return to Table of Contents](<#table of contents>)

---

## 8.0 Interfaces

### 8.1 Public Methods

#### init_schema()

```python
def init_schema(self) -> None:
    """Create tables and indexes if absent. Idempotent."""
```

#### write_sample()

```python
def write_sample(self, data: Dict[str, Any]) -> bool:
    """
    Validate and insert one telemetry sample into the raw table.

    Args:
        data: Telemetry dictionary from poll_inverter().

    Returns:
        True if a row was inserted, False on error.
    """
```

#### rollup()

```python
def rollup(self) -> int:
    """
    Aggregate recent raw samples into 15-minute rollup buckets.

    Returns:
        Number of buckets written or updated.
    """
```

#### prune()

```python
def prune(self) -> int:
    """
    Delete raw rows older than 24h and rollup rows older than 30d.

    Returns:
        Number of rows deleted.
    """
```

#### query_history()

```python
def query_history(
    self,
    metric: str,
    window_seconds: int
) -> List[Dict[str, Any]]:
    """
    Return rollup series for one metric over a trailing window.

    Args:
        metric: One of pv_power, battery_soc, battery_power, house_load.
        window_seconds: Trailing window (e.g. 30 days).

    Returns:
        List of {bucket_ts, avg, min, max} in chronological order.
    """
```

#### close()

```python
def close(self) -> None:
    """Flush and close the SQLite connection. Idempotent."""
```

[Return to Table of Contents](<#table of contents>)

---

## 9.0 Error Handling

| Error | Handling |
|-------|----------|
| Database locked | Retry briefly; log on persistent failure; do not block poll loop |
| Disk full / write error | Log error, return False, continue polling |
| Out-of-range field | Log warning, store NULL for that field |
| Corrupt database file | Log error; operator intervention (no auto-recreate) |

### 9.1 Logging

```python
# DEBUG: write/rollup/prune row counts
# INFO: schema init, periodic rollup summary
# WARNING: out-of-range fields, transient lock retries
# ERROR: write failures, corrupt database
```

[Return to Table of Contents](<#table of contents>)

---

## 10.0 Design Element Cross-References

### 10.1 Parent Documents

- Domain: [design-9e4b2c3d-domain_data.md](<design-9e4b2c3d-domain_data.md>)
- Master: [design-solax-modbus-master.md](<design-solax-modbus-master.md>)

### 10.2 Sibling Components (Data Domain)

| Component | Document | Status |
|-----------|----------|--------|
| DataValidator | [design-a6b7c8d9-component_data_validator.md](<design-a6b7c8d9-component_data_validator.md>) | Retired |
| DataBuffer | [design-c8d9e0f1-component_data_buffer.md](<design-c8d9e0f1-component_data_buffer.md>) | Retired |

### 10.3 Related Documents

- History endpoint: [design-9b7e2c4a-component_presentation_server.md](<design-9b7e2c4a-component_presentation_server.md>) (Routes: /api/history)
- Requirements: FR-010, FR-012, FR-019, NFR-008 in [requirements-solax-modbus-master.md](<../requirements/requirements-solax-modbus-master.md>)
- Change: change-a2d5f7c9

### 10.4 Source Code

| Item | Location |
|------|----------|
| Module | src/solax_modbus/data/storage.py (planned) |

[Return to Table of Contents](<#table of contents>)

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-12-30 | Initial component design for planned storage (InfluxDB). |
| 2.0 | 2026-07-16 | Superseded in place: InfluxDB replaced by local SQLite store (change-a2d5f7c9). New raw + rollup schema (avg/min/max), retention raw 1-min/24h and rollup 15-min/30d, folded write-path validation replacing the retired DataValidator, and a query_history interface for the /api/history endpoint. Removed InfluxDB connection config, tags, nanosecond precision, Flux downsampling, and buffer coupling. Added section numbering. |

---

Copyright (c) 2025 William Watson. This work is licensed under the MIT License.
