"""File preparation with explicit provenance and ordered filtering."""

from dataclasses import replace
from pathlib import Path

from .pipeline import Event, file_hash, fingerprint, iter_xes_traces, prepare, read_csv
from ..artifacts import seal, write_json


def preprocess(events: list[Event], filters: list[dict],
               lifecycle_classifier: bool = False) -> tuple[list[Event], list[dict]]:
    records = []
    current = events
    for specification in filters:
        before = {e.case_id for e in current}
        if set(specification) != {"kind", "value"}:
            raise ValueError("Each filter requires exactly kind and value")
        kind, value = specification["kind"], specification["value"]
        if not isinstance(value, str):
            raise ValueError("Filter values must be strings")
        if kind == "activity_prefix":
            selected = [e for e in current if e.activity.startswith(value)]
        elif kind == "lifecycle":
            def transition(event):
                return event.attrs.get("event", event.attrs).get("lifecycle:transition")
            if any(transition(e) is None for e in current):
                raise ValueError("Lifecycle filter requires lifecycle:transition on every event")
            selected = [e for e in current if transition(e) == value]
        else:
            raise ValueError(f"Unknown preprocessing filter: {kind}")
        records.append({"filter": specification, "events_before": len(current),
                        "events_after": len(selected),
                        "removed_cases": sorted(before - {e.case_id for e in selected})})
        current = selected
    if lifecycle_classifier:
        classified = []
        for event in current:
            transition = event.attrs.get("event", event.attrs).get("lifecycle:transition")
            if not isinstance(transition, str) or not transition:
                raise ValueError("Lifecycle classifier requires a nonempty transition")
            # JSON pair encoding avoids ambiguity when either field contains a separator.
            import json
            label = json.dumps([event.activity, transition], ensure_ascii=False, separators=(",", ":"))
            classified.append(replace(event, activity=label))
        current = classified
    return current, records


def _preprocess_xes(path, timezone, filters, classifier, adapter):
    events, totals = preprocess([], filters, classifier)
    for trace in iter_xes_traces(path, timezone, audit=adapter):
        selected, records = preprocess(trace, filters, classifier)
        events.extend(selected)
        for total, record in zip(totals, records, strict=True):
            total["events_before"] += record["events_before"]
            total["events_after"] += record["events_after"]
            total["removed_cases"].extend(record["removed_cases"])
    for total in totals:
        total["removed_cases"].sort()
    return events, totals


def prepare_file(config: dict, base_directory: Path, output: Path) -> dict:
    required = {"dataset_id", "path", "format", "source", "version", "license", "scope"}
    allowed = required | {"columns", "naive_timezone", "filters", "lifecycle_classifier",
                          "split", "seed", "expected_sha256", "expected_counts"}
    if not required.issubset(config) or set(config) - allowed:
        raise ValueError("Dataset configuration has missing or unknown fields")
    for name in required - {"path"}:
        if not isinstance(config[name], str) or not config[name].strip():
            raise ValueError(f"Dataset field {name} must be a nonempty string")
    if config["scope"] not in {"fixture", "candidate", "verified_dataset"}:
        raise ValueError("Unknown dataset scope")
    raw_path = (base_directory / config["path"]).resolve()
    digest = file_hash(raw_path)
    if config.get("expected_sha256") and digest != config["expected_sha256"]:
        raise ValueError("Raw file checksum mismatch")
    filters = config.get("filters", [])
    classifier = config.get("lifecycle_classifier", False)
    if config["format"] == "csv":
        events = read_csv(raw_path, config.get("columns", {}), config.get("naive_timezone"))
        adapter = {"empty_cases": [], "trace_count": len({e.case_id for e in events})}
        selected, filter_records = preprocess(events, filters, classifier)
    elif config["format"] == "xes":
        adapter = {}
        selected, filter_records = _preprocess_xes(raw_path, config.get("naive_timezone"), filters, classifier, adapter)
    else:
        raise ValueError("Supported input formats are csv and xes")
    if file_hash(raw_path) != digest:
        raise ValueError("Source file changed during preparation")
    prepared = prepare(selected, config.get("split"), config.get("seed", 42))
    for key, value in config.get("expected_counts", {}).items():
        if key not in prepared["counts"] or prepared["counts"][key] != value:
            raise ValueError(f"Prepared count mismatch for {key}")
    prepared.update(dataset_id=config["dataset_id"], scope=config["scope"],
                    raw_sha256=digest, config=config, config_sha256=fingerprint(config),
                    adapter=adapter, filters=filter_records,
                    events=[event.record() for event in selected])
    if output.exists():
        raise FileExistsError(f"Prepared output already exists: {output}")
    write_json(output, seal(prepared))
    return prepared
