"""Data contracts from Round 3.6, S1.

An event's source ordinal is assigned before filtering. Literal activity names
remain distinct from the reserved integer PAD and UNK tokens.
"""

from __future__ import annotations

import csv
import gzip
import hashlib
import json
import random
import xml.etree.ElementTree as ET
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Iterator, Mapping
from zoneinfo import ZoneInfo


def fingerprint(value: Any) -> str:
    encoded = json.dumps(value, ensure_ascii=False, sort_keys=True,
                         separators=(",", ":"), allow_nan=False).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def parse_timestamp(value: str, naive_timezone: str | None = None) -> datetime:
    stamp = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if stamp.tzinfo is None:
        if naive_timezone is None:
            raise ValueError("Naive timestamp requires an explicit dataset timezone")
        zone = ZoneInfo(naive_timezone)
        first = stamp.replace(tzinfo=zone, fold=0)
        second = stamp.replace(tzinfo=zone, fold=1)
        if first.utcoffset() != second.utcoffset():
            raise ValueError("Ambiguous/nonexistent local timestamp requires an explicit offset")
        stamp = first
    return stamp.astimezone(timezone.utc)


@dataclass(frozen=True)
class Event:
    case_id: str
    activity: str
    timestamp: datetime
    source_ordinal: int
    attrs: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.case_id, str) or not isinstance(self.activity, str) or not self.case_id or not self.activity:
            raise ValueError("case_id and activity must be nonempty")
        if self.timestamp.tzinfo is None or self.timestamp.utcoffset() is None:
            raise ValueError("Event timestamp must be timezone aware")
        if isinstance(self.source_ordinal, bool) or not isinstance(self.source_ordinal, int) or self.source_ordinal < 0:
            raise ValueError("source_ordinal must be a nonnegative integer")

    def record(self) -> dict[str, Any]:
        result = asdict(self)
        result["timestamp"] = self.timestamp.astimezone(timezone.utc).isoformat()
        return result


def normalize(events: Iterable[Event]) -> list[Event]:
    events = list(events)
    ordinals = [event.source_ordinal for event in events]
    if len(set(ordinals)) != len(ordinals):
        raise ValueError("source_ordinal must be unique across the input log")
    return sorted(events, key=lambda e: (e.case_id, e.timestamp, e.source_ordinal))


def group_cases(events: Iterable[Event]) -> dict[str, list[Event]]:
    cases: dict[str, list[Event]] = {}
    for event in normalize(events):
        cases.setdefault(event.case_id, []).append(event)
    return cases


def split_cases(case_ids: Iterable[str], seed: int = 42) -> dict[str, list[str]]:
    ordered = sorted(set(case_ids))
    if len(ordered) < 2:
        raise ValueError("A case-level split requires at least two cases")
    random.Random(seed).shuffle(ordered)
    boundary = max(1, min(len(ordered) - 1, int(.7 * len(ordered))))
    return {"train": sorted(ordered[:boundary]), "test": sorted(ordered[boundary:])}


@dataclass(frozen=True)
class Vocabulary:
    inputs: dict[str, int]
    outputs: dict[str, int]

    @classmethod
    def fit(cls, cases: Mapping[str, list[Event]], train_ids: list[str]) -> Vocabulary:
        activities = sorted({e.activity for case in train_ids for e in cases[case]})
        targets = sorted({e.activity for case in train_ids for e in cases[case][1:]})
        if not targets:
            raise ValueError("Training cases have no next-activity targets")
        return cls({label: i + 2 for i, label in enumerate(activities)},
                   {label: i for i, label in enumerate(targets)})


@dataclass(frozen=True)
class Prefix:
    prefix_id: str
    case_id: str
    activities: tuple[str, ...]
    occurrence_ids: tuple[int, ...]
    token_ids: tuple[int, ...]
    target: str
    target_id: int | None


def prefixes(cases: Mapping[str, list[Event]], selected: list[str],
             vocab: Vocabulary, dataset_hash: str, split_hash: str) -> list[Prefix]:
    result = []
    for case_id in sorted(selected):
        case = cases[case_id]
        for length in range(1, len(case)):
            history = case[:length]
            labels = tuple(event.activity for event in history)
            result.append(Prefix(
                fingerprint([dataset_hash, split_hash, case_id, length]), case_id,
                labels, tuple(event.source_ordinal for event in history),
                tuple(vocab.inputs.get(label, 1) for label in labels),
                case[length].activity, vocab.outputs.get(case[length].activity)))
    return result


def read_csv(path: Path, columns: Mapping[str, str],
             naive_timezone: str | None = None) -> list[Event]:
    required = {"case_id", "activity", "timestamp"}
    if set(columns) != required:
        raise ValueError("CSV columns must map case_id, activity, timestamp")
    result = []
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        if not set(columns.values()).issubset(reader.fieldnames or []):
            raise ValueError("CSV lacks configured columns")
        for ordinal, row in enumerate(reader):
            try:
                result.append(Event(row[columns["case_id"]], row[columns["activity"]],
                                    parse_timestamp(row[columns["timestamp"]], naive_timezone),
                                    ordinal, dict(row)))
            except (ValueError, TypeError) as error:
                raise ValueError(f"Invalid CSV row {ordinal + 2}: {error}") from error
    return result


def read_xes(path: Path, naive_timezone: str | None = None,
             audit: dict | None = None) -> list[Event]:
    """Read event attributes without discarding repeated events or timestamp ties."""
    return [event for trace in iter_xes_traces(path, naive_timezone, audit) for event in trace]


def iter_xes_traces(path: Path, naive_timezone: str | None = None,
                    audit: dict | None = None) -> Iterator[list[Event]]:
    """Read one complete trace at a time; ordinals count all source events."""
    ordinal = 0
    case_ids = set()
    empty_cases = []
    opener = gzip.open if path.suffix == ".gz" else open
    with opener(path, "rb") as stream:
        entries = ET.iterparse(stream, events=("start", "end"))
        _, root = next(entries)
        for phase, trace in entries:
            if phase != "end" or trace.tag.rsplit("}", 1)[-1] != "trace":
                continue
            trace_attrs = {item.attrib.get("key"): item.attrib.get("value")
                           for item in trace if item.tag.rsplit("}", 1)[-1] != "event"}
            case_id = trace_attrs.get("concept:name")
            if not isinstance(case_id, str) or not case_id or case_id in case_ids:
                raise ValueError("XES trace names must be nonempty and unique")
            case_ids.add(case_id)
            events = []
            trace_xml = [ET.tostring(item, encoding="unicode") for item in trace
                         if item.tag.rsplit("}", 1)[-1] != "event"]
            for item in trace:
                if item.tag.rsplit("}", 1)[-1] != "event":
                    continue
                attrs = {attr.attrib.get("key"): attr.attrib.get("value") for attr in item}
                try:
                    event = Event(case_id, attrs["concept:name"],
                                  parse_timestamp(attrs["time:timestamp"], naive_timezone),
                                  ordinal, {"event": attrs, "case": trace_attrs,
                                                "event_xml": ET.tostring(item, encoding="unicode"),
                                                "case_attributes_xml": list(trace_xml)})
                except (KeyError, TypeError, ValueError) as error:
                    raise ValueError(f"Invalid XES event {ordinal} in {case_id}: {error}") from error
                ordinal += 1
                events.append(event)
            if not events:
                empty_cases.append(case_id)
            root.remove(trace)
            trace.clear()
            yield events
    if audit is not None:
        audit.update(empty_cases=sorted(empty_cases), trace_count=len(case_ids))


def prepare(events: Iterable[Event], assignment: dict[str, list[str]] | None = None,
            seed: int = 42) -> dict[str, Any]:
    ordered = normalize(events)
    cases = group_cases(ordered)
    split = assignment if assignment is not None else split_cases(cases, seed)
    if set(split) != {"train", "test"}:
        raise ValueError("Split must contain exactly train and test")
    combined = split["train"] + split["test"]
    if len(combined) != len(set(combined)) or set(combined) != set(cases):
        raise ValueError("Split must cover every case exactly once")
    split = {name: sorted(ids) for name, ids in split.items()}
    if not all(split.values()):
        raise ValueError("Both train and test case sets must be nonempty")
    vocab = Vocabulary.fit(cases, split["train"])
    processed_hash = fingerprint([event.record() for event in ordered])
    split_hash = fingerprint(split)
    return {
        "schema_version": 1,
        "processed_sha256": processed_hash,
        "split_sha256": split_hash,
        "split": split,
        "split_algorithm": "CPython random.Random shuffle on sorted case IDs",
        "seed": seed,
        "vocabulary": asdict(vocab),
        "counts": {"cases": len(cases), "events": len(ordered),
                   "activities": len({e.activity for e in ordered})},
        "prefixes": {name: [asdict(p) for p in prefixes(cases, ids, vocab,
                                                       processed_hash, split_hash)]
                     for name, ids in split.items()},
    }
