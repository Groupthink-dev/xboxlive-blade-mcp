"""Tests for MCP server tool registration and gate behaviour."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from xboxlive_blade_mcp.server import (
    xbox_console_command,
    xbox_friend_add,
    xbox_friend_remove,
    xbox_send_message,
)


class TestWriteGates:
    """Verify write-gated tools reject when XBOX_WRITE_ENABLED is not set."""

    async def test_send_message_blocked(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("XBOX_WRITE_ENABLED", raising=False)
        result = await xbox_send_message(xuids=["123"], message="hello")
        assert "Write operations are disabled" in result

    async def test_friend_add_blocked(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("XBOX_WRITE_ENABLED", raising=False)
        result = await xbox_friend_add(xuid="123")
        assert "Write operations are disabled" in result

    async def test_friend_remove_blocked(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("XBOX_WRITE_ENABLED", raising=False)
        result = await xbox_friend_remove(xuid="123")
        assert "Write operations are disabled" in result


class TestConfirmGates:
    """Verify confirm-gated tools reject when confirm=False."""

    async def test_console_command_no_confirm(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("XBOX_WRITE_ENABLED", "true")
        result = await xbox_console_command(
            console_id="F400000000000001", command="power_off", confirm=False
        )
        assert "confirm=true" in result

    async def test_friend_remove_no_confirm(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("XBOX_WRITE_ENABLED", "true")
        result = await xbox_friend_remove(xuid="123", confirm=False)
        assert "confirm=true" in result


class TestMessageValidation:
    """Verify message length enforcement."""

    async def test_message_too_long(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("XBOX_WRITE_ENABLED", "true")
        long_msg = "x" * 257
        result = await xbox_send_message(xuids=["123"], message=long_msg)
        assert "256 character limit" in result

    async def test_message_at_limit(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("XBOX_WRITE_ENABLED", "true")
        msg = "x" * 256
        with patch("xboxlive_blade_mcp.server._get_client") as mock_get:
            mock_client = AsyncMock()
            mock_client.send_message.return_value = {"status": "sent", "recipients": 1}
            mock_get.return_value = mock_client
            result = await xbox_send_message(xuids=["123"], message=msg)
            assert "sent" in result.lower()
