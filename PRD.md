# PRD: Shepherd v0.1 — Real-World AI Usability Measurement

## Problem Statement

AI coding benchmarks (MMLU, HumanEval, SWE-bench) measure what models can do in isolation, but not what they actually do in real workflows with real configs, real prompts, and real users judging the outcomes. Developers using AI tools daily have no shared, reproducible record of "this approach + this config → this outcome." The "whisperer" knowledge of how to get good results from AI is trapped in individual sessions and scattered tutorials. Existing observability tools (Langfuse, Helicone, AgentOps) track tokens, latency, and cost — but miss the outcome dimension entirely.

## Solution

Shepherd is a local-first CLI tool that measures AI coding session outcomes. After a session, the developer runs `shepherd rate` to confirm what they were doing (intent) and rate how it went (satisfaction). Shepherd infers intent from session signals (skills used, MCPs used, tool patterns) and stores the result in a local SQLite database. A personal dashboard shows outcome patterns over time: which task types and approaches lead to satisfaction, and which don't. The core insight is a delegation confidence map — which tasks can you fully delegate to AI, which benefit from AI-assisted exploration, and which need intensive validation.

Shepherd is agent-agnostic. It reads session transcripts via per-agent adapters (Claude Code JSONL first, others later) that normalize to a common schema. It does not hook into any agent's event system — it processes transcripts after the session ends.

## User Stories

1. As a developer, I want to rate my AI coding sessions after they end, so that I can track whether my AI usage is actually improving over time.
2. As a developer, I want Shepherd to infer what kind of task I was working on, so that I don't have to manually categorize every session.
3. As a developer, I want to confirm or correct the inferred task type, so that the data is accurate even when inference is wrong.
4. As a developer, I want to rate my satisfaction with a session in one tap (satisfied / partial / unsatisfied), so that rating is not a burden.
5. As a developer, I want to rate multiple unrated sessions at once, so that I can catch up after a week of forgetting to rate.
6. As a developer, I want to see a list of all my sessions with their task type and satisfaction, so that I can review my AI usage history.
7. As a developer, I want to see satisfaction broken down by task type, so that I can identify which kinds of tasks AI handles well and which it doesn't.
8. As a developer, I want Shepherd to know which skills and MCP servers I used in a session, so that my approach is captured automatically without effort.
9. As a developer, I want Shepherd to leave the task type blank when it can't infer intent, so that I'm never forced to accept a wrong classification.
10. As a developer, I want all my data stored locally in SQLite, so that no session data leaves my machine without my explicit consent.
11. As a developer, I want raw CLAUDE.md section headings and individual skill names to stay local, so that proprietary information is never shared.
12. As a developer, I want to see derived summaries (section counts, category tags, boolean flags) on a future community hub, so that I can compare my patterns with others without exposing details.
13. As a developer using Claude Code, I want Shepherd to automatically detect and parse my session transcripts, so that I don't have to configure anything.
14. As a developer using other AI tools in the future, I want Shepherd to support those tools via adapters, so that I can measure outcomes across all my AI tools.
15. As a developer, I want the rating prompt to be fast (under 5 seconds), so that it doesn't disrupt my workflow.
16. As a developer, I want Shepherd to handle sessions that ended without a clean close (terminal closed, session timed out), so that no sessions are lost.
17. As a developer, I want to see which MCP servers I used in a session, so that I can evaluate whether specific MCP integrations improve outcomes.
18. As a developer, I want the CLI to be installed via pipx, so that setup is a single command.
19. As a developer, I want to run `shepherd dashboard` to see my personal outcome patterns in a local web UI, so that I can spot trends without reading a terminal.
20. As a developer, I want Shepherd to batch-process all unrated sessions with `shepherd rate --all`, so that I can rate a week's worth of sessions in one sitting.

## Implementation Decisions

- **Agent-agnostic adapter architecture**: Shepherd reads session transcripts via per-agent adapters that produce a `NormalizedSession` (8 fields: session_id, timestamp_start, end_type, task_type, intent_confirmed, satisfaction, skills_used, mcps_used). Missing fields are null or empty lists, never errors. The Claude Code adapter is v0.1; other adapters come later when users ask for them. See ADR-0001.

- **NormalizedSession contract**: Every adapter returns this shape. It is the single interface between capture and measurement. Fields: session_id (str), timestamp_start (str | None), end_type (str | None — confirmed/closed/timed_out/clear), task_type (str | None — inferred or null if no signal), intent_confirmed (bool), satisfaction (str | None — satisfied/partial/unsatisfied), skills_used (list[str]), mcps_used (list[str]). See ADR-0002.

- **IntentClassifier**: Pure function that takes a NormalizedSession (with raw transcript data available) and returns a task_type string or None. V1 uses rule-based classification: skill-to-task mappings (e.g., skill "tdd" → "feature", skill "review" → "review") and tool pattern heuristics (e.g., Edit+Write+Bash heavy → "feature"). No signal produces None, which prompts the user to classify manually. Never defaults to "exploration". See ADR-0005.

- **Post-session processing**: Shepherd reads transcripts after the session ends, not via live hooks. The `Stop` hook event is not used in v0.1. Users run `shepherd rate` manually. An optional hook nudge (printing "run shepherd rate" at session end) is a v0.2 feature.

- **Session discovery**: `SessionDiscovery` module scans known transcript locations (`~/.claude/projects/` for Claude Code) and identifies sessions that haven't been rated yet by comparing against the SQLite database.

- **Session boundary**: A session ends when: (1) the user runs `shepherd rate` and confirms, (2) a `SessionStart` with source "clear" is detected (ends the previous session for that project), or (3) a periodic sweep marks sessions with no events for >30 minutes as "timed_out". These heuristics will be validated in practice during dogfooding.

- **Storage**: Local SQLite at `~/.shepherd/sessions.db`. Schema is the 8-field NormalizedSession plus a `transcript_path` column for enrichment. All raw transcript data is preserved locally via the transcript_path reference. See ADR-0002.

- **Privacy tiers**: Local-only data includes raw CLAUDE.md section headings, individual skill names, and full skill references. Shared data (for future hub) includes only derived abstractions: section_count, has_stack_section, has_patterns_section, total_length_chars, skill_category_tags (grouped, not individual). See ADR-0004.

- **Python runtime**: Built in Python, distributed via pipx. SQLite is built-in, no native dependencies. Rich for terminal output, FastAPI for dashboard. See ADR-0003.

- **Dashboard v0.1**: Two views only: (1) session list with task_type, skills_used, mcps_used, satisfaction; (2) satisfaction breakdown by task_type. Additional views (trend over time, model breakdown, skill usage frequency) are added based on what users ask for.

- **CLI commands v0.1**: `shepherd rate` (rate most recent unrated session), `shepherd rate --all` (batch rate all unrated sessions), `shepherd list` (show unrated sessions), `shepherd dashboard` (open local web UI).

## Testing Decisions

- **What makes a good test**: Tests should verify external behavior, not implementation details. For `IntentClassifier`, this means: given a set of session signals, does it produce the correct task_type or None? For `ClaudeCodeAdapter`, this means: given a sample JSONL transcript, does it extract the correct fields? For `Storage`, this means: can I store a session and retrieve it correctly?

- **Modules with tests**:
  - `IntentClassifier`: Pure function tests — skill-to-task mappings, tool pattern heuristics, null output when no signal. Most critical module, highest test priority.
  - `NormalizedSession` / `AdapterProtocol`: Contract tests — verify that the dataclass accepts valid fields, rejects invalid ones, and that the adapter protocol enforces the interface.
  - `Storage`: CRUD tests using in-memory SQLite — store, retrieve, list, mark as rated.
  - `ClaudeCodeAdapter`: Integration tests against sample JSONL transcripts — verify that skills, MCPs, duration, and session metadata are extracted correctly.
  - `SessionDiscovery`: Tests against a mock filesystem — verify that unrated sessions are correctly identified and already-rated sessions are skipped.

- **Modules without unit tests**: CLI commands (rate, list, dashboard) are shallow orchestration over tested deep modules. Tested via integration/smoke tests, not unit tests.

- **No prior art in this repo**: This is a new project with no existing tests. Test structure will follow Python conventions (tests/ directory, pytest).

## Out of Scope

- Hook integration for automatic "run shepherd rate" prompts at session end (v0.2)
- Adapters for other AI agents (Cursor, Copilot, Windsurf, Aider) — added when users ask for them
- Community hub (separate v2 milestone)
- LLM-based intent inference (v2, after rule-based validation)
- "Would use again" rating (dashboard feature, add when satisfaction proves too coarse)
- Model breakdown, trend over time, skill usage frequency dashboard views (add based on user demand)
- Live dashboard or real-time session monitoring
- Content creator partnerships, enterprise tier, team features
- Pattern discovery engine (requires 500+ sessions on hub)

## Further Notes

- The original design used "DoD" (Definition of Done) for what Shepherd infers. This was renamed to "intent" during design review because DoD implies specific success criteria, while Shepherd infers what the user was trying to do. See ADR-0005.
- The delegation confidence map (which tasks are delegable, which benefit from exploration, which need validation) is a derived insight from 50+ sessions of intent + satisfaction data, not a per-session signal.
- V0.1 success criteria: 50-100 rated sessions, intent inference confirmation rate measurable, at least one pattern visible on the dashboard that wasn't obvious before rating.
- The two-phase validation approach: (1) calibration with deliberate sessions across all task types, (2) natural session validation measuring actual confirmation vs. override rate. The 70% accuracy target applies to phase 2.