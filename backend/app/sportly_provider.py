from __future__ import annotations

import importlib
import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from sportly.client import SportlyClient
from sportly.espn._leagues import LEAGUES


MODULE_BY_ESPN_SPORT = {
    "australian-football": "australian_football",
    "field-hockey": "field_hockey",
    "rugby-league": "rugby_league",
    "water-polo": "water_polo",
}

FRONTEND_SPORT_BY_ESPN_SPORT = {
    "australian-football": "football",
    "baseball": "baseball",
    "basketball": "basketball",
    "cricket": "cricket",
    "field-hockey": "other",
    "football": "football",
    "golf": "golf",
    "hockey": "hockey",
    "lacrosse": "lacrosse",
    "mma": "mma",
    "racing": "racing",
    "rugby": "rugby",
    "rugby-league": "rugby",
    "soccer": "football",
    "tennis": "tennis",
    "volleyball": "volleyball",
    "water-polo": "other",
}

# Complete known Sportly/ESPN league catalog. The frontend sport taxonomy stays
# stable while the backend fetches each league independently.
SPORT_CONFIG: list[tuple[str, str, str, str]] = []
for _espn_sport, _leagues in LEAGUES.items():
    _module = MODULE_BY_ESPN_SPORT.get(_espn_sport, _espn_sport.replace("-", "_"))
    _sport = FRONTEND_SPORT_BY_ESPN_SPORT.get(_espn_sport, "other")
    for _league_id, _league_name in _leagues.items():
        SPORT_CONFIG.append((_sport, _module, _league_id, _league_name))

CACHE_TTL_SECONDS = 45
MAX_WORKERS = 16
UPSTREAM_TIMEOUT_SECONDS = 6.0
_SPORTLY_CLIENT = SportlyClient(timeout=UPSTREAM_TIMEOUT_SECONDS, max_retries=0, backoff=0)

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
        return [serialize(x) for x in value]
    if isinstance(value, tuple):
        return [serialize(x) for x in value]
    if isinstance(value, dict):
        return {str(k): serialize(v) for k, v in value.items()}
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, (str, int, float, bool)):
        return value
    return str(value)


def first_value(*values: Any) -> Any:
    for value in values:
        if value is not None and value != "":
            return value
    return None


def safe_list(value: Any) -> list:
    return value if isinstance(value, list) else []


def fetch_json(url: str, timeout: int = 8) -> Any:
    req = Request(url, headers={"User-Agent": "Mozilla/5.0 (compatible; ScorePulse/1.1)", "Accept": "application/json"})
    with urlopen(req, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def extract_events(data: Any) -> list[dict[str, Any]]:
    data = serialize(data)
    if isinstance(data, list):
        return [x for x in data if isinstance(x, dict)]
    if not isinstance(data, dict):
        return []
    events = data.get("events")
    if isinstance(events, list):
        return [x for x in events if isinstance(x, dict)]
    for key in ("data", "content", "scoreboard"):
        nested = data.get(key)
        if isinstance(nested, dict) and isinstance(nested.get("events"), list):
            return [x for x in nested["events"] if isinstance(x, dict)]
        if isinstance(nested, list):
            return [x for x in nested if isinstance(x, dict)]
    return []


def get_competitors(event: dict[str, Any]) -> list[dict[str, Any]]:
    comps = safe_list(event.get("competitions"))
    if comps and isinstance(comps[0], dict):
        nested = safe_list(comps[0].get("competitors"))
        if nested:
            return [x for x in nested if isinstance(x, dict)]
    return [x for x in safe_list(event.get("competitors")) if isinstance(x, dict)]


def get_team(c: dict[str, Any]) -> dict[str, Any]:
    team = c.get("team") or {}
    if not isinstance(team, dict):
        team = {}
    logos = safe_list(team.get("logos"))
    logo = first_value(team.get("logo"), logos[0].get("href") if logos and isinstance(logos[0], dict) else None)
    return {
        "id": str(first_value(team.get("id"), c.get("id"), "unknown")),
        "name": first_value(team.get("displayName"), team.get("name"), team.get("shortDisplayName"), team.get("nickname"), "Unknown"),
        "shortName": first_value(team.get("abbreviation"), team.get("shortDisplayName"), team.get("nickname"), team.get("name"), "Unknown"),
        "logo": logo,
    }


def get_status(event: dict[str, Any]) -> str:
    status = event.get("status") or {}
    if not isinstance(status, dict):
        status = {}
    st = status.get("type") or {}
    if not isinstance(st, dict):
        st = {}
    state = str(first_value(st.get("state"), status.get("state"), "")).lower()
    combined = " ".join(str(x or "").lower() for x in (state, st.get("name"), st.get("detail"), status.get("detail")))
    if "postpon" in combined:
        return "postponed"
    if "cancel" in combined:
        return "cancelled"
    if state in {"in", "live"}:
        return "halftime" if "half" in combined else "live"
    if state in {"post", "finished", "complete", "completed"} or "final" in combined:
        return "finished"
    return "scheduled"


def get_score(event: dict[str, Any], competitors: list[dict[str, Any]]) -> dict[str, Any] | None:
    if not competitors:
        return None
    home = away = None
    for c in competitors:
        side = str(c.get("homeAway", "")).lower()
        lines = safe_list(c.get("linescores"))
        latest = lines[-1] if lines and isinstance(lines[-1], dict) else {}
        score = first_value(c.get("score"), latest.get("displayValue"), latest.get("value"))
        if side == "home":
            home = score
        elif side == "away":
            away = score
    if home is None and away is None:
        return None
    status = event.get("status") or {}
    if not isinstance(status, dict):
        status = {}
    st = status.get("type") or {}
    if not isinstance(st, dict):
        st = {}
    return {
        "home": first_value(home, "-"),
        "away": first_value(away, "-"),
        "period": first_value(status.get("displayClock"), status.get("clock"), st.get("shortDetail"), st.get("detail"), status.get("detail")),
    }


def get_league(event: dict[str, Any], league_id: str, league_name: str) -> dict[str, Any]:
    comps = safe_list(event.get("competitions"))
    comp = comps[0] if comps and isinstance(comps[0], dict) else {}
    event_league = event.get("league") or {}
    if not isinstance(event_league, dict):
        event_league = {}
    comp_league = comp.get("league") or {}
    if not isinstance(comp_league, dict):
        comp_league = {}
    merged = {**comp_league, **event_league}
    logos = safe_list(merged.get("logos"))
    return {
        "id": str(first_value(merged.get("id"), league_id)),
        "name": first_value(merged.get("name"), merged.get("shortName"), league_name, league_id),
        "country": first_value(merged.get("country")),
        "logo": first_value(merged.get("logo"), logos[0].get("href") if logos and isinstance(logos[0], dict) else None),
    }


def make_event_id(sport: str, league_id: str, provider_id: Any) -> str:
    return f"{sport}-{league_id}-{provider_id}"


def normalize_event(event: dict[str, Any], sport: str, league_id: str, league_name: str) -> dict[str, Any] | None:
    if not isinstance(event, dict) or not event.get("id"):
        return None
    competitors = get_competitors(event)
    if len(competitors) < 2:
        return None
    home = next((x for x in competitors if str(x.get("homeAway", "")).lower() == "home"), competitors[0])
    away = next((x for x in competitors if str(x.get("homeAway", "")).lower() == "away"), competitors[1])
    comps = safe_list(event.get("competitions"))
    comp = comps[0] if comps and isinstance(comps[0], dict) else {}
    venue = comp.get("venue") or {}
    if not isinstance(venue, dict):
        venue = {}
    broadcasts = safe_list(comp.get("broadcasts"))
    broadcast = None
    if broadcasts and isinstance(broadcasts[0], dict):
        names = safe_list(broadcasts[0].get("names"))
        if names:
            broadcast = names[0]
    return {
        "id": make_event_id(sport, league_id, event["id"]),
        "sport": sport,
        "league": get_league(event, league_id, league_name),
        "status": get_status(event),
        "startTime": first_value(event.get("date"), event.get("startDate"), datetime.now(timezone.utc).isoformat()),
        "home": get_team(home),
        "away": get_team(away),
        "score": get_score(event, competitors),
        "venue": first_value(venue.get("fullName"), venue.get("name")),
        "broadcast": broadcast,
    }


def normalize_sportly_event(event: dict[str, Any], sport: str, league_id: str, league_name: str) -> dict[str, Any] | None:
    raw = event.get("raw") if isinstance(event, dict) else None
    if isinstance(raw, dict) and raw.get("competitions"):
        result = normalize_event(raw, sport, league_id, league_name)
        if result:
            return result
    if not isinstance(event, dict) or not event.get("id"):
        return None
    competitors = [x for x in safe_list(event.get("competitors")) if isinstance(x, dict)]
    if len(competitors) < 2:
        return None
    home = next((x for x in competitors if str(x.get("homeAway", "")).lower() == "home"), competitors[0])
    away = next((x for x in competitors if str(x.get("homeAway", "")).lower() == "away"), competitors[1])
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

    hs = first_value(home.get("score"), "-")
    aw = first_value(away.get("score"), "-")
    score = {"home": hs, "away": aw, "period": first_value(status.get("clock"), status.get("displayClock"), detail)} if hs != "-" or aw != "-" else None

    return {
        "id": make_event_id(sport, league_id, event["id"]),
        "sport": sport,
        "league": {"id": str(league_id), "name": league_name, "country": None, "logo": None},
        "status": normalized_status,
        "startTime": first_value(event.get("date"), datetime.now(timezone.utc).isoformat()),
        "home": get_team(home),
        "away": get_team(away),
        "score": score,
        "venue": None,
        "broadcast": None,
    }


def _fetch_one(config: tuple[str, str, str, str]) -> tuple[list[dict[str, Any]], dict[str, Any] | None]:
    sport, module_name, league_id, league_name = config
    try:
        module = importlib.import_module(f"sportly.espn.{module_name}")
        raw = serialize(module.scoreboard(league_id, limit=100, client=_SPORTLY_CLIENT))
        result: list[dict[str, Any]] = []
        for event in extract_events(raw):
            normalized = None
            raw_event = event.get("raw")
            if isinstance(raw_event, dict) and raw_event.get("competitions"):
                normalized = normalize_event(raw_event, sport, league_id, league_name)
            if normalized is None:
                normalized = normalize_sportly_event(event, sport, league_id, league_name)
            if normalized:
                result.append(normalized)
        return result, None
    except Exception as exc:
        return [], {"sport": sport, "league": league_id, "leagueName": league_name, "error": str(exc)}


def _fetch_sportly_events() -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    events: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []
    successful = 0
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = [executor.submit(_fetch_one, cfg) for cfg in SPORT_CONFIG]
        for future in as_completed(futures):
            league_events, error = future.result()
            events.extend(league_events)
            if error is None:
                successful += 1
            else:
                errors.append(error)
    return events, errors, {"configuredLeagues": len(SPORT_CONFIG), "successfulLeagues": successful, "failedLeagues": len(errors)}


def _fetch_cricket_core_events() -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    # Retained as a fallback because some ESPN cricket site scoreboard routes
    # have historically returned 404 while the Core API remains available.
    events: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []
    url = "https://sports.core.api.espn.com/v2/sports/cricket/leagues/icc-cricket/events?limit=100"
    try:
        payload = fetch_json(url)
        items = safe_list(payload.get("items")) if isinstance(payload, dict) else []
        for item in items:
            if not isinstance(item, dict):
                continue
            event = item
            if item.get("$ref"):
                try:
                    event = fetch_json(item["$ref"])
                except Exception:
                    continue
            competitors = get_competitors(event)
            if len(competitors) < 2 or not event.get("id"):
                continue
            sport_event = normalize_event(event, "cricket", "icc-cricket", "ICC Cricket")
            if sport_event:
                events.append(sport_event)
    except HTTPError as exc:
        errors.append({"sport": "cricket", "league": "icc-cricket", "error": f"HTTP {exc.code}"})
    except URLError as exc:
        errors.append({"sport": "cricket", "league": "icc-cricket", "error": f"Unavailable: {exc.reason}"})
    except Exception as exc:
        errors.append({"sport": "cricket", "league": "icc-cricket", "error": str(exc)})
    return events, errors


def _fetch_live_events() -> dict[str, Any]:
    events, errors, coverage = _fetch_sportly_events()
    cricket_events, cricket_errors = _fetch_cricket_core_events()
    events.extend(cricket_events)
    errors.extend(cricket_errors)

    unique: list[dict[str, Any]] = []
    seen: set[str] = set()
    for event in events:
        event_id = str(event.get("id"))
        if event_id in seen:
            continue
        seen.add(event_id)
        unique.append(event)

    order = {"live": 0, "halftime": 1, "scheduled": 2, "postponed": 3, "cancelled": 4, "finished": 5}
    unique.sort(key=lambda e: (order.get(e.get("status"), 99), str(e.get("startTime") or "")))
    coverage["events"] = len(unique)
    coverage["errors"] = len(errors)
    return {"updatedAt": datetime.now(timezone.utc).isoformat(), "events": unique, "errors": errors[:50], "coverage": coverage}


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
