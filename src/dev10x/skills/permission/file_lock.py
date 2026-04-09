from __future__ import annotations

import fcntl
import json
import os
import tempfile
from collections.abc import Generator
from contextlib import contextmanager
from pathlib import Path
from typing import Any


@contextmanager
def locked_json_update(path: Path) -> Generator[dict[str, Any], None, None]:
    path.parent.mkdir(parents=True, exist_ok=True)
    lock_path = path.with_suffix(".lock")
    lock_fd = os.open(str(lock_path), os.O_CREAT | os.O_RDWR)
    try:
        fcntl.flock(lock_fd, fcntl.LOCK_EX)
        if path.exists():
            data = json.loads(path.read_text())
        else:
            data = {}
        yield data
        fd, tmp = tempfile.mkstemp(
            dir=str(path.parent),
            suffix=".tmp",
        )
        try:
            os.write(fd, (json.dumps(data, indent=2) + "\n").encode())
            os.fsync(fd)
            os.close(fd)
            os.rename(tmp, str(path))
        except BaseException:
            os.close(fd)
            os.unlink(tmp)
            raise
    finally:
        fcntl.flock(lock_fd, fcntl.LOCK_UN)
        os.close(lock_fd)
        try:
            os.unlink(str(lock_path))
        except FileNotFoundError:
            pass
