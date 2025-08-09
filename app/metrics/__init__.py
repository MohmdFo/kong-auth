"""
Kong Auth Service Metrics Module

This module provides Prometheus metrics for monitoring the Kong Auth Service.
It includes metrics for:
- Request counts and durations
- Authentication success/failure rates
- Consumer creation/deletion counts
- JWT token generation counts
- Kong API interaction metrics
- Active consumers and tokens gauges
- Error rates and types

Usage:
    from app.metrics import metrics_router
    app.include_router(metrics_router, prefix="/metrics", tags=["metrics"])
"""

from .routers import router as metrics_router

__all__ = [
    "metrics_router",
]
