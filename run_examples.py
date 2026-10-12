"""Run a fixed list of questions through every prompting strategy and write examples.md.
Usage: python3 run_examples.py [--provider gemini|claude|openai]"""
import argparse, contextlib, io, os, re
import app

QUESTIONS = [
    "Which team scored the most total points in 2019?",
    "How many wins did each SEC team have in 2021?",
    "Which team had the best turnover margin in 2022?",
    "What is Ohio St.'s win percentage in each season?",
    "Which conference averaged the most passing yards per team in 2023?",
    "Which team gave up the fewest points per game in 2018, and how many?",
    "Which teams had a losing record but a positive turnover margin in 2020?",
    "Who was the best team ever?",
]

p = argparse.ArgumentParser()
p.add_argument("--provider", choices=app.PROVIDERS, default=os.environ.get("LLM_PROVIDER", "gemini"))
a = p.parse_args()
app.load_env()
llm = app.PROVIDERS[a.provider]
out = [f"# Example runs (provider: {a.provider}, model: {os.environ.get('GEMINI_MODEL', 'default')})\n"]
for q in QUESTIONS:
    out.append(f"## {q}\n")
    for strat in app.EXAMPLES:
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            try:
                text, tokens = app.answer(llm, q, strat)
            except (Exception, SystemExit) as e:
                text, tokens = f"ERROR: {e}", None
        sql = "\n".join(re.findall(r"^\[(?:RETRY )?SQL\] (.*)$", buf.getvalue(), flags=re.M)[-1:])
        out.append(f"**{strat}** (tokens: {tokens})\n\n```sql\n{sql}\n```\n\n{text}\n")
        open("examples.md", "w").write("\n".join(out))  # save progress after every call
open("examples.md", "w").write("\n".join(out))
print("wrote examples.md")
