"""Tests for token-efficient output formatters."""

from __future__ import annotations

from xboxlive_blade_mcp.formatters import (
    format_achievement_summary,
    format_achievements,
    format_clips,
    format_consoles,
    format_friends,
    format_game_details,
    format_games,
    format_inbox,
    format_info,
    format_presence,
    format_screenshots,
    format_search_results,
    format_store_results,
)

from .conftest import (
    make_achievement,
    make_console,
    make_friend,
    make_game,
    make_profile,
)


class TestFormatInfo:
    def test_authenticated(self) -> None:
        result = format_info({"gamertag": "TestPlayer", "xuid": "123", "authenticated": True})
        assert "gamertag=TestPlayer" in result
        assert "auth=valid" in result

    def test_unauthenticated(self) -> None:
        result = format_info({"authenticated": False})
        assert "auth=invalid" in result


class TestFormatProfile:
    def test_basic_profile(self) -> None:
        from xboxlive_blade_mcp.formatters import format_profile

        result = format_profile(make_profile())
        assert "TestPlayer" in result
        assert "gamerscore=15230" in result
        assert "account_tier=Gold" in result


class TestFormatAchievements:
    def test_earned_achievement(self) -> None:
        achievements = [make_achievement(earned=True)]
        result = format_achievements(achievements, title="Halo")
        assert "## Halo" in result
        assert "First Blood" in result
        assert "earned=" in result

    def test_locked_achievement(self) -> None:
        achievements = [make_achievement(earned=False)]
        result = format_achievements(achievements)
        assert "locked" in result

    def test_empty(self) -> None:
        assert "(no achievements)" in format_achievements([])

    def test_summary_header(self) -> None:
        achievements = [
            make_achievement(name="A", gamerscore=50, earned=True),
            make_achievement(name="B", gamerscore=100, earned=False),
        ]
        result = format_achievements(achievements, title="TestGame")
        assert "1/2 unlocked" in result
        assert "50/150G" in result


class TestFormatAchievementSummary:
    def test_basic(self) -> None:
        result = format_achievement_summary({
            "gamerscore": "15000",
            "titles_played": 42,
            "completion_percentage": 65.5,
        })
        assert "gamerscore=15000" in result
        assert "titles_played=42" in result


class TestFormatGames:
    def test_game_with_progress(self) -> None:
        result = format_games([make_game()])
        assert "Halo Infinite" in result
        assert "earned_gamerscore=1250" in result
        assert "last_played=" in result

    def test_empty(self) -> None:
        assert "(no games)" in format_games([])


class TestFormatFriends:
    def test_online_friend(self) -> None:
        result = format_friends([make_friend()])
        assert "FriendPlayer" in result
        assert "Online" in result
        assert "playing=Halo Infinite" in result

    def test_empty(self) -> None:
        assert "(no friends)" in format_friends([])


class TestFormatPresence:
    def test_online_playing(self) -> None:
        result = format_presence({
            "gamertag": "Player",
            "state": "Online",
            "current_game": "Forza",
            "rich_presence": "Racing at Silverstone",
        })
        assert "Player" in result
        assert "Online" in result
        assert "playing=Forza" in result
        assert "Racing at Silverstone" in result


class TestFormatSearchResults:
    def test_results(self) -> None:
        result = format_search_results([{"gamertag": "Found", "xuid": "123"}])
        assert "Found" in result

    def test_empty(self) -> None:
        assert "(no results)" in format_search_results([])


class TestFormatInbox:
    def test_message(self) -> None:
        result = format_inbox([{
            "sender": "Friend",
            "sent": "2026-04-07T10:00:00Z",
            "summary": "Hey, wanna play?",
            "is_read": False,
        }])
        assert "Friend" in result
        assert "UNREAD" in result

    def test_empty(self) -> None:
        assert "(no messages)" in format_inbox([])


class TestFormatClips:
    def test_clip(self) -> None:
        result = format_clips([{
            "title_name": "Halo Infinite",
            "date_recorded": "2026-04-01T12:00:00Z",
            "duration_seconds": 30,
            "views": 42,
            "clip_id": "abc",
        }])
        assert "Halo Infinite" in result
        assert "duration_seconds=30" in result


class TestFormatScreenshots:
    def test_screenshot(self) -> None:
        result = format_screenshots([{
            "title_name": "Forza",
            "date_taken": "2026-04-01T12:00:00Z",
            "views": 10,
            "screenshot_id": "def",
        }])
        assert "Forza" in result


class TestFormatConsoles:
    def test_console(self) -> None:
        result = format_consoles([make_console()])
        assert "Living Room Xbox" in result
        assert "XboxSeriesX" in result
        assert "ON" in result

    def test_empty(self) -> None:
        assert "(no consoles)" in format_consoles([])


class TestFormatStoreResults:
    def test_product(self) -> None:
        result = format_store_results([{"name": "Halo", "product_id": "123", "publisher": "Xbox Game Studios"}])
        assert "Halo" in result

    def test_empty(self) -> None:
        assert "(no results)" in format_store_results([])


class TestFormatGameDetails:
    def test_details(self) -> None:
        result = format_game_details({
            "name": "Halo Infinite",
            "product_id": "9NP1P1WFS0LB",
            "publisher": "Xbox Game Studios",
            "developer": "343 Industries",
            "description": "Master Chief returns in Halo Infinite",
        })
        assert "Halo Infinite" in result
        assert "publisher=Xbox Game Studios" in result
        assert "desc=" in result
