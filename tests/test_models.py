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

        adapter = FakeAdapter()
        assert hasattr(adapter, "parse")
        assert callable(adapter.parse)