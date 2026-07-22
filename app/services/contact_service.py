import logging

from app.models.contact import ContactRecord, ContactRequest, ContactResponse
from app.repositories.contact_repository import ContactRepository
from app.services.ai_service import AIService
from app.services.email_service import EmailService
from app.services.metrics_service import MetricsService

logger = logging.getLogger(__name__)


class ContactService:
    def __init__(
        self,
        contact_repository: ContactRepository,
        ai_service: AIService,
        email_service: EmailService,
        metrics_service: MetricsService,
    ) -> None:
        self.contact_repository = contact_repository
        self.ai_service = ai_service
        self.email_service = email_service
        self.metrics_service = metrics_service

    async def create_contact(self, payload: ContactRequest) -> ContactResponse:
        ai_analysis = await self.ai_service.analyze_contact(payload)

        contact = ContactRecord(
            name=payload.name,
            phone=payload.phone,
            email=payload.email,
            comment=payload.comment,
            ai_analysis=ai_analysis,
        )

        saved_contact = self.contact_repository.create(contact)

        await self.email_service.send_owner_notification(saved_contact)
        await self.email_service.send_user_copy(saved_contact)

        self.metrics_service.increment_contact_metrics(ai_analysis)

        logger.info(
            "Contact request processed successfully | contact_id=%s | ai_available=%s",
            saved_contact.id,
            ai_analysis.is_available,
        )

        return ContactResponse(
            id=saved_contact.id,
            status="accepted",
            message="Contact request has been accepted.",
            ai_analysis=ai_analysis,
        )
