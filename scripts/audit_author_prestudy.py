"""Check the archived E1, E2 and E3 CSVs without running the author models."""

import argparse
import csv
from hashlib import sha256
from io import StringIO
import json
import math
from pathlib import Path
from statistics import mean
from zipfile import ZipFile

from nhom19_process_xai.artifacts import write_json
from nhom19_process_xai.data.pipeline import file_hash


ARCHIVE_SHA256 = "b1b88b2d7797fbe3369dccc5c4fe8d9a96af5d52293954279d4bab2f0bcc169e"
ROOT = "Supplementary_Material/Trained_Models/"
BINS = ("[0.00,\n0.25)", "[0.25,\n0.50)", "[0.50,\n0.75)", "[0.75,\n1.00]")
QUANTILES = (0, .25, .5, .75, 1)


def values(rows, column):
    result = [float(row[column]) for row in rows if row[column]]
    if not all(math.isfinite(value) for value in result):
        raise ValueError(f"Non-finite value in {column}")
    return result


def quantiles(series):
    ordered = sorted(series)
    if not ordered:
        return [None] * len(QUANTILES)
    result = []
    for fraction in QUANTILES:
        index = (len(ordered) - 1) * fraction
        lo, hi = math.floor(index), math.ceil(index)
        result.append(ordered[lo] + (index - lo) * (ordered[hi] - ordered[lo]))
    return result


def verify_quantiles(series, row):
    found = quantiles(series)
    for fraction, observed in zip(QUANTILES, found, strict=True):
        archived = row[f"p-{fraction:.2f}"]
        if ((observed is None) != (archived == "")
                or (observed is not None and not math.isclose(observed, float(archived), abs_tol=1e-12))):
            raise ValueError(f"Archived quantile mismatch for {row['']} at {fraction}")
    return found


def audit_log(archive, folder):
    members = {}

    def load(file):
        path = f"{folder}/{file}.csv"
        raw = archive.read(path)
        rows = list(csv.DictReader(StringIO(raw.decode("utf-8-sig"))))
        members[file] = {"member": path, "sha256": sha256(raw).hexdigest(), "rows": len(rows)}
        return rows

    feature = load("attn_feature_importance")
    feature_summary = load("attn_feature_importance_summary")
    columns = [key for key in feature[0] if key]
    if [row[""] for row in feature_summary] != columns:
        raise ValueError("E1 summary columns differ from raw archive")
    e1 = {column: verify_quantiles(values(feature, column), row)
          for column, row in zip(columns, feature_summary, strict=True)}
    kendall = values(feature, "kendalltau-correlation")

    e2_raw = load("attn_uniform_weights_attn")
    groups = {label: [] for label in BINS}
    for row in e2_raw:
        maximum = float(row["max-attn"])
        if not 0 <= maximum <= 1 or row["attnX"] != BINS[min(3, math.floor(4 * maximum))]:
            raise ValueError("Archived maximum-attention bin differs from its stored maximum")
        groups[row["attnX"]].append(row)
    max_summary = {row[""]: row for row in load("attn_uniform_weights_attn_summary")}
    if set(max_summary) != {f"JSD for attn: {label}" for label, rows in groups.items() if rows}:
        raise ValueError("Archived Figure 5 bins differ from the summary")
    e2_bins = [{"label": label, "count": len(rows), "jsd_quantiles":
                verify_quantiles(values(rows, "JSD"), max_summary[f"JSD for attn: {label}"]) if rows else None}
               for label, rows in groups.items()]

    models = load("attn_uniform_weights_jsd_tvd")
    if [row["model-name"] for row in models] != [f"{arm}-{i}" for arm in ("seed", "uniform") for i in range(5)]:
        raise ValueError("Unexpected archived E2 model names")
    model_summary = {(row["type"], row[""]): row for row in load("attn_uniform_weights_jsd_tvd_summary")}
    metrics = ("JSD", "TVD", "cosine")
    if set(model_summary) != {(arm, metric) for arm in ("seed", "uniform") for metric in metrics}:
        raise ValueError("Unexpected archived E2 model summary groups")
    e2_models = {}
    for arm in ("seed", "uniform"):
        arm_rows = [row for row in models if row["model-name"].startswith(arm + "-")]
        for metric in metrics:
            series = values(arm_rows, metric)
            e2_models.setdefault(arm, {})[metric] = {"mean": mean(series), "quantiles":
                                                     verify_quantiles(series, model_summary[arm, metric])}

    masking = load("attn_masking")
    tvd = values(masking, "TVD")
    masking_summary, = load("attn_masking_summary")
    if len(tvd) != len(masking) or masking_summary[""] != "TVD":
        raise ValueError("Unexpected archived E3 masking rows")
    e3 = {"rows": len(tvd), "mean_tvd": mean(tvd), "quantiles": verify_quantiles(tvd, masking_summary)}

    return {"csvs": members, "E1": {"rows": len(feature), "kendall_valid": len(kendall),
                                     "kendall_mean": mean(kendall), "quantiles": e1},
            "E2": {"max_attention_rows": len(e2_raw), "bins": e2_bins, "models": e2_models}, "E3": e3}


def audit(path):
    digest = file_hash(path)
    if digest != ARCHIVE_SHA256:
        raise ValueError("Archive SHA-256 does not match the verified author supplement")
    with ZipFile(path) as archive:
        suffix = "/metrics/attn_feature_importance.csv"
        folders = sorted(name.removesuffix("/attn_feature_importance.csv") for name in archive.namelist()
                         if name.startswith(ROOT) and name.endswith(suffix))
        if len(set(folders)) != 12 or len(folders) != 12:
            raise ValueError("Expected twelve distinct archived preliminary-study runs")
        runs = {folder.split("/")[-2].removeprefix("training_"): audit_log(archive, folder) for folder in folders}
    return {"status": "verified", "scope": "archived CSV consistency", "archive_sha256": digest, "runs": runs}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    report = audit(args.archive)
    write_json(args.output, report)
    print(json.dumps({"status": report["status"], "runs": len(report["runs"]),
                      "csvs": sum(len(run["csvs"]) for run in report["runs"].values())}))
