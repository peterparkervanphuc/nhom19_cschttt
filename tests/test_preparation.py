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
