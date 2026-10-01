from __future__ import annotations

import importlib
import json
import time
from datetime import datetime, timezone
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


# Sportly scoreboard() returns Game models. The original provider payload is
# normally preserved in Game.raw. Cricket is handled separately because the
# normal ESPN Site API cricket scoreboard endpoint returns 404.
SPORT_CONFIG = [
    ("basketball", "basketball", "nba"),
    ("football", "football", "nfl"),
    ("football", "soccer", "eng.1"),
    ("hockey", "hockey", "nhl"),
    ("baseball", "baseball", "mlb"),
    ("tennis", "tennis", "atp"),
    ("golf", "golf", "pga"),
    ("mma", "mma", "bellator"),
    ("racing", "racing", "f1"),
    ("lacrosse", "lacrosse", "pll"),
    ("volleyball", "volleyball", "womens-college-volleyball"),
    ("rugby", "rugby", "180659"),
    ("rugby", "rugby_league", "3"),
    ("other", "water_polo", "mens-college-water-polo"),
    ("other", "field_hockey", "womens-college-field-hockey"),
    ("other", "australian_football", "afl"),
]

CACHE_TTL_SECONDS = 20
_live_cache: dict[str, Any] | None = None
_live_cache_at = 0.0


def serialize(value: Any) -> Any:
    if value is None:
        return None
    if hasattr(value, "model_dump"):
        try:
            return value.model_dump(mode="json")
        except TypeError:
            try:
                return value.model_dump()
            except Exception:
                pass
    if hasattr(value, "dict"):
        try:
            return value.dict()
        except Exception:
            pass
    if isinstance(value, list):
        return [serialize(item) for item in value]
    if isinstance(value, tuple):
        return [serialize(item) for item in value]
    if isinstance(value, dict):
        return {str(key): serialize(item) for key, item in value.items()}
    if isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, datetime):
        return value.isoformat()
    return str(value)


def first_value(*values: Any) -> Any:
    for value in values:
        if value is not None and value != "":
            return value
    return None


def safe_list(value: Any) -> list:
    return value if isinstance(value, list) else []


def fetch_json(url: str, timeout: int = 10) -> Any:
    request = Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (compatible; ScorePulse/1.0)",
            "Accept": "application/json",
        },
    )
    with urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def extract_events(data: Any) -> list[dict[str, Any]]:
    data = serialize(data)
    if isinstance(data, dict):
        events = data.get("events")
        if isinstance(events, list):
            return [x for x in events if isinstance(x, dict)]
        for key in ("data", "content", "scoreboard"):
            nested = data.get(key)
            if isinstance(nested, dict):
                nested_events = nested.get("events")
                if isinstance(nested_events, list):
                    return [x for x in nested_events if isinstance(x, dict)]
            if isinstance(nested, list):
                return [x for x in nested if isinstance(x, dict)]
    if isinstance(data, list):
        return [x for x in data if isinstance(x, dict)]
    return []


def get_competitors(event: dict[str, Any]) -> list[dict[str, Any]]:
    competitions = safe_list(event.get("competitions"))
    if competitions and isinstance(competitions[0], dict):
        competitors = safe_list(competitions[0].get("competitors"))
        if competitors:
            return [x for x in competitors if isinstance(x, dict)]
    return [x for x in safe_list(event.get("competitors")) if isinstance(x, dict)]


def get_team(competitor: dict[str, Any]) -> dict[str, Any]:
    team = competitor.get("team") or {}
    if not isinstance(team, dict):
        team = {}
    logos = safe_list(team.get("logos"))
    return {
        "id": str(first_value(team.get("id"), competitor.get("id"), "unknown")),
        "name": first_value(team.get("displayName"), team.get("name"), team.get("shortDisplayName"), team.get("nickname"), "Unknown"),
        "shortName": first_value(team.get("abbreviation"), team.get("shortDisplayName"), team.get("nickname"), team.get("name"), "Unknown"),
        "logo": first_value(
            team.get("logo"),
            logos[0].get("href") if logos and isinstance(logos[0], dict) else None,
        ),
    }


def get_status(event: dict[str, Any]) -> str:
    status = event.get("status") or {}
    if not isinstance(status, dict):
        status = {}
    status_type = status.get("type") or {}
    if not isinstance(status_type, dict):
        status_type = {}
    state = str(first_value(status_type.get("state"), status.get("state"), "")).lower()
    name = str(first_value(status_type.get("name"), status.get("name"), "")).lower()
    detail = str(first_value(status_type.get("detail"), status.get("detail"), "")).lower()
    combined = f"{state} {name} {detail}"
    if "postpon" in combined:
        return "postponed"
    if "cancel" in combined:
        return "cancelled"
    if state in {"in", "live"}:
        return "halftime" if "halftime" in combined or "half time" in combined else "live"
    if state in {"post", "finished", "complete", "completed"} or "final" in combined:
        return "finished"
    return "scheduled"


def get_score(event: dict[str, Any], competitors: list[dict[str, Any]]) -> dict[str, Any] | None:
    if not competitors:
        return None
    home = away = None
    for competitor in competitors:
        side = str(competitor.get("homeAway", "")).lower()
        linescores = safe_list(competitor.get("linescores"))
        latest = linescores[-1] if linescores and isinstance(linescores[-1], dict) else {}
        score = first_value(
            competitor.get("score"),
            latest.get("displayValue") if isinstance(latest, dict) else None,
            latest.get("value") if isinstance(latest, dict) else None,
        )
        if side == "home":
            home = score
        elif side == "away":
            away = score
    if home is None and away is None:
        return None
    status = event.get("status") or {}
    if not isinstance(status, dict):
        status = {}
    status_type = status.get("type") or {}
    if not isinstance(status_type, dict):
        status_type = {}
    return {
        "home": first_value(home, "-"),
        "away": first_value(away, "-"),
        "period": first_value(status.get("displayClock"), status.get("clock"), status_type.get("shortDetail"), status_type.get("detail"), status.get("detail")),
    }


def get_league_data(event: dict[str, Any], league_id: str, league_name: str | None = None) -> dict[str, Any]:
    competitions = safe_list(event.get("competitions"))
    competition = competitions[0] if competitions and isinstance(competitions[0], dict) else {}
    event_league = event.get("league") or {}
    if not isinstance(event_league, dict):
        event_league = {}
    competition_league = competition.get("league") or {}
    if not isinstance(competition_league, dict):
        competition_league = {}
    league = {**competition_league, **event_league}
    logos = safe_list(league.get("logos"))
    return {
        "id": str(first_value(league.get("id"), league_id)),
        "name": first_value(league.get("name"), league.get("shortName"), league_name, league_id),
        "country": first_value(league.get("country")),
        "logo": first_value(league.get("logo"), logos[0].get("href") if logos and isinstance(logos[0], dict) else None),
    }


def normalize_event(event: dict[str, Any], sport: str, league_id: str, league_name: str | None = None) -> dict[str, Any] | None:
    if not isinstance(event, dict):
        return None
    event_id = event.get("id")
    if not event_id:
        return None
    competitors = get_competitors(event)
    if len(competitors) < 2:
        return None
    home = next((x for x in competitors if str(x.get("homeAway", "")).lower() == "home"), None)
    away = next((x for x in competitors if str(x.get("homeAway", "")).lower() == "away"), None)
    if home is None or away is None:
        home, away = competitors[0], competitors[1]
    competitions = safe_list(event.get("competitions"))
    competition = competitions[0] if competitions and isinstance(competitions[0], dict) else {}
    broadcasts = safe_list(competition.get("broadcasts"))
    broadcast = None
    if broadcasts and isinstance(broadcasts[0], dict):
        names = safe_list(broadcasts[0].get("names"))
        if names:
            broadcast = names[0]
    venue = competition.get("venue") or {}
    if not isinstance(venue, dict):
        venue = {}
    return {
        "id": f"{sport}-{event_id}",
        "sport": sport,
        "league": get_league_data(event, league_id, league_name),
        "status": get_status(event),
        "startTime": first_value(event.get("date"), event.get("startDate"), datetime.now(timezone.utc).isoformat()),
        "home": get_team(home),
        "away": get_team(away),
        "score": get_score(event, competitors),
        "venue": first_value(venue.get("fullName"), venue.get("name")),
        "broadcast": broadcast,
    }


def normalize_sportly_event(event: dict[str, Any], sport: str, league_id: str, league_name: str | None = None) -> dict[str, Any] | None:
    """Fallback for Sportly's serialized Game model."""
    if not isinstance(event, dict) or not event.get("id"):
        return None
    raw = event.get("raw") or {}
    if isinstance(raw, dict) and raw.get("competitions"):
        normalized = normalize_event(raw, sport, league_id, league_name)
        if normalized:
            return normalized
    competitors = [x for x in safe_list(event.get("competitors")) if isinstance(x, dict)]
    if len(competitors) < 2:
        return None
    home = next((x for x in competitors if str(x.get("homeAway", "")).lower() == "home"), None)
    away = next((x for x in competitors if str(x.get("homeAway", "")).lower() == "away"), None)
    if home is None or away is None:
        first, second = competitors[0], competitors[1]
        if str(first.get("homeAway", "")).lower() == "away":
            home, away = second, first
        else:
            home, away = first, second
    status = event.get("status") or {}
    if not isinstance(status, dict):
        status = {}
    state = str(status.get("state") or "").lower()
    detail = str(first_value(status.get("detail"), status.get("shortDetail"), ""))
    combined = f"{state} {detail}".lower()
    if "postpon" in combined:
        normalized_status = "postponed"
    elif "cancel" in combined:
        normalized_status = "cancelled"
    elif state in {"in", "live"}:
        normalized_status = "halftime" if "half" in combined else "live"
    elif state in {"post", "finished", "complete"} or bool(status.get("completed")):
        normalized_status = "finished"
    else:
        normalized_status = "scheduled"
    def sportly_team(c: dict[str, Any]) -> dict[str, Any]:
        team = c.get("team") or {}
        if not isinstance(team, dict):
            team = {}
        logos = safe_list(team.get("logos"))
        return {
            "id": str(first_value(team.get("id"), c.get("id"), "unknown")),
            "name": first_value(team.get("displayName"), team.get("name"), team.get("shortDisplayName"), team.get("nickname"), "Unknown"),
            "shortName": first_value(team.get("abbreviation"), team.get("shortDisplayName"), team.get("nickname"), team.get("name"), "Unknown"),
            "logo": first_value(team.get("logo"), logos[0].get("href") if logos and isinstance(logos[0], dict) else None),
        }
    hs = first_value(home.get("score"))
    aw = first_value(away.get("score"))
    score = None
    if hs is not None or aw is not None:
        score = {"home": first_value(hs, "-"), "away": first_value(aw, "-"), "period": first_value(status.get("clock"), status.get("displayClock"), status.get("detail"))}
    raw_competitions = safe_list(raw.get("competitions")) if isinstance(raw, dict) else []
    raw_comp = raw_competitions[0] if raw_competitions and isinstance(raw_competitions[0], dict) else {}
    venue = raw_comp.get("venue") or {}
    if not isinstance(venue, dict):
        venue = {}
    return {
        "id": f"{sport}-{event['id']}",
        "sport": sport,
        "league": {"id": str(league_id), "name": first_value(league_name, league_id), "country": None, "logo": None},
        "status": normalized_status,
        "startTime": first_value(event.get("date"), datetime.now(timezone.utc).isoformat()),
        "home": sportly_team(home),
        "away": sportly_team(away),
        "score": score,
        "venue": first_value(venue.get("fullName"), venue.get("name")),
        "broadcast": None,
    }


def load_sportly_module(module_name: str):
    return importlib.import_module(f"sportly.espn.{module_name}")


def _fetch_sportly_events() -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    events: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []
    for sport, module_name, league in SPORT_CONFIG:
        try:
            module = load_sportly_module(module_name)
            raw_dict = serialize(module.scoreboard(league))
            league_name = None
            if isinstance(raw_dict, dict):
                leagues = safe_list(raw_dict.get("leagues"))
                if leagues and isinstance(leagues[0], dict):
                    league_name = first_value(leagues[0].get("name"), leagues[0].get("shortName"))
            for event in extract_events(raw_dict):
                normalized = None
                raw_event = event.get("raw")
                if isinstance(raw_event, dict) and raw_event.get("competitions"):
                    normalized = normalize_event(raw_event, sport, league, league_name)
                if normalized is None:
                    normalized = normalize_sportly_event(event, sport, league, league_name)
                if normalized:
                    events.append(normalized)
        except Exception as exc:
            errors.append({"sport": sport, "league": league, "error": str(exc)})
    return events, errors


def normalize_cricket_event(event: dict[str, Any], league_id: str = "icc-cricket", league_name: str | None = None) -> dict[str, Any] | None:
    if not isinstance(event, dict) or not event.get("id"):
        return None
    competitions = safe_list(event.get("competitions"))
    competition = competitions[0] if competitions and isinstance(competitions[0], dict) else {}
    competitors = [x for x in safe_list(competition.get("competitors")) if isinstance(x, dict)]
    if not competitors:
        competitors = [x for x in safe_list(event.get("competitors")) if isinstance(x, dict)]
    if len(competitors) < 2:
        return None
    home = next((x for x in competitors if str(x.get("homeAway", "")).lower() == "home"), competitors[0])
    away = next((x for x in competitors if str(x.get("homeAway", "")).lower() == "away"), competitors[1])
    def cricket_team(c: dict[str, Any]) -> dict[str, Any]:
        team = c.get("team") or {}
        if not isinstance(team, dict):
            team = {}
        logos = safe_list(team.get("logos"))
        return {
            "id": str(first_value(team.get("id"), c.get("id"), "unknown")),
            "name": first_value(team.get("displayName"), team.get("name"), team.get("shortDisplayName"), team.get("abbreviation"), "Unknown"),
            "shortName": first_value(team.get("abbreviation"), team.get("shortDisplayName"), team.get("name"), "Unknown"),
            "logo": first_value(team.get("logo"), logos[0].get("href") if logos and isinstance(logos[0], dict) else None),
        }
    status = event.get("status") or {}
    if not isinstance(status, dict):
        status = {}
    st = status.get("type") or {}
    if not isinstance(st, dict):
        st = {}
    combined = f"{st.get('state','')} {status.get('state','')} {st.get('detail','')} {status.get('detail','')}".lower()
    state = str(first_value(st.get("state"), status.get("state"), "")).lower()
    if "postpon" in combined:
        normalized_status = "postponed"
    elif "cancel" in combined:
        normalized_status = "cancelled"
    elif state in {"in", "live"}:
        normalized_status = "live"
    elif state in {"post", "finished", "complete", "completed"}:
        normalized_status = "finished"
    else:
        normalized_status = "scheduled"
    hs, aw = first_value(home.get("score")), first_value(away.get("score"))
    score = None
    if hs is not None or aw is not None:
        score = {"home": first_value(hs, "-"), "away": first_value(aw, "-"), "period": first_value(status.get("detail"), status.get("displayClock"), status.get("clock"))}
    league = event.get("league") or competition.get("league") or {}
    if not isinstance(league, dict):
        league = {}
    venue = competition.get("venue") or {}
    if not isinstance(venue, dict):
        venue = {}
    return {
        "id": f"cricket-{event['id']}",
        "sport": "cricket",
        "league": {"id": str(first_value(league.get("id"), league_id)), "name": first_value(league.get("name"), league.get("shortName"), league_name, "Cricket"), "country": first_value(league.get("country")), "logo": first_value(league.get("logo"))},
        "status": normalized_status,
        "startTime": first_value(event.get("date"), event.get("startDate"), datetime.now(timezone.utc).isoformat()),
        "home": cricket_team(home),
        "away": cricket_team(away),
        "score": score,
        "venue": first_value(venue.get("fullName"), venue.get("name")),
        "broadcast": None,
    }


def _fetch_cricket_events() -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    events: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []
    url = "https://sports.core.api.espn.com/v2/sports/cricket/leagues/icc-cricket/events?limit=100"
    try:
        payload = fetch_json(url)
        items = safe_list(payload.get("items")) if isinstance(payload, dict) else []
        if not items and isinstance(payload, dict):
            items = safe_list(payload.get("events"))
        for item in items:
            if not isinstance(item, dict):
                continue
            event = item
            ref = item.get("$ref")
            if ref:
                try:
                    event = fetch_json(ref)
                except Exception:
                    continue
            normalized = normalize_cricket_event(event, "icc-cricket", "ICC Cricket")
            if normalized:
                events.append(normalized)
    except HTTPError as exc:
        errors.append({"sport": "cricket", "league": "icc-cricket", "error": f"ESPN cricket Core API HTTP {exc.code}"})
    except URLError as exc:
        errors.append({"sport": "cricket", "league": "icc-cricket", "error": f"ESPN cricket Core API unavailable: {exc.reason}"})
    except Exception as exc:
        errors.append({"sport": "cricket", "league": "icc-cricket", "error": str(exc)})
    return events, errors


def _fetch_live_events() -> dict[str, Any]:
    sportly_events, sportly_errors = _fetch_sportly_events()
    cricket_events, cricket_errors = _fetch_cricket_events()
    events = sportly_events + cricket_events
    errors = sportly_errors + cricket_errors
    unique_events: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    for event in events:
        event_id = str(event.get("id"))
        if event_id in seen_ids:
            continue
        seen_ids.add(event_id)
        unique_events.append(event)
    order = {"live": 0, "halftime": 1, "scheduled": 2, "postponed": 3, "cancelled": 4, "finished": 5}
    unique_events.sort(key=lambda e: (order.get(e.get("status"), 99), str(e.get("startTime") or "")))
    return {"updatedAt": datetime.now(timezone.utc).isoformat(), "events": unique_events, "errors": errors}


def get_live_events(force_refresh: bool = False):
    global _live_cache, _live_cache_at
    now = time.monotonic()
    if not force_refresh and _live_cache is not None and now - _live_cache_at < CACHE_TTL_SECONDS:
        return _live_cache
    result = _fetch_live_events()
    _live_cache = result
    _live_cache_at = now
    return result


def search_live_events(query: str, limit: int = 50):
    q = query.strip().lower()
    if not q:
        return []
    results = []
    for event in get_live_events().get("events", []):
        home = event.get("home") or {}
        away = event.get("away") or {}
        league = event.get("league") or {}
        haystack = " ".join(str(v or "") for v in (home.get("name"), home.get("shortName"), away.get("name"), away.get("shortName"), league.get("name"), event.get("sport"), event.get("status"))).lower()
        if q in haystack:
            results.append(event)
        if len(results) >= limit:
            break
    return results
