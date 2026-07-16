# Copyright (c) 2025 William Watson. This work is licensed under the MIT License.
"""
SQLite time-series store for Solax inverter telemetry history.

Records raw samples, aggregates into downsampled rollup buckets, enforces
retention windows, and serves history queries for trend visualisation.

Design: design-b7c8d9e0-component_data_storage.md
"""

from __future__ import annotations

import logging
import sqlite3
import threading
import time
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# Valid metrics for storage and query
STORED_METRICS = ("pv_power", "battery_power", "battery_soc", "grid_power_total")

# Retention windows in seconds
RAW_RETENTION_SECONDS = 86400  # 24 hours
ROLLUP_RETENTION_SECONDS = 2592000  # 30 days

# Rollup bucket size in seconds (15 minutes)
ROLLUP_BUCKET_SECONDS = 900

# Range validation bounds
RANGE_BOUNDS: Dict[str, tuple] = {
    "pv_power": (0, 15000),
    "battery_power": (-15000, 15000),
    "battery_soc": (0, 100),
    "grid_power_total": (-15000, 15000),
}


class TimeSeriesStore:
    """
    Local SQLite store for telemetry time-series data.

    Persists raw samples and downsampled rollup aggregates, prunes both by age,
    and serves history for trend visualisation. Thread-safe; uses a single lock
    to guard all database access.
    """

    def __init__(self, db_path: str = "solax_history.db") -> None:
        """
        Open (or create) the SQLite store at db_path.

        Args:
            db_path: Path to the SQLite database file.

        Notes:
            Opens with check_same_thread=False and guards access with a lock,
            since the poll loop writes and HTTP handlers read. WAL journal mode
            is enabled for concurrent read during write.
        """
        self.db_path = db_path
        self._lock = threading.Lock()
        self._conn: Optional[sqlite3.Connection] = None
        self._closed = False

        try:
            self._conn = sqlite3.connect(db_path, check_same_thread=False)
            self._conn.execute("PRAGMA journal_mode=WAL")
            self.init_schema()
            logger.info("TimeSeriesStore opened: %s", db_path)
        except sqlite3.DatabaseError as e:
            logger.error(
                "Failed to open SQLite database %s: %s (operator intervention required)",
                db_path,
                e,
                exc_info=True,
            )
            raise

    def init_schema(self) -> None:
        """
        Create tables and indexes if absent.

        Idempotent; safe to call multiple times.
        """
        with self._lock:
            if self._conn is None:
                return
            try:
                cursor = self._conn.cursor()
                # Raw samples table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS raw (
                        ts               INTEGER NOT NULL,
                        pv_power         INTEGER,
                        battery_power    INTEGER,
                        battery_soc      INTEGER,
                        grid_power_total INTEGER
                    )
                """)
                cursor.execute(
                    "CREATE INDEX IF NOT EXISTS idx_raw_ts ON raw(ts)"
                )

                # Rollup aggregates table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS rollup (
                        bucket_ts  INTEGER NOT NULL,
                        metric     TEXT    NOT NULL,
                        avg        REAL,
                        min        REAL,
                        max        REAL,
                        PRIMARY KEY (bucket_ts, metric)
                    )
                """)
                cursor.execute(
                    "CREATE INDEX IF NOT EXISTS idx_rollup_ts ON rollup(bucket_ts)"
                )

                self._conn.commit()
                logger.info("TimeSeriesStore schema initialized")
            except sqlite3.Error as e:
                logger.error("Schema init failed: %s", e, exc_info=True)

    def write_sample(self, data: Dict[str, Any]) -> bool:
        """
        Validate and insert one telemetry sample into the raw table.

        Derives pv_power as pv1_power + pv2_power; battery_power and battery_soc
        are read directly; grid_power_total is the sum of grid_power_r/s/t.
        Out-of-range fields are stored as NULL; the row is always inserted.

        Args:
            data: Telemetry dictionary from poll_inverter().

        Returns:
            True if a row was inserted, False on error.
        """
        if self._conn is None or self._closed:
            return False

        try:
            validated = self._validate(data)
            ts = int(time.time())

            with self._lock:
                cursor = self._conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO raw (ts, pv_power, battery_power, battery_soc, grid_power_total)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        ts,
                        validated.get("pv_power"),
                        validated.get("battery_power"),
                        validated.get("battery_soc"),
                        validated.get("grid_power_total"),
                    ),
                )
                self._conn.commit()
                logger.debug("Wrote sample at ts=%d", ts)
                return True

        except sqlite3.Error as e:
            logger.error("write_sample failed: %s", e, exc_info=True)
            return False
        except Exception as e:
            logger.error("Unexpected error in write_sample: %s", e, exc_info=True)
            return False

    def _validate(self, data: Dict[str, Any]) -> Dict[str, Optional[int]]:
        """
        Derive and range-check the four stored metrics from telemetry.

        Args:
            data: Raw telemetry dictionary.

        Returns:
            Dictionary with pv_power, battery_power, battery_soc, grid_power_total.
            Out-of-range values are set to None.
        """
        result: Dict[str, Optional[int]] = {}

        # pv_power: pv1_power + pv2_power
        pv1 = data.get("pv1_power")
        pv2 = data.get("pv2_power")
        if pv1 is not None and pv2 is not None:
            pv_power = int(pv1) + int(pv2)
            if self._in_range("pv_power", pv_power):
                result["pv_power"] = pv_power
            else:
                logger.warning("pv_power=%d out of range, storing NULL", pv_power)
                result["pv_power"] = None
        else:
            result["pv_power"] = None

        # battery_power: direct read
        bp = data.get("battery_power")
        if bp is not None:
            bp_int = int(bp)
            if self._in_range("battery_power", bp_int):
                result["battery_power"] = bp_int
            else:
                logger.warning("battery_power=%d out of range, storing NULL", bp_int)
                result["battery_power"] = None
        else:
            result["battery_power"] = None

        # battery_soc: direct read
        soc = data.get("battery_soc")
        if soc is not None:
            soc_int = int(soc)
            if self._in_range("battery_soc", soc_int):
                result["battery_soc"] = soc_int
            else:
                logger.warning("battery_soc=%d out of range, storing NULL", soc_int)
                result["battery_soc"] = None
        else:
            result["battery_soc"] = None

        # grid_power_total: sum of grid_power_r + grid_power_s + grid_power_t
        # Missing individual phases are treated as 0; if all three are absent,
        # grid_power_total is NULL.
        gpr = data.get("grid_power_r")
        gps = data.get("grid_power_s")
        gpt = data.get("grid_power_t")

        if gpr is None and gps is None and gpt is None:
            result["grid_power_total"] = None
        else:
            total = (int(gpr) if gpr is not None else 0) + \
                    (int(gps) if gps is not None else 0) + \
                    (int(gpt) if gpt is not None else 0)
            if self._in_range("grid_power_total", total):
                result["grid_power_total"] = total
            else:
                logger.warning(
                    "grid_power_total=%d out of range, storing NULL", total
                )
                result["grid_power_total"] = None

        return result

    def _in_range(self, metric: str, value: int) -> bool:
        """Check if value is within the defined bounds for the metric."""
        bounds = RANGE_BOUNDS.get(metric)
        if bounds is None:
            return True
        return bounds[0] <= value <= bounds[1]

    def rollup(self) -> int:
        """
        Aggregate recent raw samples into 15-minute rollup buckets.

        Computes avg, min, max per metric per bucket and upserts into rollup.

        Returns:
            Number of bucket-metric rows written or updated.
        """
        if self._conn is None or self._closed:
            return 0

        rows_affected = 0

        try:
            with self._lock:
                cursor = self._conn.cursor()

                for metric in STORED_METRICS:
                    cursor.execute(
                        f"""
                        INSERT INTO rollup (bucket_ts, metric, avg, min, max)
                        SELECT (ts - (ts % ?)) AS bucket_ts,
                               ? AS metric,
                               AVG({metric}),
                               MIN({metric}),
                               MAX({metric})
                        FROM raw
                        WHERE {metric} IS NOT NULL
                        GROUP BY bucket_ts
                        ON CONFLICT(bucket_ts, metric) DO UPDATE SET
                            avg = excluded.avg,
                            min = excluded.min,
                            max = excluded.max
                        """,
                        (ROLLUP_BUCKET_SECONDS, metric),
                    )
                    rows_affected += cursor.rowcount

                self._conn.commit()
                logger.info("Rollup completed: %d bucket-metric rows affected", rows_affected)

        except sqlite3.Error as e:
            logger.error("rollup failed: %s", e, exc_info=True)

        return rows_affected

    def prune(self) -> int:
        """
        Delete raw rows older than 24 hours and rollup rows older than 30 days.

        Returns:
            Total number of rows deleted.
        """
        if self._conn is None or self._closed:
            return 0

        now = int(time.time())
        raw_cutoff = now - RAW_RETENTION_SECONDS
        rollup_cutoff = now - ROLLUP_RETENTION_SECONDS
        total_deleted = 0

        try:
            with self._lock:
                cursor = self._conn.cursor()

                cursor.execute("DELETE FROM raw WHERE ts < ?", (raw_cutoff,))
                raw_deleted = cursor.rowcount
                total_deleted += raw_deleted

                cursor.execute("DELETE FROM rollup WHERE bucket_ts < ?", (rollup_cutoff,))
                rollup_deleted = cursor.rowcount
                total_deleted += rollup_deleted

                self._conn.commit()
                logger.info(
                    "Prune completed: %d raw rows, %d rollup rows deleted",
                    raw_deleted,
                    rollup_deleted,
                )

        except sqlite3.Error as e:
            logger.error("prune failed: %s", e, exc_info=True)

        return total_deleted

    def query_history(
        self, metric: str, window_seconds: int
    ) -> List[Dict[str, Any]]:
        """
        Return rollup series for one metric over a trailing window.

        Args:
            metric: One of pv_power, battery_power, battery_soc, grid_power_total.
            window_seconds: Trailing window in seconds (e.g. 30 days = 2592000).

        Returns:
            List of {bucket_ts, avg, min, max} dictionaries in chronological order.

        Raises:
            ValueError: If metric is not one of the stored metrics.
        """
        if metric not in STORED_METRICS:
            raise ValueError(f"Unknown metric: {metric}")

        if self._conn is None or self._closed:
            return []

        now = int(time.time())
        cutoff = now - window_seconds
        results: List[Dict[str, Any]] = []

        try:
            with self._lock:
                cursor = self._conn.cursor()
                cursor.execute(
                    """
                    SELECT bucket_ts, avg, min, max
                    FROM rollup
                    WHERE metric = ? AND bucket_ts >= ?
                    ORDER BY bucket_ts ASC
                    """,
                    (metric, cutoff),
                )
                for row in cursor.fetchall():
                    results.append({
                        "bucket_ts": row[0],
                        "avg": row[1],
                        "min": row[2],
                        "max": row[3],
                    })

        except sqlite3.Error as e:
            logger.error("query_history failed: %s", e, exc_info=True)

        return results

    def close(self) -> None:
        """
        Flush and close the SQLite connection.

        Idempotent; safe to call multiple times.
        """
        if self._closed:
            return

        self._closed = True
        with self._lock:
            if self._conn is not None:
                try:
                    self._conn.close()
                    logger.info("TimeSeriesStore closed: %s", self.db_path)
                except sqlite3.Error as e:
                    logger.error("Error closing store: %s", e, exc_info=True)
                finally:
                    self._conn = None
