"""Resume the complete E1 variant stream at committed batch boundaries."""

from contextlib import closing
from itertools import islice
import json
import math
from pathlib import Path
import sqlite3
import time

from ..artifacts import seal, write_json
from ..data.pipeline import file_hash, fingerprint
from ..evaluate.metrics import summary
from ..model.predictor import Predictor
from ..model.training import run_lock, source_hash
from ..resources import resource_snapshot
from .perturbations import training_dfg, variants
from .studies import e1_accumulate, e1_records, e1_state, e1_summary


def encode(value):
    return json.dumps(seal(value), ensure_ascii=False, allow_nan=False, separators=(",", ":"))


def decode(value):
    envelope = json.loads(value)
    payload = envelope["payload"]
    if fingerprint(payload) != envelope["sha256"]:
        raise ValueError("E1 ledger checksum mismatch")
    return payload


def run_streaming_e1(prepared: dict, checkpoint: Path, output: Path, max_seconds: float,
                     *, stop_after_variants: int | None = None) -> dict:
    if not math.isfinite(max_seconds) or max_seconds <= 0:
        raise ValueError("E1 wall time quota must be finite and positive")
    if stop_after_variants is not None and stop_after_variants < 1:
        raise ValueError("E1 variant quota must be positive")

    predictor = Predictor(checkpoint, prepared)
    graph, starts = training_dfg(prepared)
    prefixes = prepared["prefixes"]["test"]
    prefix_ids = [prefix["prefix_id"] for prefix in prefixes]
    identity = {"study": "E1", "schema_version": 1, "dataset": fingerprint(prepared),
                "source": source_hash(), "checkpoint": predictor.checkpoint_id,
                "prefix_ids": prefix_ids}
    directory = output.parent / (output.stem + "-e1-run")
    database = directory / "records.sqlite"
    started = time.monotonic()
    added = 0
    stop_reason = None
    with run_lock(directory):
        if output.exists():
            raise FileExistsError("Completed study output already exists")
        with closing(sqlite3.connect(database)) as db:
            with db:
                db.execute("CREATE TABLE IF NOT EXISTS identity (id INTEGER PRIMARY KEY CHECK(id=1), payload TEXT NOT NULL)")
                db.execute("CREATE TABLE IF NOT EXISTS prefixes "
                           "(prefix_id TEXT PRIMARY KEY, complete INTEGER NOT NULL, payload TEXT NOT NULL)")
                db.execute("CREATE TABLE IF NOT EXISTS variants "
                           "(prefix_id TEXT, ordinal INTEGER, payload TEXT NOT NULL, PRIMARY KEY(prefix_id,ordinal))")
                previous = db.execute("SELECT payload FROM identity WHERE id=1").fetchone()
                if previous is None:
                    db.execute("INSERT INTO identity VALUES (1,?)", (encode(identity),))
                elif decode(previous[0]) != identity:
                    raise ValueError("E1 resume identity mismatch")

            for prefix in prefixes:
                prefix_id = prefix["prefix_id"]
                saved = db.execute("SELECT complete,payload FROM prefixes WHERE prefix_id=?", (prefix_id,)).fetchone()
                if saved and saved[0]:
                    continue
                labels = prefix["activities"]
                state = decode(saved[1]) if saved else e1_state(sorted(set(labels)))
                cursor = state["completed_variants"]
                remaining = islice(variants(labels, prefix_id, graph, starts), cursor, None)
                records = e1_records(predictor, prefix, remaining)
                while True:
                    if time.monotonic() - started >= max_seconds:
                        stop_reason = "wall_time_quota"
                        break
                    if stop_after_variants is not None and added >= stop_after_variants:
                        stop_reason = "requested_variant_checkpoint"
                        break
                    resources = resource_snapshot(directory)
                    if resources["disk_free_bytes"] < 1024**3:
                        stop_reason = "disk_floor"
                        break
                    if resources["system_available_ram_bytes"] is not None and resources["system_available_ram_bytes"] < 256 * 1024**2:
                        stop_reason = "available_ram_floor"
                        break
                    batch = []
                    exhausted = False
                    for _ in range(64):
                        if time.monotonic() - started >= max_seconds:
                            break
                        if stop_after_variants is not None and added + len(batch) >= stop_after_variants:
                            break
                        row = next(records, None)
                        if row is None:
                            exhausted = True
                            break
                        e1_accumulate(state, row)
                        batch.append((prefix_id, cursor + len(batch), encode(row)))
                    if batch or exhausted:
                        payload = e1_summary(prefix_id, state) if exhausted else state
                        with db:
                            db.executemany("INSERT INTO variants VALUES (?,?,?)", batch)
                            db.execute("INSERT OR REPLACE INTO prefixes VALUES (?,?,?)",
                                       (prefix_id, int(exhausted), encode(payload)))
                    cursor += len(batch)
                    added += len(batch)
                    if exhausted:
                        break
                if stop_reason:
                    break

            records = [decode(payload) for (payload,) in db.execute(
                "SELECT payload FROM prefixes WHERE complete=1 ORDER BY prefix_id")]
            completed = db.execute("SELECT COUNT(*) FROM variants").fetchone()[0]
            status = "completed" if len(records) == len(prefixes) else "incomplete"
            progress = {"identity": identity, "status": status, "scope": prepared.get("scope"),
                        "expected_prefixes": len(prefixes), "completed_prefixes": len(records),
                        "completed_variants": completed, "new_variants": added, "stop_reason": stop_reason,
                        "wall_seconds_this_session": time.monotonic() - started}
            write_json(directory / "progress.json", seal(progress))

        if status == "incomplete":
            return progress
        if sum(row["completed_variants"] for row in records) != completed:
            raise ValueError("E1 ledger row count differs from prefix summaries")
        result = {**progress, "study": "E1", "baseline_checkpoint": predictor.checkpoint_id,
                  "storage": "sealed-per-variant-sqlite", "records": records,
                  "tau_b": summary([row["tau_b"] for row in records]),
                  "records_database": str(database.relative_to(output.parent)),
                  "records_sha256": file_hash(database)}
        write_json(output, seal(result))
        return result
