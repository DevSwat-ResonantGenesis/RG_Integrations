"""
Skill registry for RG_Integrations.

Add a new integration by:
  1. Implementing a subclass of BaseIntegrationSkill in this directory
     (mirror the file structure used in RG_Chat/app/services/tools/*.py)
  2. Importing and registering it in the SKILLS dict below.

The /execute/{tool_id} endpoint resolves tool_id -> skill via this dict.
"""

from __future__ import annotations

from typing import Dict

from .base import BaseIntegrationSkill
from .figma import FigmaSkill
from .google_calendar import GoogleCalendarSkill
from .google_drive import GoogleDriveSkill
from .oauth_integrations import OAUTH_TOOLS
from .sigma import SigmaSkill


SKILLS: Dict[str, BaseIntegrationSkill] = {
    "figma": FigmaSkill(),
    "google_drive": GoogleDriveSkill(),
    "google_calendar": GoogleCalendarSkill(),
    "sigma": SigmaSkill(),
    # 26 OAuth integrations from oauth_integrations.py:
    # notion, discord, asana, clickup, linear, monday, miro, atlassian,
    # zoom, calendly, dropbox, dribbble, typeform, hubspot, salesforce,
    # pipedrive, attio, zoho_crm, mailchimp, airtable, gitlab, linkedin,
    # twitter_x, xero, microsoft, youtube.
    **OAUTH_TOOLS,
    # Future:
    # (dev_tools.py, github_tools.py, email_tools.py, google_docs_tools.py
    #  — see MIGRATION_PLAYBOOK.md in repo root)
}


def get_skill(tool_id: str) -> BaseIntegrationSkill | None:
    """Resolve a tool_id to its skill instance, or None if unknown."""
    return SKILLS.get(tool_id)
