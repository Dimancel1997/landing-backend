from app.models.contact import AIAnalysis, Sentiment
from app.models.metrics import MetricsResponse
from app.repositories.metrics_repository import MetricsRepository


class MetricsService:
    def __init__(self, metrics_repository: MetricsRepository) -> None:
        self.metrics_repository = metrics_repository

    def increment_contact_metrics(self, ai_analysis: AIAnalysis) -> None:
        metrics = self.metrics_repository.get()

        metrics["total_contacts"] += 1

        if ai_analysis.is_available:
            metrics["ai_success_count"] += 1
        else:
            metrics["ai_fallback_count"] += 1

        sentiment = ai_analysis.sentiment.value
        metrics["sentiment_distribution"][sentiment] = (
            metrics["sentiment_distribution"].get(sentiment, 0) + 1
        )

        self.metrics_repository.save(metrics)

    def get_metrics(self) -> MetricsResponse:
        metrics = self.metrics_repository.get()

        return MetricsResponse(
            total_contacts=metrics["total_contacts"],
            ai_success_count=metrics["ai_success_count"],
            ai_fallback_count=metrics["ai_fallback_count"],
            sentiment_distribution={
                Sentiment(key): value
                for key, value in metrics["sentiment_distribution"].items()
            },
        )
