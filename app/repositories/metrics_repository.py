from pathlib import Path
from typing import Any

from app.models.contact import Sentiment
from app.repositories.json_repository import JsonRepository

DEFAULT_METRICS = {
    "total_contacts": 0,
    "ai_success_count": 0,
    "ai_fallback_count": 0,
    "sentiment_distribution": {
        Sentiment.positive.value: 0,
        Sentiment.neutral.value: 0,
        Sentiment.negative.value: 0,
        Sentiment.unknown.value: 0,
    },
}


class MetricsRepository:
    def __init__(self, storage_dir: Path) -> None:
        self.repository = JsonRepository(
            file_path=storage_dir / "metrics.json",
            default_data=DEFAULT_METRICS,
        )

    def get(self) -> dict[str, Any]:
        return self.repository.read()

    def save(self, metrics: dict[str, Any]) -> None:
        self.repository.write(metrics)
