"""Compare completed independent studies with the verified author CSV archive."""

import argparse
import csv
import json
from pathlib import Path
from statistics import mean, median

from nhom19_process_xai.artifacts import read_sealed, seal, write_json
from nhom19_process_xai.data.pipeline import file_hash


LOGS = {
    "bpic12-v1": "bpic12_GPU", "bpic12-o-v1": "bpic12_o_GPU",
    "bpic12-w-v1": "bpic12_w_GPU", "bpic12-wc-v1": "bpic12_wc_GPU",
    "bpic13-cp-v1": "bpic13_closed_problems_GPU", "bpic13-i-v1": "bpic13_incidents_GPU",
    "helpdesk-v1": "helpdesk_GPU", "sepsis-v1": "sepsis_GPU",
    "synthetic-complex-model": "complex_model", "synthetic-long-dist-dep": "long_dist_dep",
    "synthetic-looped-and": "looped_and", "synthetic-sequence": "sequence",
}


def load_audit(path):
    raw = json.loads(path.read_text(encoding="utf-8-sig"))
    return read_sealed(path) if "payload" in raw and "sha256" in raw else raw


def study_path(root, study):
    local = root / f"{study}-stream.json"
    if local.exists():
        return local
    locator = root / f"{study}-location.json"
    if locator.exists():
        external = Path(read_sealed(locator)["manifest"])
        if external.is_file():
            return external
    return local


def compare(artifacts, output):
    if output.exists():
        raise FileExistsError(output)
    archive_path = artifacts / "author-runtime/prestudy-archive-audit.json"
    archive = load_audit(archive_path)
    assert archive["status"] == "verified"
    rows, missing = [], []

    def add(log, experiment, metric, reference, measured, author_n, our_n, path, member):
        difference = measured - reference
        omit_relative = metric == "median_tau_b" or abs(reference) <= 1e-6
        relative = None if omit_relative else difference / abs(reference) * 100
        rows.append({"experiment": experiment, "log": log, "metric": metric,
                     "paper_result": reference, "our_result": measured,
                     "signed_difference": difference, "absolute_difference": abs(difference),
                     "relative_difference_percent": relative,
                     "relative_difference_note": "Omitted for correlations or near-zero references (abs <= 1e-6)" if omit_relative else "Descriptive reference-relative difference; protocols differ",
                     "reproduction_status": "PARTIALLY REPRODUCED; matched historical conditions not established",
                     "reference_kind": "Author supplementary CSV; not an exact number printed in the paper",
                     "author_n": author_n, "our_n": our_n,
                     "our_source": str(path), "our_source_sha256": file_hash(path),
                     "author_member": member["member"], "author_member_sha256": member["sha256"]})

    for log, name in LOGS.items():
        root, author = artifacts / log, archive["runs"][name]
        e1 = next((p for p in [root / "E1-stream.json", root / "E1.json"] if p.exists()), None)
        if e1 is not None:
            result = read_sealed(e1)
            assert result["status"] == "completed"
            values = [r["tau_b"] for r in result["records"] if r["tau_b"] is not None]
            if values:
                add(log, "E1", "median_tau_b", author["E1"]["quantiles"]["kendalltau-correlation"][2],
                    median(values), author["E1"]["kendall_valid"], len(values), e1,
                    author["csvs"]["attn_feature_importance"])
        else:
            missing.append({"log": log, "experiment": "E1", "reason": "No completed primary manifest"})
        e2 = study_path(root, "E2")
        if e2.exists():
            result = read_sealed(e2)
            assert result["status"] == "completed" and result["completed_units"] == result["expected_units"]
            for ours, archived in [("BASE", "seed"), ("E2-FC", "uniform")]:
                pairs = [p for p in result["pairs"] if p["arm"] == ours]
                assert len(pairs) == 5 and all(p["completed_prefixes"] == result["expected_prefixes"] for p in pairs)
                for metric in ["jsd", "tvd"]:
                    add(log, "E2", f"{ours}_five_model_mean_{metric}",
                        author["E2"]["models"][archived][metric.upper()]["mean"],
                        mean(p[metric]["mean"] for p in pairs), 5, 5, e2,
                        author["csvs"]["attn_uniform_weights_jsd_tvd"])
        else:
            missing.append({"log": log, "experiment": "E2", "reason": "No completed primary manifest"})
        e3 = study_path(root, "E3")
        if e3.exists():
            candidates = [folder / f for folder in dict.fromkeys([root, e3.parent])
                          for f in ["e3-attention-reference-audit.json", "e3-occurrence-audit.json",
                                    "e3-record-audit.json"]]
            selected = next((p for p in candidates if p.exists()
                             and "occurrence_weighted_prediction_tvd" in load_audit(p)), None)
            if selected is None:
                raise ValueError(f"Missing verified occurrence-weighted E3 result: {log}")
            audit = load_audit(selected)
            assert audit["status"] == "verified" and audit["manifest_sha256"] == file_hash(e3)
            values = audit["occurrence_weighted_prediction_tvd"]
            for metric, reference in [("mean", author["E3"]["mean_tvd"]), ("median", author["E3"]["quantiles"][2])]:
                add(log, "E3", f"occurrence_{metric}_tvd", reference, values[metric], author["E3"]["rows"],
                    values["n_valid"], selected, author["csvs"]["attn_masking"])
        else:
            missing.append({"log": log, "experiment": "E3", "reason": "No completed primary manifest; external locator may hold a partial run"})

    output.mkdir(parents=True)
    result = {"status": "PARTIALLY COMPLETE", "reference_sha256": file_hash(archive_path),
              "archive_sha256": archive["archive_sha256"], "rows": rows, "missing": missing,
              "interpretation": "Descriptive differences only. Historical split, architecture, initialization, masking and cohort conditions differ; numerical reproduction is not established.",
              "difference_definition": "our - archive; absolute = abs(our - archive); relative = 100*(our-archive)/abs(archive). Ratios of correlations and references with abs <= 1e-6 are omitted as misleading; this reporting rule does not alter experiment metrics."}
    write_json(output / "comparison.json", seal(result))
    with (output / "comparison.csv").open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifacts", type=Path, default=Path("artifacts"))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = compare(args.artifacts, args.output)
    print(json.dumps({"status": result["status"], "comparison_rows": len(result["rows"]), "uncompleted_studies": result["missing"]}))
