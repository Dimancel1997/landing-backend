from typing import Any
from sqlalchemy.orm import Session

from app.db.models import MetricsDB
from app.models.contact import Sentiment


class MetricsRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def _get_or_create(self) -> MetricsDB:
        metrics = self.db.query(MetricsDB).filter(MetricsDB.id == 1).first()
        if not metrics:
            metrics = MetricsDB(id=1)
            self.db.add(metrics)
            self.db.commit()
            self.db.refresh(metrics)
        return metrics

    def get(self) -> dict[str, Any]:
        metrics = self._get_or_create()
        return {
            "total_contacts": metrics.total_contacts,
            "ai_success_count": metrics.ai_success_count,
            "ai_fallback_count": metrics.ai_fallback_count,
            "sentiment_distribution": {
                Sentiment.positive.value: metrics.sentiment_positive,
                Sentiment.neutral.value: metrics.sentiment_neutral,
                Sentiment.negative.value: metrics.sentiment_negative,
                Sentiment.unknown.value: metrics.sentiment_unknown,
            },
        }

    def save(self, metrics_data: dict[str, Any]) -> None:
        metrics = self._get_or_create()
        metrics.total_contacts = metrics_data.get("total_contacts", 0)
        metrics.ai_success_count = metrics_data.get("ai_success_count", 0)
        metrics.ai_fallback_count = metrics_data.get("ai_fallback_count", 0)

        sentiment_dist = metrics_data.get("sentiment_distribution", {})
        metrics.sentiment_positive = sentiment_dist.get(Sentiment.positive.value, 0)
        metrics.sentiment_neutral = sentiment_dist.get(Sentiment.neutral.value, 0)
        metrics.sentiment_negative = sentiment_dist.get(Sentiment.negative.value, 0)
        metrics.sentiment_unknown = sentiment_dist.get(Sentiment.unknown.value, 0)

        self.db.commit()
