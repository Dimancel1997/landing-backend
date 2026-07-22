import json
import logging
import threading
from pathlib import Path
from typing import Any

from app.core.exceptions import StorageException

logger = logging.getLogger(__name__)


class JsonRepository:
    """Small thread-safe JSON file storage helper."""

    _lock = threading.Lock()

    def __init__(self, file_path: Path, default_data: Any) -> None:
        self.file_path = file_path
        self.default_data = default_data
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        self._ensure_file_exists()

    def _ensure_file_exists(self) -> None:
        if not self.file_path.exists():
            self.write(self.default_data)

    def read(self) -> Any:
        with self._lock:
            try:
                if not self.file_path.exists():
                    self.file_path.write_text(
                        json.dumps(self.default_data, ensure_ascii=False, indent=2),
                        encoding="utf-8",
                    )
                return json.loads(self.file_path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError) as exc:
                logger.exception("Cannot read storage file: %s", self.file_path)
                raise StorageException("Cannot read storage file.") from exc

    def write(self, data: Any) -> None:
        with self._lock:
            try:
                self.file_path.write_text(
                    json.dumps(data, ensure_ascii=False, indent=2, default=str),
                    encoding="utf-8",
                )
            except OSError as exc:
                logger.exception("Cannot write storage file: %s", self.file_path)
                raise StorageException("Cannot write storage file.") from exc
