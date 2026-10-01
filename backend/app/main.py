from fastapi import FastAPI
from .sportly_provider import get_live_events

app = FastAPI(
    title="Score Pulse API",
    version="1.0.0",
)


@app.get("/")
def root():
    return {
        "service": "score-pulse-api",
        "status": "online",
        "version": "1.0.0",
    }


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "score-pulse-api",
    }


@app.get("/api/live")
def live_scores():
    result = get_live_events()

    return {
        "success": True,
        "updatedAt": result["updatedAt"],
        "events": result["events"],
        "errors": result["errors"],
    }
