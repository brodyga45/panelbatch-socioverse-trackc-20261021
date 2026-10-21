"""Actual upstream simulator parity/performance, no live model or reference edits."""
import hashlib
import json
import argparse
from contextlib import nullcontext
import statistics
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path

from bulk_panel_probe import ROOT, BulkPanelStore, DuckDbTrajectoryStore
import duckdb
import studies.opinion_diffusion
from studies.opinion_diffusion.model import make_opinion_bundles
from socioverse.engine import build_simulator
from socioverse.schemas import WarmStartSpec


def database(db):
    con = duckdb.connect(str(db), read_only=True)
    try:
        return {
            "panel": con.execute("SELECT * FROM panel ORDER BY step, agent_id").fetchall(),
            "metrics": con.execute("SELECT * FROM metrics ORDER BY step").fetchall(),
            "events": con.execute("SELECT * FROM events ORDER BY step, note").fetchall(),
        }
    finally:
        con.close()


def run(root, name, cls, n, seed, *, parent=None):
    path = root / name / "study.duckdb"
    _, env, pop, cfg = make_opinion_bundles(n_agents=n, n_steps=6, seed=seed)
    cfg.decision_args = {**cfg.decision_args, "llm_kind": "scripted"}
    if parent:
        cfg.warm_start = WarmStartSpec(source_version="parent", source_trajectory=str(parent), resume_from=3)
    if cls is BulkPanelStore:
        cfg.store_ref = "panel_batch.arrow"
    sim = build_simulator(env_bundle=env, pop_bundle=pop, sim_config=cfg, store_path=path)
    assert type(sim.store) is cls
    decided = []
    original_decide = sim.decision.decide_batch
    def spy(obs, memories):
        decided.append(obs[0].step if obs else None)
        return original_decide(obs, memories)
    sim.decision.decide_batch = spy
    start = time.perf_counter()
    hist = sim.run()
    duration = time.perf_counter() - start
    data = database(path)
    assert len(data["panel"]) == n * 7
    assert len(hist.rows) == 7
    con = duckdb.connect()
    try:
        # Finalization's portable panel export must match its source database too.
        exported = con.execute("SELECT * FROM read_parquet(?) ORDER BY step, agent_id",
                               [str(path.parent / "panel.parquet")]).fetchall()
        assert exported == data["panel"]
    finally:
        con.close()
    return duration, data, path, decided


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--archive-to',type=Path)
    args = parser.parse_args()
    started = time.perf_counter()
    result = {"at": datetime.now(timezone.utc).isoformat(), "LLM_calls": 0, "cash_spend": 0,
              "workload": "Unmodified official opinion_diffusion model in scripted mode, 6 steps; synthetic agents",
              "timing_scope": "sim.run: population, dynamics, storage, live panel/progress output, metrics, Parquet finalization",
              "limitations": ["Local single host, not cross-platform or independent judging",
                              "No evidence about true human opinion, empirical validity, or LLM-bound speedup",
                              "No peak-memory claim"], "cases": []}
    if args.archive_to:
        args.archive_to.mkdir(parents=True,exist_ok=False)
        context = nullcontext(str(args.archive_to))
    else:
        context = tempfile.TemporaryDirectory(prefix="codex-socioverse-study-")
    with context as tmp:
        root = Path(tmp)
        for n in (256, 2048):
            timings = {"baseline": [], "bulk": []}
            for seed in (17, 42, 99):
                data = {}
                choices = [("baseline", DuckDbTrajectoryStore), ("bulk", BulkPanelStore)]
                if seed == 42:
                    choices.reverse()
                for name, cls in choices:
                    sec, values, _, calls = run(root, f"{name}-{n}-{seed}", cls, n, seed)
                    timings[name].append(sec)
                    data[name] = values
                    assert calls == [1, 2, 3, 4, 5, 6]
                assert data["baseline"] == data["bulk"], "Actual study outputs changed"
            row = {"agents": n, "seeds": [17, 42, 99], "run_seconds": timings,
                   "median_full_run_speedup": statistics.median(timings["baseline"]) / statistics.median(timings["bulk"]),
                   "exact_panel_metrics_events_parity": True, "parquet_parity": True}
            result["cases"].append(row)
            print(json.dumps(row), flush=True)
        _, parent_data, parent, _ = run(root, "branch-parent", DuckDbTrajectoryStore, 32, 42)
        _, baseline, _, calls1 = run(root, "branch-baseline", DuckDbTrajectoryStore, 32, 42, parent=parent)
        _, bulk, _, calls2 = run(root, "branch-bulk", BulkPanelStore, 32, 42, parent=parent)
        assert baseline == bulk
        assert calls1 == calls2 == [4, 5, 6]
        for child in (baseline, bulk):
            # Action source is deliberately replay; remaining panel fields reproduce prefix.
            assert [r[:-1] for r in child["panel"] if r[1] <= 3] == [r[:-1] for r in parent_data["panel"] if r[1] <= 3]
            assert child["metrics"][:4] == parent_data["metrics"][:4]
        result["branch"] = {"inherited_steps": [0, 1, 2, 3], "decision_steps": calls1,
                            "both_writers_exact_parity": True, "parent_prefix_reproduced": True}
    result["wall_seconds"] = time.perf_counter() - started
    result['raw_databases_retained'] = bool(args.archive_to)
    target = args.archive_to/'benchmark-result.json' if args.archive_to else ROOT/'bulk-study-probe-result.json'
    target.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"complete": True, "wall_seconds": result["wall_seconds"]}), flush=True)


if __name__ == "__main__":
    main()
