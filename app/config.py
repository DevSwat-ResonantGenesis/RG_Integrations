"""Configuration for RG_Integrations service."""

from __future__ import annotations

import os


class Config:
    """Runtime configuration sourced from environment variables."""

    SERVICE_NAME: str = "rg_integrations"
    SERVICE_VERSION: str = "0.1.0"

    # Internal service URLs (Docker network)
    AUTH_SERVICE_URL: str = os.getenv("AUTH_SERVICE_URL", "http://auth_service:8000")

    # Service-to-service shared secret. RG_Chat sends this in x-internal-secret
    # so we can reject calls coming from outside the Docker network.
    INTERNAL_SECRET: str = os.getenv("INTERNAL_SECRET", "")

    # If False, /execute will accept calls without the internal secret. Useful
    # in dev; should be True in prod.
    ENFORCE_INTERNAL_SECRET: bool = os.getenv("ENFORCE_INTERNAL_SECRET", "false").lower() == "true"

    HTTP_TIMEOUT_SECONDS: float = float(os.getenv("INTEGRATIONS_HTTP_TIMEOUT", "30"))


config = Config()
