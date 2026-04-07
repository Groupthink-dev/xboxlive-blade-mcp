# Xbox Live Blade MCP — LLM Skill Guide

## Token Efficiency Rules (MANDATORY)

1. **Use `xbox_games` not repeated `xbox_game_details`** — game library returns achievement progress in one call.
2. **Use `xbox_friends` for social overview** — includes presence state, no need to call `xbox_presence` per-friend.
3. **Use `xbox_achievement_summary` before `xbox_achievements`** — summary is one lightweight call vs full achievement list.
4. **Use `xbox_games_recent` with small `limit`** — default 10, not the full library.
5. **Pass `xuid`** when targeting another user — avoids redundant gamertag→XUID resolution.
6. **Use `limit` parameter** — all list tools accept `limit` to cap results.
7. **Check `xbox_info` first** — confirms auth is valid before making data calls.
8. **Use `title_id` filter** — `xbox_clips` and `xbox_screenshots` accept `title_id` to narrow results.

## Quick Start — 5 Most Common Operations

```
xbox_info                                      # Auth status, gamertag, write gate
xbox_profile                                   # Your profile with gamerscore
xbox_friends limit=10                          # Friends with online status
xbox_games_recent limit=5                      # Recently played games
xbox_achievements title_id="1240327261"        # Achievements for a game
```

## Tool Reference

### Read Tools (17) — no gate required

| Tool | Purpose | Contract | Best for |
|------|---------|----------|----------|
| `xbox_info` | Auth status, gamertag, write gate | — | Session start |
| `xbox_profile` | Profile: gamertag, gamerscore, tier, bio | profile | User lookup |
| `xbox_search_users` | Search users by gamertag | search_users | Finding players |
| `xbox_achievements` | Achievements for a game with earned status | achievements | Per-game progress |
| `xbox_achievement_summary` | Overall gamerscore, titles, completion % | achievement_summary | Quick stats |
| `xbox_achievement_compare` | Compare achievements between two users | achievement_compare | Competitive |
| `xbox_achievement_groups` | Per-group completion (base, DLC) | achievement_groups | Completionists |
| `xbox_games` | Full game library with playtime | games_played | Library overview |
| `xbox_games_recent` | Recently played (last N) | games_recent | Activity check |
| `xbox_games_purchased` | Owned/purchased titles | games_purchased | Entitlements |
| `xbox_game_details` | Store metadata for a product | game_details | Title info |
| `xbox_search_games` | Search Xbox Store catalog | search_games | Discovery |
| `xbox_friends` | Friends with online/game status | friends | Social overview |
| `xbox_presence` | Detailed presence for one user | presence | Is X online? |
| `xbox_inbox` | Message inbox | — | Check messages |
| `xbox_clips` | Game clips with URIs | — | Media review |
| `xbox_screenshots` | Screenshots with URIs | — | Media review |
| `xbox_consoles` | Registered consoles + power state | devices | Console status |

### Write Tools (3) — require XBOX_WRITE_ENABLED=true

| Tool | Purpose | Contract | Gate |
|------|---------|----------|------|
| `xbox_send_message` | Send text message (max 256 chars) | send_message | write |
| `xbox_friend_add` | Add friend / accept request | friend_add | write |
| `xbox_console_command` | SmartGlass: power, volume, media, nav | — | write+confirm |

### Confirm-Gated Tools (1) — require write + confirm=true

| Tool | Purpose | Why gated |
|------|---------|-----------|
| `xbox_friend_remove` | Remove a friend | Social relationship change |

## Workflow Examples

### Who's online?
```
xbox_friends limit=20
xbox_presence xuid="2535428504476914"
```

### Game progress check
```
xbox_games_recent limit=5
xbox_achievements title_id="1240327261"
xbox_achievement_summary
```

### Find and message a player
```
xbox_search_users query="CoolGamer"
xbox_send_message xuids=["2535428504476914"] message="GG!"
```

### Console control
```
xbox_consoles
xbox_console_command console_id="F400000000000001" command="power_on" confirm=true
```

### Achievement hunting
```
xbox_achievement_summary
xbox_games limit=5
xbox_achievements title_id="1240327261" limit=50
xbox_achievement_compare title_id="1240327261" xuid="2535428504476914"
```

## Security Notes

- Write ops require `XBOX_WRITE_ENABLED=true` environment variable
- SmartGlass power/reboot commands require explicit `confirm=true`
- Friend removal requires `confirm=true`
- OAuth tokens are cached locally (default: `~/.xboxlive-blade-mcp/tokens.json`)
- Tokens auto-refresh — re-auth only needed if tokens fully expire (extended inactivity)
- All error output has credentials scrubbed (XBL3.0 tokens, JWTs, client secrets)
- No Xbox credentials are ever included in tool responses
