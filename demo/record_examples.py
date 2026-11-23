"""Regenerate only the small set of recorded examples used in the walkthrough."""
import json
from pathlib import Path
from research import execute, load
from nhom19_process_xai.artifacts import seal

examples = []
for dataset, length, positions in [("helpdesk-v1",3,[2,0]),("synthetic-sequence",4,[1])]:
    model, cases, init = load(dataset)
    row = next(rows[length] for rows in cases.values() if length in rows)
    for pos in positions:
        sample = execute(model,dataset,row,pos)
        sample["init_ms"] = init
        print(dataset,row["case_id"],pos,init,sample["ms"],sample["tvd"])
        examples.append(sample)
Path(__file__).with_name("examples.json").write_text(
    json.dumps(seal({"examples":examples}),ensure_ascii=False), encoding="utf8")
