"""Research adapter shared by the live workstation and offline examples."""
from collections import defaultdict
from pathlib import Path
from time import perf_counter
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
PROFILE = "E3-PAPER"


def paths(dataset):
    return (ROOT / "data/processed" / f"{dataset}.json",
            ROOT / "artifacts" / dataset / "base/checkpoint.pt")


def inventory():
    return sorted(p.stem for p in (ROOT / "data/processed").glob("*.json")
                  if paths(p.stem)[1].is_file())


def load(dataset):
    from nhom19_process_xai.artifacts import read_sealed
    from nhom19_process_xai.model.predictor import Predictor
    start = perf_counter()
    data, checkpoint = paths(dataset)
    prepared = read_sealed(data)
    model = Predictor(checkpoint, prepared)
    cases = defaultdict(dict)
    for row in prepared["prefixes"]["test"]:
        cases[row["case_id"]][len(row["activities"])] = row
    return model, dict(cases), (perf_counter()-start)*1000


def execute(model, dataset, row, pos):
    from nhom19_process_xai.evaluate.metrics import tvd
    seq = row["activities"]
    masked = seq.copy()
    masked[pos] = None
    start = perf_counter()
    base = model.predict(seq)
    t1 = perf_counter()
    input_arm = model.predict(masked)
    t2 = perf_counter()
    score_arm = model.predict(seq, (pos,), PROFILE)
    t3 = perf_counter()
    matrices = [base.attention.tolist(), score_arm.effective_attention.tolist()]
    t4 = perf_counter()
    probs = [p.probabilities.tolist() for p in (base,input_arm,score_arm)]
    distances = [tvd(probs[a],probs[b]) for a,b in [(0,1),(0,2),(1,2)]]
    return dict(dataset=dataset, case=row["case_id"], prefix=row["prefix_id"],
                activities=seq, target=row["target"], pos=pos, profile=PROFILE,
                checkpoint=model.checkpoint_id, dataset_hash=model.identity["dataset_sha256"],
                device=str(next(model.model.parameters()).device), classes=list(base.class_order),
                probabilities=probs, attention=matrices, tvd=distances,
                ms=dict(base=(t1-start)*1000,input=(t2-t1)*1000,score=(t3-t2)*1000,
                        attention_export=(t4-t3)*1000,total=(perf_counter()-start)*1000))
