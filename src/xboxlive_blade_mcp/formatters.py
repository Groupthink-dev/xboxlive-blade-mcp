"""Token-efficient output formatters for Xbox Live Blade MCP server.

All formatters return compact strings optimised for LLM consumption:
- One line per entity/item
- Pipe-delimited fields
- Null-field omission
"""

from __future__ import annotations

from typing import Any


def _pick(data: dict[str, Any], *keys: str) -> list[str]:
    """Extract non-None key=value pairs from a dict."""
    parts = []
    for k in keys:
        v = data.get(k)
        if v is not None and v != "":
            parts.append(f"{k}={v}")
    return parts


def _ts_short(ts: str) -> str:
    """Shorten an ISO timestamp to date or datetime."""
    if not ts:
        return "?"
    if "T" in ts:
        return ts[:16]  # YYYY-MM-DDTHH:MM
    return ts[:10]


# ---------------------------------------------------------------------------
# Info
# ---------------------------------------------------------------------------


def format_info(data: dict[str, Any]) -> str:
    """Format xbox_info results."""
    parts = []
    if data.get("gamertag"):
        parts.append(f"gamertag={data['gamertag']}")
    if data.get("xuid"):
        parts.append(f"xuid={data['xuid']}")
    parts.append(f"auth={'valid' if data.get('authenticated') else 'invalid'}")
    if data.get("token_expires"):
        parts.append(f"token_expires={_ts_short(data['token_expires'])}")
    return " | ".join(parts)


# ---------------------------------------------------------------------------
# Profile
# ---------------------------------------------------------------------------


def format_profile(profile: dict[str, Any]) -> str:
    """Format a user profile as a compact string."""
    parts = [profile.get("gamertag", "?")]
    parts.extend(_pick(
        profile,
        "xuid", "gamerscore", "account_tier", "tenure_level",
        "reputation", "preferred_color", "real_name",
    ))
    if profile.get("bio"):
        bio = profile["bio"][:80]
        parts.append(f"bio={bio}")
    return " | ".join(str(p) for p in parts)


# ---------------------------------------------------------------------------
# Achievements
# ---------------------------------------------------------------------------


def format_achievements(achievements: list[dict[str, Any]], title: str = "") -> str:
    """Format achievement list as compact lines."""
    if not achievements:
        return "(no achievements)"
    lines = []
    if title:
        earned = sum(1 for a in achievements if a.get("earned"))
        total_g = sum(a.get("gamerscore", 0) for a in achievements)
        earned_g = sum(a.get("gamerscore", 0) for a in achievements if a.get("earned"))
        lines.append(f"## {title} ({earned}/{len(achievements)} unlocked, {earned_g}/{total_g}G)")
    for a in achievements:
        parts = [a.get("name", "?")]
        if a.get("gamerscore"):
            parts.append(f"{a['gamerscore']}G")
        if a.get("earned"):
            parts.append(f"earned={_ts_short(a.get('earned_date', ''))}")
        else:
            parts.append("locked")
        if a.get("rare"):
            parts.append("rare")
        if a.get("description"):
            parts.append(a["description"][:60])
        lines.append(" | ".join(str(p) for p in parts))
    return "\n".join(lines)


def format_achievement_summary(summary: dict[str, Any]) -> str:
    """Format achievement summary."""
    parts = []
    parts.extend(_pick(
        summary,
        "gamerscore", "total_achievements", "earned_achievements",
        "completion_percentage", "titles_played",
    ))
    return " | ".join(parts)


# ---------------------------------------------------------------------------
# Games
# ---------------------------------------------------------------------------


def format_games(games: list[dict[str, Any]]) -> str:
    """Format game list as compact lines."""
    if not games:
        return "(no games)"
    lines = []
    for g in games:
        parts = [g.get("name", "?")]
        parts.extend(_pick(
            g,
            "title_id", "total_gamerscore", "earned_gamerscore",
            "achievement_count", "earned_achievements",
        ))
        if g.get("last_played"):
            parts.append(f"last_played={_ts_short(g['last_played'])}")
        if g.get("total_playtime_minutes"):
            hours = g["total_playtime_minutes"] / 60
            parts.append(f"playtime={hours:.1f}h")
        lines.append(" | ".join(str(p) for p in parts))
    return "\n".join(lines)


def format_game_details(game: dict[str, Any]) -> str:
    """Format detailed game info."""
    parts = [game.get("name", "?")]
    parts.extend(_pick(
        game,
        "title_id", "product_id", "publisher", "developer",
        "release_date", "category", "price",
    ))
    if game.get("description"):
        parts.append(f"desc={game['description'][:120]}")
    return " | ".join(str(p) for p in parts)


# ---------------------------------------------------------------------------
# Social
# ---------------------------------------------------------------------------


def format_friends(friends: list[dict[str, Any]]) -> str:
    """Format friends list as compact lines."""
    if not friends:
        return "(no friends)"
    lines = []
    for f in friends:
        parts = [f.get("gamertag", "?")]
        status = f.get("presence_state", "unknown")
        parts.append(status)
        if f.get("xuid"):
            parts.append(f"xuid={f['xuid']}")
        if f.get("current_game"):
            parts.append(f"playing={f['current_game']}")
        if f.get("last_seen"):
            parts.append(f"last_seen={_ts_short(f['last_seen'])}")
        if f.get("gamerscore"):
            parts.append(f"gamerscore={f['gamerscore']}")
        lines.append(" | ".join(str(p) for p in parts))
    return "\n".join(lines)


def format_presence(presence: dict[str, Any]) -> str:
    """Format presence data."""
    parts = [presence.get("gamertag", "?")]
    parts.append(presence.get("state", "unknown"))
    if presence.get("current_game"):
        parts.append(f"playing={presence['current_game']}")
    if presence.get("rich_presence"):
        parts.append(presence["rich_presence"])
    if presence.get("last_seen"):
        parts.append(f"last_seen={_ts_short(presence['last_seen'])}")
    return " | ".join(str(p) for p in parts)


def format_search_results(results: list[dict[str, Any]]) -> str:
    """Format user search results."""
    if not results:
        return "(no results)"
    lines = []
    for r in results:
        parts = [r.get("gamertag", "?")]
        parts.extend(_pick(r, "xuid", "gamerscore", "reputation"))
        lines.append(" | ".join(str(p) for p in parts))
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Messages
# ---------------------------------------------------------------------------


def format_inbox(messages: list[dict[str, Any]]) -> str:
    """Format message inbox as compact lines."""
    if not messages:
        return "(no messages)"
    lines = []
    for m in messages:
        parts = []
        if m.get("sender"):
            parts.append(f"from={m['sender']}")
        if m.get("sent"):
            parts.append(_ts_short(m["sent"]))
        if m.get("summary"):
            parts.append(m["summary"][:80])
        if m.get("is_read") is False:
            parts.append("UNREAD")
        lines.append(" | ".join(str(p) for p in parts))
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Media (clips / screenshots)
# ---------------------------------------------------------------------------


def format_clips(clips: list[dict[str, Any]]) -> str:
    """Format game clips as compact lines."""
    if not clips:
        return "(no clips)"
    lines = []
    for c in clips:
        parts = [c.get("title_name", "?")]
        if c.get("date_recorded"):
            parts.append(_ts_short(c["date_recorded"]))
        parts.extend(_pick(c, "duration_seconds", "views", "likes", "clip_id"))
        if c.get("uri"):
            parts.append(f"uri={c['uri']}")
        lines.append(" | ".join(str(p) for p in parts))
    return "\n".join(lines)


def format_screenshots(screenshots: list[dict[str, Any]]) -> str:
    """Format screenshots as compact lines."""
    if not screenshots:
        return "(no screenshots)"
    lines = []
    for s in screenshots:
        parts = [s.get("title_name", "?")]
        if s.get("date_taken"):
            parts.append(_ts_short(s["date_taken"]))
        parts.extend(_pick(s, "views", "likes", "screenshot_id"))
        if s.get("uri"):
            parts.append(f"uri={s['uri']}")
        lines.append(" | ".join(str(p) for p in parts))
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Consoles (SmartGlass)
# ---------------------------------------------------------------------------


def format_consoles(consoles: list[dict[str, Any]]) -> str:
    """Format console list as compact lines."""
    if not consoles:
        return "(no consoles)"
    lines = []
    for c in consoles:
        parts = [c.get("name", "?")]
        parts.extend(_pick(c, "console_id", "console_type", "power_state"))
        if c.get("is_on") is True:
            parts.append("ON")
        elif c.get("is_on") is False:
            parts.append("OFF")
        lines.append(" | ".join(str(p) for p in parts))
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Store / Catalog
# ---------------------------------------------------------------------------


def format_store_results(products: list[dict[str, Any]]) -> str:
    """Format store search results as compact lines."""
    if not products:
        return "(no results)"
    lines = []
    for p in products:
        parts = [p.get("name", "?")]
        parts.extend(_pick(p, "product_id", "price", "category", "publisher"))
        lines.append(" | ".join(str(pp) for pp in parts))
    return "\n".join(lines)
