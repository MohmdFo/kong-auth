"""
Kong Auth Service Metrics Definitions

This module defines all Prometheus metrics used by the Kong Auth Service.
Metrics are organized into categories:
- Request metrics: General request counts and durations
- Authentication metrics: Success/failure rates for authentication
- Consumer management metrics: Consumer creation/deletion counts
- JWT token metrics: Token generation and validation counts
- Kong API interaction metrics: Calls to Kong Admin API
- Error metrics: Error counts and types
- Service health metrics: Active consumers and tokens gauges
- Casdoor integration metrics: Casdoor authentication success/failure
"""

from prometheus_client import CollectorRegistry, Counter, Histogram, Gauge

# Create a dedicated registry for your metrics
registry = CollectorRegistry()

# Request metrics
REQUEST_COUNT = Counter(
    "kong_auth_request_count",
    "Total number of requests to Kong Auth Service",
    ["method", "endpoint", "status_code"],
    registry=registry,
)

REQUEST_DURATION_SECONDS = Histogram(
    "kong_auth_request_duration_seconds",
    "Duration of API requests in seconds",
    ["method", "endpoint"],
    registry=registry,
)

# Authentication metrics
AUTH_SUCCESS_COUNT = Counter(
    "kong_auth_authentication_success_total",
    "Total number of successful authentications",
    ["username", "method"],
    registry=registry,
)

AUTH_FAILURE_COUNT = Counter(
    "kong_auth_authentication_failure_total",
    "Total number of failed authentications",
    ["username", "method", "error_type"],
    registry=registry,
)

# Consumer management metrics
CONSUMER_CREATED_COUNT = Counter(
    "kong_auth_consumer_created_total",
    "Total number of Kong consumers created",
    ["username"],
    registry=registry,
)

CONSUMER_DELETED_COUNT = Counter(
    "kong_auth_consumer_deleted_total",
    "Total number of Kong consumers deleted",
    ["username"],
    registry=registry,
)

# JWT token metrics
JWT_TOKEN_GENERATED_COUNT = Counter(
    "kong_auth_jwt_tokens_generated_total",
    "Total number of JWT tokens generated",
    ["username", "token_type"],
    registry=registry,
)

JWT_TOKEN_VALIDATED_COUNT = Counter(
    "kong_auth_jwt_tokens_validated_total",
    "Total number of JWT tokens validated",
    ["username", "status"],
    registry=registry,
)

# Kong API interaction metrics
KONG_API_CALLS_COUNT = Counter(
    "kong_auth_kong_api_calls_total",
    "Total number of calls to Kong Admin API",
    ["endpoint", "method", "status"],
    registry=registry,
)

KONG_API_DURATION_SECONDS = Histogram(
    "kong_auth_kong_api_duration_seconds",
    "Duration of Kong Admin API calls in seconds",
    ["endpoint", "method"],
    registry=registry,
)

# Error metrics
ERROR_COUNT = Counter(
    "kong_auth_errors_total",
    "Total number of errors occurred",
    ["method", "endpoint", "error_type"],
    registry=registry,
)

# Service health metrics
ACTIVE_CONSUMERS_GAUGE = Gauge(
    "kong_auth_active_consumers",
    "Number of active Kong consumers",
    registry=registry,
)

ACTIVE_TOKENS_GAUGE = Gauge(
    "kong_auth_active_tokens",
    "Number of active JWT tokens",
    registry=registry,
)

# Casdoor integration metrics
CASDOOR_AUTH_SUCCESS_COUNT = Counter(
    "kong_auth_casdoor_auth_success_total",
    "Total number of successful Casdoor authentications",
    ["username"],
    registry=registry,
)

CASDOOR_AUTH_FAILURE_COUNT = Counter(
    "kong_auth_casdoor_auth_failure_total",
    "Total number of failed Casdoor authentications",
    ["username", "error_type"],
    registry=registry,
)
