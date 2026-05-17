"""
RG_Integrations service — main entry point.

Owns the execution logic for all 3rd-party integrations (Figma, Google Drive,
GitHub, Salesforce, etc.) that used to live in
RG_Chat/app/services/tools/*.py.

RG_Chat calls this service over HTTP via the tool registry's `handler_fn`.
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from .config import config
from .routers import router
from .skills import SKILLS

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(levelname)s %(message)s")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(
        "[%s] startup — version=%s, skills_loaded=%d, enforce_secret=%s",
        config.SERVICE_NAME,
        config.SERVICE_VERSION,
        len(SKILLS),
        config.ENFORCE_INTERNAL_SECRET,
    )
    logger.info("[%s] available skills: %s", config.SERVICE_NAME, sorted(SKILLS.keys()))
    yield
    logger.info("[%s] shutdown", config.SERVICE_NAME)


app = FastAPI(
    title="RG_Integrations",
    description=(
        "Execution service for 3rd-party integrations (Figma, GitHub, "
        "Google Workspace, CRM, etc.). Reads tool metadata from the canonical "
        "rg_tool_registry; owns the actual API-call code."
    ),
    version=config.SERVICE_VERSION,
    lifespan=lifespan,
)

app.include_router(router)


@app.get("/")
async def root():
    return {"service": config.SERVICE_NAME, "version": config.SERVICE_VERSION, "status": "ok"}
