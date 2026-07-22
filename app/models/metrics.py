from pydantic import BaseModel, Field

from app.models.contact import Sentiment


class MetricsResponse(BaseModel):
    total_contacts: int = Field(..., examples=[42])
    ai_success_count: int = Field(..., examples=[38])
    ai_fallback_count: int = Field(..., examples=[4])
    sentiment_distribution: dict[Sentiment, int]
