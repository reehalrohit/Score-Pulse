export type Sport =
  | "cricket"
  | "football"
  | "basketball"
  | "tennis"
  | "hockey"
  | "baseball"
  | "golf"
  | "racing"
  | "mma"
  | "rugby"
  | "volleyball"
  | "lacrosse"
  | "other";

export type MatchStatus =
  | "scheduled"
  | "live"
  | "halftime"
  | "finished"
  | "postponed"
  | "cancelled";

export interface Team {
  id: string;
  name: string;
  shortName?: string;
  logo?: string;
}

export interface League {
  id: string;
  name: string;
  country?: string;
  logo?: string;
}

export interface Score {
  home: string | number;
  away: string | number;
  period?: string;
}

export interface LiveEvent {
  id: string;
  sport: Sport;
  league: League;
  status: MatchStatus;
  startTime: string;
  home: Team;
  away: Team;
  score?: Score;
  venue?: string;
  broadcast?: string;
  period?: string;
}
