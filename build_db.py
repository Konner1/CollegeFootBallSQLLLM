"""Build cfb.db from the Kaggle CSVs in ../archive (one CSV per season, inconsistent headers/formats)."""
import csv, re, sqlite3
from pathlib import Path

HERE = Path(__file__).resolve().parent
ARCHIVE = HERE.parent / "archive"
norm = lambda s: re.sub(r"[^a-z0-9]", "", s.lower())


def num(v, cast=float):
    v = (v or "").replace(",", "").replace("\xa0", "").strip()
    if v in ("", "-", "NA", "N/A"):
        return None
    x = float(v)
    return int(x) if cast is int else x


def top(v):  # "\xa0\xa0\xa0352:08" or "375:09" -> seconds
    m = re.search(r"(\d+):(\d+)", v or "")
    return int(m[1]) * 60 + int(m[2]) if m else None


ALIASES = {"App State": "Appalachian St.", "Coastal Caro.": "Coastal Carolina", "La.-Monroe": "ULM", "Northern Ill.": "NIU"}


def split_team(raw):  # "LSU (SEC)" -> ("LSU", "SEC")
    raw = raw.replace("\xa0", " ").strip()
    m = re.match(r"^(.*?)\s*\(([^)]*)\)\s*$", raw)
    if not m:
        return ALIASES.get(raw, raw), None
    conf = {"MWC": "Mountain West", "CUSA": "C-USA", "Independent": "FBS Independent", "": None}.get(m[2].strip(), m[2].strip())
    return ALIASES.get(m[1].strip(), m[1].strip()), conf


# (table, column, candidate normalized CSV headers, int?)
FIELDS = {
    "offense": [("plays", ["offplays"], 1), ("total_yards", ["offyards"], 1), ("yards_per_game", ["offyardspergame"], 0),
        ("touchdowns", ["touchdowns"], 1), ("total_points", ["totalpoints"], 1), ("points_per_game", ["pointspergame"], 0),
        ("pass_attempts", ["passattempts"], 1), ("pass_completions", ["passcompletions"], 1), ("pass_yards", ["passyards"], 1),
        ("pass_tds", ["passtouchdowns"], 1), ("rush_attempts", ["rushattempts"], 1), ("rush_yards", ["rushyds"], 1),
        ("rush_tds", ["rushingtd"], 1), ("first_downs", ["firstdowns"], 1),
        ("third_down_attempts", ["3rdattempts", "x3rdattempts"], 1), ("third_down_conversions", ["3rdconversions", "x3rdconversions"], 1),
        ("redzone_attempts", ["redzoneattempts"], 1), ("redzone_scores", ["redzonescores"], 1)],
    "defense": [("points_allowed", ["pointsallowed"], 1), ("yards_allowed", ["yardsallowed"], 1),
        ("pass_yards_allowed", ["opppassydsallowed"], 1), ("rush_yards_allowed", ["opprushyardsalloweed"], 1),
        ("sacks", ["sacks"], 1), ("tackles_for_loss", ["totaltackleforloss"], 1),
        ("interceptions", ["opponentsintercepted"], 1), ("fumbles_recovered", ["fumblesrecovered"], 1)],
    "game_management": [("penalties", ["penalties"], 1), ("penalty_yards", ["penaltyyards"], 1),
        ("turnovers_gained", ["turnoversgain"], 1), ("turnovers_lost", ["turnoverslost"], 1),
        ("turnover_margin", ["turnovermargin"], 1)],
}


def pick(row, cands):
    for c in cands:
        if c in row:
            return row[c]
    raise KeyError(cands)


db = sqlite3.connect(HERE / "cfb.db")
for t in ("game_management", "defense", "offense", "team_seasons", "teams", "conferences"):
    db.execute(f"DROP TABLE IF EXISTS {t}")
db.executescript((HERE / "schema.sql").read_text())
ids = {"teams": {}, "conferences": {}}


def get_id(table, col, name):
    if name is None:
        return None
    if name not in ids[table]:
        ids[table][name] = db.execute(f"INSERT INTO {table}({col}) VALUES (?)", (name,)).lastrowid
    return ids[table][name]


for path in sorted(ARCHIVE.glob("cfb[0-9][0-9].csv")):
    season = 2000 + int(path.stem[3:])
    for raw in csv.DictReader(open(path, encoding="utf-8-sig")):
        r = {norm(k): v for k, v in raw.items() if k}
        if not r.get("team", "").strip():
            continue
        team, conf = split_team(r["team"])
        if "winloss" in r:
            wl = re.findall(r"\d+", r["winloss"])
            if len(wl) < 2:
                print(f"skip {season} {r['team']!r}: no record ({r['winloss']!r})")
                continue
            w, l = int(wl[0]), int(wl[1])
        else:
            w, l = num(r["win"], int), num(r["loss"], int)
        tsid = db.execute("INSERT INTO team_seasons(team_id,season,conference_id,games,wins,losses) VALUES (?,?,?,?,?,?)",
                          (get_id("teams", "team_name", team), season, get_id("conferences", "conference_name", conf),
                           num(r["games"], int), w, l)).lastrowid
        for table, fields in FIELDS.items():
            cols = [f[0] for f in fields]
            vals = [num(pick(r, f[1]), int if f[2] else float) for f in fields]
            if table == "game_management":
                cols.append("time_of_possession_seconds"); vals.append(top(r["timeofpossession"]))
            db.execute(f"INSERT INTO {table}(team_season_id,{','.join(cols)}) VALUES (?{',?' * len(cols)})", [tsid] + vals)
db.commit()
for t in ("conferences", "teams", "team_seasons", "offense", "defense", "game_management"):
    print(f"{t:16}", db.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0])
