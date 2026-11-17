"""Render measured E1/E2/E3 artifacts; preserve null and scope information."""

import argparse
import csv
import json
from pathlib import Path
import sqlite3

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from nhom19_process_xai.artifacts import read_sealed, seal, write_json
from nhom19_process_xai.data.pipeline import file_hash


def render(e1_path: Path, e2_path: Path, e3_path: Path, output: Path):
    if output.exists():
        raise FileExistsError("Use a fresh figure output directory")
    e1, e2, e3 = [read_sealed(path) for path in (e1_path, e2_path, e3_path)]
    if any(item["status"] != "completed" for item in (e1, e2, e3)):
        raise ValueError("Primary figures require completed study artifacts")
    database = e3_path.parent / e3["records_database"]
    if file_hash(database) != e3["records_sha256"]:
        raise ValueError("E3 database checksum mismatch")
    output.mkdir(parents=True)
    files = []

    def save(figure, name):
        figure.tight_layout()
        for extension in ("png", "svg"):
            path = output / f"{name}.{extension}"
            figure.savefig(path, dpi=160, bbox_inches="tight")
            files.append(path)
        plt.close(figure)

    values = [row["tau_b"] for row in e1["records"] if row["tau_b"] is not None]
    figure, axes = plt.subplots(figsize=(7, 4.5))
    axes.hist(values, bins=np.linspace(-1, 1, 21), color="#245a83", edgecolor="white")
    axes.set(xlim=(-1, 1), xlabel="Kendall tau-b", ylabel="Number of valid prefixes",
             title=f"E1 · {e1_path.parent.name}\n{len(values):,}/{len(e1['records']):,} valid; undefined values excluded")
    save(figure, "E1-tau")

    figure, axes = plt.subplots(figsize=(7, 4.5))
    for arm, color, marker in [("BASE", "#245a83", "o"), (e2["profile"], "#a65522", "^")]:
        pairs = [pair for pair in e2["pairs"] if pair["arm"] == arm]
        axes.scatter([pair["jsd"]["mean"] for pair in pairs], [pair["tvd"]["mean"] for pair in pairs],
                     c=color, marker=marker, s=55, label=arm)
    axes.set(xlim=(0, None), ylim=(0, None), xlabel="Mean attention JSD (natural logarithm)",
             ylabel="Mean prediction TVD", title=f"E2 · {e2_path.parent.name}\nOne point per seed; all test prefixes; descriptive only")
    axes.legend(frameon=False)
    save(figure, "E2-paired-means")
    pair_table = output / "E2-paired-means.csv"
    with pair_table.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream)
        writer.writerow(["arm", "seed", "completed_prefixes", "attention_jsd_mean", "prediction_tvd_mean"])
        for pair in e2["pairs"]:
            writer.writerow([pair["arm"], pair["seed"], pair["completed_prefixes"],
                             pair["jsd"]["mean"], pair["tvd"]["mean"]])
    files.append(pair_table)

    values = []
    with sqlite3.connect(database.resolve().as_uri() + "?mode=ro", uri=True) as connection:
        for (payload,) in connection.execute("SELECT payload FROM records ORDER BY prefix_id"):
            row = json.loads(payload)["payload"]
            values.append(row["prediction_tvd"]["mean"])
    if len(values) != e3["expected_prefixes"]:
        raise ValueError("E3 figure population differs from scheduled prefixes")
    figure, axes = plt.subplots(figsize=(7, 4.5))
    axes.hist(values, bins=np.linspace(0, 1, 31), color="#245a83", edgecolor="white")
    axes.set(xlim=(0, 1), xlabel="Mean prediction TVD per prefix (INPUT vs SCORE)",
             ylabel="Number of prefixes", title=f"{e3['profile']} · {e3_path.parent.name}\nAll {len(values):,} prefixes; equal prefix weighting")
    save(figure, "E3-prefix-TVD")
    manifest = {"status": "completed", "interpretation": "Measured independent runs; no statistical significance claim",
                "renderer_sha256": file_hash(Path(__file__)),
                "sources": {str(path.resolve()): file_hash(path) for path in (e1_path, e2_path, e3_path)},
                "files": {path.name: file_hash(path) for path in files}}
    write_json(output / "manifest.json", seal(manifest))
    return manifest


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    for name in ("e1", "e2", "e3", "output"):
        parser.add_argument("--" + name, type=Path, required=True)
    args = parser.parse_args()
    result = render(args.e1, args.e2, args.e3, args.output)
    print(json.dumps({"status": result["status"], "files": len(result["files"])}))
