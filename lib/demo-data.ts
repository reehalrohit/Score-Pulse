import { LiveEvent } from "./types";

export const demoEvents: LiveEvent[] = [
  {
    id: "demo-cricket-1",
    sport: "cricket",
    league: {
      id: "icc-cricket",
      name: "International Cricket"
    },
    status: "live",
    startTime: new Date().toISOString(),
    home: {
      id: "india",
      name: "India",
      shortName: "IND"
    },
    away: {
      id: "australia",
      name: "Australia",
      shortName: "AUS"
    },
    score: {
      home: "168/4",
      away: "—",
      period: "32.4 ov"
    }
  },
  {
    id: "demo-football-1",
    sport: "football",
    league: {
      id: "eng.1",
      name: "Premier League",
      country: "England"
    },
    status: "live",
    startTime: new Date().toISOString(),
    home: {
      id: "arsenal",
      name: "Arsenal",
      shortName: "ARS"
    },
    away: {
      id: "chelsea",
      name: "Chelsea",
      shortName: "CHE"
    },
    score: {
      home: 2,
      away: 1,
      period: "67'"
    }
  },
  {
    id: "demo-basketball-1",
    sport: "basketball",
    league: {
      id: "nba",
      name: "NBA"
    },
    status: "live",
    startTime: new Date().toISOString(),
    home: {
      id: "lal",
      name: "Los Angeles Lakers",
      shortName: "LAL"
    },
    away: {
      id: "gsw",
      name: "Golden State Warriors",
      shortName: "GSW"
    },
    score: {
      home: 94,
      away: 91,
      period: "Q4"
    }
  }
];
