"""
Base Integration Skill (RG_Integrations service edition)
=========================================================

Every 3rd-party integration in this service inherits from BaseIntegrationSkill.
The shape is identical to the one previously in
RG_Chat/app/services/tools/base.py so existing skill code can be moved
across with zero behavioral change.
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class BaseIntegrationSkill(ABC):
    """Base class for all modular integration skills."""

    skill_id: str = ""
    skill_name: str = ""
    api_key_names: List[str] = []  # Keys to look for in context["user_api_keys"]

    def get_credentials(self, context: Dict[str, Any]) -> Optional[str]:
        """Extract API key / token from the execution context.

        For now the credential is passed through `context["user_api_keys"]`
        from RG_Chat. A future iteration will have this service fetch the
        credential directly from RG_Auth using `user_id`.
        """
        user_keys = context.get("user_api_keys") or {}
        for key_name in self.api_key_names:
            val = user_keys.get(key_name)
            if val:
                return val
        return None

    @abstractmethod
    async def execute(
        self, message: str, user_id: str, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute the skill action. Must be implemented by each skill."""
        ...

    def _no_credentials_error(self) -> Dict[str, Any]:
        """Standard error when credentials are missing."""
        return {
            "success": False,
            "action": self.skill_id,
            "error": (
                f"**{self.skill_name}** is not connected. "
                f"Go to **Settings → Connect Profiles** and add your "
                f"{self.skill_name} API key/token to use this skill."
            ),
        }
