"""Record creation, typed handoffs, actual runs and SQL results for the demo.

Writes two NEW forked studies outside upstream. Existing outputs are never replaced.
The trace is real CLI output and is also saved as timed JSONL for an edited video.
"""
import argparse
import hashlib
import json
import shutil
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from bulk_panel_probe import ROOT, BulkPanelStore
from bulk_study_probe import database
from skills.sv_workspace import fork_study, init_manifest, load_study_yaml, save_study_yaml, study_paths, write_roster
from socioverse.engine import build_simulator
from socioverse.schemas import EnvironmentBundle, PopulationBundle, SimulationConfig, StudySpec
from socioverse.validation import validate_handoff, write_artifact
from studies.opinion_diffusion.model import ring_edges, OpinionPopulationProvider


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    root = args.output.resolve()
    root.mkdir(parents=True, exist_ok=False)
    trace = []
    started = time.perf_counter()
    def emit(line):
        trace.append({'elapsed': time.perf_counter()-started, 'text': line})
        print(line, flush=True)
        (root/'trace.jsonl').write_text(''.join(json.dumps(row,ensure_ascii=False)+'\n' for row in trace))

    emit('PanelBatch | actual recorded local CLI run | synthetic agents only')
    emit('No paid API, credentials or live language model is used.')
    # Author a fresh fork BEFORE its first run. The official reference stays intact.
    shutil.copytree(ROOT/'upstream/studies/opinion_diffusion', root/'opinion_diffusion')
    results = {}
    durations = {}
    for mode in ('baseline','bulk'):
        sid = 'panel_batch_'+mode
        study_dir = fork_study(root, 'opinion_diffusion', sid, status='local-systems-demo')
        paths = study_paths(study_dir)
        spec = load_study_yaml(paths['study'])
        spec.title = 'PanelBatch persistence parity ('+mode+')'
        spec.title_i18n = {}
        spec.research_question = 'Does bulk panel ingestion preserve the same synthetic study results?'
        spec.research_question_i18n = {}
        spec.hypothesis = 'Changing only the trajectory writer preserves all panel values, metrics and events.'
        spec.hypothesis_i18n = {}
        spec.n_steps = 6
        spec.seed = 42
        spec.time_unit = 'abstract'
        spec.step_meaning = 'One synthetic decision round; no real-world time interpretation.'
        spec.created_by = 'demo_study.py (fork of opinion_diffusion; AI-assisted)'
        save_study_yaml(paths['study'], spec)
        pop = validate_handoff(paths['population'], PopulationBundle)
        pop.provider_args = {**pop.provider_args, 'n_agents':128}
        pop.interaction.edges = ring_edges(128)
        pop.personas = OpinionPopulationProvider(pop).build(seed=42)
        pop.materialized_count = len(pop.personas)
        env = validate_handoff(paths['environment'], EnvironmentBundle)
        env.provider_args = {**env.provider_args, 'n_agents':128}
        cfg = validate_handoff(paths['simulation'], SimulationConfig)
        cfg.n_steps, cfg.seed = 6, 42
        cfg.store_ref = 'duckdb' if mode == 'baseline' else 'panel_batch.arrow'
        cfg.decision_args = {**cfg.decision_args, 'llm_kind':'scripted'}
        for key, value in [('population',pop),('environment',env),('simulation',cfg)]:
            write_artifact(paths[key],value)
        validate_handoff(paths['study'],StudySpec)
        # The template's original grounding is kept, with an explicit scope addition.
        grounding = json.loads(paths['grounding'].read_text())
        grounding['panel_batch_scope'] = {'basis':'assumed','synthetic':True,
            'purpose':'systems storage compatibility; not inference about real people',
            'population_count':128,'new_empirical_data':False}
        paths['grounding'].write_text(json.dumps(grounding,ensure_ascii=False,indent=2)+'\n')
        init_manifest(study_dir, note='New synthetic systems demo, configured before first run')
        emit(f'CREATE {sid}: forked official reference; typed P/E/B handoffs valid')
        emit(f'CONFIG agents=128 steps=6 seed=42 llm_kind=scripted store_ref={cfg.store_ref}')
        def progress(step,metrics):
            emit(f'{mode:8s} step={step} mean={metrics.get("mean_opinion",0):.6f} std={metrics.get("opinion_std",0):.6f}')
        sim = build_simulator(env_bundle=env,pop_bundle=pop,sim_config=cfg,
                              store_path=paths['duckdb'],on_step=progress)
        _, roster = sim.materialize_initial()
        write_roster(paths['roster'],roster)
        emit(f'ROSTER materialized {len(roster)} persistent synthetic agent IDs')
        sources = Counter()
        original = sim.decision.decide_batch
        def counted(obs,memories):
            acts=original(obs,memories)
            sources.update(a.source for a in acts)
            return acts
        sim.decision.decide_batch=counted
        begin=time.perf_counter()
        hist=sim.run()
        durations[mode]=time.perf_counter()-begin
        write_artifact(paths['metrics'],hist)
        results[mode]=database(paths['duckdb'])
        emit(f'COMPLETE {mode}: {len(results[mode]["panel"])} panel rows; decision sources={dict(sources)}')
        emit(f'FILES {sid}/trajectory/study.duckdb, panel.parquet, metrics.parquet, metrics_history.json')
    # study_id is in workspace metadata, not in the shared six-column panel schema.
    assert results['baseline']==results['bulk']
    fingerprint=hashlib.sha256(json.dumps(results['bulk'],sort_keys=True).encode()).hexdigest()
    emit('CHECK exact sorted panel / metrics / events parity: PASS')
    emit('DATA SHA256 '+fingerprint)
    emit('This 128-agent recorded run demonstrates operation, not a performance estimate.')
    emit('See the separate 3-seed benchmark and fresh-process memory check for costs.')
    summary={'at':datetime.now(timezone.utc).isoformat(),'actual_trace':True,
             'P':'128 synthetic persistent agents','E':'official template environment;6abstract rounds',
             'B':'unchanged scripted decision rule','LLM_calls':0,'new_cash_spend':0,
             'panel_rows_each':896,'exact_parity':True,'SHA256':fingerprint,
             'demo_runtime_seconds_not_benchmark':durations,'study_paths':['panel_batch_baseline','panel_batch_bulk'],
             'full_raw_data_retained':True,'upstream_modified':False,
             'report_does_not_use_demo_as_speedup_estimate':True}
    (root/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')


if __name__=='__main__':
    main()
