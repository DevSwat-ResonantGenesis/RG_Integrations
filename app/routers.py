"""HTTP API for RG_Integrations."""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel

from .config import config
from .skills import SKILLS, get_skill

logger = logging.getLogger(__name__)

router = APIRouter()


# ── Request / response models ───────────────────────────────────────


class ExecuteRequest(BaseModel):
    """Body for POST /execute/{tool_id}.

    `context` is the same dict shape RG_Chat's ToolExecutor builds:
        {
            "user_api_keys": {...},     # raw provider tokens
            "user_role": "user",
            "is_superuser": False,
            "unlimited_credits": False,
            "github_token": "...",      # optional
            "org_id": "...",            # optional
            ... any other chat context ...
        }
    """

    message: str
    user_id: str
    context: Dict[str, Any] = {}


class ExecuteResponse(BaseModel):
    """Response from a skill.execute() call.

    The skill returns a free-form dict (success, action, summary, error, ...);
    we pass it through verbatim.
    """

    success: bool
    action: Optional[str] = None
    summary: Optional[str] = None
    error: Optional[str] = None
    data: Optional[Dict[str, Any]] = None

    class Config:
        extra = "allow"


class SkillListResponse(BaseModel):
    skills: List[str]
    count: int


# ── Endpoints ───────────────────────────────────────────────────────


def _check_internal_secret(x_internal_secret: Optional[str]) -> None:
    """Reject calls that don't carry the expected internal s2s secret.

    Only enforced when ENFORCE_INTERNAL_SECRET=true (production).
    """
    if not config.ENFORCE_INTERNAL_SECRET:
        return
    expected = config.INTERNAL_SECRET
    if not expected:
        # Misconfigured — fail closed.
        raise HTTPException(status_code=503, detail="Service misconfigured: INTERNAL_SECRET missing")
    if x_internal_secret != expected:
        raise HTTPException(status_code=403, detail="Invalid internal secret")


@router.get("/health")
async def health() -> Dict[str, Any]:
    """Liveness + skill inventory."""
    return {
        "service": config.SERVICE_NAME,
        "version": config.SERVICE_VERSION,
        "status": "ok",
        "skills_loaded": list(SKILLS.keys()),
    }


@router.get("/skills", response_model=SkillListResponse)
async def list_skills() -> SkillListResponse:
    """List all skill IDs this service can execute."""
    names = sorted(SKILLS.keys())
    return SkillListResponse(skills=names, count=len(names))


@router.post("/execute/{tool_id}")
async def execute_tool(
    tool_id: str,
    body: ExecuteRequest,
    x_internal_secret: Optional[str] = Header(default=None),
    x_user_id: Optional[str] = Header(default=None),
) -> Dict[str, Any]:
    """Execute the named skill and return its result dict.

    Auth model (current):
      - Optional `x-internal-secret` header enforced when ENFORCE_INTERNAL_SECRET=true
      - `body.context["user_api_keys"]` carries provider tokens (RG_Chat sends
        these from the user's connected profiles)

    Auth model (future):
      - This service will read `user_api_keys` directly from RG_Auth using
        `body.user_id` and an internal s2s JWT, removing the need for chat
        to pass raw tokens.
    """
    _check_internal_secret(x_internal_secret)

    skill = get_skill(tool_id)
    if skill is None:
        raise HTTPException(
            status_code=404,
            detail=f"No skill registered for tool_id={tool_id!r}. "
                   f"Loaded: {sorted(SKILLS.keys())}",
        )

    # Use header user_id if request body's user_id is blank (defensive).
    user_id = body.user_id or x_user_id or ""
    if not user_id:
        raise HTTPException(status_code=400, detail="user_id required")

    try:
        result = await skill.execute(body.message, user_id, body.context or {})
        if not isinstance(result, dict):
            result = {"success": True, "data": result}
        result.setdefault("tool_id", tool_id)
        return result
    except Exception as e:
        logger.exception(f"Skill {tool_id} failed for user {user_id}: {e}")
        return {
            "success": False,
            "tool_id": tool_id,
            "error": f"{type(e).__name__}: {str(e)[:300]}",
        }
