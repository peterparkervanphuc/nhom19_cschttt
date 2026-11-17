"""Replay the archived BPIC13-CP SavedModel in the separate author CPU environment."""

import argparse
import hashlib
import json
import lzma
import pickletools
import platform
import tempfile
from collections import Counter
from pathlib import Path
from xml.etree import ElementTree
from zipfile import ZipFile

import keras
import numpy as np
import sklearn
import tensorflow as tf
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score


ARCHIVE_SHA256 = "b1b88b2d7797fbe3369dccc5c4fe8d9a96af5d52293954279d4bab2f0bcc169e"
RUN = "Supplementary_Material/Trained_Models/training_bpic13_closed_problems_GPU"
SPLIT = "Supplementary_Material/Real_Life_Event_Logs/bpic2013_closed_problems/exp_bpic13_closed_problems"


def archive_hash(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def vocabulary(archive, name):
    plain = lzma.decompress(archive.read(f"{RUN}/dicts/{name}.xz"))
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
    with archive.open(f"{SPLIT}/{filename}") as stream:
        root = ElementTree.parse(stream).getroot()
    namespace = {"xes": root.tag.split("}")[0][1:]} if root.tag.startswith("{") else None
    prefix = "xes:" if namespace else ""
    result = {}
    for trace in root.findall(prefix + "trace", namespace):
        name = trace.find(f"{prefix}string[@key='concept:name']", namespace).attrib["value"]
        if name in result:
            raise ValueError("Duplicate archived test case")
        labels = [event.find(f"{prefix}string[@key='concept:name']", namespace).attrib["value"]
                  for event in trace.findall(prefix + "event", namespace)]
        if not labels:
            raise ValueError("Empty archived source trace")
        result[name] = labels
    return result


def predictive_metrics(targets, predictions):
    values = {"accuracy": accuracy_score(targets, predictions)}
    for average in ("micro", "macro", "weighted"):
        for name, metric in (("precision", precision_score), ("recall", recall_score), ("f1", f1_score)):
            values[f"{name}_{average}"] = metric(targets, predictions, average=average, zero_division=0)
    return values


def audit(archive_path):
    if archive_hash(archive_path) != ARCHIVE_SHA256:
        raise ValueError("The author archive differs from the verified supplement")
    if (platform.python_version(), tf.__version__, keras.__version__) != ("3.7.12", "2.6.5", "2.6.0"):
        raise ValueError("Use the pinned Python, TensorFlow and Keras diagnostic environment")
    tf.config.set_visible_devices([], "GPU")
    tf.config.threading.set_inter_op_parallelism_threads(1)
    tf.config.threading.set_intra_op_parallelism_threads(1)
    with ZipFile(archive_path) as archive, tempfile.TemporaryDirectory() as temp:
        config = json.loads(archive.read(f"{RUN}/exp_bpic13_closed_problems_GPU.json"))
        if not config["data_source"]["test_data"].endswith("test_pref.xes"):
            raise ValueError("Archived evaluation no longer selects the prefix file")
        expected = json.loads(archive.read(f"{RUN}/metrics.json"))
        inputs, labels = vocabulary(archive, "x_word_dict"), vocabulary(archive, "y_word_dict")
        inverse = {index: label for label, index in labels.items()}
        prefixes, suffixes = traces(archive, "test_pref.xes"), traces(archive, "test_suf.xes")
        if inputs.get("[PAD]") != 0 or prefixes.keys() != suffixes.keys() or len(prefixes) != 1486:
            raise ValueError("Archived evaluation population or padding mismatch")
        files = {}
        for name in ("saved_model.pb", "keras_metadata.pb", "variables/variables.index",
                     "variables/variables.data-00000-of-00001"):
            path = Path(temp) / name
            path.parent.mkdir(exist_ok=True)
            data = archive.read(f"{RUN}/model/model/{name}")
            path.write_bytes(data)
            files[name] = hashlib.sha256(data).hexdigest()
        model = tf.saved_model.load(temp)
        predictor = model.signatures["serving_default"]
        _, named_inputs = predictor.structured_input_signature
        param, spec = next(iter(named_inputs.items()))
        if len(named_inputs) != 1 or spec.shape.rank != 2:
            raise ValueError("Unexpected SavedModel input signature")
        width = spec.shape[1] or int(model.max_case_length.numpy())

        def predict(sequences):
            padded = tf.keras.preprocessing.sequence.pad_sequences(
                [[inputs[label] for label in sequence] for sequence in sequences], maxlen=width
            )
            predictions = []
            for start in range(0, len(padded), 32):
                results = predictor(**{param: tf.convert_to_tensor(padded[start:start + 32], dtype=spec.dtype)})
                logits, = results.values()
                if logits.shape.rank != 2 or logits.shape[1] != len(labels):
                    raise ValueError("Unexpected SavedModel output shape")
                predictions.extend(inverse[int(index)] for index in tf.argmax(logits, axis=1))
            return predictions

        ids = sorted(prefixes)
        last_predictions = predict([prefixes[key][:-1] for key in ids])
        next_predictions = predict([prefixes[key] for key in ids])
        last_metrics = predictive_metrics([prefixes[key][-1] for key in ids], last_predictions)
        next_metrics = predictive_metrics([suffixes[key][0] for key in ids], next_predictions)
    fully_masked = tf.keras.layers.Softmax()(tf.constant([[.5, .2, 1.]], tf.float32),
                                            mask=tf.constant([[False, False, False]]))
    return {"scope": "archived inference replay on CPU", "archive_sha256": ARCHIVE_SHA256,
            "model_files": files, "python": platform.python_version(), "tensorflow": tf.__version__,
            "keras": keras.__version__, "sklearn": sklearn.__version__, "numpy": np.__version__,
            "test_prefixes": len(ids), "padding_width": width, "input_dtype": spec.dtype.name,
            "last_prefix_predictions": dict(Counter(last_predictions)),
            "first_suffix_predictions": dict(Counter(next_predictions)),
            "last_prefix_target_metrics": last_metrics, "first_suffix_target_metrics": next_metrics,
            "archived_metrics": expected,
            "matches_archived_metrics": set(last_metrics) == set(expected)
            and all(abs(value - expected[key]) < 1e-12 for key, value in last_metrics.items()),
            "fully_masked_softmax_row": fully_masked.numpy()[0].tolist()}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    report = audit(args.archive)
    with args.output.open("x", encoding="utf-8") as destination:
        json.dump(report, destination, indent=2, allow_nan=False)
        destination.write("\n")
    print(json.dumps(report))
