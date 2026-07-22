from fastapi import APIRouter, Depends

from app.api.deps import get_metrics_service
from app.models.metrics import MetricsResponse
from app.services.metrics_service import MetricsService

router = APIRouter()


@router.get("/metrics", response_model=MetricsResponse)
async def get_metrics(
    metrics_service: MetricsService = Depends(get_metrics_service),
) -> MetricsResponse:
    return metrics_service.get_metrics()
