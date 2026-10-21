"""Semantic regression checks at the official engine/store boundary, no network."""
import importlib.util
from pathlib import Path

from bulk_panel_probe import ROOT, BulkPanelStore, DuckDbTrajectoryStore, atomicity
from bulk_study_probe import run


def test_official_registry_and_complete_study_parity(tmp_path):
    _, a, _, _ = run(tmp_path, "baseline", DuckDbTrajectoryStore, 24, 42)
    _, b, _, _ = run(tmp_path, "bulk", BulkPanelStore, 24, 42)
    assert a == b


def test_registered_store_preserves_counterfactual_replay(tmp_path):
    _, parent_data, parent, _ = run(tmp_path, "parent", DuckDbTrajectoryStore, 24, 42)
    _, a, _, calls_a = run(tmp_path, "baseline-child", DuckDbTrajectoryStore, 24, 42, parent=parent)
    _, b, _, calls_b = run(tmp_path, "bulk-child", BulkPanelStore, 24, 42, parent=parent)
    assert a == b
    assert calls_a == calls_b == [4, 5, 6]
    assert b["metrics"][:4] == parent_data["metrics"][:4]


def test_batch_rollback_and_connection_recovery(tmp_path):
    assert len(atomicity(tmp_path)) == 2


def test_existing_upstream_smoke_and_messages_contract(tmp_path):
    # Reuse the actual upstream assertions with the compatible store in its public seam.
    spec = importlib.util.spec_from_file_location("upstream_engine_smoke", ROOT / "upstream/tests/test_engine_smoke.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.DuckDbTrajectoryStore = BulkPanelStore
    module.test_smoke_run(tmp_path / "engine")
    module.test_store_writes_each_batch_in_one_transaction(tmp_path / "transactions")
