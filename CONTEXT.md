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
| **Intent inference** | The process of deriving task_type from session signals. V1 is rule-based (skill-to-task mappings + tool pattern heuristics). No signal = null, ask the user. Never default to "exploration". |
| **Two-tier data model** | Local-only fields (raw section headings, individual skill names) stay on the device. Shared fields (derived booleans, counts, category tags) are safe for the hub. |
| **Shepherd** | The project name. Not "AgentBench" — that name belongs to THUDM's ICLR 2024 benchmark project. |

## Key Decisions

- **Outcome measurement, not event capture.** Shepherd differentiates on measuring whether AI sessions were useful, not on capturing session events. Existing tools (cLens, Hook Hero) handle capture; Shepherd consumes their output.
- **Post-session processing.** Shepherd reads transcripts after the session ends, not via live hooks. This makes it agent-agnostic and simpler to build.
- **Separate CLI.** `shepherd rate --all` for batch rating. Optional hook nudge for Claude Code users later.
- **Missing data is honest.** If intent can't be inferred, leave it null and ask the user. Never impute with assumptions.
- **Minimal v0.1.** 8-field schema, two dashboard views, one adapter. Add based on what users ask for.