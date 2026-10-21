PanelBatch — SocioVerse Track C feasibility candidate

Status: team PanelBatch-brodyga45 registered in Track C on21Oct2026, confirmed
by the official site and email. Platform account, final submission, acceptance,
award, settled payment and empirical findings about real people remain unverified.

Dependency: official Apache-2.0 SocioVerse2, commit
9c3ac774816511c121184ca11f539dc398ba1544, in upstream/.
The upstream source and reference studies are unchanged. Preserve LICENSE/NOTICE.
Our compatible writer is panel_batch_store.py. Import it to register
store_ref="panel_batch.arrow" in SimulationConfig. Events/messages/finalization
keep using the original store; only panel insertion uses a single Arrow relation.
No network, account, credentials or model provider is needed by the probes.

Reproduction from a fresh Python3.12 virtual environment:
  python3 -m venv venv
  venv/bin/python -m pip install -r requirements-probe.txt
  PANEL_BATCH_PYTHON=venv/bin/python ./reproduce.sh
Beforehand obtain the official public repository as upstream/ and check out the
exact commit above. Do not copy any local .env, credentials or real-person data.
The measured local environment is captured in bulk-panel-probe-result.json.

The component benchmark covers128/1024/8192 synthetic agents, four panel batches,
three repeats with alternating writer order, Unicode/nested/null JSON, identical
ordered database values, and whole-batch rollback followed by connection recovery.
The actual simulator benchmark uses the existing opinion_diffusion scripted model,
256/2048 synthetic agents, six steps, seeds17/42/99, full Parquet finalization and
exact panel/metrics/events equality. A branch replays0..3 and decides only4..6.
Temporary databases/live logs are written in OS temp and removed when tests finish.

The original local measurement found median component-write speedups11.94/28.89/
38.23x, and full-run median speedups2.01x(256agents)/9.96x(2048agents). Small-run
variance and first-use initialization are visible in raw timings. These are one
host's measurements, not a speed guarantee, peak-memory improvement or claim of
faster live LLM inference. The probe class was subsequently extracted unchanged
and connected through the official store registry; four semantic checks passed
in2.16seconds. Historical benchmark files record the measured source revision.

An organizer reply on21Oct explicitly permits controlled deterministic local
Track C experiments without paid LLM calls, with the same reproducibility and
report/package/demo requirements and conclusions limited to measured results.
The full repository is required for this platform component. Awards are in USD;
international remittance follows winner identity/bank checks after8Nov, with no
in-person attendance required. The organizer will confirm whether the entrant's
sole-trader business account can receive payment at the award stage; this is not
yet approved. No repeat inquiry is needed. Source-code polish or this README is
not award/acceptance evidence.

Updated candidate data:
- archived-study-series-v2/ retains full raw databases, Parquet and traces for
  a separate confirmation series. Full-run median ratios3.81x(256)/8.14x(2048).
  The earlier2.01x/9.96x pilot is retained separately, not silently discarded.
- recorded-studies-v2/ contains typed metadata, consistent128-agent population,
  actual trajectories and original CLI trace for an88-second edited demo.
  The video is a labelled replay of real output, not a screen recording.
- reproduce.sh now writes a new run directory and preserves packaged evidence.
  It prints its OS-temp output path; the new raw results remain for inspection.
- The report remains a5-page working draft; current cockpit formatting and
  eventual award bank settlement are still to be confirmed.

Linux compatibility was checked on21Oct2026 by a standard public GitHub Actions
Ubuntu x86_64 runner, Python3.12.15, DuckDB1.5.6 and Arrow26.0.0. Four semantic
tests passed; an actual128-agent baseline/bulk study produced896rows each with
exact panel/metrics/events parity. This is compatibility, not Linux speed or
independent human review. Exact tested source and logs are linked in
linux-compatibility.json. No paid runner, artifact storage or cache was used.

Researcher decision (report section4): absolute median savings were0.442s at256agents and3.378s at2048agents in the archived six-step series. The conditional extra-work table is arithmetic, not new LLM measurements. Consider the original writer or a small upstream batching patch; no superiority over that unimplemented alternative is claimed. Integration depends on private connection state, fixed columns, batch memory and exclusive connection use. See adoption-analysis.json.

A separate reviewing agent reproduced the exactv4 packaged entrypoint on this Mac using an existing environment:896rows per writer, exact panel/metrics/events parity. See independent-agent-entrypoint-check.json. This is not human review, a speed replication or prize proof.
