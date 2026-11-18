from datetime import datetime, timezone

import pytest

from nhom19_process_xai.data.pipeline import (
    Event, normalize, parse_timestamp, prepare, read_csv, read_xes, split_cases,
)


@pytest.fixture
def events():
    traces = {"c1": "AAB", "c2": "AC", "c3": "BAC", "c4": "AAC", "c5": "BD"}
    result = []
    for case, trace in traces.items():
        for label in trace:
            result.append(Event(case, label, datetime(2025, 1, 1, tzinfo=timezone.utc), len(result)))
    return result


def test_contract_fixture(events):
    result = prepare(events, {"train": ["c1", "c2", "c3"], "test": ["c4", "c5"]})
    assert result["vocabulary"] == {"inputs": {"A": 2, "B": 3, "C": 4},
                                     "outputs": {"A": 0, "B": 1, "C": 2}}
    train = result["prefixes"]["train"]
    test = result["prefixes"]["test"]
    assert [p["token_ids"] for p in train] == [(2,), (2, 2), (2,), (3,), (3, 2)]
    assert [p["target_id"] for p in train] == [0, 1, 2, 0, 2]
    assert [p["target"] for p in test] == ["A", "C", "D"]
    assert [p["target_id"] for p in test] == [0, 2, None]
    assert len({p["prefix_id"] for p in train + test}) == 8
    assert prepare(reversed(events), result["split"]) == result


def test_unknown_input_and_reserved_literal():
    stamp = datetime.now(timezone.utc)
    events = [Event("train", "[PAD]", stamp, 0), Event("train", "A", stamp, 1),
              Event("test", "D", stamp, 2), Event("test", "A", stamp, 3)]
    result = prepare(events, {"train": ["train"], "test": ["test"]})
    assert result["vocabulary"]["inputs"]["[PAD]"] >= 2
    assert result["prefixes"]["test"][0]["token_ids"] == (1,)
    assert result["prefixes"]["test"][0]["target_id"] == 0


def test_split_leakage_and_repeated_events(events):
    with pytest.raises(ValueError, match="exactly once"):
        prepare(events, {"train": ["c1", "c2", "c3"], "test": ["c3", "c4", "c5"]})
    assert len(normalize(events)) == 13
    assert split_cases(["c3", "c2", "c1"]) == split_cases(["c1", "c2", "c3"])
    with pytest.raises(ValueError, match="unique"):
        normalize(events + [events[0]])


def test_timestamp_policy():
    with pytest.raises(ValueError, match="timezone"):
        parse_timestamp("2025-01-01T00:00:00")
    assert parse_timestamp("2025-01-01T07:00:00+07:00") == parse_timestamp("2025-01-01T00:00:00Z")
    with pytest.raises(ValueError, match="Ambiguous"):
        parse_timestamp("2025-11-02T01:30:00", "America/New_York")


def test_csv_adapter(tmp_path):
    path = tmp_path / "events.csv"
    path.write_text('case,activity,time\na,A,2025-01-01T00:00:00Z\na,A,2025-01-01T00:00:00Z\n', encoding="utf-8")
    events = read_csv(path, {"case_id": "case", "activity": "activity", "timestamp": "time"})
    assert [e.source_ordinal for e in events] == [0, 1]
    assert events[0].attrs["activity"] == "A"


def test_xes_adapter(tmp_path):
    path = tmp_path / "fixture.xes"
    path.write_text('''<log xmlns="http://www.xes-standard.org/"><trace>
    <string key="concept:name" value="c1"/>
    <event><string key="concept:name" value="A"/><date key="time:timestamp" value="2025-01-01T00:00:00Z"/></event>
    <event><string key="concept:name" value="A"/><date key="time:timestamp" value="2025-01-01T00:00:00Z"/></event>
    </trace></log>''', encoding="utf-8")
    events = read_xes(path)
    assert [e.activity for e in events] == ["A", "A"]
    assert [e.source_ordinal for e in events] == [0, 1]
