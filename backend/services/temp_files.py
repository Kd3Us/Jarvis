"""Temporary file management with guaranteed cleanup (JAR-20).

Temporary files may hold personal data (voice, photos), so every file
created here is removed after use, even when an error occurs.
"""

from __future__ import annotations

import os
import tempfile
import threading
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Self


class TempFileManager:
    def __init__(self, prefix: str = "jarvis_") -> None:
        self._prefix = prefix
        self._paths: set[Path] = set()
        self._lock = threading.Lock()

    def create(self, data: bytes = b"", suffix: str = "") -> Path:
        fd, name = tempfile.mkstemp(prefix=self._prefix, suffix=suffix)
        path = Path(name)
        try:
            with os.fdopen(fd, "wb") as file:
                file.write(data)
        except BaseException:
            path.unlink(missing_ok=True)
            raise
        with self._lock:
            self._paths.add(path)
        return path

    def remove(self, path: str | Path) -> None:
        path = Path(path)
        with self._lock:
            if path not in self._paths:
                return  # not ours: never delete it
        try:
            path.unlink(missing_ok=True)
        except OSError:
            return  # keep it tracked so cleanup() retries
        with self._lock:
            self._paths.discard(path)

    @contextmanager
    def temp_file(self, data: bytes = b"", suffix: str = "") -> Iterator[Path]:
        path = self.create(data, suffix)
        try:
            yield path
        finally:
            self.remove(path)

    def cleanup(self) -> None:
        with self._lock:
            paths = list(self._paths)
        for path in paths:
            self.remove(path)

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *exc_info) -> None:
        self.cleanup()
