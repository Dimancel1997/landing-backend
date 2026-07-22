from pathlib import Path
from typing import Any

from app.repositories.json_repository import JsonRepository


class RateLimitRepository:
    def __init__(self, storage_dir: Path) -> None:
        self.repository = JsonRepository(
            file_path=storage_dir / "rate_limits.json",
            default_data={},
        )

    def get_all(self) -> dict[str, Any]:
        return self.repository.read()

    def save_all(self, data: dict[str, Any]) -> None:
        self.repository.write(data)
