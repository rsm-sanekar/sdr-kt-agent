# MCP Servers for SDR Onboarding

Two servers separated by concern:

## Data Server: sdr-onboarding-data

Read-only resources backed by `data/raw/` CSVs.

| Resource URI | Returns | M01 step |
|---|---|---|
| `sdr-profiles://all` | All hire profiles as JSON list | (any step needing the catalog) |
| `sdr-profiles://{hire_id}` | Single hire by ID | Steps 1, 3, 10 |
| `ae-profiles://all` | All AE mentor profiles as JSON list | Step 3 |

Source: [data_server.py](data_server.py). Backing data: [data/raw/sdr_profiles.csv](../data/raw/sdr_profiles.csv) and [data/raw/ae_profiles.csv](../data/raw/ae_profiles.csv).

## Tools Server: sdr-onboarding-tools

Callable tools that wrap our skills and automations.

### `invoke_onboarding_plan(hire_id: str, horizon_days: int = 30) -> dict`
- **Purpose:** Generate a deterministic pre-boarding learning plan for a new SDR hire.
- **Wraps:** [automations/generate-onboarding-plan](../automations/generate-onboarding-plan)
- **M01 step:** Step 1 (Pre-boarding)
- **Returns:** JSON envelope with `status`, `next_action`, `artifact_refs`, `outputs`. On success `next_action="rank-trail-guides"` and `artifact_refs` points to `data/working/<run_id>/01_onboarding_plan.md`.

### `invoke_trail_guide_ranking(hire_id: str, top_n: int = 5) -> dict`
- **Purpose:** Score every AE mentor on a transparent five-component 0-100 scale and return the top-N ranking for this hire.
- **Wraps:** [automations/rank-trail-guides](../automations/rank-trail-guides)
- **M01 step:** Step 3 (Mentor pairing)
- **Returns:** JSON envelope with `status`, `next_action`, `artifact_refs`, `outputs`. On success `next_action="welcome-new-hire"` and `artifact_refs` points to `data/working/<run_id>/02_trail_guides.md`.

### `preview_envelope_schema() -> dict`
- **Purpose:** Return a documentation dict describing the seven keys of the standard JSON envelope so the model can reason uniformly about every `invoke_*` tool's response.
- **Wraps:** Nothing — pure reference data inlined in the server.
- **M01 step:** N/A (used at Step 10 and any step that needs a model reminder of envelope shape).
- **Returns:** A dict whose keys are `status`, `next_action`, `confidence`, `review_required`, `artifact_refs`, `outputs`, `error`, each mapped to a one-line description of the field's meaning.

Source: [tools_server.py](tools_server.py).

## How skills decide which tool to invoke at which step

| Workflow step | Skill/automation that runs | Which MCP tool/resource it uses | Decision signal |
|---|---|---|---|
| Step 1 — Pre-boarding | `generate-onboarding-plan` (LLM skill) | `invoke_onboarding_plan` | User asks for a plan |
| Step 2 — Mentor pairing | `rank-trail-guides` (automation) | `invoke_trail_guide_ranking` | Prior envelope `next_action = rank-trail-guides` |
| Step 3 — Welcome email | `welcome-new-hire` (automation) | `sdr-profiles` + `ae-profiles` (data server) | Reads hire + chosen mentor; renders a template-fill email |
| Coaching review (standalone) | `score-cold-call` (LLM skill) | `preview_envelope_schema` (reference) | Model reminder of envelope shape |

## Running the servers

Registered in [`../.mcp.json`](../.mcp.json) so Claude Code launches them. To run directly:

```bash
uv run python -m mcp_servers.data_server
uv run python -m mcp_servers.tools_server
```

To inspect a server with the MCP inspector UI:

```bash
uv run mcp dev mcp_servers/data_server.py
uv run mcp dev mcp_servers/tools_server.py
```
