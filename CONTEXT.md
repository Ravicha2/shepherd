# Shepherd — Domain Context

## Glossary

| Term | Definition |
|------|-----------|
| **Intent** | What the user was trying to accomplish in a session. Inferred from session signals (skills, tool patterns, CLAUDE.md shape) and confirmed by the user. Replaces the earlier term "DoD" (Definition of Done), which incorrectly implied specific success criteria. |
| **Approach** | How the user attempted their intent: which skills were invoked, which MCP servers were used, what tools were called. Captured automatically from the session transcript. |
| **Outcome** | Whether the session met the user's needs. Measured by a three-point satisfaction rating: satisfied, partial, unsatisfied. |
| **Delegation confidence map** | A derived insight showing which task types can be trusted to AI (delegable), which benefit from AI exploration, and which require intensive validation. Not a per-session signal — emerges from patterns across 50+ sessions. |
| **NormalizedSession** | The adapter contract: 8 fields (session_id, timestamp_start, end_type, task_type, intent_confirmed, satisfaction, skills_used, mcps_used) that every agent adapter must produce. Missing fields are null or [], never errors. |
| **Adapter** | An agent-specific module that reads a transcript format (Claude Code JSONL, Cursor SQLite, etc.) and returns a NormalizedSession. Shepherd is agent-agnostic; adapters make it work with any agent. |
| **IntentClassifier** | Pure function that takes a NormalizedSession and returns a task_type string or None. V1 uses rule-based classification. No signal → None, prompt user. Never defaults to "exploration". |
| **Two-tier data model** | Local-only fields (raw section headings, individual skill names) stay on the device. Shared fields (derived booleans, counts, category tags) are safe for a future hub. |

## Key Decisions

- **Outcome measurement, not event capture.** Shepherd differentiates on measuring whether AI sessions were useful, not on capturing session events. Existing tools handle capture; Shepherd consumes their output.
- **Post-session processing.** Shepherd reads transcripts after the session ends, not via live hooks. Agent-agnostic by design. See ADR-0001.
- **Minimal schema, add-when-needed.** 8 fields in v0.1. New fields are indexed only when dashboard views prove a need. Raw transcript is always available for enrichment via `transcript_path`. See ADR-0002.
- **Intent inference, not DoD.** Infers what the user was doing, asks them to confirm. No "Definition of Done" text field. See ADR-0005.
- **Missing data is honest.** If intent can't be inferred, leave it null and ask the user. Never impute with assumptions.
- **Local-first storage.** SQLite at `~/.shepherd/sessions.db`. Nothing leaves the machine without explicit opt-in. See ADR-0004.
- **Python runtime via pipx.** Chosen for author velocity and zero-dependency SQLite. See ADR-0003.

## Module Structure

```
shepherd/
├── adapters/          # Per-agent transcript parsers → NormalizedSession
│   └── claude_code.py # Claude Code JSONL adapter (v0.1)
├── classifier.py      # IntentClassifier (rule-based) → task_type or None
├── models.py          # NormalizedSession dataclass, AdapterProtocol
├── storage.py         # SQLite CRUD at ~/.shepherd/sessions.db
├── discovery.py       # Finds unrated transcripts by scanning filesystem
├── cli.py             # CLI: rate, list, dashboard
└── dashboard.py       # Local web UI (FastAPI)
```

## CLI Commands (v0.1)

| Command | Purpose |
|---------|---------|
| `shepherd rate` | Rate most recent unrated session |
| `shepherd rate --all` | Batch rate all unrated sessions |
| `shepherd list` | Show unrated sessions |
| `shepherd dashboard` | Open local web UI |

## Session Boundaries

A session ends when:
1. User runs `shepherd rate` and confirms
2. A `SessionStart` with source `"clear"` is detected (ends previous session for that project)
3. A periodic sweep marks sessions with no events for >30 min as `timed_out`

## NormalizedSession Fields

| Field | Type | Values |
|-------|------|--------|
| `session_id` | `str` | Unique identifier |
| `timestamp_start` | `str \| None` | ISO 8601 |
| `end_type` | `str \| None` | `confirmed` / `closed` / `timed_out` / `clear` |
| `task_type` | `str \| None` | `feature` / `bugfix` / `refactor` / `exploration` / `review` / `docs` |
| `intent_confirmed` | `bool` | User confirmed inferred task_type |
| `satisfaction` | `str \| None` | `satisfied` / `partial` / `unsatisfied` |
| `skills_used` | `list[str]` | Skills invoked in session |
| `mcps_used` | `list[str]` | MCP servers used |

## Adapter Status

| Adapter | Status | Input Format | Source |
|---------|--------|-------------|--------|
| Claude Code | v0.1 | JSONL | `~/.claude/projects/` |
| Cursor | Planned | SQLite | Local DB |
| Aider | Planned | Markdown | Chat logs |
| Copilot | Planned | JSON | VS Code logs |

## Out of Scope (v0.1)

- Hook integration for automatic "run shepherd rate" prompts (v0.2)
- Adapters for other AI agents — added when users ask
- Community hub (v2 milestone)
- LLM-based intent inference (v2, after rule-based validation)
- "Would use again" rating, trend views, model breakdown, skill frequency (add on demand)
- Live dashboard or real-time session monitoring