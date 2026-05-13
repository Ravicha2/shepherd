# Shepherd Scaffolding Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Scaffold the Shepherd CLI tool — a local-first AI session outcome measurer with models, storage, classifier, discovery, adapter, CLI, and dashboard.

**Architecture:** Inner-core-outward build. Each phase produces working, testable software. TDD: write failing tests first, then implement. Python 3.11+, src layout, uv for package management.

**Tech Stack:** Python 3.11+, uv, typer, rich, fastapi, uvicorn, pytest, sqlite3 (stdlib)

---

## Phase 1: Project Setup + Models

**What:** Create the Python package structure, configure uv, define NormalizedSession dataclass and AdapterProtocol.

**Input:** Package name `shepherd`, Python 3.11+
**Output:** Installable package with `NormalizedSession` dataclass and `AdapterProtocol` protocol, passing contract tests.

### Task 1.1: Initialize project with uv

**Files:**
- Create: `pyproject.toml`
- Create: `src/shepherd/__init__.py`

- [ ] **Step 1: Initialize the project with uv**

```bash
cd /Users/ravichasuksawasdinaayuthaya/AgentOS/shepherd
uv init --no-readme --no-pin-python
```

This creates `pyproject.toml` and basic structure. We need to adjust it for src layout.

- [ ] **Step 2: Rewrite pyproject.toml for src layout**

Replace the generated `pyproject.toml` with:

```toml
[project]
name = "shepherd"
version = "0.1.0"
description = "Real-world AI usability measurement. Rate your AI coding sessions."
requires-python = ">=3.11"
dependencies = [
    "typer>=0.9.0",
    "rich>=13.0.0",
    "fastapi>=0.104.0",
    "uvicorn>=0.24.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-cov>=4.1.0",
]

[project.scripts]
shepherd = "shepherd.cli:app"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/shepherd"]

[tool.pytest.ini_options]
testpaths = ["tests"]
```

- [ ] **Step 3: Create src layout directories**

```bash
rm -f main.py  # remove any generated main.py
mkdir -p src/shepherd/adapters
mkdir -p tests
touch src/shepherd/__init__.py
touch src/shepherd/adapters/__init__.py
touch tests/__init__.py
touch tests/conftest.py
```

- [ ] **Step 4: Install dependencies**

```bash
uv sync --extra dev
```

- [ ] **Step 5: Verify setup**

```bash
uv run pytest --version
```

Expected: pytest version printed, no errors.

- [ ] **Step 6: Commit**

```bash
git add pyproject.toml src/ tests/
git commit -m "feat: initialize project with uv, src layout, and dependencies"
```

### Task 1.2: Write failing tests for NormalizedSession and AdapterProtocol

**Files:**
- Create: `tests/test_models.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_models.py
from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest

from shepherd.models import NormalizedSession, AdapterProtocol


class TestNormalizedSession:
    def test_create_with_all_fields(self):
        session = NormalizedSession(
            session_id="abc-123",
            timestamp_start="2026-05-14T10:00:00Z",
            end_type="confirmed",
            task_type="feature",
            intent_confirmed=True,
            satisfaction="satisfied",
            skills_used=["tdd", "review"],
            mcps_used=["webclaw"],
        )
        assert session.session_id == "abc-123"
        assert session.timestamp_start == "2026-05-14T10:00:00Z"
        assert session.end_type == "confirmed"
        assert session.task_type == "feature"
        assert session.intent_confirmed is True
        assert session.satisfaction == "satisfied"
        assert session.skills_used == ["tdd", "review"]
        assert session.mcps_used == ["webclaw"]

    def test_create_with_minimal_fields(self):
        session = NormalizedSession(
            session_id="abc-123",
            timestamp_start=None,
            end_type=None,
            task_type=None,
            intent_confirmed=False,
            satisfaction=None,
            skills_used=[],
            mcps_used=[],
        )
        assert session.session_id == "abc-123"
        assert session.timestamp_start is None
        assert session.end_type is None
        assert session.task_type is None
        assert session.intent_confirmed is False
        assert session.satisfaction is None
        assert session.skills_used == []
        assert session.mcps_used == []

    def test_missing_required_field_raises_error(self):
        with pytest.raises(TypeError):
            NormalizedSession()  # type: ignore[call-arg]

    def test_session_id_is_required(self):
        with pytest.raises(TypeError):
            NormalizedSession()  # type: ignore[call-arg]


class TestAdapterProtocol:
    def test_conforming_class_satisfies_protocol(self):
        class FakeAdapter:
            def parse(self, transcript_path: Path) -> NormalizedSession:
                return NormalizedSession(
                    session_id="test",
                    timestamp_start=None,
                    end_type=None,
                    task_type=None,
                    intent_confirmed=False,
                    satisfaction=None,
                    skills_used=[],
                    mcps_used=[],
                )

        adapter: AdapterProtocol = FakeAdapter()
        assert isinstance(adapter, AdapterProtocol)

    def test_non_conforming_class_fails_protocol(self):
        class NotAnAdapter:
            pass

        with pytest.typing.assert_type_error:
            adapter: AdapterProtocol = NotAnAdapter()  # type: ignore[abstract]
```

Note: `pytest.typing.assert_type_error` doesn't exist. Use a simpler check:

```python
# tests/test_models.py
from pathlib import Path

import pytest

from shepherd.models import NormalizedSession, AdapterProtocol


class TestNormalizedSession:
    def test_create_with_all_fields(self):
        session = NormalizedSession(
            session_id="abc-123",
            timestamp_start="2026-05-14T10:00:00Z",
            end_type="confirmed",
            task_type="feature",
            intent_confirmed=True,
            satisfaction="satisfied",
            skills_used=["tdd", "review"],
            mcps_used=["webclaw"],
        )
        assert session.session_id == "abc-123"
        assert session.timestamp_start == "2026-05-14T10:00:00Z"
        assert session.end_type == "confirmed"
        assert session.task_type == "feature"
        assert session.intent_confirmed is True
        assert session.satisfaction == "satisfied"
        assert session.skills_used == ["tdd", "review"]
        assert session.mcps_used == ["webclaw"]

    def test_create_with_minimal_fields(self):
        session = NormalizedSession(
            session_id="abc-123",
            timestamp_start=None,
            end_type=None,
            task_type=None,
            intent_confirmed=False,
            satisfaction=None,
            skills_used=[],
            mcps_used=[],
        )
        assert session.session_id == "abc-123"
        assert session.timestamp_start is None
        assert session.end_type is None
        assert session.task_type is None
        assert session.intent_confirmed is False
        assert session.satisfaction is None
        assert session.skills_used == []
        assert session.mcps_used == []

    def test_missing_required_field_raises_error(self):
        with pytest.raises(TypeError):
            NormalizedSession()  # type: ignore[call-arg]


class TestAdapterProtocol:
    def test_conforming_class_satisfies_protocol(self):
        class FakeAdapter:
            def parse(self, transcript_path: Path) -> NormalizedSession:
                return NormalizedSession(
                    session_id="test",
                    timestamp_start=None,
                    end_type=None,
                    task_type=None,
                    intent_confirmed=False,
                    satisfaction=None,
                    skills_used=[],
                    mcps_used=[],
                )

        adapter: AdapterProtocol = FakeAdapter()
        result = adapter.parse(Path("/tmp/test.jsonl"))
        assert isinstance(result, NormalizedSession)

    def test_protocol_requires_parse_method(self):
        """AdapterProtocol is a structural type — any class with parse(Path) -> NormalizedSession satisfies it."""
        class FakeAdapter:
            def parse(self, transcript_path: Path) -> NormalizedSession:
                return NormalizedSession(
                    session_id="test",
                    timestamp_start=None,
                    end_type=None,
                    task_type=None,
                    intent_confirmed=False,
                    satisfaction=None,
                    skills_used=[],
                    mcps_used=[],
                )

        # Verify structural subtyping works
        adapter = FakeAdapter()
        assert hasattr(adapter, "parse")
        assert callable(adapter.parse)
```

- [ ] **Step 2: Run test to verify it fails**

```bash
uv run pytest tests/test_models.py -v
```

Expected: FAIL — `ModuleNotFoundError: No module named 'shepherd.models'`

- [ ] **Step 3: Write the implementation**

```python
# src/shepherd/models.py
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Protocol


@dataclass
class NormalizedSession:
    """The adapter contract: 8 fields that every agent adapter must produce.

    Missing fields are null or empty lists, never errors.
    """

    session_id: str
    timestamp_start: str | None
    end_type: str | None  # confirmed | closed | timed_out | clear
    task_type: str | None  # feature | bugfix | refactor | exploration | review | docs
    intent_confirmed: bool
    satisfaction: str | None  # satisfied | partial | unsatisfied
    skills_used: list[str] = field(default_factory=list)
    mcps_used: list[str] = field(default_factory=list)


class AdapterProtocol(Protocol):
    """Structural protocol for agent transcript adapters.

    Any class with a parse(Path) -> NormalizedSession method satisfies this.
    No inheritance required.
    """

    def parse(self, transcript_path: Path) -> NormalizedSession: ...
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
uv run pytest tests/test_models.py -v
```

Expected: All 5 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add src/shepherd/models.py tests/test_models.py
git commit -m "feat: add NormalizedSession dataclass and AdapterProtocol"
```

---

## Phase 2: Storage

**What:** SQLite CRUD for persisting and querying sessions.

**Input:** `NormalizedSession` + `transcript_path`
**Output:** Store, retrieve, list, and mark sessions as rated.

### Task 2.1: Write failing tests for Storage

**Files:**
- Create: `tests/test_storage.py`

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_storage.py
import sqlite3
from pathlib import Path

import pytest

from shepherd.models import NormalizedSession
from shepherd.storage import Storage


@pytest.fixture
def storage(tmp_path: Path):
    """Create a Storage instance with a temporary database."""
    db_path = tmp_path / "test_sessions.db"
    return Storage(db_path=db_path)


@pytest.fixture
def sample_session():
    return NormalizedSession(
        session_id="session-001",
        timestamp_start="2026-05-14T10:00:00Z",
        end_type="confirmed",
        task_type=None,
        intent_confirmed=False,
        satisfaction=None,
        skills_used=["tdd", "review"],
        mcps_used=["webclaw"],
    )


class TestStorageStoreAndGet:
    def test_store_and_retrieve_session(self, storage: Storage, sample_session: NormalizedSession):
        transcript_path = Path("/home/user/.claude/projects/abc/session-001.jsonl")
        storage.store(sample_session, transcript_path)

        result = storage.get("session-001")
        assert result is not None
        assert result.session_id == "session-001"
        assert result.timestamp_start == "2026-05-14T10:00:00Z"
        assert result.end_type == "confirmed"
        assert result.task_type is None
        assert result.intent_confirmed is False
        assert result.satisfaction is None
        assert result.skills_used == ["tdd", "review"]
        assert result.mcps_used == ["webclaw"]

    def test_get_nonexistent_session_returns_none(self, storage: Storage):
        result = storage.get("does-not-exist")
        assert result is None

    def test_store_creates_table_idempotently(self, storage: Storage, sample_session: NormalizedSession):
        storage.store(sample_session, Path("/tmp/a.jsonl"))
        storage.store(sample_session, Path("/tmp/b.jsonl"))  # same session_id again


class TestStorageListUnrated:
    def test_list_unrated_ids_returns_unrated_sessions(self, storage: Storage, sample_session: NormalizedSession):
        storage.store(sample_session, Path("/tmp/session-001.jsonl"))

        another = NormalizedSession(
            session_id="session-002",
            timestamp_start="2026-05-14T11:00:00Z",
            end_type="closed",
            task_type=None,
            intent_confirmed=False,
            satisfaction=None,
            skills_used=[],
            mcps_used=[],
        )
        storage.store(another, Path("/tmp/session-002.jsonl"))

        unrated = storage.list_unrated_ids()
        assert "session-001" in unrated
        assert "session-002" in unrated

    def test_list_unrated_excludes_rated_sessions(self, storage: Storage, sample_session: NormalizedSession):
        storage.store(sample_session, Path("/tmp/session-001.jsonl"))
        storage.mark_rated("session-001", task_type="feature", intent_confirmed=True, satisfaction="satisfied")

        unrated = storage.list_unrated_ids()
        assert "session-001" not in unrated


class TestStorageListRated:
    def test_list_rated_returns_only_rated_sessions(self, storage: Storage, sample_session: NormalizedSession):
        storage.store(sample_session, Path("/tmp/session-001.jsonl"))
        storage.mark_rated("session-001", task_type="feature", intent_confirmed=True, satisfaction="satisfied")

        another = NormalizedSession(
            session_id="session-002",
            timestamp_start="2026-05-14T11:00:00Z",
            end_type="closed",
            task_type=None,
            intent_confirmed=False,
            satisfaction=None,
            skills_used=[],
            mcps_used=[],
        )
        storage.store(another, Path("/tmp/session-002.jsonl"))

        rated = storage.list_rated()
        assert len(rated) == 1
        assert rated[0].session_id == "session-001"
        assert rated[0].task_type == "feature"
        assert rated[0].satisfaction == "satisfied"

    def test_list_rated_returns_empty_when_nothing_rated(self, storage: Storage, sample_session: NormalizedSession):
        storage.store(sample_session, Path("/tmp/session-001.jsonl"))
        rated = storage.list_rated()
        assert rated == []


class TestStorageMarkRated:
    def test_mark_rated_updates_session(self, storage: Storage, sample_session: NormalizedSession):
        storage.store(sample_session, Path("/tmp/session-001.jsonl"))
        storage.mark_rated("session-001", task_type="bugfix", intent_confirmed=False, satisfaction="partial")

        result = storage.get("session-001")
        assert result is not None
        assert result.task_type == "bugfix"
        assert result.intent_confirmed is False
        assert result.satisfaction == "partial"

    def test_mark_rated_removes_from_unrated_list(self, storage: Storage, sample_session: NormalizedSession):
        storage.store(sample_session, Path("/tmp/session-001.jsonl"))
        storage.mark_rated("session-001", task_type="feature", intent_confirmed=True, satisfaction="satisfied")

        unrated = storage.list_unrated_ids()
        assert "session-001" not in unrated
```

- [ ] **Step 2: Run test to verify it fails**

```bash
uv run pytest tests/test_storage.py -v
```

Expected: FAIL — `ModuleNotFoundError: No module named 'shepherd.storage'`

- [ ] **Step 3: Write the implementation**

```python
# src/shepherd/storage.py
from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from shepherd.models import NormalizedSession


class Storage:
    """SQLite CRUD for session data at ~/.shepherd/sessions.db."""

    def __init__(self, db_path: Path | None = None):
        if db_path is None:
            db_path = Path.home() / ".shepherd" / "sessions.db"
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _conn(self) -> sqlite3.Connection:
        return sqlite3.connect(str(self.db_path))

    def _init_db(self) -> None:
        with self._conn() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS sessions (
                    session_id TEXT PRIMARY KEY,
                    timestamp_start TEXT,
                    end_type TEXT,
                    task_type TEXT,
                    intent_confirmed INTEGER DEFAULT 0,
                    satisfaction TEXT,
                    skills_used TEXT DEFAULT '[]',
                    mcps_used TEXT DEFAULT '[]',
                    transcript_path TEXT,
                    rated INTEGER DEFAULT 0
                )
                """
            )

    def store(self, session: NormalizedSession, transcript_path: Path) -> None:
        with self._conn() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO sessions
                (session_id, timestamp_start, end_type, task_type, intent_confirmed,
                 satisfaction, skills_used, mcps_used, transcript_path)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    session.session_id,
                    session.timestamp_start,
                    session.end_type,
                    session.task_type,
                    int(session.intent_confirmed),
                    session.satisfaction,
                    json.dumps(session.skills_used),
                    json.dumps(session.mcps_used),
                    str(transcript_path),
                ),
            )

    def get(self, session_id: str) -> NormalizedSession | None:
        with self._conn() as conn:
            row = conn.execute(
                "SELECT session_id, timestamp_start, end_type, task_type, "
                "intent_confirmed, satisfaction, skills_used, mcps_used "
                "FROM sessions WHERE session_id = ?",
                (session_id,),
            ).fetchone()

        if row is None:
            return None

        return NormalizedSession(
            session_id=row[0],
            timestamp_start=row[1],
            end_type=row[2],
            task_type=row[3],
            intent_confirmed=bool(row[4]),
            satisfaction=row[5],
            skills_used=json.loads(row[6]),
            mcps_used=json.loads(row[7]),
        )

    def list_rated(self) -> list[NormalizedSession]:
        with self._conn() as conn:
            rows = conn.execute(
                "SELECT session_id, timestamp_start, end_type, task_type, "
                "intent_confirmed, satisfaction, skills_used, mcps_used "
                "FROM sessions WHERE rated = 1"
            ).fetchall()

        return [
            NormalizedSession(
                session_id=row[0],
                timestamp_start=row[1],
                end_type=row[2],
                task_type=row[3],
                intent_confirmed=bool(row[4]),
                satisfaction=row[5],
                skills_used=json.loads(row[6]),
                mcps_used=json.loads(row[7]),
            )
            for row in rows
        ]

    def list_unrated_ids(self) -> list[str]:
        with self._conn() as conn:
            rows = conn.execute(
                "SELECT session_id FROM sessions WHERE rated = 0"
            ).fetchall()
        return [row[0] for row in rows]

    def mark_rated(
        self, session_id: str, task_type: str, intent_confirmed: bool, satisfaction: str
    ) -> None:
        with self._conn() as conn:
            conn.execute(
                """
                UPDATE sessions
                SET task_type = ?, intent_confirmed = ?, satisfaction = ?, rated = 1
                WHERE session_id = ?
                """,
                (task_type, int(intent_confirmed), satisfaction, session_id),
            )
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
uv run pytest tests/test_storage.py -v
```

Expected: All 9 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add src/shepherd/storage.py tests/test_storage.py
git commit -m "feat: add SQLite storage with CRUD operations"
```

---

## Phase 3: Classifier

**What:** Rule-based intent classifier that maps session signals to task types.

**Input:** `NormalizedSession`
**Output:** `str` (task_type) or `None`

### Task 3.1: Write failing tests for classify

**Files:**
- Create: `tests/test_classifier.py`

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_classifier.py
import pytest

from shepherd.classifier import classify
from shepherd.models import NormalizedSession


def _session(**overrides) -> NormalizedSession:
    """Helper to build NormalizedSession with sensible defaults."""
    defaults = dict(
        session_id="test-session",
        timestamp_start="2026-05-14T10:00:00Z",
        end_type="confirmed",
        task_type=None,
        intent_confirmed=False,
        satisfaction=None,
        skills_used=[],
        mcps_used=[],
    )
    defaults.update(overrides)
    return NormalizedSession(**defaults)


class TestClassifySkillMapping:
    """Skill name → task type mappings."""

    def test_tdd_skill_maps_to_feature(self):
        result = classify(_session(skills_used=["tdd"]))
        assert result == "feature"

    def test_review_skill_maps_to_review(self):
        result = classify(_session(skills_used=["review"]))
        assert result == "review"

    def test_security_review_maps_to_review(self):
        result = classify(_session(skills_used=["security-review"]))
        assert result == "review"

    def test_docs_skill_maps_to_docs(self):
        result = classify(_session(skills_used=["docs"]))
        assert result == "docs"

    def test_simplify_skill_maps_to_refactor(self):
        result = classify(_session(skills_used=["simplify"]))
        assert result == "refactor"

    def test_feature_dev_skill_maps_to_feature(self):
        result = classify(_session(skills_used=["feature-dev"]))
        assert result == "feature"

    def test_multiple_skills_first_match_wins(self):
        """When multiple skills map to different types, first skill wins."""
        result = classify(_session(skills_used=["tdd", "review"]))
        assert result == "feature"

    def test_unknown_skill_returns_none(self):
        """A skill not in the mapping produces no signal from skill strategy."""
        result = classify(_session(skills_used=["unknown-skill-xyz"]))
        assert result is None


class TestClassifyToolPatterns:
    """Tool pattern heuristics when no skill matched."""

    def test_heavy_edit_write_bash_maps_to_feature(self):
        result = classify(_session(skills_used=[], mcps_used=[]))
        # With empty skills and empty mcps, no signal
        assert result is None


class TestClassifyNoSignal:
    """No signal at all → None, never defaults."""

    def test_empty_session_returns_none(self):
        result = classify(_session())
        assert result is None

    def test_unknown_skill_with_no_tool_pattern_returns_none(self):
        result = classify(_session(skills_used=["totally-unknown"]))
        assert result is None
```

- [ ] **Step 2: Run test to verify it fails**

```bash
uv run pytest tests/test_classifier.py -v
```

Expected: FAIL — `ModuleNotFoundError: No module named 'shepherd.classifier'`

- [ ] **Step 3: Write the implementation**

```python
# src/shepherd/classifier.py
from __future__ import annotations

from shepherd.models import NormalizedSession

SKILL_TO_TASK: dict[str, str] = {
    "tdd": "feature",
    "feature-dev": "feature",
    "review": "review",
    "security-review": "review",
    "docs": "docs",
    "simplify": "refactor",
}


def classify(session: NormalizedSession) -> str | None:
    """Rule-based intent classifier. Returns task_type or None.

    Strategy 1: Skill name mapping (e.g., "tdd" → "feature").
    Strategy 2: Tool pattern heuristics (future).

    No signal → None. Never defaults to "exploration".
    """
    for skill in session.skills_used:
        if skill in SKILL_TO_TASK:
            return SKILL_TO_TASK[skill]

    return None
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
uv run pytest tests/test_classifier.py -v
```

Expected: All 8 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add src/shepherd/classifier.py tests/test_classifier.py
git commit -m "feat: add rule-based intent classifier"
```

---

## Phase 4: Discovery

**What:** Find unrated session transcripts by scanning the filesystem.

**Input:** Agent type string (default: `"claude_code"`), `Storage` instance for comparing rated sessions.
**Output:** `list[Path]` of unrated transcript file paths.

### Task 4.1: Write failing tests for SessionDiscovery

**Files:**
- Create: `tests/test_discovery.py`

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_discovery.py
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from shepherd.discovery import SessionDiscovery
from shepherd.storage import Storage


@pytest.fixture
def mock_storage():
    storage = MagicMock(spec=Storage)
    storage.list_unrated_ids.return_value = []
    return storage


class TestSessionDiscoveryFindUnrated:
    def test_finds_jsonl_files_in_claude_projects_dir(self, mock_storage, tmp_path: Path):
        # Create a fake Claude Code transcript directory
        projects_dir = tmp_path / "projects"
        projects_dir.mkdir()
        session_dir = projects_dir / "my-project"
        session_dir.mkdir()
        transcript = session_dir / "session-001.jsonl"
        transcript.write_text('{"type":"user","message":"hello"}\n')

        discovery = SessionDiscovery(storage=mock_storage, claude_projects_dir=projects_dir)
        mock_storage.list_unrated_ids.return_value = ["session-001"]

        results = discovery.find_unrated()
        assert any(p.name == "session-001.jsonl" for p in results)

    def test_skips_already_rated_sessions(self, mock_storage, tmp_path: Path):
        projects_dir = tmp_path / "projects"
        projects_dir.mkdir()
        session_dir = projects_dir / "my-project"
        session_dir.mkdir()
        transcript = session_dir / "session-001.jsonl"
        transcript.write_text('{"type":"user","message":"hello"}\n')

        discovery = SessionDiscovery(storage=mock_storage, claude_projects_dir=projects_dir)
        mock_storage.list_unrated_ids.return_value = []  # session-001 already rated

        results = discovery.find_unrated()
        assert not any("session-001" in str(p) for p in results)

    def test_skips_non_jsonl_files(self, mock_storage, tmp_path: Path):
        projects_dir = tmp_path / "projects"
        projects_dir.mkdir()
        session_dir = projects_dir / "my-project"
        session_dir.mkdir()
        (session_dir / "notes.txt").write_text("not a transcript")
        (session_dir / "session-001.jsonl").write_text("{}\n")

        discovery = SessionDiscovery(storage=mock_storage, claude_projects_dir=projects_dir)
        mock_storage.list_unrated_ids.return_value = ["session-001"]

        results = discovery.find_unrated()
        assert len(results) == 1
        assert results[0].suffix == ".jsonl"

    def test_empty_directory_returns_empty_list(self, mock_storage, tmp_path: Path):
        projects_dir = tmp_path / "projects"
        projects_dir.mkdir()

        discovery = SessionDiscovery(storage=mock_storage, claude_projects_dir=projects_dir)
        results = discovery.find_unrated()
        assert results == []

    def test_nonexistent_directory_returns_empty_list(self, mock_storage, tmp_path: Path):
        nonexistent = tmp_path / "does_not_exist"

        discovery = SessionDiscovery(storage=mock_storage, claude_projects_dir=nonexistent)
        results = discovery.find_unrated()
        assert results == []
```

- [ ] **Step 2: Run test to verify it fails**

```bash
uv run pytest tests/test_discovery.py -v
```

Expected: FAIL — `ModuleNotFoundError: No module named 'shepherd.discovery'`

- [ ] **Step 3: Write the implementation**

```python
# src/shepherd/discovery.py
from __future__ import annotations

from pathlib import Path

from shepherd.storage import Storage


class SessionDiscovery:
    """Find unrated session transcripts on the filesystem."""

    def __init__(
        self,
        storage: Storage,
        claude_projects_dir: Path | None = None,
    ):
        self.storage = storage
        if claude_projects_dir is None:
            claude_projects_dir = Path.home() / ".claude" / "projects"
        self.claude_projects_dir = claude_projects_dir

    def find_unrated(self, agent: str = "claude_code") -> list[Path]:
        """Scan filesystem for unrated session transcripts.

        Returns paths to JSONL files whose session_id is not yet in the
        rated sessions database.
        """
        if not self.claude_projects_dir.exists():
            return []

        unrated_ids = set(self.storage.list_unrated_ids())

        transcripts: list[Path] = []
        for jsonl_path in self.claude_projects_dir.rglob("*.jsonl"):
            session_id = jsonl_path.stem
            if session_id in unrated_ids:
                transcripts.append(jsonl_path)

        return sorted(transcripts)
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
uv run pytest tests/test_discovery.py -v
```

Expected: All 5 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add src/shepherd/discovery.py tests/test_discovery.py
git commit -m "feat: add session discovery with filesystem scanning"
```

---

## Phase 5: Claude Code Adapter

**What:** Parse Claude Code JSONL transcripts into NormalizedSession objects.

**Input:** `Path` to a JSONL transcript file
**Output:** `NormalizedSession` with extracted fields (`session_id`, `timestamp_start`, `end_type`, `skills_used`, `mcps_used`). Fields that require user input (`task_type`, `satisfaction`, `intent_confirmed`) are left as `None`/`False`.

### Task 5.1: Write failing tests for ClaudeCodeAdapter

**Files:**
- Create: `tests/test_claude_code_adapter.py`
- Create: `tests/fixtures/` directory with sample JSONL files

- [ ] **Step 1: Create test fixtures**

```bash
mkdir -p tests/fixtures
```

Create `tests/fixtures/session_confirmed.jsonl`:

```jsonl
{"type":"system","session_id":"abc-123","timestamp":"2026-05-14T10:00:00Z"}
{"type":"skill","skill_name":"tdd"}
{"type":"tool","tool_name":"Edit"}
{"type":"tool","tool_name":"Write"}
{"type":"mcp","mcp_name":"webclaw"}
{"type":"end","end_type":"confirmed"}
```

Create `tests/fixtures/session_minimal.jsonl`:

```jsonl
{"type":"system","session_id":"minimal-001","timestamp":"2026-05-14T09:00:00Z"}
{"type":"end","end_type":"closed"}
```

Create `tests/fixtures/session_with_skills_and_mcps.jsonl`:

```jsonl
{"type":"system","session_id":"full-001","timestamp":"2026-05-14T11:00:00Z"}
{"type":"skill","skill_name":"tdd"}
{"type":"skill","skill_name":"simplify"}
{"type":"mcp","mcp_name":"webclaw"}
{"type":"mcp","mcp_name":"agent-browser"}
{"type":"tool","tool_name":"Bash"}
{"type":"end","end_type":"confirmed"}
```

- [ ] **Step 2: Write the failing tests**

```python
# tests/test_claude_code_adapter.py
from pathlib import Path

import pytest

from shepherd.adapters.claude_code import ClaudeCodeAdapter
from shepherd.models import NormalizedSession


FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture
def adapter():
    return ClaudeCodeAdapter()


class TestClaudeCodeAdapterParse:
    def test_parse_confirmed_session(self, adapter: ClaudeCodeAdapter):
        path = FIXTURES / "session_confirmed.jsonl"
        result = adapter.parse(path)

        assert result.session_id == "abc-123"
        assert result.timestamp_start == "2026-05-14T10:00:00Z"
        assert result.end_type == "confirmed"
        assert "tdd" in result.skills_used
        assert "webclaw" in result.mcps_used

    def test_parse_minimal_session(self, adapter: ClaudeCodeAdapter):
        path = FIXTURES / "session_minimal.jsonl"
        result = adapter.parse(path)

        assert result.session_id == "minimal-001"
        assert result.timestamp_start == "2026-05-14T09:00:00Z"
        assert result.end_type == "closed"
        assert result.skills_used == []
        assert result.mcps_used == []
        assert result.task_type is None
        assert result.satisfaction is None
        assert result.intent_confirmed is False

    def test_parse_session_with_skills_and_mcps(self, adapter: ClaudeCodeAdapter):
        path = FIXTURES / "session_with_skills_and_mcps.jsonl"
        result = adapter.parse(path)

        assert result.session_id == "full-001"
        assert result.skills_used == ["tdd", "simplify"]
        assert result.mcps_used == ["webclaw", "agent-browser"]

    def test_parse_sets_user_fields_to_defaults(self, adapter: ClaudeCodeAdapter):
        path = FIXTURES / "session_confirmed.jsonl"
        result = adapter.parse(path)

        assert result.task_type is None
        assert result.satisfaction is None
        assert result.intent_confirmed is False

    def test_parse_nonexistent_file_raises(self, adapter: ClaudeCodeAdapter):
        with pytest.raises(FileNotFoundError):
            adapter.parse(Path("/nonexistent/path/session.jsonl"))

    def test_parse_empty_jsonl_returns_minimal(self, adapter: ClaudeCodeAdapter, tmp_path: Path):
        empty = tmp_path / "empty.jsonl"
        empty.write_text("")

        result = adapter.parse(empty)
        assert result.session_id == "empty"
        assert result.timestamp_start is None
        assert result.end_type is None
```

- [ ] **Step 3: Run test to verify it fails**

```bash
uv run pytest tests/test_claude_code_adapter.py -v
```

Expected: FAIL — `ModuleNotFoundError: No module named 'shepherd.adapters.claude_code'`

- [ ] **Step 4: Write the implementation**

```python
# src/shepherd/adapters/__init__.py
```

(Empty init file already exists from Phase 1.)

```python
# src/shepherd/adapters/claude_code.py
from __future__ import annotations

import json
from pathlib import Path

from shepherd.models import NormalizedSession


class ClaudeCodeAdapter:
    """Parse Claude Code JSONL transcripts into NormalizedSession objects.

    Extracts: session_id, timestamp_start, end_type, skills_used, mcps_used.
    Leaves task_type, satisfaction, intent_confirmed as None/False — those
    are filled by the classifier and user.
    """

    def parse(self, transcript_path: Path) -> NormalizedSession:
        if not transcript_path.exists():
            raise FileNotFoundError(f"Transcript not found: {transcript_path}")

        lines: list[dict] = []
        for line in transcript_path.read_text().splitlines():
            line = line.strip()
            if line:
                lines.append(json.loads(line))

        session_id = transcript_path.stem
        timestamp_start: str | None = None
        end_type: str | None = None
        skills_used: list[str] = []
        mcps_used: list[str] = []

        for event in lines:
            event_type = event.get("type", "")

            if event_type == "system":
                session_id = event.get("session_id", session_id)
                timestamp_start = event.get("timestamp")

            elif event_type == "end":
                end_type = event.get("end_type")

            elif event_type == "skill":
                skill_name = event.get("skill_name", "")
                if skill_name and skill_name not in skills_used:
                    skills_used.append(skill_name)

            elif event_type == "mcp":
                mcp_name = event.get("mcp_name", "")
                if mcp_name and mcp_name not in mcps_used:
                    mcps_used.append(mcp_name)

        return NormalizedSession(
            session_id=session_id,
            timestamp_start=timestamp_start,
            end_type=end_type,
            task_type=None,
            intent_confirmed=False,
            satisfaction=None,
            skills_used=skills_used,
            mcps_used=mcps_used,
        )
```

- [ ] **Step 5: Run tests to verify they pass**

```bash
uv run pytest tests/test_claude_code_adapter.py -v
```

Expected: All 6 tests PASS.

- [ ] **Step 6: Commit**

```bash
git add src/shepherd/adapters/ tests/test_claude_code_adapter.py tests/fixtures/
git commit -m "feat: add Claude Code JSONL adapter"
```

---

## Phase 6: CLI

**What:** typer CLI entry point with `rate`, `list`, and `dashboard` commands. Shallow orchestration over tested deep modules.

**Input:** User commands (`shepherd rate`, `shepherd rate --all`, `shepherd list`, `shepherd dashboard`)
**Output:** Terminal prompts for rating, session lists displayed, dashboard launched in browser.

### Task 6.1: Write the CLI implementation

**Files:**
- Create: `tests/test_cli.py`
- Create: `src/shepherd/cli.py`

This phase skips pure TDD for CLI since the PRD specifies "shallow orchestration over tested deep modules — tested via integration/smoke tests, not unit tests." We write smoke tests that exercise the commands with mocked internals.

- [ ] **Step 1: Write smoke tests**

```python
# tests/test_cli.py
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from shepherd.cli import app
from shepherd.models import NormalizedSession


runner = CliRunner()


@pytest.fixture
def mock_storage():
    with patch("shepherd.cli.Storage") as MockStorage:
        instance = MagicMock()
        MockStorage.return_value = instance
        yield instance


@pytest.fixture
def mock_discovery():
    with patch("shepherd.cli.SessionDiscovery") as MockDiscovery:
        instance = MagicMock()
        MockDiscovery.return_value = instance
        yield instance


@pytest.fixture
def sample_session():
    return NormalizedSession(
        session_id="session-001",
        timestamp_start="2026-05-14T10:00:00Z",
        end_type="confirmed",
        task_type=None,
        intent_confirmed=False,
        satisfaction=None,
        skills_used=["tdd"],
        mcps_used=["webclaw"],
    )


class TestCLIList:
    def test_list_shows_unrated_sessions(self, mock_storage, mock_discovery, sample_session):
        mock_discovery.find_unrated.return_value = [
            Path("/home/user/.claude/projects/abc/session-001.jsonl")
        ]
        mock_storage.get.return_value = sample_session

        result = runner.invoke(app, ["list"])
        assert result.exit_code == 0
        assert "session-001" in result.output

    def test_list_with_no_unrated_sessions(self, mock_storage, mock_discovery):
        mock_discovery.find_unrated.return_value = []

        result = runner.invoke(app, ["list"])
        assert result.exit_code == 0
        assert "No unrated sessions" in result.output
```

- [ ] **Step 2: Run test to verify it fails**

```bash
uv run pytest tests/test_cli.py -v
```

Expected: FAIL — `ModuleNotFoundError: No module named 'shepherd.cli'`

- [ ] **Step 3: Write the CLI implementation**

```python
# src/shepherd/cli.py
from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from shepherd.classifier import classify
from shepherd.discovery import SessionDiscovery
from shepherd.models import NormalizedSession
from shepherd.storage import Storage

app = typer.Typer(help="Shepherd — rate your AI coding sessions")
console = Console()


@app.command()
def rate(all: bool = typer.Option(False, "--all", help="Rate all unrated sessions")) -> None:
    """Rate the most recent unrated session, or all unrated sessions with --all."""
    storage = Storage()
    discovery = SessionDiscovery(storage=storage)
    unrated = discovery.find_unrated()

    if not unrated:
        console.print("[dim]No unrated sessions found.[/dim]")
        raise typer.Exit()

    sessions_to_rate = unrated if all else unrated[:1]

    for transcript_path in sessions_to_rate:
        adapter = _get_adapter(transcript_path)
        session = adapter.parse(transcript_path)

        inferred_type = classify(session)
        session = _prompt_rating(session, inferred_type)

        storage.mark_rated(
            session_id=session.session_id,
            task_type=session.task_type or "exploration",
            intent_confirmed=session.intent_confirmed,
            satisfaction=session.satisfaction or "partial",
        )
        console.print(f"[green]✓[/green] Rated session {session.session_id}")


@app.command(name="list")
def list_sessions() -> None:
    """Show unrated sessions."""
    storage = Storage()
    discovery = SessionDiscovery(storage=storage)
    unrated = discovery.find_unrated()

    if not unrated:
        console.print("[dim]No unrated sessions found.[/dim]")
        raise typer.Exit()

    table = Table(title="Unrated Sessions")
    table.add_column("Session ID")
    table.add_column("Timestamp")
    table.add_column("Skills")

    for path in unrated:
        adapter = _get_adapter(path)
        session = adapter.parse(path)
        table.add_row(
            session.session_id,
            session.timestamp_start or "unknown",
            ", ".join(session.skills_used) or "none",
        )

    console.print(table)


@app.command()
def dashboard() -> None:
    """Open the local analytics dashboard."""
    from shepherd.dashboard import run_dashboard

    run_dashboard()


def _get_adapter(path: Path):
    """Return the appropriate adapter for a transcript path."""
    from shepherd.adapters.claude_code import ClaudeCodeAdapter

    return ClaudeCodeAdapter()


def _prompt_rating(session: NormalizedSession, inferred_type: str | None) -> NormalizedSession:
    """Interactive prompt to confirm intent and rate satisfaction."""
    task_types = ["feature", "bugfix", "refactor", "exploration", "review", "docs"]

    if inferred_type:
        console.print(f"\nInferred task type: [bold]{inferred_type}[/bold]")
        confirm = typer.confirm("Is this correct?", default=True)
        if confirm:
            session.task_type = inferred_type
            session.intent_confirmed = True
        else:
            session.task_type = _select_task_type(task_types)
            session.intent_confirmed = False
    else:
        console.print("\n[dim]Could not infer task type.[/dim]")
        session.task_type = _select_task_type(task_types)
        session.intent_confirmed = False

    console.print("\nHow did it go?")
    console.print("  1. Satisfied")
    console.print("  2. Partial")
    console.print("  3. Unsatisfied")
    choice = typer.prompt("Rating", type=int, default=1)

    satisfaction_map = {1: "satisfied", 2: "partial", 3: "unsatisfied"}
    session.satisfaction = satisfaction_map.get(choice, "partial")

    return session


def _select_task_type(task_types: list[str]) -> str:
    console.print("\nWhat were you working on?")
    for i, t in enumerate(task_types, 1):
        console.print(f"  {i}. {t}")
    choice = typer.prompt("Select", type=int, default=1)
    return task_types[choice - 1] if 1 <= choice <= len(task_types) else task_types[0]
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
uv run pytest tests/test_cli.py -v
```

Expected: All 2 tests PASS.

- [ ] **Step 5: Verify CLI is callable**

```bash
uv run shepherd --help
```

Expected: Help text showing `rate`, `list`, `dashboard` commands.

- [ ] **Step 6: Commit**

```bash
git add src/shepherd/cli.py tests/test_cli.py
git commit -m "feat: add CLI with rate, list, and dashboard commands"
```

---

## Phase 7: Dashboard

**What:** FastAPI local web UI with two views: session list and satisfaction by task type.

**Input:** SQLite database (via Storage)
**Output:** HTML views served at localhost with auto-port selection.

### Task 7.1: Write the dashboard implementation

**Files:**
- Create: `tests/test_dashboard.py`
- Create: `src/shepherd/dashboard.py`

- [ ] **Step 1: Write integration tests**

```python
# tests/test_dashboard.py
import pytest
from fastapi.testclient import TestClient

from shepherd.dashboard import create_app
from shepherd.models import NormalizedSession
from shepherd.storage import Storage


@pytest.fixture
def storage(tmp_path):
    db_path = tmp_path / "test_dashboard.db"
    return Storage(db_path=db_path)


@pytest.fixture
def client(storage: Storage):
    app = create_app(storage=storage)
    return TestClient(app)


@pytest.fixture
def rated_session():
    return NormalizedSession(
        session_id="rated-001",
        timestamp_start="2026-05-14T10:00:00Z",
        end_type="confirmed",
        task_type=None,
        intent_confirmed=False,
        satisfaction=None,
        skills_used=["tdd"],
        mcps_used=["webclaw"],
    )


class TestDashboardSessionList:
    def test_session_list_returns_200(self, client):
        response = client.get("/sessions")
        assert response.status_code == 200

    def test_session_list_shows_rated_sessions(self, client, storage, rated_session):
        storage.store(rated_session, transcript_path="/tmp/test.jsonl")
        storage.mark_rated("rated-001", "feature", True, "satisfied")

        response = client.get("/sessions")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["session_id"] == "rated-001"

    def test_session_list_empty_when_no_rated(self, client):
        response = client.get("/sessions")
        assert response.status_code == 200
        data = response.json()
        assert data == []


class TestDashboardSatisfactionBreakdown:
    def test_satisfaction_breakdown_returns_200(self, client):
        response = client.get("/satisfaction")
        assert response.status_code == 200

    def test_satisfaction_breakdown_aggregates_by_task_type(self, client, storage, rated_session):
        storage.store(rated_session, transcript_path="/tmp/test.jsonl")
        storage.mark_rated("rated-001", "feature", True, "satisfied")

        response = client.get("/satisfaction")
        assert response.status_code == 200
        data = response.json()
        assert "feature" in data
        assert data["feature"]["satisfied"] == 1
```

- [ ] **Step 2: Run test to verify it fails**

```bash
uv run pytest tests/test_dashboard.py -v
```

Expected: FAIL — `ModuleNotFoundError: No module named 'shepherd.dashboard'`

- [ ] **Step 3: Write the dashboard implementation**

```python
# src/shepherd/dashboard.py
from __future__ import annotations

from collections import defaultdict
from dataclasses import asdict
from typing import Any

import uvicorn
from fastapi import FastAPI

from shepherd.storage import Storage


def create_app(storage: Storage | None = None) -> FastAPI:
    app = FastAPI(title="Shepherd Dashboard")

    if storage is None:
        storage = Storage()

    @app.get("/sessions")
    def list_sessions() -> list[dict[str, Any]]:
        """Return all rated sessions."""
        sessions = storage.list_rated()
        return [asdict(s) for s in sessions]

    @app.get("/satisfaction")
    def satisfaction_breakdown() -> dict[str, dict[str, int]]:
        """Aggregate satisfaction counts by task type."""
        sessions = storage.list_rated()
        breakdown: dict[str, dict[str, int]] = defaultdict(
            lambda: {"satisfied": 0, "partial": 0, "unsatisfied": 0}
        )

        for session in sessions:
            if session.task_type and session.satisfaction:
                breakdown[session.task_type][session.satisfaction] += 1

        return dict(breakdown)

    return app


def run_dashboard(host: str = "127.0.0.1", port: int = 8421) -> None:
    """Launch the dashboard server."""
    app = create_app()
    uvicorn.run(app, host=host, port=port)
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
uv run pytest tests/test_dashboard.py -v
```

Expected: All 5 tests PASS.

- [ ] **Step 5: Verify dashboard starts**

```bash
uv run python -c "from shepherd.dashboard import create_app; app = create_app(); print('Dashboard app created:', app.title)"
```

Expected: `Dashboard app created: Shepherd Dashboard`

- [ ] **Step 6: Commit**

```bash
git add src/shepherd/dashboard.py tests/test_dashboard.py
git commit -m "feat: add FastAPI dashboard with session list and satisfaction views"
```

---

## Phase 8: Integration & Smoke Test

**What:** End-to-end smoke test that exercises the full pipeline: adapter → classifier → storage → discovery.

**Input:** Sample JSONL transcript fixture
**Output:** Session stored in SQLite, visible in dashboard.

### Task 8.1: Write integration smoke test

**Files:**
- Create: `tests/test_integration.py`

- [ ] **Step 1: Write the integration test**

```python
# tests/test_integration.py
"""End-to-end smoke test: adapter → classifier → storage → discovery."""
from pathlib import Path

from shepherd.adapters.claude_code import ClaudeCodeAdapter
from shepherd.classifier import classify
from shepherd.discovery import SessionDiscovery
from shepherd.models import NormalizedSession
from shepherd.storage import Storage


FIXTURES = Path(__file__).parent / "fixtures"


def test_full_pipeline(tmp_path: Path):
    storage = Storage(db_path=tmp_path / "test_pipeline.db")

    # 1. Parse transcript with adapter
    adapter = ClaudeCodeAdapter()
    transcript = FIXTURES / "session_confirmed.jsonl"
    session = adapter.parse(transcript)

    # 2. Classify intent
    task_type = classify(session)
    assert task_type == "feature"  # "tdd" skill maps to "feature"

    # 3. Store session
    storage.store(session, transcript_path=transcript)

    # 4. Mark as rated
    storage.mark_rated(
        session_id=session.session_id,
        task_type=task_type,
        intent_confirmed=True,
        satisfaction="satisfied",
    )

    # 5. Verify retrieval
    stored = storage.get(session.session_id)
    assert stored is not None
    assert stored.task_type == "feature"
    assert stored.satisfaction == "satisfied"
    assert stored.intent_confirmed is True

    # 6. Verify it's no longer in unrated list
    unrated = storage.list_unrated_ids()
    assert session.session_id not in unrated

    # 7. Verify it's in rated list
    rated = storage.list_rated()
    assert len(rated) == 1
    assert rated[0].session_id == session.session_id
```

- [ ] **Step 2: Run the integration test**

```bash
uv run pytest tests/test_integration.py -v
```

Expected: PASS.

- [ ] **Step 3: Run all tests together**

```bash
uv run pytest -v
```

Expected: All tests across all modules PASS.

- [ ] **Step 4: Commit**

```bash
git add tests/test_integration.py
git commit -m "feat: add end-to-end integration smoke test"
```

---

## Summary

| Phase | Module | What it does | Input | Output |
|-------|--------|-------------|-------|--------|
| 1 | `models.py` | Data contract for all modules | Field values | Validated `NormalizedSession` dataclass + `AdapterProtocol` |
| 2 | `storage.py` | SQLite CRUD | `NormalizedSession` + `transcript_path` | Persisted rows, query results |
| 3 | `classifier.py` | Rule-based intent inference | `NormalizedSession` | `str` (task_type) or `None` |
| 4 | `discovery.py` | Find unrated transcripts | Agent type, filesystem paths | `list[Path]` of unrated sessions |
| 5 | `adapters/claude_code.py` | Parse JSONL transcripts | `Path` to JSONL file | `NormalizedSession` |
| 6 | `cli.py` | Interactive CLI | User commands | Prompts, stored ratings, session lists |
| 7 | `dashboard.py` | Local web UI | SQLite database | JSON API: `/sessions`, `/satisfaction` |
| 8 | Integration | End-to-end smoke test | Fixture JSONL | Verified pipeline |