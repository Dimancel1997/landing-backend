from fastapi import APIRouter, Depends, Request, status

from app.api.deps import get_contact_service, get_rate_limit_service
from app.models.contact import ContactRequest, ContactResponse
from app.services.contact_service import ContactService
from app.services.rate_limit_service import RateLimitService

router = APIRouter()


@router.post(
    "/contact",
    response_model=ContactResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_contact(
    payload: ContactRequest,
    request: Request,
    contact_service: ContactService = Depends(get_contact_service),
    rate_limit_service: RateLimitService = Depends(get_rate_limit_service),
) -> ContactResponse:
    client_host = request.client.host if request.client else "unknown"

    rate_limit_service.check(client_host)

    return await contact_service.create_contact(payload)
