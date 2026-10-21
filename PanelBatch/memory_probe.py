"""Fresh-process memory/cold-start check, separate from write-only timings."""
import json
import resource
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path


def worker(mode):
    from bulk_study_probe import run
    from bulk_panel_probe import BulkPanelStore, DuckDbTrajectoryStore
    cls = {"baseline": DuckDbTrajectoryStore, "bulk": BulkPanelStore}[mode]
    with tempfile.TemporaryDirectory(prefix="codex-panel-memory-") as tmp:
        cpu = time.process_time()
        seconds, data, _, decided = run(Path(tmp), mode, cls, 2048, 42)
        cpu = time.process_time() - cpu
        usage = resource.getrusage(resource.RUSAGE_SELF)
        peak_bytes = usage.ru_maxrss if sys.platform == "darwin" else usage.ru_maxrss * 1024
        print(json.dumps({"mode": mode, "sim_run_seconds": seconds,
                          "worker_cpu_seconds_including_validation": cpu,
                          "process_peak_RSS_bytes_including_imports_and_validation": peak_bytes,
                          "records": len(data["panel"]), "decision_steps": decided}))


if __name__ == "__main__":
    if len(sys.argv) == 2:
        worker(sys.argv[1])
    else:
        start = time.perf_counter()
        results = []
        for mode in ("baseline", "bulk"):
            child = subprocess.run([sys.executable, __file__, mode], check=True, text=True,
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=60)
            result = json.loads(child.stdout)
            results.append(result)
            print(json.dumps(result), flush=True)
        report = {"at": datetime.now(timezone.utc).isoformat(), "results": results,
                  "wall_seconds": time.perf_counter() - start,
                  "limitations": ["One fresh process per writer, not a repeated statistical estimate",
                                  "Peak includes common imports, full simulation and output validation",
                                  "RSS is not total machine energy or allocated monetary compute cost"],
                  "LLM_calls": 0, "cash_spend": 0}
        Path(__file__).with_name("memory-probe-result.json").write_text(json.dumps(report, indent=2) + "\n")
