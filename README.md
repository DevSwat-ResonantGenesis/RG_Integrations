# RG_Integrations

Execution service for 3rd-party integrations (Figma, GitHub, Google
Workspace, CRMs, etc.). Owns the actual API-call code; reads tool
metadata from the canonical `rg_tool_registry` (volume-mounted at
`/app/rg_tool_registry`).

## Why this service exists

Before Workstream 3, every integration lived inside `RG_Chat`. That
prevented `agent_engine_service`, `public_guest_chat_service`, and
future services from reusing the same code, and it kept secrets +
OAuth + provider rate-limits coupled to the chat process.

Now: any service that needs to call a 3rd party makes a single
HTTP POST to `rg_integrations`. RG_Chat does this transparently via
`RemoteIntegrationSkill` (registered as a `handler_fn` on the registry).

## Endpoints

| Method | Path                  | Purpose                                          |
| ------ | --------------------- | ------------------------------------------------ |
| GET    | `/`                   | Service banner                                   |
| GET    | `/health`             | Liveness + list of loaded skill IDs              |
| GET    | `/skills`             | All skill IDs this service can execute           |
| POST   | `/execute/{tool_id}`  | Run the named skill                              |

`POST /execute/{tool_id}` body:
```json
{
  "message": "show my figma files",
  "user_id": "user-uuid",
  "context": {
    "user_api_keys": { "figma": "..." },
    "user_role": "user",
    "is_superuser": false
  }
}
```
Returns the skill's own dict (`success`, `action`, `summary`, `error`, ...).

## Auth (current)

- Optional `x-internal-secret` header, enforced only when
  `ENFORCE_INTERNAL_SECRET=true` (production).
- `user_api_keys` are passed in the request body from RG_Chat.

## Auth (planned)

- This service will pull `user_api_keys` directly from `RG_Auth`
  using `user_id` + an internal s2s JWT, removing the need for chat
  to forward raw tokens. Tracking issue: TBD.

## Migration playbook (for the other 52 integrations)

Each migration is a four-step pattern. Total time per integration: ~5 min.

### 1. Move the skill code into this repo

```bash
# Source still lives in RG_Chat:
cp ../RG_Chat/app/services/tools/<integration>.py app/skills/<integration>.py

# Fix imports: BaseIntegrationSkill now comes from .base (already correct
# because both files use the same identifier).
```

### 2. Register it in `app/skills/__init__.py`

```python
from .<integration> import <Integration>Skill

SKILLS: Dict[str, BaseIntegrationSkill] = {
    "figma": FigmaSkill(),
    "<integration>": <Integration>Skill(),
    ...
}
```

> If the source file exports a `*_TOOLS` dict (e.g. `WEB_TOOLS`,
> `GITHUB_TOOLS`) just unpack it: `**WEB_TOOLS`.

### 3. Collapse the RG_Chat side to a thin delegate

```python
# RG_Chat/app/services/tools/<integration>.py
from ._remote import RemoteIntegrationSkill

class <Integration>Skill(RemoteIntegrationSkill):
    skill_id = "<integration>"
    skill_name = "<Display Name>"
    api_key_names = [...]  # unchanged
```

The class name is what `tools/__init__.py` imports. Every other
RG_Chat call site keeps working: `INTEGRATION_SKILLS["<integration>"]`
still resolves; `tool_handler_registration` still wires its `execute()`
as a `handler_fn`; `ToolExecutor.execute()` still looks up the handler
from the registry. The only difference is that `execute()` is now an
HTTP POST instead of the real API call.

### 4. Verify

```bash
# Rebuild + restart the service
docker compose -f docker-compose.unified.yml build rg_integrations
docker compose -f docker-compose.unified.yml up -d rg_integrations

# Rebuild + restart chat
docker compose -f docker-compose.unified.yml up -d chat_service

# Smoke test
docker exec chat_service python -c "
import asyncio, json
async def main():
    from app.services.tool_handler_registration import register_all_handlers, register_inline_executors
    from app.services.tool_executor import tool_executor
    from app.services.tools_registry import ToolDefinition, ToolCategory
    register_all_handlers(); register_inline_executors(tool_executor)
    td = ToolDefinition(id='<integration>', name='<Name>', description='', icon='', category=ToolCategory.UTILITY)
    r = await tool_executor.execute(tool=td, message='ping', user_id='smoke', context={'user_api_keys': {}})
    print(json.dumps(r, indent=2))
asyncio.run(main())
"
```

Expected: `success=False`, `error` mentions "not connected" (because no
api key was provided). That confirms (1) chat dispatched to the registry
handler, (2) registry resolved to `RemoteIntegrationSkill`, (3) HTTP
POST landed in `rg_integrations`, (4) the skill ran and emitted its
own error path.

### 5. Delete the original code

Only after the smoke test passes for that integration:

```bash
# The file in RG_Chat/app/services/tools/<integration>.py now contains
# ONLY the 4-line RemoteIntegrationSkill subclass — that stays so
# tools/__init__.py's INTEGRATION_SKILLS keeps a "figma" entry.
# The 100-200 LOC of provider code was deleted in step 3.
```

## Outstanding migrations (52 to go)

These files in `RG_Chat/app/services/tools/` are pending migration. Each
provides one or more skill_ids:

| File                   | Skill IDs (count) | Complexity                      |
| ---------------------- | ----------------- | ------------------------------- |
| `google_drive.py`      | 1                 | OAuth refresh                   |
| `google_calendar.py`   | 1                 | OAuth refresh, biggest file     |
| `google_docs_tools.py` | google_docs, google_sheets, create_presentation (3) | OAuth refresh |
| `sigma.py`             | 1                 | trivial                         |
| `web_tools.py`         | ~12               | API keys, multiple providers    |
| `dev_tools.py`         | execute_code, get_current_time, … (~5) | mostly utility |
| `github_tools.py`      | github_* (~10)    | PAT auth                        |
| `filesystem_tools.py`  | file_*, find_by_name, grep_search (~10) | IDE service proxy |
| `media_tools.py`       | generate_image, generate_audio, generate_video, generate_chart, generate_music (5) | provider keys |
| `email_tools.py`       | gmail_*, send_email, slack_*, configure_smtp, delete_smtp (~8) | OAuth + SMTP |
| `oauth_integrations.py`| salesforce, hubspot, notion, slack, asana, monday, miro, … (~25) | OAuth heavy |

`oauth_integrations.py` is the largest single migration; the
`dev_tools` and `filesystem_tools` ones may be better placed in
`agent_engine_service` / `ide_platform_service` rather than this service
— that decision is per-integration.
