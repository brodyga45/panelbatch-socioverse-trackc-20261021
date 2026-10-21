"""Opt-in bulk trajectory writer for SocioVerse2. Original work: brodyga45.

Uses the official store interface; preserves inherited events/messages/finalization.
The upstream dependency retains its Apache-2.0 licence and NOTICE.
"""
import json
import pyarrow as pa
from socioverse.io.duckdb_store import DuckDbTrajectoryStore
from socioverse.schemas.trajectory import TrajectoryRecord
from socioverse.engine.registry import register


@register("store", "panel_batch.arrow")
class BulkPanelStore(DuckDbTrajectoryStore):
    """Single Arrow-to-SQL insert per step, with the original schema/transaction."""

    def record(self, records: list[TrajectoryRecord]) -> None:
        if not records:
            return
        columns = [
            [r.agent_id for r in records],
            [r.step for r in records],
            [json.dumps(r.state, ensure_ascii=False) for r in records],
            [r.action_kind for r in records],
            [json.dumps(r.action_payload, ensure_ascii=False) for r in records],
            [r.action_source for r in records],
        ]
        self.insert_columns(columns)

    def insert_columns(self, columns: list[list]) -> None:
        names = ["agent_id", "step", "state", "action_kind", "action_payload", "action_source"]
        types = [pa.string(), pa.int32(), pa.string(), pa.string(), pa.string(), pa.string()]
        table = pa.Table.from_arrays([pa.array(c, type=t) for c, t in zip(columns, types)], names=names)
        con = self._con
        con.register("_probe_panel_batch", table)
        try:
            con.execute("BEGIN TRANSACTION")
            try:
                con.execute("INSERT INTO panel SELECT agent_id, step, state::JSON, "
                            "action_kind, action_payload::JSON, action_source FROM _probe_panel_batch")
            except BaseException:
                con.execute("ROLLBACK")
                raise
            con.execute("COMMIT")
        finally:
            con.unregister("_probe_panel_batch")

