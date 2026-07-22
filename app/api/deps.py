from functools import lru_cache

from app.core.config import get_settings
from app.repositories.contact_repository import ContactRepository
from app.repositories.metrics_repository import MetricsRepository
from app.repositories.rate_limit_repository import RateLimitRepository
from app.services.ai_service import AIService
from app.services.contact_service import ContactService
from app.services.email_service import EmailService
from app.services.metrics_service import MetricsService
from app.services.rate_limit_service import RateLimitService


@lru_cache
def get_contact_repository() -> ContactRepository:
    return ContactRepository(get_settings().storage_dir)


@lru_cache
def get_metrics_repository() -> MetricsRepository:
    return MetricsRepository(get_settings().storage_dir)


@lru_cache
def get_rate_limit_repository() -> RateLimitRepository:
    return RateLimitRepository(get_settings().storage_dir)


@lru_cache
def get_ai_service() -> AIService:
    return AIService(get_settings())


@lru_cache
def get_email_service() -> EmailService:
    return EmailService(get_settings())


@lru_cache
def get_metrics_service() -> MetricsService:
    return MetricsService(get_metrics_repository())


@lru_cache
def get_rate_limit_service() -> RateLimitService:
    settings = get_settings()
    return RateLimitService(
        get_rate_limit_repository(),
        max_requests=settings.rate_limit_max_requests,
        window_seconds=settings.rate_limit_window_seconds,
    )


@lru_cache
def get_contact_service() -> ContactService:
    return ContactService(
        contact_repository=get_contact_repository(),
        ai_service=get_ai_service(),
        email_service=get_email_service(),
        metrics_service=get_metrics_service(),
    )
