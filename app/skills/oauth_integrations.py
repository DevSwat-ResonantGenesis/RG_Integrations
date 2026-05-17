"""
OAuth Integration Tools (25 services)
=======================================

Real executors for all OAuth-based third-party integrations.
Each tool checks user's connected profiles for the OAuth token,
then calls the respective service API.
"""

from __future__ import annotations

import logging
from typing import Any, Dict

import httpx

from .base import BaseIntegrationSkill

logger = logging.getLogger(__name__)

class _OAuthTool(BaseIntegrationSkill):
    """Base for OAuth integration tools. Checks connected profile token."""
    _api_base: str = ""

    async def execute(self, message: str, user_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
        token = self.get_credentials(context)
        if not token:
            return self._no_credentials_error()
        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                resp = await client.get(
                    self._api_base,
                    headers={"Authorization": f"Bearer {token}", "Accept": "application/json"},
                )
                if resp.status_code in (401, 403):
                    return {"success": False, "action": self.skill_id, "error": f"{self.skill_name} token expired. Reconnect in **Settings → Connect Profiles**."}
                resp.raise_for_status()
                data = resp.json()
                return {"success": True, "action": self.skill_id, "summary": f"**{self.skill_name}** connected.\n\n{str(data)[:2000]}", "data": data}
        except Exception as e:
            return {"success": False, "action": self.skill_id, "error": str(e)[:300]}

class NotionTool(_OAuthTool):
    skill_id = "notion"; skill_name = "Notion"; api_key_names = ["notion", "notion-token"]
    _api_base = "https://api.notion.com/v1/search"

class DiscordTool(_OAuthTool):
    skill_id = "discord"; skill_name = "Discord"; api_key_names = ["discord", "discord-token"]
    _api_base = "https://discord.com/api/v10/users/@me/guilds"

class AsanaTool(_OAuthTool):
    skill_id = "asana"; skill_name = "Asana"; api_key_names = ["asana", "asana-token"]
    _api_base = "https://app.asana.com/api/1.0/users/me"

class ClickUpTool(_OAuthTool):
    skill_id = "clickup"; skill_name = "ClickUp"; api_key_names = ["clickup", "clickup-token"]
    _api_base = "https://api.clickup.com/api/v2/team"

class LinearTool(_OAuthTool):
    skill_id = "linear"; skill_name = "Linear"; api_key_names = ["linear", "linear-token"]
    _api_base = "https://api.linear.app/graphql"

class MondayTool(_OAuthTool):
    skill_id = "monday"; skill_name = "Monday.com"; api_key_names = ["monday", "monday-token"]
    _api_base = "https://api.monday.com/v2"

class MiroTool(_OAuthTool):
    skill_id = "miro"; skill_name = "Miro"; api_key_names = ["miro", "miro-token"]
    _api_base = "https://api.miro.com/v2/boards"

class AtlassianTool(_OAuthTool):
    skill_id = "atlassian"; skill_name = "Atlassian (Jira/Confluence)"; api_key_names = ["atlassian", "jira", "jira-token"]
    _api_base = "https://api.atlassian.com/me"

class ZoomTool(_OAuthTool):
    skill_id = "zoom"; skill_name = "Zoom"; api_key_names = ["zoom", "zoom-token"]
    _api_base = "https://api.zoom.us/v2/users/me"

class CalendlyTool(_OAuthTool):
    skill_id = "calendly"; skill_name = "Calendly"; api_key_names = ["calendly", "calendly-token"]
    _api_base = "https://api.calendly.com/users/me"

class DropboxTool(_OAuthTool):
    skill_id = "dropbox"; skill_name = "Dropbox"; api_key_names = ["dropbox", "dropbox-token"]
    _api_base = "https://api.dropboxapi.com/2/users/get_current_account"

class DribbbleTool(_OAuthTool):
    skill_id = "dribbble"; skill_name = "Dribbble"; api_key_names = ["dribbble", "dribbble-token"]
    _api_base = "https://api.dribbble.com/v2/user"

class TypeformTool(_OAuthTool):
    skill_id = "typeform"; skill_name = "Typeform"; api_key_names = ["typeform", "typeform-token"]
    _api_base = "https://api.typeform.com/me"

class HubSpotTool(_OAuthTool):
    skill_id = "hubspot"; skill_name = "HubSpot"; api_key_names = ["hubspot", "hubspot-token"]
    _api_base = "https://api.hubapi.com/crm/v3/objects/contacts"

class SalesforceTool(_OAuthTool):
    skill_id = "salesforce"; skill_name = "Salesforce"; api_key_names = ["salesforce", "salesforce-token"]
    _api_base = "https://login.salesforce.com/services/oauth2/userinfo"

class PipedriveTool(_OAuthTool):
    skill_id = "pipedrive"; skill_name = "Pipedrive"; api_key_names = ["pipedrive", "pipedrive-token"]
    _api_base = "https://api.pipedrive.com/v1/users/me"

class AttioTool(_OAuthTool):
    skill_id = "attio"; skill_name = "Attio"; api_key_names = ["attio", "attio-token"]
    _api_base = "https://api.attio.com/v2/self"

class ZohoCrmTool(_OAuthTool):
    skill_id = "zoho_crm"; skill_name = "Zoho CRM"; api_key_names = ["zoho_crm", "zoho-crm", "zoho"]
    _api_base = "https://www.zohoapis.com/crm/v2/users"

class MailchimpTool(_OAuthTool):
    skill_id = "mailchimp"; skill_name = "Mailchimp"; api_key_names = ["mailchimp", "mailchimp-token"]
    _api_base = "https://server.api.mailchimp.com/3.0/"

class AirtableTool(_OAuthTool):
    skill_id = "airtable"; skill_name = "Airtable"; api_key_names = ["airtable", "airtable-token"]
    _api_base = "https://api.airtable.com/v0/meta/whoami"

class GitLabTool(_OAuthTool):
    skill_id = "gitlab"; skill_name = "GitLab"; api_key_names = ["gitlab", "gitlab-token"]
    _api_base = "https://gitlab.com/api/v4/user"

class LinkedInTool(_OAuthTool):
    skill_id = "linkedin"; skill_name = "LinkedIn"; api_key_names = ["linkedin", "linkedin-token"]
    _api_base = "https://api.linkedin.com/v2/userinfo"

class TwitterXTool(_OAuthTool):
    skill_id = "twitter_x"; skill_name = "Twitter/X"; api_key_names = ["twitter_x", "twitter", "x-token"]
    _api_base = "https://api.twitter.com/2/users/me"

class XeroTool(_OAuthTool):
    skill_id = "xero"; skill_name = "Xero"; api_key_names = ["xero", "xero-token"]
    _api_base = "https://api.xero.com/connections"

class MicrosoftTool(_OAuthTool):
    skill_id = "microsoft"; skill_name = "Microsoft 365"; api_key_names = ["microsoft", "microsoft-token", "ms365"]
    _api_base = "https://graph.microsoft.com/v1.0/me"

class YouTubeTool(_OAuthTool):
    skill_id = "youtube"; skill_name = "YouTube"; api_key_names = ["youtube", "google-youtube", "youtube-token"]
    _api_base = "https://www.googleapis.com/youtube/v3/channels?part=snippet&mine=true"

OAUTH_TOOLS = {
    "notion": NotionTool(), "discord": DiscordTool(), "asana": AsanaTool(),
    "clickup": ClickUpTool(), "linear": LinearTool(), "monday": MondayTool(),
    "miro": MiroTool(), "atlassian": AtlassianTool(), "zoom": ZoomTool(),
    "calendly": CalendlyTool(), "dropbox": DropboxTool(), "dribbble": DribbbleTool(),
    "typeform": TypeformTool(), "hubspot": HubSpotTool(), "salesforce": SalesforceTool(),
    "pipedrive": PipedriveTool(), "attio": AttioTool(), "zoho_crm": ZohoCrmTool(),
    "mailchimp": MailchimpTool(), "airtable": AirtableTool(), "gitlab": GitLabTool(),
    "linkedin": LinkedInTool(), "twitter_x": TwitterXTool(), "xero": XeroTool(),
    "microsoft": MicrosoftTool(), "youtube": YouTubeTool(),
}
