"""Natural-language interface to cfb.db (college football team stats, 2013-2023).
Question -> LLM (schema + strategy prompt) -> SQL -> SQLite (read-only) -> LLM -> plain-English answer.

Usage: python3 app.py [--provider gemini|claude|openai] [--strategy zero_shot|single_domain|cross_domain] ["question"]
Keys (env or .env): GEMINI_API_KEY / OPENAI_API_KEY. The `claude` provider uses the Claude Code CLI login, no key.
"""
import argparse, json, os, re, sqlite3, subprocess, sys, tempfile, time
from pathlib import Path
from urllib import error, request
try:  # python.org builds on macOS often lack CA certs; certifi fixes that if installed
    import certifi, ssl
    CTX = ssl.create_default_context(cafile=certifi.where())
except ImportError:
    CTX = None

HERE = Path(__file__).resolve().parent
MAX_ROWS = 200
SCHEMA = (HERE / "schema.sql").read_text()
NOTES = """Notes: season is the year (2013-2023). team_name uses abbreviations like 'Ohio St.', 'Michigan', 'Alabama'.
Win percentage = wins * 1.0 / games. Every stats table joins to team_seasons on team_season_id; team_seasons joins to teams and conferences.
Season totals only (not per game) unless the column name says per_game. The 2013-2016 data is missing some Mountain West teams."""

# Strategies from Nan et al. 2023 (arXiv:2305.11853)
SINGLE_DOMAIN = """Example questions with correct SQL for THIS database:
Q: Which team scored the most total points in 2019?
SQL: SELECT t.team_name, o.total_points FROM offense o JOIN team_seasons ts USING(team_season_id) JOIN teams t USING(team_id) WHERE ts.season = 2019 ORDER BY o.total_points DESC LIMIT 1;
Q: How many wins did each SEC team have in 2021?
SQL: SELECT t.team_name, ts.wins FROM team_seasons ts JOIN teams t USING(team_id) JOIN conferences c USING(conference_id) WHERE c.conference_name = 'SEC' AND ts.season = 2021 ORDER BY ts.wins DESC;
"""
CROSS_DOMAIN = """Example questions with correct SQL for a DIFFERENT database (a restaurant schema:
dishes(dish_id, name, price, category), orders(order_id, dish_id, qty, ordered_at)):
Q: What is the most ordered dish?
SQL: SELECT d.name FROM orders o JOIN dishes d ON o.dish_id = d.dish_id GROUP BY d.dish_id ORDER BY SUM(o.qty) DESC LIMIT 1;
Q: How much revenue did each category make?
SQL: SELECT d.category, SUM(d.price * o.qty) FROM orders o JOIN dishes d ON o.dish_id = d.dish_id GROUP BY d.category;
"""
EXAMPLES = {"zero_shot": "", "single_domain": SINGLE_DOMAIN, "cross_domain": CROSS_DOMAIN}


# ---------- providers: each returns (text, total_tokens or None) ----------

def load_env():
    env = HERE / ".env"
    if env.exists():
        for line in env.read_text().splitlines():
            if "=" in line and not line.startswith("#"):
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip().strip('"\''))


def need(name):
    if not os.environ.get(name):
        sys.exit(f"Set {name} in your environment or in .env (see .env.example).")
    return os.environ[name]


def _post(url, headers, body):
    req = request.Request(url, json.dumps(body).encode(), {"Content-Type": "application/json", **headers})
    for attempt in range(8):  # retry transient overload / rate-limit errors with backoff
        try:
            with request.urlopen(req, timeout=120, context=CTX) as r:
                return json.load(r)
        except error.HTTPError as e:
            body_txt = e.read().decode()
            if e.code in (429, 503) and attempt < 7:
                m = re.search(r"retry in ([\d.]+)s", body_txt)  # free tier: honor the server's hint
                wait = float(m[1]) + 1 if m else 2 ** attempt * 2
                if wait > 90:  # daily quota, not a per-minute limit: waiting won't help
                    sys.exit(f"Daily quota used up for this model (resets in ~{wait / 3600:.1f}h). "
                             "Try another: GEMINI_MODEL=gemini-3.1-flash-lite python3 app.py")
                print(f"[rate limited, retrying in {wait:.0f}s...]", file=sys.stderr)
                time.sleep(wait)
                continue
            sys.exit(f"API error {e.code}: {body_txt[:300]}")


def gemini(system, user):
    model = os.environ.get("GEMINI_MODEL", "gemini-3.1-flash-lite")
    d = _post(f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
              {"x-goog-api-key": need("GEMINI_API_KEY")},
              {"systemInstruction": {"parts": [{"text": system}]}, "contents": [{"role": "user", "parts": [{"text": user}]}],
               "generationConfig": {"temperature": 0}})
    return d["candidates"][0]["content"]["parts"][0]["text"].strip(), d.get("usageMetadata", {}).get("totalTokenCount")


def openai(system, user):
    d = _post("https://api.openai.com/v1/chat/completions", {"Authorization": f"Bearer {need('OPENAI_API_KEY')}"},
              {"model": os.environ.get("OPENAI_MODEL", "gpt-4o-mini"), "temperature": 0,
               "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}]})
    return d["choices"][0]["message"]["content"].strip(), d["usage"]["total_tokens"]


def claude(system, user):
    # Claude Code CLI in headless mode: no tools, no session saved, run from an empty dir so no project files are read.
    with tempfile.TemporaryDirectory() as tmp:
        p = subprocess.run(["claude", "-p", "--tools", "", "--no-session-persistence", "--disable-slash-commands",
                            "--model", os.environ.get("CLAUDE_MODEL", "haiku"), "--system-prompt", system,
                            "--output-format", "json"], input=user, capture_output=True, text=True, cwd=tmp, timeout=180)
    if p.returncode:
        sys.exit(f"claude CLI failed: {p.stderr[:300]}")
    d = json.loads(p.stdout)
    u = d.get("usage", {})
    return d["result"].strip(), (u.get("input_tokens", 0) + u.get("output_tokens", 0)) or None


PROVIDERS = {"gemini": gemini, "openai": openai, "claude": claude}


# ---------- app logic ----------

def clean_sql(text):
    return re.sub(r"^```(?:sql)?|```$", "", text.strip(), flags=re.M).strip()


def run_sql(sql):
    if not re.match(r"^\s*(select|with)\b", sql, re.I) or ";" in sql.strip().rstrip(";"):
        raise ValueError("Only a single read-only SELECT is allowed.")
    db = sqlite3.connect(f"file:{HERE / 'cfb.db'}?mode=ro", uri=True)  # read-only connection
    cur = db.execute(sql)
    return [c[0] for c in cur.description], cur.fetchmany(MAX_ROWS)


def answer(llm, question, strategy):
    system = ("You translate questions into a single SQLite SELECT query for this schema. "
              "Return ONLY the SQL, no explanation.\n\n" + SCHEMA + "\n" + NOTES + "\n\n" + EXAMPLES[strategy])
    sql, t1 = llm(system, question)
    sql = clean_sql(sql)
    print(f"\n[SQL] {sql}")
    try:
        cols, rows = run_sql(sql)
    except Exception as e:  # one retry: show the model its error
        sql, t = llm(system, f"{question}\n\nYour previous SQL failed:\n{sql}\nError: {e}\nReturn corrected SQL only.")
        t1 = (t1 or 0) + (t or 0)
        sql = clean_sql(sql)
        print(f"[RETRY SQL] {sql}")
        try:
            cols, rows = run_sql(sql)
        except Exception as e:
            return f"That query failed ({e}). Try rephrasing the question.", t1
    print(f"[ROWS] {len(rows)} returned")
    note = f" (results truncated to the first {MAX_ROWS} rows)" if len(rows) == MAX_ROWS else ""
    text, t2 = llm("Answer the user's question in one or two plain-English sentences using ONLY the query results. "
                   "If the results are empty, say no matching data was found.",
                   f"Question: {question}\nColumns: {cols}\nRows{note}: {rows}")
    return text, (t1 or 0) + (t2 or 0) or None


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--provider", choices=PROVIDERS, default=os.environ.get("LLM_PROVIDER", "gemini"))
    p.add_argument("--strategy", choices=EXAMPLES, default="zero_shot")
    p.add_argument("question", nargs="?")
    a = p.parse_args()
    load_env()
    llm = PROVIDERS[a.provider]
    qs = [a.question] if a.question else iter(lambda: input("\nAsk about college football (blank to quit): ").strip(), "")
    for q in qs:
        text, tokens = answer(llm, q, a.strategy)
        print(f"[ANSWER] {text}\n[tokens used: {tokens}]")


if __name__ == "__main__":
    main()
