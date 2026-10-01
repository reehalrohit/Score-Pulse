from fastapi import FastAPI
from .sportly_provider import get_live_events

app = FastAPI(
    title="Score Pulse API",
    version="1.0.0"
)


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "score-pulse-api"
    }


@app.get("/api/live")
def live_scores():
    return {
        "success": True,
        "events": get_live_events()
    }
