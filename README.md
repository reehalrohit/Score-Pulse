# Score Pulse

> Every Sport. Every Score. Live.

Score Pulse is a modern sports-data platform for live scores,
fixtures, standings, teams, players and match information.

## Features

- 🏏 Cricket
- ⚽ Football
- 🏀 Basketball
- 🎾 Tennis
- 🏒 Hockey
- ⚾ Baseball
- 🏎️ Racing
- 🥊 MMA
- 🏉 Rugby
- 🏐 Volleyball
- 🏆 League standings
- 👤 Player pages
- 🏟️ Team pages
- 🔴 Live match centre
- 🔎 Sports search
- ⭐ Favorites
- 📱 PWA support
- 🌙 Dark UI
- ⚡ Automatic live-score refresh

## Architecture

```text
Next.js frontend
       │
       ▼
/api/*
       │
       ▼
FastAPI backend
       │
       ▼
Sportly provider layer
       │
       ├── ESPN
       ├── MLB
       ├── NBA
       ├── NFL
       ├── NHL
       ├── FotMob
       └── Sofascore
