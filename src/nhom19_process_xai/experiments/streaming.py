"""Durable per-prefix E2/E3 records, bounded independently of log size."""

from contextlib import closing
from datetime import datetime, timezone
import json
import math
from pathlib import Path
import sqlite3
import time

from ..artifacts import read_sealed, seal, write_json
from ..data.pipeline import file_hash, fingerprint
from ..evaluate.metrics import summary
from ..model.predictor import Predictor
from ..model.training import TrainingConfig, run_lock, source_hash, train
from ..resources import resource_snapshot
from .studies import e2_pair, e3_prefix


def run_streaming_study(name: str, prepared: dict, checkpoint: Path, output: Path,
                        profile: str | None = None, max_seconds: float = 3600,
                        stop_after_units: int | None = None) -> dict:
    """Resume sealed units; quotas interrupt coverage, never sample the primary set.

    Time/RAM/disk checks occur between prefix units or model-training jobs. One
    prefix and one whole model job must fit memory/time; they are not preempted.
    """
    profiles = {"E2": {"E2-FC", "E2-AC", "E2-UNI"}, "E3": {"E3-PAPER", "E3-AUTHOR"}}
    defaults = {"E2": "E2-FC", "E3": "E3-PAPER"}
    if name not in profiles:
        raise ValueError("Streaming runner supports E2 and E3")
    profile = profile or defaults[name]
    if (profile not in profiles[name] or not math.isfinite(max_seconds) or max_seconds <= 0
            or (stop_after_units is not None and stop_after_units < 1)):
        raise ValueError("Invalid profile or execution quota")
    if output.exists():
        raise FileExistsError("Completed study output already exists")
    baseline = Predictor(checkpoint, prepared)
    prefixes = sorted(prepared["prefixes"]["test"], key=lambda row: row["prefix_id"])
    directory = output.parent / (output.stem + "-run")
    identity = {"study": name, "profile": profile, "dataset": fingerprint(prepared),
                "checkpoint": baseline.checkpoint_id, "source": source_hash(),
                "prefix_ids": [row["prefix_id"] for row in prefixes]}
    arms = [("BASE", seed) for seed in range(2001, 2006)] + [(profile, seed) for seed in range(2006, 2011)] if name == "E2" else [(profile, None)]
    expected = len(prefixes) * len(arms)
    started, cpu_started = time.perf_counter(), time.process_time()
    before = resource_snapshot(directory)
    session = {"started_utc": datetime.now(timezone.utc).isoformat(), "before": before,
               "max_seconds": max_seconds, "stop_after_units": stop_after_units,
               "check_boundary": "between prefix units and whole training jobs",
               "minimum_ram_bytes": 256 * 1024**2, "minimum_disk_bytes": 1024**3}
    with run_lock(directory):
        if output.exists():
            raise FileExistsError("Completed study output already exists")
        with closing(sqlite3.connect(directory / "records.sqlite")) as connection:
            progress_path = directory / "progress.json"
            if progress_path.exists():
                previous = read_sealed(progress_path)
                if previous["identity"] != identity:
                    raise ValueError("Streaming study resume identity mismatch")
                sessions = previous["sessions"]
            else:
                if (directory / "records.sqlite").stat().st_size:
                    raise ValueError("Records database has no owning manifest")
                sessions = []
            connection.execute("CREATE TABLE IF NOT EXISTS records (arm TEXT, seed TEXT, prefix_id TEXT, payload TEXT, PRIMARY KEY(arm,seed,prefix_id))")
            connection.commit()
            progress = {"identity": identity, "scope": prepared.get("scope"), "expected_units": expected,
                        "completed_units": connection.execute("SELECT count(*) FROM records").fetchone()[0],
                        "status": "incomplete", "sessions": sessions, "active_session": session}
            write_json(progress_path, seal(progress))
            added, stop = 0, None

            def quota():
                if stop_after_units is not None and added >= stop_after_units:
                    return "requested_unit_checkpoint"
                if time.perf_counter() - started >= max_seconds:
                    return "wall_time_quota"
                snapshot = resource_snapshot(directory)
                if snapshot["disk_free_bytes"] < session["minimum_disk_bytes"]:
                    return "disk_floor"
                available = snapshot["system_available_ram_bytes"]
                if available is not None and available < session["minimum_ram_bytes"]:
                    return "available_ram_floor"
                return None

            for arm, seed in arms:
                stop = quota()
                if stop:
                    break
                modified = None
                if name == "E2":
                    model_dir = directory / "models" / f"{arm}-{seed}"
                    config = TrainingConfig(**{**baseline.identity["training"], "profile": arm, "seed": seed})
                    train(prepared, model_dir, config, resume=(model_dir / "checkpoint.pt").exists())
                    modified = Predictor(model_dir / "checkpoint.pt", prepared)
                for prefix in prefixes:
                    key = (arm, str(seed), prefix["prefix_id"])
                    existing = connection.execute("SELECT payload FROM records WHERE arm=? AND seed=? AND prefix_id=?", key).fetchone()
                    if existing:
                        envelope = json.loads(existing[0])
                        if fingerprint(envelope["payload"]) != envelope["sha256"]:
                            raise ValueError("Study unit checksum mismatch")
                        saved = envelope["payload"]
                        if saved["prefix_id"] != prefix["prefix_id"]:
                            raise ValueError("Study unit prefix mismatch")
                        if modified is not None and saved["modified_checkpoint"] != modified.checkpoint_id:
                            raise ValueError("Study unit checkpoint mismatch")
                        continue
                    stop = quota()
                    if stop:
                        break
                    if name == "E2":
                        row = {"prefix_id": prefix["prefix_id"],
                               **e2_pair(baseline.predict(prefix["activities"]), modified.predict(prefix["activities"]))}
                    else:
                        row = e3_prefix(baseline, prefix, profile)
                    connection.execute("INSERT INTO records VALUES (?,?,?,?)", (*key, json.dumps(seal(row), allow_nan=False)))
                    connection.commit()
                    added += 1
                    progress["completed_units"] += 1
                    if added % 25 == 0:
                        write_json(progress_path, seal(progress))
                if stop:
                    break
            completed = connection.execute("SELECT count(*) FROM records").fetchone()[0]
            session.update(ended_utc=datetime.now(timezone.utc).isoformat(),
                           wall_seconds=time.perf_counter() - started, cpu_seconds=time.process_time() - cpu_started,
                           completed_units=added, stop_reason=stop, after=resource_snapshot(directory))
            progress.update(status="completed" if completed == expected else "incomplete", completed_units=completed,
                            pending_units=expected - completed, coverage=completed / expected if expected else None,
                            active_session=None, sessions=[*sessions, session])
            write_json(progress_path, seal(progress))
            if completed != expected:
                return progress
            pairs = []
            for arm, seed in arms:
                primary, secondary = [], []
                cursor = connection.execute("SELECT payload FROM records WHERE arm=? AND seed=? ORDER BY prefix_id", (arm, str(seed)))
                for (payload,) in cursor:
                    envelope = json.loads(payload)
                    row = envelope["payload"]
                    if fingerprint(row) != envelope["sha256"]:
                        raise ValueError("Study unit checksum mismatch")
                    primary.append(row["jsd"] if name == "E2" else row["prediction_tvd"]["mean"])
                    if name == "E2":
                        secondary.append(row["prediction_tvd"])
                pair = {"arm": arm, "seed": seed, "completed_prefixes": len(primary)}
                if name == "E2":
                    pair.update(jsd=summary(primary), tvd=summary(secondary),
                                checkpoint_sha256=file_hash(directory / "models" / f"{arm}-{seed}" / "checkpoint.pt"))
                else:
                    pair["prediction_tvd"] = summary(primary)
                pairs.append(pair)
        result = {"schema_version": 1, "storage": "sealed-per-prefix-sqlite", "study": name, "profile": profile,
                  "status": "completed", "identity": identity, "scope": prepared.get("scope"),
                  "baseline_checkpoint": baseline.checkpoint_id, "expected_units": expected, "completed_units": completed,
                  "expected_prefixes": len(prefixes), "completed_prefixes": len(prefixes), "pairs": pairs,
                  "records_database": str((directory / "records.sqlite").relative_to(output.parent)),
                  "records_sha256": file_hash(directory / "records.sqlite"), "sessions": progress["sessions"]}
        write_json(output, seal(result))
        return result
