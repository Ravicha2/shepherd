# Shepherd Scaffolding Design

## Build Order

Inner core outward, each module tested before the next is built:

1. `models.py` — NormalizedSession dataclass + AdapterProtocol
2. `storage.py` — SQLite CRUD
3. `classifier.py` — IntentClassifier pure function
4. `discovery.py` — SessionDiscovery
5. `adapters/claude_code.py` — Claude Code JSONL adapter
6. `cli.py` — typer CLI entry point
7. `dashboard.py` — FastAPI local web UI

Each module gets tests written first (TDD), then implementation.

## Package Structure

```
shepherd/
├── pyproject.toml          # uv-managed, pytest, rich, fastapi deps
├── src/
│   └── shepherd/
│       ├── __init__.py
│       ├── models.py       # NormalizedSession, AdapterProtocol
│       ├── storage.py      # SQLite CRUD
│       ├── classifier.py   # IntentClassifier
│       ├── discovery.py    # SessionDiscovery
│       ├── cli.py          # typer CLI entry point
│       ├── dashboard.py    # FastAPI local web UI
│       └── adapters/
│           ├── __init__.py
│           └── claude_code.py
├── tests/
│   ├── test_models.py
│   ├── test_storage.py
│   ├── test_classifier.py
│   ├── test_discovery.py
│   ├── test_claude_code_adapter.py
│   └── conftest.py
└── docs/                   # existing ADRs, PRD, etc.
```

- Python 3.11+, src layout, managed with **uv**
- Dependencies: `typer` (CLI), `rich` (terminal output), `fastapi` + `uvicorn` (dashboard), `pytest` (dev)
- Entry point: `shepherd = shepherd.cli:app` in pyproject.toml `[project.scripts]`

## models.py

```python
@dataclass
class NormalizedSession:
    session_id: str
    timestamp_start: str | None
    end_type: str | None          # confirmed | closed | timed_out | clear
    task_type: str | None         # feature | bugfix | refactor | exploration | review | docs
    intent_confirmed: bool
    satisfaction: str | None      # satisfied | partial | unsatisfied
    skills_used: list[str]
    mcps_used: list[str]

class AdapterProtocol(Protocol):
    def parse(self, transcript_path: Path) -> NormalizedSession: ...
```

Plain `@dataclass`, no Pydantic. Valid values enforced by classifier and CLI, not by the data model. `AdapterProtocol` uses `typing.Protocol` for structural subtyping — no inheritance required. String literals for `end_type`, `task_type`, `satisfaction` — extensible without code changes (ADR-0002).

## storage.py

```python
class Storage:
    def __init__(self, db_path: Path = Path("~/.shepherd/sessions.db")): ...
    def store(self, session: NormalizedSession, transcript_path: Path) -> None: ...
    def get(self, session_id: str) -> NormalizedSession | None: ...
    def list_rated(self) -> list[NormalizedSession]: ...
    def list_unrated_ids(self) -> list[str]: ...
    def mark_rated(self, session_id: str, task_type: str, intent_confirmed: bool, satisfaction: str) -> None: ...
```

Table `sessions` has all 8 NormalizedSession fields + `transcript_path`. Tests use in-memory SQLite (`:memory:`).

## classifier.py

```python
def classify(session: NormalizedSession) -> str | None:
    """Rule-based intent classifier. Returns task_type or None."""
```

Pure function. Two strategies:
1. **Skill mapping** — hardcoded dict mapping skill names to task types (e.g., `tdd` → `feature`, `review` → `review`, `docs` → `docs`, `security-review` → `review`)
2. **Tool pattern heuristics** — if no skill matched, check tool usage patterns (heavy Edit+Write+Bash → `feature`, heavy Read+Grep → `exploration`)

No signal → `None`. Never defaults to "exploration". Highest test priority module.

## discovery.py

```python
class SessionDiscovery:
    def __init__(self, storage: Storage): ...
    def find_unrated(self, agent: str = "claude_code") -> list[Path]: ...
```

Scans `~/.claude/projects/` for Claude Code JSONL transcripts. Compares against `storage.list_unrated_ids()` to skip already-rated sessions. Returns list of paths.

## adapters/claude_code.py

```python
class ClaudeCodeAdapter:
    def parse(self, transcript_path: Path) -> NormalizedSession: ...
```

Reads Claude Code JSONL transcripts. Extracts: `session_id`, `timestamp_start`, `end_type`, `skills_used`, `mcps_used`. Leaves `task_type`, `satisfaction`, `intent_confirmed` as `None`/`False`. Integration tests against sample JSONL transcripts.

## cli.py

typer app with 4 commands:
- `shepherd rate` — find most recent unrated session, confirm intent, rate satisfaction
- `shepherd rate --all` — batch rate all unrated sessions
- `shepherd list` — show unrated sessions
- `shepherd dashboard` — launch FastAPI server + open browser

Shallow orchestration over tested deep modules. Tested via integration/smoke tests, not unit tests.

## dashboard.py

FastAPI app with two views:
1. Session list — task_type, skills_used, mcps_used, satisfaction per session
2. Satisfaction by task type — aggregate outcome percentages

Served at localhost, auto-port. Reads from Storage, no writes.

## Testing Strategy

Per PRD:
- **classifier** — highest priority, pure function tests (skill-to-task, tool patterns, null on no signal)
- **models/AdapterProtocol** — contract tests (valid fields accepted, invalid rejected, protocol enforced)
- **storage** — CRUD tests using in-memory SQLite
- **claude_code adapter** — integration tests against fabricated JSONL test fixtures (Claude Code transcript format is reverse-engineered from actual `~/.claude/projects/` JSONL files)
- **discovery** — tests against mock filesystem
- **cli/dashboard** — integration/smoke tests only, not unit tests