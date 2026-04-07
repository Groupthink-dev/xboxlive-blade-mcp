"""Shared constants, types, and write-gate for Xbox Live Blade MCP server."""

from __future__ import annotations

import logging
import os
import re
from pathlib import Path

logger = logging.getLogger(__name__)

DEFAULT_LIMIT = 25
DEFAULT_TOKEN_DIR = Path.home() / ".xboxlive-blade-mcp"


def get_token_path() -> Path:
    """Return the path to cached Xbox Live OAuth tokens."""
    custom = os.environ.get("XBOX_TOKEN_PATH", "").strip()
    if custom:
        return Path(custom).expanduser()
    return DEFAULT_TOKEN_DIR / "tokens.json"


def get_client_id() -> str:
    """Return the Azure app client ID."""
    value = os.environ.get("XBOX_CLIENT_ID", "").strip()
    if not value:
        raise ValueError(
            "XBOX_CLIENT_ID not configured. "
            "Register an Azure app at https://portal.azure.com and set XBOX_CLIENT_ID."
        )
    return value


def get_client_secret() -> str:
    """Return the Azure app client secret (empty string for public clients)."""
    return os.environ.get("XBOX_CLIENT_SECRET", "").strip()


def is_write_enabled() -> bool:
    """Check if write operations are enabled via env var."""
    return os.environ.get("XBOX_WRITE_ENABLED", "").lower() == "true"


def require_write() -> str | None:
    """Return an error message if writes are disabled, else None."""
    if not is_write_enabled():
        return "Error: Write operations are disabled. Set XBOX_WRITE_ENABLED=true to enable."
    return None


def require_confirm(confirm: bool) -> str | None:
    """Return an error message if confirm is not set, else None."""
    if not confirm:
        return "Error: This is a destructive or security-sensitive operation. Set confirm=true to proceed."
    return None


def scrub_credentials(text: str) -> str:
    """Remove tokens and sensitive data from text."""
    # Strip Bearer tokens
    text = re.sub(r"Bearer\s+[A-Za-z0-9._\-]+", "Bearer ****", text)
    # Strip XBL3.0 tokens
    text = re.sub(r"XBL3\.0\s+x=[^;]+;[A-Za-z0-9._\-]+", "XBL3.0 ****", text)
    # Strip JWT-like tokens (eyJ...)
    text = re.sub(r"eyJ[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]*", "****", text)
    # Strip client secrets
    text = re.sub(r"client_secret=[^\s&]+", "client_secret=****", text, flags=re.IGNORECASE)
    # Strip access tokens in URLs
    text = re.sub(r"access_token=[^\s&]+", "access_token=****", text, flags=re.IGNORECASE)
    return text
