from __future__ import annotations

import importlib

from .sportly_provider import SPORT_CONFIG, normalize_event, normalize_sportly_event, serialize


# IDs generated after the league-expansion fix contain the league slug:
#   football-eng.1-123456
# This lets Match Centre resolve the event directly without searching every
# league again. Legacy IDs are also supported for existing cached/bookmarked
# links from the previous deployment.
LEGACY_CONFIG = [
    ("basketball", "basketball", "nba", "National Basketball Association"),
    ("football", "football", "nfl", "National Football League"),
    ("football", "soccer", "eng.1", "English Premier League"),
    ("hockey", "hockey", "nhl", "National Hockey League"),
    ("baseball", "baseball", "mlb", "Major League Baseball"),
    ("tennis", "tennis", "atp", "ATP Tour"),
    ("golf", "golf", "pga", "PGA TOUR"),
    ("mma", "mma", "bellator", "Bellator MMA"),
    ("racing", "racing", "f1", "Formula 1"),
    ("lacrosse", "lacrosse", "pll", "Premier Lacrosse League"),
    ("volleyball", "volleyball", "womens-college-volleyball", "NCAA Women's Volleyball"),
    ("rugby", "rugby", "180659", "Six Nations"),
    ("rugby", "rugby_league", "3", "Rugby League"),
    ("other", "water_polo", "mens-college-water-polo", "NCAA Men's Water Polo"),
    ("other", "field_hockey", "womens-college-field-hockey", "NCAA Women's Field Hockey"),
    ("football", "australian_football", "afl", "Australian Football League"),
]


def _resolve_new_id(event_id: str):
    for sport, module_name, league_id, league_name in SPORT_CONFIG:
        prefix = f"{sport}-{league_id}-"
        if event_id.startswith(prefix):
            return sport, module_name, league_id, league_name, event_id[len(prefix):]
    return None


def _load_one(sport: str, module_name: str, league_id: str, league_name: str, provider_id: str):
    module = importlib.import_module(f"sportly.espn.{module_name}")
    if not hasattr(module, "game"):
        return None

    raw = module.game(provider_id, league_id)
    data = serialize(raw)
    if not isinstance(data, dict):
        return None

    # Sportly Game serialization normally contains the original ESPN event in
    # raw. Accept both Sportly models and an already-unwrapped event payload.
    event = data.get("event")
    if isinstance(event, dict):
        normalized = normalize_event(event, sport, league_id, league_name)
    else:
        normalized = normalize_sportly_event(data, sport, league_id, league_name)

    if normalized:
        return {"success": True, "event": normalized, "raw": data}
    return None


def get_event_details(event_id: str):
    resolved = _resolve_new_id(event_id)
    if resolved:
        sport, module_name, league_id, league_name, provider_id = resolved
        try:
            return _load_one(sport, module_name, league_id, league_name, provider_id)
        except Exception:
            return None

    # Legacy ID format: sport-providerEventId. Keep these links working using
    # the leagues that were present before the expansion deployment.
    if "-" not in event_id:
        return None
    sport, provider_id = event_id.split("-", 1)

    for candidate_sport, module_name, league_id, league_name in LEGACY_CONFIG:
        if candidate_sport != sport:
            continue
        try:
            result = _load_one(sport, module_name, league_id, league_name, provider_id)
            if result:
                return result
        except Exception:
            continue

    return None
