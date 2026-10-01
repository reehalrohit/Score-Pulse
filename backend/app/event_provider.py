from __future__ import annotations

import importlib

from .sportly_provider import SPORT_CONFIG, normalize_event, serialize


def get_event_details(event_id: str):
    if "-" not in event_id:
        return None

    sport, provider_id = event_id.split("-", 1)

    candidates = [item for item in SPORT_CONFIG if item[0] == sport]

    for _, module_name, league in candidates:
        try:
            module = importlib.import_module(f"sportly.espn.{module_name}")
            if not hasattr(module, "game"):
                continue
            raw = module.game(provider_id, league)
            data = serialize(raw)
            if isinstance(data, dict):
                event = data.get("event")
                if isinstance(event, dict):
                    data = event
                normalized = normalize_event(data, sport, league)
                if normalized:
                    return {"success": True, "event": normalized, "raw": data}
        except Exception:
            continue

    return None
