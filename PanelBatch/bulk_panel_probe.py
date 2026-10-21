"""Bounded Track-C feasibility probe, using synthetic rows and no model calls.

This measures the official store against a compatible bulk writer. It is not
a contest submission or a claim about real social behaviour. Upstream is intact.
"""
from __future__ import annotations

import hashlib
import json
import argparse
import platform
import statistics
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path

import duckdb
import pyarrow as pa

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "upstream"))
from socioverse.io.duckdb_store import DuckDbTrajectoryStore
from socioverse.schemas.trajectory import TrajectoryRecord


from panel_batch_store import BulkPanelStore


def make_rows(n: int, t: int) -> list[TrajectoryRecord]:
    return [TrajectoryRecord(
        agent_id=f"synthetic-{i:05d}", step=t,
        state={"position": [i % 11, i % 7], "score": ((i * 37 + t) % 101) / 100,
               "label": "пример 🧪", "nullable": None, "nested": {"active": i % 2 == 0}},
        action_kind=None if t == 0 else "move",
        action_payload={} if t == 0 else {"delta": (i + t) % 3 - 1, "tags": ["a", "b"]},
        action_source=None if t == 0 else "rule",
    ) for i in range(n)]


def fingerprint(store) -> str:
    rows = store._con.execute("SELECT * FROM panel ORDER BY step, agent_id").fetchall()
    return hashlib.sha256(json.dumps(rows, ensure_ascii=False, separators=(",", ":")).encode()).hexdigest()


def atomicity(root: Path) -> dict:
    result = {}
    for cls in (DuckDbTrajectoryStore, BulkPanelStore):
        s = cls(root / f"atomic-{cls.__name__}.duckdb", export_parquet=False)
        s.open()
        s.record(make_rows(2, 0))
        before = fingerprint(s)
        invalid_rows = [("new-good", 1, "{}", "move", "{}", "rule"),
                        ("new-bad", 1, "not valid JSON", "move", "{}", "rule")]
        try:
            if cls is BulkPanelStore:
                s.insert_columns([list(c) for c in zip(*invalid_rows)])
            else:
                s._insert_batch("INSERT INTO panel VALUES (?, ?, ?::JSON, ?, ?::JSON, ?)", invalid_rows)
        except duckdb.Error:
            pass
        else:
            raise AssertionError("Invalid JSON batch unexpectedly accepted")
        assert fingerprint(s) == before, "Partial failed batch changed the study"
        s.record(make_rows(2, 1))
        assert s._con.execute("SELECT count(*) FROM panel").fetchone()[0] == 4
        s.finalize()
        result[cls.__name__] = "invalid second row rolled back whole batch; subsequent valid batch committed"
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output-json',type=Path)
    args = parser.parse_args()
    started = time.perf_counter()
    output = {"at": datetime.now(timezone.utc).isoformat(), "data": "synthetic, no real individuals",
              "python": sys.version, "platform": platform.platform(), "duckdb": duckdb.__version__,
              "pyarrow": pa.__version__, "LLM_calls": 0, "cash_spend": 0,
              "limitations": ["Single local host; other workloads may cause timing noise",
                              "Storage component only, not full study or end-to-end agent speedup",
                              "No peak-memory measurement or award/eligibility/payment validation"], "cases": []}
    with tempfile.TemporaryDirectory(prefix="codex-socioverse-probe-") as tmp:
        root = Path(tmp)
        output["atomicity"] = atomicity(root)
        for n in (128, 1024, 8192):
            batches = [make_rows(n, t) for t in range(4)]
            timings = {"baseline": [], "bulk": []}
            hashes = set()
            for repeat in range(3):
                # Alternate order, limiting a systematic warm-cache advantage.
                choices = [("baseline", DuckDbTrajectoryStore), ("bulk", BulkPanelStore)]
                if repeat % 2:
                    choices.reverse()
                for name, cls in choices:
                    s = cls(root / f"{name}-{n}-{repeat}.duckdb", export_parquet=False)
                    s.open()
                    begin = time.perf_counter()
                    for batch in batches:
                        s.record(batch)
                    timings[name].append(time.perf_counter() - begin)
                    hashes.add(fingerprint(s))
                    assert s._con.execute("SELECT count(*) FROM panel").fetchone()[0] == n * 4
                    s.finalize()
            assert len(hashes) == 1, "Stored values changed across writers or repeats"
            row = {"agents": n, "steps_including_initial": 4, "records": n * 4,
                   "write_seconds": timings, "exact_ordered_database_parity": True,
                   "database_sha256": hashes.pop(),
                   "median_speedup": statistics.median(timings["baseline"]) / statistics.median(timings["bulk"])}
            output["cases"].append(row)
            print(json.dumps(row), flush=True)
    output["wall_seconds"] = time.perf_counter() - started
    target = args.output_json or ROOT / "bulk-panel-probe-result.json"
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"result": str(target), "wall_seconds": output["wall_seconds"]}), flush=True)


if __name__ == "__main__":
    main()
