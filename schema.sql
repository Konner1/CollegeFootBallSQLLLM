-- College football team stats, 2013-2023 (source: Kaggle "College Football Team Stats 2013 to 2023")
CREATE TABLE conferences (
  conference_id INTEGER PRIMARY KEY,
  conference_name TEXT NOT NULL UNIQUE      -- e.g. SEC, Big Ten, Pac-12
);
CREATE TABLE teams (
  team_id INTEGER PRIMARY KEY,
  team_name TEXT NOT NULL UNIQUE            -- e.g. Alabama, Ohio St.
);
-- one row per team per season; conference is per season because teams move
CREATE TABLE team_seasons (
  team_season_id INTEGER PRIMARY KEY,
  team_id INTEGER NOT NULL REFERENCES teams(team_id),
  season INTEGER NOT NULL,                  -- 2013..2023
  conference_id INTEGER REFERENCES conferences(conference_id),
  games INTEGER, wins INTEGER, losses INTEGER,
  UNIQUE (team_id, season)
);
CREATE TABLE offense (
  team_season_id INTEGER PRIMARY KEY REFERENCES team_seasons(team_season_id),
  plays INTEGER, total_yards INTEGER, yards_per_game REAL, touchdowns INTEGER,
  total_points INTEGER, points_per_game REAL,
  pass_attempts INTEGER, pass_completions INTEGER, pass_yards INTEGER, pass_tds INTEGER,
  rush_attempts INTEGER, rush_yards INTEGER, rush_tds INTEGER,
  first_downs INTEGER, third_down_attempts INTEGER, third_down_conversions INTEGER,
  redzone_attempts INTEGER, redzone_scores INTEGER
);
CREATE TABLE defense (
  team_season_id INTEGER PRIMARY KEY REFERENCES team_seasons(team_season_id),
  points_allowed INTEGER, yards_allowed INTEGER,
  pass_yards_allowed INTEGER, rush_yards_allowed INTEGER,
  sacks INTEGER, tackles_for_loss INTEGER,
  interceptions INTEGER, fumbles_recovered INTEGER
);
CREATE TABLE game_management (
  team_season_id INTEGER PRIMARY KEY REFERENCES team_seasons(team_season_id),
  penalties INTEGER, penalty_yards INTEGER,
  turnovers_gained INTEGER, turnovers_lost INTEGER, turnover_margin INTEGER,
  time_of_possession_seconds INTEGER        -- season total
);
