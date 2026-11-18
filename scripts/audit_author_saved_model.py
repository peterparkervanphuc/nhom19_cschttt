"""Replay Table 2 checkpoints in the separate author CPU environment."""

import argparse
import hashlib
import json
import lzma
import pickletools
import platform
import subprocess
import sys
import tempfile
from collections import Counter
from pathlib import Path, PureWindowsPath
from xml.etree import ElementTree
from zipfile import ZipFile

import keras
import numpy as np
import sklearn
import tensorflow as tf
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score


ARCHIVE_SHA256 = "b1b88b2d7797fbe3369dccc5c4fe8d9a96af5d52293954279d4bab2f0bcc169e"
AUTHOR_COMMIT = "494b315a555e713bdd61f0edd7d033c31d5850bf"
ARCHIVED_PREFIX_COUNTS = {
    "bpic12_GPU": 75104,
    "bpic12_o_GPU": 7681,
    "bpic12_w_GPU": 48335,
    "bpic12_wc_GPU": 18923,
    "bpic13_closed_problems_GPU": 1486,
    "bpic13_incidents_GPU": 17580,
    "helpdesk_GPU": 5025,
    "sepsis_GPU": 4154,
    "complex_model": 21462,
    "long_dist_dep": 1944,
    "looped_and": 10941,
    "sequence": 3300,
}


def archive_hash(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def vocabulary(archive, model_directory, name):
    plain = lzma.decompress(archive.read(f"{model_directory}/dicts/{name}.xz"))
    structure = {"PROTO", "EMPTY_DICT", "BINPUT", "MARK", "SETITEMS", "STOP"}
    fields = []
    for opcode, value, _ in pickletools.genops(plain):
        if opcode.name in {"BINUNICODE", "BININT1"}:
            fields.append(value)
        elif opcode.name not in structure:
            raise ValueError("Unexpected archived vocabulary opcode")
    keys, indices = fields[::2], fields[1::2]
    if (len(keys) != len(indices) or len(keys) != len(set(keys))
            or not all(isinstance(key, str) for key in keys)
            or set(indices) != set(range(len(keys)))):
        raise ValueError("Invalid archived vocabulary")
    return dict(zip(keys, indices))


def traces(archive, filename):
    with archive.open(filename) as stream:
        elements = ElementTree.iterparse(stream, events=("start", "end"))
        _, root = next(elements)
        namespace = root.tag.split("}")[0] + "}" if root.tag.startswith("{") else ""
        activity = f"{namespace}string[@key='concept:name']"
        names = set()
        for event_type, trace in elements:
            if event_type != "end" or trace.tag != namespace + "trace":
                continue
            name = trace.find(activity).attrib["value"]
            if name in names:
                raise ValueError("Duplicate archived test case")
            names.add(name)
            labels = [event.find(activity).attrib["value"] for event in trace.findall(namespace + "event")]
            if not labels:
                raise ValueError("Empty archived source trace")
            root.remove(trace)
            yield name, labels


def aligned_cases(archive, prefix_member):
    suffix_member = prefix_member[:-len("test_pref.xes")] + "test_suf.xes"
    if suffix_member in archive.namelist():
        suffix_targets = {name: labels[0] for name, labels in traces(archive, suffix_member)}
        for name, labels in traces(archive, prefix_member):
            yield name, labels, suffix_targets.pop(name)
        if suffix_targets:
            raise ValueError("Unmatched archived suffix samples")
    else:
        test_member = prefix_member[:-len("test_pref.xes")] + "test.xes"
        test = [labels for _, labels in traces(archive, test_member)]
        for name, labels in traces(archive, prefix_member):
            kind, case_index, prefix_length = name.split("_")
            index, length = int(case_index), int(prefix_length)
            if (kind != "Case" or not 0 <= index < len(test) or length != len(labels)
                    or not 0 < length < len(test[index]) or labels != test[index][:length]):
                raise ValueError(f"Archived prefix does not match its source case: {name}")
            yield name, labels, test[index][length]


def predictive_metrics(targets, predictions):
    values = {"accuracy": accuracy_score(targets, predictions)}
    for average in ("micro", "macro", "weighted"):
        for name, metric in (("precision", precision_score), ("recall", recall_score), ("f1", f1_score)):
            values[f"{name}_{average}"] = metric(targets, predictions, average=average, zero_division=0)
    return values


def relabel_upper_bound(targets, predictions):
    counts = {}
    for target, prediction in zip(targets, predictions):
        counts.setdefault(prediction, Counter())[target] += 1
    return sum(max(column.values()) for column in counts.values()) / len(targets)


def audit(archive_path, run, loader, author_root=None):
    if archive_hash(archive_path) != ARCHIVE_SHA256:
        raise ValueError("The author archive differs from the verified supplement")
    if (platform.python_version(), tf.__version__, keras.__version__) != ("3.7.12", "2.6.5", "2.6.0"):
        raise ValueError("Use the pinned Python, TensorFlow and Keras diagnostic environment")
    tf.config.set_visible_devices([], "GPU")
    tf.config.threading.set_inter_op_parallelism_threads(1)
    tf.config.threading.set_intra_op_parallelism_threads(1)
    custom_objects = None
    if loader == "keras-predict":
        author_root = author_root.resolve()
        git = ["git", "-C", str(author_root)]
        if (subprocess.check_output(git + ["rev-parse", "HEAD"], text=True).strip() != AUTHOR_COMMIT
                or subprocess.check_output(git + ["status", "--porcelain", "--untracked-files=no"], text=True)):
            raise ValueError("Keras predict replay requires the clean, pinned author source")
        sys.dont_write_bytecode = True
        sys.path.insert(0, str(author_root))
        from processtransformer.models.transformer import Transformer
        custom_objects = {"Transformer": Transformer}
    model_directory = f"Supplementary_Material/Trained_Models/training_{run}"
    with ZipFile(archive_path) as archive, tempfile.TemporaryDirectory() as temp:
        config_member = f"{model_directory}/exp_{run}.json"
        if config_member not in archive.namelist():
            config_member, = [name for name in archive.namelist()
                              if name.rpartition("/")[0] == model_directory
                              and name.rpartition("/")[2].startswith("exp_") and name.endswith(".json")]
        config = json.loads(archive.read(config_member))
        legacy_path = PureWindowsPath(config["data_source"]["test_data"])
        if legacy_path.name != "test_pref.xes":
            raise ValueError("Archived evaluation no longer selects the prefix file")
        ending = "/" + "/".join(legacy_path.parts[-3:])
        prefix_member, = [name for name in archive.namelist() if name.endswith(ending)]
        expected = json.loads(archive.read(f"{model_directory}/metrics.json"))
        inputs = vocabulary(archive, model_directory, "x_word_dict")
        labels = vocabulary(archive, model_directory, "y_word_dict")
        inverse = {index: label for label, index in labels.items()}
        if inputs.get("[PAD]") != 0:
            raise ValueError("Archived padding token mismatch")
        files = {}
        for name in ("saved_model.pb", "keras_metadata.pb", "variables/variables.index",
                     "variables/variables.data-00000-of-00001"):
            path = Path(temp) / name
            path.parent.mkdir(exist_ok=True)
            data = archive.read(f"{model_directory}/model/model/{name}")
            path.write_bytes(data)
            files[name] = hashlib.sha256(data).hexdigest()
        if loader in {"keras", "keras-predict"}:
            model = tf.keras.models.load_model(temp, compile=False, custom_objects=custom_objects)
            width = int(model.max_case_length.numpy())
            dtype = tf.as_dtype(model.dtype)
        else:
            model = tf.saved_model.load(temp)
            predictor = model.signatures["serving_default"]
            _, named_inputs = predictor.structured_input_signature
            param, spec = next(iter(named_inputs.items()))
            if len(named_inputs) != 1 or spec.shape.rank != 2:
                raise ValueError("Unexpected SavedModel input signature")
            width = spec.shape[1] or int(model.max_case_length.numpy())
            dtype = spec.dtype

        def predict(sequences, margins):
            padded = tf.keras.preprocessing.sequence.pad_sequences(
                [[inputs[label] for label in sequence] for sequence in sequences], maxlen=width
            )
            tensor = tf.convert_to_tensor(padded, dtype=dtype)
            if loader == "keras-predict":
                logits = model.predict(padded, verbose=0)
            elif loader == "keras":
                logits = model(tensor, training=False).numpy()
            else:
                logits, = predictor(**{param: tensor}).values()
                logits = logits.numpy()
            if logits.ndim != 2 or logits.shape[1] != len(labels) or not np.isfinite(logits).all():
                raise ValueError("Unexpected SavedModel output shape")
            if len(labels) >= 2:
                top_two = np.sort(np.partition(logits, -2, axis=1)[:, -2:], axis=1).astype(np.float64)
                margins.extend(top_two[:, 1] - top_two[:, 0])
            return [inverse[int(index)] for index in np.argmax(logits, axis=1)]

        last_predictions, next_predictions = [], []
        last_margins, next_margins = [], []
        last_targets, next_targets, batch = [], [], []
        cases = aligned_cases(archive, prefix_member)
        if loader == "keras-predict":
            cases = sorted(cases, key=lambda row: row[0])
        for _, prefix, next_target in cases:
            last_targets.append(prefix[-1])
            next_targets.append(next_target)
            batch.append(prefix)
            if len(batch) == 32 and loader != "keras-predict":
                last_predictions.extend(predict([sequence[:-1] for sequence in batch], last_margins))
                next_predictions.extend(predict(batch, next_margins))
                batch.clear()
        if batch:
            last_predictions.extend(predict([sequence[:-1] for sequence in batch], last_margins))
            next_predictions.extend(predict(batch, next_margins))
        if len(last_targets) != ARCHIVED_PREFIX_COUNTS[run]:
            raise ValueError("Archived evaluation population mismatch")
        last_metrics = predictive_metrics(last_targets, last_predictions)
        next_metrics = predictive_metrics(next_targets, next_predictions)
        suffix_member = prefix_member[:-len("test_pref.xes")] + "test_suf.xes"
        next_target_source = suffix_member if suffix_member in archive.namelist() else "Case_i_j verified against test.xes"
    fully_masked = tf.keras.layers.Softmax()(tf.constant([[.5, .2, 1.]], tf.float32),
                                            mask=tf.constant([[False, False, False]]))
    return {"scope": "archived inference replay on CPU", "archive_sha256": ARCHIVE_SHA256,
            "run": run, "loader": loader, "config_member": config_member, "prefix_member": prefix_member,
            "author_source_commit": AUTHOR_COMMIT if loader == "keras-predict" else None,
            "next_target_source": next_target_source,
            "model_files": files, "python": platform.python_version(), "tensorflow": tf.__version__,
            "keras": keras.__version__, "sklearn": sklearn.__version__, "numpy": np.__version__,
            "test_prefixes": len(last_targets), "padding_width": width, "input_dtype": dtype.name,
            "last_prefix_predictions": dict(Counter(last_predictions)),
            "first_suffix_predictions": dict(Counter(next_predictions)),
            "last_prefix_target_metrics": last_metrics, "first_suffix_target_metrics": next_metrics,
            "last_prefix_relabel_accuracy_upper_bound": relabel_upper_bound(last_targets, last_predictions),
            "first_suffix_relabel_accuracy_upper_bound": relabel_upper_bound(next_targets, next_predictions),
            "small_top_two_logit_margins": {target: {str(limit): int(np.count_nonzero(np.asarray(values) <= limit))
                                                    for limit in (0., 1e-7, 1e-5, .001, .01)}
                                           for target, values in (("last_prefix", last_margins),
                                                                  ("first_suffix", next_margins))},
            "archived_metrics": expected,
            "matches_archived_metrics": set(last_metrics) == set(expected)
            and all(abs(value - expected[key]) < 1e-12 for key, value in last_metrics.items()),
            "fully_masked_softmax_row": fully_masked.numpy()[0].tolist()}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--run", choices=ARCHIVED_PREFIX_COUNTS, default="bpic13_closed_problems_GPU")
    parser.add_argument("--loader", choices=("signature", "keras", "keras-predict"), default="signature")
    parser.add_argument("--author-root", type=Path, help="Required for the isolated keras-predict comparison")
    args = parser.parse_args()
    if args.loader == "keras-predict" and args.author_root is None:
        parser.error("--loader keras-predict requires --author-root")
    if args.output.exists():
        raise FileExistsError(args.output)
    report = audit(args.archive, args.run, args.loader, args.author_root)
    with args.output.open("x", encoding="utf-8") as destination:
        json.dump(report, destination, indent=2, allow_nan=False)
        destination.write("\n")
    print(json.dumps(report))
