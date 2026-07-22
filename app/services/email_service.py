import logging
from datetime import datetime

from app.core.config import Settings
from app.models.contact import ContactRecord

logger = logging.getLogger(__name__)

DEFAULT_USER_REPLY = (
    "Спасибо за обращение! Мы получили вашу заявку и скоро свяжемся с вами."
)


class EmailService:
    """
    Email delivery imitation.

    In production this service can be replaced with SMTP, SendGrid,
    Amazon SES or any other provider without changing business logic.
    """

    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    async def send_owner_notification(self, contact: ContactRecord) -> None:
        logger.info(
            "EMAIL_TO_OWNER | to=%s | subject=%s | contact_id=%s | sent_at=%s",
            self.settings.owner_email,
            "New landing contact request",
            contact.id,
            datetime.utcnow().isoformat(),
        )
        logger.info(
            "EMAIL_TO_OWNER_BODY | name=%s | phone=%s | email=%s | comment=%s | "
            "sentiment=%s | category=%s | ai_reply=%s",
            contact.name,
            contact.phone,
            contact.email,
            contact.comment,
            contact.ai_analysis.sentiment,
            contact.ai_analysis.category,
            contact.ai_analysis.suggested_reply,
        )

    async def send_user_copy(self, contact: ContactRecord) -> None:
        logger.info(
            "EMAIL_TO_USER | to=%s | subject=%s | contact_id=%s | sent_at=%s",
            contact.email,
            "We received your request",
            contact.id,
            datetime.utcnow().isoformat(),
        )
        logger.info(
            "EMAIL_TO_USER_BODY | name=%s | message=%s",
            contact.name,
            contact.ai_analysis.suggested_reply or DEFAULT_USER_REPLY,
        )
