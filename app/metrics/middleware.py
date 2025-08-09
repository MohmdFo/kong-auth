import time
import logging
from fastapi import Request
from .base import (
    REQUEST_COUNT,
    REQUEST_DURATION_SECONDS,
    ERROR_COUNT,
    AUTH_SUCCESS_COUNT,
    AUTH_FAILURE_COUNT
)

logger = logging.getLogger(__name__)

async def metrics_middleware(request: Request, call_next):
    # Start time to calculate request processing duration
    start_time = time.time()

    try:
        # Process the request and get the response
        response = await call_next(request)

        # Calculate the request duration (time taken to process the request)
        duration = time.time() - start_time

        # Increment the request count metric (method, endpoint, status_code)
        REQUEST_COUNT.labels(
            method=request.method, 
            endpoint=request.url.path, 
            status_code=str(response.status_code)
        ).inc()

        # Record the request duration (latency)
        REQUEST_DURATION_SECONDS.labels(
            method=request.method, 
            endpoint=request.url.path
        ).observe(duration)

        # Track authentication success/failure
        if request.url.path in ["/me", "/create-consumer", "/generate-token-auto", "/auto-generate-consumer"]:
            if response.status_code >= 200 and response.status_code < 300:
                # Extract username from request if possible
                username = "unknown"
                try:
                    # Try to get username from path or headers
                    if hasattr(request, 'user') and request.user:
                        username = request.user.name
                    elif "username" in request.url.path:
                        # Extract from path like /consumers/{username}
                        path_parts = request.url.path.split('/')
                        if len(path_parts) > 2:
                            username = path_parts[-1]
                except:
                    username = "unknown"
                
                AUTH_SUCCESS_COUNT.labels(username=username, method=request.method).inc()
            elif response.status_code in [401, 403, 422]:
                AUTH_FAILURE_COUNT.labels(
                    username="unknown", 
                    method=request.method, 
                    error_type=f"http_{response.status_code}"
                ).inc()

        # Track errors
        if str(response.status_code).startswith("4") or str(response.status_code).startswith("5"):
            ERROR_COUNT.labels(
                method=request.method, 
                endpoint=request.url.path, 
                error_type=f"http_{response.status_code}"
            ).inc()

        return response
        
    except Exception as e:
        # Log the error but don't let it break the application
        logger.error(f"Error in metrics middleware: {e}")
        
        # Still try to record the error metric
        try:
            ERROR_COUNT.labels(
                method=request.method, 
                endpoint=request.url.path, 
                error_type="middleware_error"
            ).inc()
        except:
            pass
            
        # Re-raise the exception to maintain normal error handling
        raise
