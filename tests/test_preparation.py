from datetime import datetime, timezone
import json
from pathlib import Path

import pytest

from nhom19_process_xai.artifacts import read_sealed, seal, write_json
from nhom19_process_xai.data.pipeline import Event, read_xes
from nhom19_process_xai.data.preparation import prepare_file, preprocess


def test_ordered_filters_and_occurrences():
    date = datetime(2025, 1, 1, tzinfo=timezone.utc)
    events = [Event("c1", "W_A", date, 0, {"lifecycle:transition": "start"}),
              Event("c1", "W_A", date, 1, {"lifecycle:transition": "complete"}),
              Event("c2", "O_A", date, 2, {"lifecycle:transition": "complete"})]
    filtered, audit = preprocess(events, [{"kind": "activity_prefix", "value": "W_"},
                                           {"kind": "lifecycle", "value": "complete"}])
    assert [event.source_ordinal for event in filtered] == [1]
    assert audit[0]["removed_cases"] == ["c2"]
    assert audit[1]["events_before"] == 2 and audit[1]["events_after"] == 1
    assert len(events) == 3
    with pytest.raises(ValueError, match="Unknown"):
        preprocess(events, [{"kind": "silent_drop", "value": "x"}])


def test_xes_empty_and_duplicate_case(tmp_path):
    path = tmp_path / "empty.xes"
    path.write_text('<log><trace><string key="concept:name" value="empty"/></trace></log>')
    audit = {}
    assert read_xes(path, audit=audit) == []
    assert audit == {"empty_cases": ["empty"], "trace_count": 1}
    path.write_text('<log><trace><string key="concept:name" value="c"/></trace><trace><string key="concept:name" value="c"/></trace></log>')
    with pytest.raises(ValueError, match="unique"):
        read_xes(path)


def test_filtered_xes_matches_full_log_filtering(tmp_path):
    def event(label, lifecycle):
        return (f'<event><string key="concept:name" value="{label}"/>'
                f'<string key="lifecycle:transition" value="{lifecycle}"/>'
                '<date key="time:timestamp" value="2025-01-01T00:00:00Z"/></event>')

    traces = {"b": [("O_A", ""), ("W_A", "complete"), ("W_B", "complete")],
              "a": [("W_B", "start"), ("W_B", "complete"), ("W_A", "complete")],
              "x": [("O_B", "complete")], "y": [("W_A", "start")], "empty": []}
    source = tmp_path / "log.xes"
    source.write_text('<log xmlns="http://www.xes-standard.org/">' + "".join(
        f'<trace><string key="concept:name" value="{case}"/>'
        + "".join(event(*activity) for activity in activities) + '</trace>'
        for case, activities in traces.items()) + '</log>', encoding="utf-8")
    filters = [{"kind": "activity_prefix", "value": "W_"}, {"kind": "lifecycle", "value": "complete"}]
    raw_audit = {}
    expected, expected_filters = preprocess(read_xes(source, audit=raw_audit), filters, True)
    config = {"dataset_id": "example", "path": source.name, "format": "xes", "source": "generated",
              "version": "1", "license": "test", "scope": "fixture", "filters": filters,
              "lifecycle_classifier": True}
    output = tmp_path / "prepared.json"
    actual = prepare_file(config, tmp_path, output)
    assert read_sealed(output)["events"] == [event.record() for event in expected]
    assert [entry["source_ordinal"] for entry in actual["events"]] == [1, 2, 4, 5]
    assert actual["adapter"] == raw_audit == {"empty_cases": ["empty"], "trace_count": 5}
    assert actual["filters"] == expected_filters
    assert [row["removed_cases"] for row in actual["filters"]] == [["x"], ["y"]]


def test_checksum_and_nonoverwrite(tmp_path):
    config_path = Path(__file__).parents[1] / "configs/fixture/dataset.json"
    config = json.loads(config_path.read_text())
    output = tmp_path / "data.json"
    prepare_file(config, config_path.parent, output)
    with pytest.raises(FileExistsError):
        prepare_file(config, config_path.parent, output)
    config["expected_sha256"] = "0" * 64
    with pytest.raises(ValueError, match="checksum"):
        prepare_file(config, config_path.parent, tmp_path / "wrong.json")
    sealed = tmp_path / "sealed.json"
    write_json(sealed, seal({"a": 1}))
    sealed.write_text(sealed.read_text().replace('"a": 1', '"a": 2'))
    with pytest.raises(ValueError, match="checksum"):
        read_sealed(sealed)
