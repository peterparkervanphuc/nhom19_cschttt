"""Atomic artifact writes and checksummed envelopes."""

import json
import os
import tempfile
from pathlib import Path
from typing import Any, Callable

from .data.pipeline import fingerprint


def atomic_write(path: Path, writer: Callable[[Path], None]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, name = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    os.close(descriptor)
    temporary = Path(name)
    try:
        writer(temporary)
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def write_json(path: Path, value: Any) -> None:
    content = json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + "\n"
    atomic_write(path, lambda temporary: temporary.write_text(content, encoding="utf-8"))


def seal(value: dict) -> dict:
    return {"payload": value, "sha256": fingerprint(value)}


def read_sealed(path: Path) -> dict:
    envelope = json.loads(path.read_text(encoding="utf-8"))
    if set(envelope) != {"payload", "sha256"} or fingerprint(envelope["payload"]) != envelope["sha256"]:
        raise ValueError(f"Artifact checksum mismatch: {path}")
    return envelope["payload"]
