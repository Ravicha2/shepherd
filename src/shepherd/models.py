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