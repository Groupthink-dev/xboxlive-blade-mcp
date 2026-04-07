"""Shared test fixtures for Xbox Live Blade MCP tests."""

from __future__ import annotations

import os
from typing import Any

import pytest


@pytest.fixture(autouse=True)
def _clean_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Ensure no real Xbox credentials leak into tests."""
    for key in list(os.environ.keys()):
        if key.startswith("XBOX_"):
            monkeypatch.delenv(key, raising=False)


@pytest.fixture()
def xbox_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Set up Xbox Live environment."""
    monkeypatch.setenv("XBOX_CLIENT_ID", "test-client-id-12345")
    monkeypatch.setenv("XBOX_CLIENT_SECRET", "test-secret")
    monkeypatch.setenv("XBOX_TOKEN_PATH", "/tmp/xbox-test-tokens.json")


@pytest.fixture()
def xbox_env_write(monkeypatch: pytest.MonkeyPatch, xbox_env: None) -> None:
    """Xbox env with write enabled."""
    monkeypatch.setenv("XBOX_WRITE_ENABLED", "true")


# ---------------------------------------------------------------------------
# Mock data builders
# ---------------------------------------------------------------------------


def make_profile(
    gamertag: str = "TestPlayer",
    xuid: str = "2535428504476914",
    gamerscore: str = "15230",
    account_tier: str = "Gold",
) -> dict[str, Any]:
    return {
        "gamertag": gamertag,
        "xuid": xuid,
        "gamerscore": gamerscore,
        "account_tier": account_tier,
        "tenure_level": "5",
        "preferred_color": "",
        "real_name": "",
        "bio": "Test bio",
    }


def make_achievement(
    name: str = "First Blood",
    gamerscore: int = 50,
    earned: bool = True,
    earned_date: str = "2026-01-15T10:00:00Z",
    rare: bool = False,
    description: str = "Win your first match",
) -> dict[str, Any]:
    return {
        "name": name,
        "gamerscore": gamerscore,
        "earned": earned,
        "earned_date": earned_date if earned else "",
        "rare": rare,
        "description": description,
    }


def make_friend(
    gamertag: str = "FriendPlayer",
    xuid: str = "2535428504476999",
    presence_state: str = "Online",
    current_game: str | None = "Halo Infinite",
    gamerscore: int = 8500,
) -> dict[str, Any]:
    result: dict[str, Any] = {
        "gamertag": gamertag,
        "xuid": xuid,
        "presence_state": presence_state,
        "gamerscore": gamerscore,
    }
    if current_game:
        result["current_game"] = current_game
    return result


def make_game(
    name: str = "Halo Infinite",
    title_id: str = "1240327261",
    total_gamerscore: int = 2000,
    earned_gamerscore: int = 1250,
    last_played: str = "2026-04-01T18:30:00Z",
) -> dict[str, Any]:
    return {
        "name": name,
        "title_id": title_id,
        "total_gamerscore": total_gamerscore,
        "earned_gamerscore": earned_gamerscore,
        "achievement_count": 100,
        "earned_achievements": 62,
        "last_played": last_played,
    }


def make_console(
    name: str = "Living Room Xbox",
    console_id: str = "F400000000000001",
    console_type: str = "XboxSeriesX",
    power_state: str = "On",
) -> dict[str, Any]:
    return {
        "name": name,
        "console_id": console_id,
        "console_type": console_type,
        "power_state": power_state,
        "is_on": power_state == "On",
    }
