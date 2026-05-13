# Agent-agnostic adapter architecture

Shepherd reads session transcripts via per-agent adapters that normalize to a common `NormalizedSession` shape, rather than integrating directly into Claude Code's hook system. This makes Shepherd work with any AI coding agent (Cursor, Copilot, Aider, etc.) without depending on any agent's event system. The trade-off: no real-time capture or live dashboard. We chose portability over immediacy because the core insight (intent + approach + outcome) is derived post-session, not during it.

**Considered options:**
- Claude Code hooks (live events, agent-specific, real-time) — rejected because it locks Shepherd to one agent and makes multi-agent comparison impossible
- Adapter architecture (post-session, per-agent modules, portable) — chosen because each adapter is thin, missing fields are null not errors, and the core system never changes when adding agents

**Consequences:** Each new agent requires writing an adapter, but adapters are small modules that just parse a transcript format. Claude Code's JSONL is the richest source; other agents may have sparser data, which the NormalizedSession shape handles gracefully.