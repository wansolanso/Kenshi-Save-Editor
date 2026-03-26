"""Tests for GameDataResolver."""
from __future__ import annotations

from src.game_data import GameDataResolver


class TestGameDataResolver:
    def test_resolve_known_sid(self):
        resolver = GameDataResolver()
        resolver._names = {"42-gamedata.base": "Iron Club"}
        resolver._loaded = True
        assert resolver.resolve("42-gamedata.base") == "Iron Club"

    def test_resolve_unknown_sid_returns_sid(self):
        resolver = GameDataResolver()
        resolver._loaded = True
        assert resolver.resolve("999-unknown.mod") == "999-unknown.mod"

    def test_resolve_empty_returns_empty(self):
        resolver = GameDataResolver()
        assert resolver.resolve("") == ""

    def test_resolve_or_sid_found(self):
        resolver = GameDataResolver()
        resolver._names = {"42-gamedata.base": "Iron Club"}
        name, found = resolver.resolve_or_sid("42-gamedata.base")
        assert name == "Iron Club"
        assert found is True

    def test_resolve_or_sid_not_found(self):
        resolver = GameDataResolver()
        name, found = resolver.resolve_or_sid("999-unknown.mod")
        assert name == "999-unknown.mod"
        assert found is False

    def test_resolve_or_sid_empty(self):
        resolver = GameDataResolver()
        name, found = resolver.resolve_or_sid("")
        assert name == ""
        assert found is False

    def test_resolve_by_id_found(self):
        resolver = GameDataResolver()
        resolver._names = {"42-gamedata.base": "Iron Club", "100-rebirth.mod": "Sword"}
        assert resolver.resolve_by_id("42") == "Iron Club"

    def test_resolve_by_id_not_found(self):
        resolver = GameDataResolver()
        resolver._names = {}
        assert resolver.resolve_by_id("999") == "999"

    def test_is_loaded_default_false(self):
        resolver = GameDataResolver()
        assert resolver.is_loaded is False

    def test_total_names(self):
        resolver = GameDataResolver()
        resolver._names = {"a": "A", "b": "B"}
        assert resolver.total_names == 2
