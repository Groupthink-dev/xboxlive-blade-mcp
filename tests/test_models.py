"""Tests for models — config parsing, write gates, credential scrubbing."""

from __future__ import annotations

import pytest

from xboxlive_blade_mcp.models import (
    get_client_id,
    get_token_path,
    is_write_enabled,
    require_confirm,
    require_write,
    scrub_credentials,
)


class TestGetClientId:
    def test_returns_env_value(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("XBOX_CLIENT_ID", "abc-123")
        assert get_client_id() == "abc-123"

    def test_raises_when_missing(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("XBOX_CLIENT_ID", raising=False)
        with pytest.raises(ValueError, match="XBOX_CLIENT_ID not configured"):
            get_client_id()


class TestGetTokenPath:
    def test_default_path(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("XBOX_TOKEN_PATH", raising=False)
        path = get_token_path()
        assert path.name == "tokens.json"
        assert ".xboxlive-blade-mcp" in str(path)

    def test_custom_path(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("XBOX_TOKEN_PATH", "/tmp/custom-tokens.json")
        assert str(get_token_path()) == "/tmp/custom-tokens.json"


class TestWriteGate:
    def test_disabled_by_default(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("XBOX_WRITE_ENABLED", raising=False)
        assert is_write_enabled() is False
        assert require_write() is not None

    def test_enabled(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("XBOX_WRITE_ENABLED", "true")
        assert is_write_enabled() is True
        assert require_write() is None

    def test_case_insensitive(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("XBOX_WRITE_ENABLED", "TRUE")
        assert is_write_enabled() is True


class TestConfirmGate:
    def test_not_confirmed(self) -> None:
        assert require_confirm(False) is not None

    def test_confirmed(self) -> None:
        assert require_confirm(True) is None


class TestScrubCredentials:
    def test_bearer_token(self) -> None:
        text = "Bearer eyJhbGciOiJIUzI1NiJ9.payload.signature"
        assert "eyJ" not in scrub_credentials(text)

    def test_xbl3_token(self) -> None:
        text = "XBL3.0 x=1234567890;longTokenString"
        assert "longTokenString" not in scrub_credentials(text)

    def test_client_secret(self) -> None:
        text = "client_secret=super-secret-value&other=safe"
        assert "super-secret-value" not in scrub_credentials(text)

    def test_jwt_token(self) -> None:
        text = "token is eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.payload.sig"
        assert "eyJ" not in scrub_credentials(text)

    def test_preserves_safe_text(self) -> None:
        text = "Connection failed for xbox.example.com"
        assert scrub_credentials(text) == text
