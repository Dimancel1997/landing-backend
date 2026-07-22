from functools import lru_cache

from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.session import get_db
from app.repositories.contact_repository import ContactRepository
from app.repositories.metrics_repository import MetricsRepository
from app.repositories.rate_limit_repository import RateLimitRepository
from app.services.ai_service import AIService
from app.services.contact_service import ContactService
from app.services.email_service import EmailService
from app.services.metrics_service import MetricsService
from app.services.rate_limit_service import RateLimitService


def get_contact_repository(db: Session = Depends(get_db)) -> ContactRepository:
    return ContactRepository(db)


def get_metrics_repository(db: Session = Depends(get_db)) -> MetricsRepository:
    return MetricsRepository(db)


def get_rate_limit_repository(db: Session = Depends(get_db)) -> RateLimitRepository:
    return RateLimitRepository(db)


@lru_cache
def get_ai_service() -> AIService:
    return AIService(get_settings())


@lru_cache
def get_email_service() -> EmailService:
    return EmailService(get_settings())


def get_metrics_service(
    metrics_repo: MetricsRepository = Depends(get_metrics_repository),
) -> MetricsService:
    return MetricsService(metrics_repo)


def get_rate_limit_service(
    rate_limit_repo: RateLimitRepository = Depends(get_rate_limit_repository),
) -> RateLimitService:
    settings = get_settings()
    return RateLimitService(
        rate_limit_repo,
        max_requests=settings.rate_limit_max_requests,
        window_seconds=settings.rate_limit_window_seconds,
    )


def get_contact_service(
    contact_repo: ContactRepository = Depends(get_contact_repository),
    ai_service: AIService = Depends(get_ai_service),
    email_service: EmailService = Depends(get_email_service),
    metrics_service: MetricsService = Depends(get_metrics_service),
) -> ContactService:
    return ContactService(
        contact_repository=contact_repo,
        ai_service=ai_service,
        email_service=email_service,
        metrics_service=metrics_service,
    )
