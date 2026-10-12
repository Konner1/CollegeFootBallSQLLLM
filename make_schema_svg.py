"""Render schema.sql as schema.svg (simple ER diagram). Usage: python3 make_schema_svg.py"""
import re, sqlite3
db = sqlite3.connect(":memory:")
db.executescript(open("schema.sql").read())
tables = [r[0] for r in db.execute("select name from sqlite_master where type='table' order by rowid")]
info = {t: db.execute(f"pragma table_info({t})").fetchall() for t in tables}
fks = {t: {r[3]: r[2] for r in db.execute(f"pragma foreign_key_list({t})")} for t in tables}
pos = {"conferences": (40, 40), "teams": (40, 250), "team_seasons": (380, 100),
       "offense": (760, 20), "defense": (760, 500), "game_management": (380, 420)}
W, RH = 300, 20
def height(t): return 34 + RH * len(info[t])
out = ['<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="780" font-family="Menlo,monospace" font-size="12">',
       '<rect width="100%" height="100%" fill="#fff"/>']
anchor = {}
for t in tables:
    x, y = pos[t]; h = height(t); anchor[t] = (x, y, h)
    out.append(f'<rect x="{x}" y="{y}" width="{W}" height="{h}" fill="#f6f8fa" stroke="#24292f"/>')
    out.append(f'<rect x="{x}" y="{y}" width="{W}" height="26" fill="#0b3d91"/>')
    out.append(f'<text x="{x+8}" y="{y+18}" fill="#fff" font-weight="bold">{t}</text>')
    for i, (_, n, ty, nn, _, pk) in enumerate(info[t]):
        tag = "PK " if pk else ("FK " if n in fks[t] else "   ")
        out.append(f'<text x="{x+8}" y="{y+46+i*RH}" xml:space="preserve">{tag}{n} <tspan fill="#6e7781">{ty}</tspan></text>')
for t in tables:
    for col, ref in fks[t].items():
        x1, y1, h1 = anchor[t]; x2, y2, h2 = anchor[ref]
        i = [c[1] for c in info[t]].index(col)
        sy = y1 + 46 + i * RH - 4
        if x1 < x2 + W and x2 < x1 + W:  # vertically stacked: connect bottom of parent to top of child
            a, b = (x2 + W / 2, y2 + h2), (x1 + W / 2, y1)
            out.append(f'<path d="M{a[0]},{a[1]} L{b[0]},{b[1]}" fill="none" stroke="#cf222e" stroke-width="1.5"/>')
        else:
            if x2 + W <= x1: a, b = (x1, sy), (x2 + W, y2 + 13)
            else: a, b = (x1 + W, sy), (x2, y2 + 13)
            mx = (a[0] + b[0]) / 2
            out.append(f'<path d="M{a[0]},{a[1]} C{mx},{a[1]} {mx},{b[1]} {b[0]},{b[1]}" fill="none" stroke="#cf222e" stroke-width="1.5"/>')
        out.append(f'<circle cx="{b[0]}" cy="{b[1]}" r="4" fill="#cf222e"/>')
out.append("</svg>")
open("schema.svg", "w").write("\n".join(out))
print("wrote schema.svg")
