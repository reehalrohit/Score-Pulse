from __future__ import annotations

import importlib
from datetime import datetime, timezone
from typing import Any


SPORT_CONFIG = [
    ("basketball", "basketball", "nba"),
    ("football", "football", "nfl"),
    ("football", "soccer", "eng.1"),
    ("hockey", "hockey", "nhl"),
    ("baseball", "baseball", "mlb"),
    ("cricket", "cricket", "icc-cricket"),
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


def serialize(value: Any) -> Any:
    if value is None:
        return None

    if hasattr(value, "model_dump"):
        try:
            return value.model_dump(mode="json")
        except TypeError:
            return value.model_dump()

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
        return {
            str(key): serialize(item)
            for key, item in value.items()
        }

    if isinstance(value, (str, int, float, bool)):
        return value

    return str(value)


def first_value(*values):
    for value in values:
        if value is not None and value != "":
            return value

    return None


def get_competitors(event: dict[str, Any]):
    competitions = event.get("competitions") or []

    if competitions:
        competitors = competitions[0].get("competitors") or []
        if competitors:
            return competitors

    return event.get("competitors") or []


def get_team(competitor: dict[str, Any]) -> dict[str, Any]:
    team = competitor.get("team") or {}

    return {
        "id": str(
            first_value(
                team.get("id"),
                competitor.get("id"),
                "unknown",
            )
        ),
        "name": first_value(
            team.get("displayName"),
            team.get("name"),
            team.get("shortDisplayName"),
            "Unknown",
        ),
        "shortName": first_value(
            team.get("abbreviation"),
            team.get("shortDisplayName"),
            team.get("name"),
        ),
        "logo": first_value(
            team.get("logo"),
            (
                (team.get("logos") or [{}])[0].get("href")
                if team.get("logos")
                else None
            ),
        ),
    }


def get_status(event: dict[str, Any]) -> str:
    status = event.get("status") or {}
    status_type = status.get("type") or {}

    state = str(
        first_value(
            status_type.get("state"),
            status.get("state"),
            "",
        )
    ).lower()

    name = str(
        first_value(
            status_type.get("name"),
            status.get("name"),
            "",
        )
    ).lower()

    if "postpon" in name or "postpon" in state:
        return "postponed"

    if "cancel" in name or "cancel" in state:
        return "cancelled"

    if state in {"in", "live"}:
        if "halftime" in name or "half" in name:
            return "halftime"

        return "live"

    if state in {"post", "finished", "complete"}:
        return "finished"

    return "scheduled"


def get_score(
    event: dict[str, Any],
    competitors: list[dict[str, Any]],
) -> dict[str, Any] | None:
    if not competitors:
        return None

    home = None
    away = None

    for competitor in competitors:
        side = str(competitor.get("homeAway", "")).lower()
        score = first_value(
            competitor.get("score"),
            (competitor.get("linescores") or [{}])[-1].get("value")
            if competitor.get("linescores")
            else None,
        )

        if side == "home":
            home = score

        elif side == "away":
            away = score

    if home is None and away is None:
        return None

    status = event.get("status") or {}

    return {
        "home": first_value(home, "-"),
        "away": first_value(away, "-"),
        "period": first_value(
            status.get("displayClock"),
            status.get("clock"),
            (status.get("type") or {}).get("shortDetail"),
            (status.get("type") or {}).get("detail"),
        ),
    }


def normalize_event(
    event: dict[str, Any],
    sport: str,
    league_id: str,
    league_name: str | None = None,
) -> dict[str, Any] | None:
    event_id = event.get("id")

    if not event_id:
        return None

    competitors = get_competitors(event)

    home_competitor = next(
        (
            item
            for item in competitors
            if str(item.get("homeAway", "")).lower() == "home"
        ),
        None,
    )

    away_competitor = next(
        (
            item
            for item in competitors
            if str(item.get("homeAway", "")).lower() == "away"
        ),
        None,
    )

    if home_competitor is None or away_competitor is None:
        return None

    competition = (
        (event.get("competitions") or [{}])[0]
        if event.get("competitions")
        else {}
    )

    event_league = (
        event.get("league")
        or competition.get("league")
        or {}
    )

    name = first_value(
        event_league.get("name"),
        event_league.get("shortName"),
        league_name,
        league_id,
    )

    return {
        "id": f"{sport}-{event_id}",
        "sport": sport,
        "league": {
            "id": str(
                first_value(
                    event_league.get("id"),
                    league_id,
                )
            ),
            "name": name,
            "country": first_value(
                event_league.get("country"),
            ),
            "logo": first_value(
                event_league.get("logo"),
                (
                    (event_league.get("logos") or [{}])[0].get("href")
                    if event_league.get("logos")
                    else None
                ),
            ),
        },
        "status": get_status(event),
        "startTime": first_value(
            event.get("date"),
            datetime.now(timezone.utc).isoformat(),
        ),
        "home": get_team(home_competitor),
        "away": get_team(away_competitor),
        "score": get_score(event, competitors),
        "venue": first_value(
            competition.get("venue", {}).get("fullName")
            if competition.get("venue")
            else None,
        ),
        "broadcast": first_value(
            (
                competition.get("broadcasts") or [{}]
            )[0].get("names", [None])[0]
            if competition.get("broadcasts")
            else None,
        ),
    }


def extract_events(data: Any) -> list[dict[str, Any]]:
    data = serialize(data)

    if isinstance(data, dict):
        events = data.get("events")

        if isinstance(events, list):
            return events

        # Some provider responses may wrap the scoreboard.
        for key in ("data", "content", "scoreboard"):
            nested = data.get(key)

            if isinstance(nested, dict):
                nested_events = nested.get("events")

                if isinstance(nested_events, list):
                    return nested_events

            if isinstance(nested, list):
                return nested

    if isinstance(data, list):
        return [
            item
            for item in data
            if isinstance(item, dict)
        ]

    return []


def load_sportly_module(module_name: str):
    return importlib.import_module(
        f"sportly.espn.{module_name}"
    )


def get_live_events():
    """
    Fetch scoreboards from Sportly/ESPN and normalize them
    into the Score Pulse LiveEvent schema.
    """

    events: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []

    for sport, module_name, league in SPORT_CONFIG:
        try:
            module = load_sportly_module(module_name)

            raw = module.scoreboard(league)

            raw_dict = serialize(raw)

            league_name = None

            if isinstance(raw_dict, dict):
                leagues = raw_dict.get("leagues") or []

                if leagues and isinstance(leagues[0], dict):
                    league_name = first_value(
                        leagues[0].get("name"),
                        leagues[0].get("shortName"),
                    )

            for event in extract_events(raw_dict):
                normalized = normalize_event(
                    event=event,
                    sport=sport,
                    league_id=league,
                    league_name=league_name,
                )

                if normalized:
                    events.append(normalized)

        except Exception as exc:
            errors.append({
                "sport": sport,
                "league": league,
                "error": str(exc),
            })

    return {
        "updatedAt": datetime.now(timezone.utc).isoformat(),
        "events": events,
        "errors": errors,
    }
