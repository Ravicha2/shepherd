from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from shepherd.models import NormalizedSession


@dataclass
class PendingSession:
    """A session discovered on disk, parsed, and classified — ready for user rating.

    This is the deep module boundary. Callers receive PendingSession objects
    and never touch adapters, discovery, or classifier directly.
    """

    session: NormalizedSession
    transcript_path: Path
    inferred_type: str | None


class Pipeline:
    """Owns the discovery → parse → classify → rate flow.

    Zero-config for the default case: ``Pipeline()`` just works.
    Override ``db_path`` for tests or custom storage locations.
    """

    def __init__(self, db_path: Path | None = None) -> None:
        # Delayed imports to avoid circular deps; these modules will be
        # implemented in later phases.
        from shepherd.classifier import classify
        from shepherd.storage import Storage
        from shepherd.discovery import SessionDiscovery

        self._storage = Storage(db_path=db_path)
        self._discovery = SessionDiscovery(storage=self._storage)
        self._classify = classify
        self._adapters: dict[str, object] = {}

    def _register_adapters(self) -> None:
        from shepherd.adapters.claude_code import ClaudeCodeAdapter

        self._adapters["claude_code"] = ClaudeCodeAdapter()

    def find_unrated(self) -> list[PendingSession]:
        """Discover, parse, and classify all unrated sessions.

        Returns PendingSession objects with pre-computed intent classification.
        """
        raise NotImplementedError("Implemented in Phase 6")

    def rate(
        self,
        pending: PendingSession,
        task_type: str,
        intent_confirmed: bool,
        satisfaction: str,
    ) -> None:
        """Store a user-confirmed rating for a pending session."""
        raise NotImplementedError("Implemented in Phase 6")