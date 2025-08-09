# app/metrics/endpoints.py
from fastapi import APIRouter
from fastapi.responses import Response
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from .base import registry

router = APIRouter()


@router.get("/metrics")
def get_metrics():
    """
    Prometheus metrics endpoint for Kong Auth Service.
    
    Returns metrics in Prometheus format including:
    - Request counts and durations
    - Authentication success/failure rates
    - Consumer creation/deletion counts
    - JWT token generation counts
    - Kong API interaction metrics
    - Active consumers and tokens gauges
    - Error rates and types
    """
    data = generate_latest(registry)
    return Response(content=data, media_type=CONTENT_TYPE_LATEST)
