from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse

from .sportly_provider import get_live_events, search_live_events
from .event_provider import get_event_details

app = FastAPI(title="Score Pulse API", version="1.1.0")


@app.get("/")
def root():
    return {"service": "score-pulse-api", "status": "online", "version": "1.1.0"}


@app.get("/health")
def health():
    return {"status": "ok", "service": "score-pulse-api"}


@app.get("/api/live")
def live_scores():
    result = get_live_events()
    return {
        "success": True,
        "source": "sportly",
        "updatedAt": result["updatedAt"],
        "coverage": result.get("coverage", {}),
        "events": result["events"],
        "errors": result["errors"],
    }


@app.get("/api/search")
def search(q: str = Query(default="", max_length=100)):
    query = q.strip()
    if not query:
        return {"success": True, "source": "sportly", "results": []}
    return {"success": True, "source": "sportly", "results": search_live_events(query)}


@app.get("/api/events/{event_id:path}")
def event_details(event_id: str):
    result = get_event_details(event_id)
    if result is None:
        return JSONResponse(status_code=404, content={"success": False, "event": None})
    return result
