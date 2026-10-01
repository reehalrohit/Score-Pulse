from typing import Any


def serialize(value: Any):
    if value is None:
        return None

    if hasattr(value, "model_dump"):
        return value.model_dump(mode="json")

    if isinstance(value, list):
        return [serialize(item) for item in value]

    if isinstance(value, dict):
        return {
            str(key): serialize(item)
            for key, item in value.items()
        }

    return value


def get_live_events():
    """
    Sportly provider layer.

    The provider is intentionally isolated here so the frontend
    never communicates directly with ESPN/FotMob/Sofascore.
    """

    try:
        from sportly.espn import basketball, football, soccer, hockey

        events = []

        providers = [
            ("basketball", basketball, "nba"),
            ("football", football, "nfl"),
            ("soccer", soccer, "eng.1"),
            ("hockey", hockey, "nhl"),
        ]

        for sport, module, league in providers:
            try:
                data = module.scoreboard(league=league)
                events.append({
                    "sport": sport,
                    "league": league,
                    "data": serialize(data)
                })
            except Exception as exc:
                events.append({
                    "sport": sport,
                    "league": league,
                    "error": str(exc)
                })

        return events

    except Exception as exc:
        return [{
            "error": str(exc)
        }]
