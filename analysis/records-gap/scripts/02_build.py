"""Step 2: build annual record series per event and sex, plus marathon-major winners.

For each event and year, the standing world record is the best mark set up to
and including that year. The women/men performance ratio uses speed for timed
events (men's time / women's time) and distance or height for field events.
"""
from pathlib import Path
import json, re
import numpy as np
import pandas as pd
import wikiparse as W

ROOT = Path(__file__).resolve().parents[1]
META = json.loads((ROOT / "data" / "events_meta.json").read_text(encoding="utf-8"))
LAST = 2026
DROP = re.compile(r"indoor|short course|all-time|champion|road|low-altitude|wheelchair|handcycle|inline|professional",
                  re.I)
MEN = re.compile(r"\bmen\b|\bmen's\b", re.I)
WOMEN = re.compile(r"\bwomen\b|\bwomen's\b", re.I)


def marks(title, sex, kind, single_sex_page):
    rows = []
    for head, df in W.tables(title):
        if DROP.search(head):
            continue
        if not single_sex_page:
            if sex == "M" and not (MEN.search(head) and not WOMEN.search(head)):
                continue
            if sex == "W" and not WOMEN.search(head):
                continue
        p = W.progression(df, kind)
        if p is not None:
            med = p["mark"].median()
            p = p[(p["mark"] > .6 * med) & (p["mark"] < 1.6 * med)]   # drop misparsed cells
            rows.append(p)
    if not rows:
        return None
    out = pd.concat(rows).sort_values("year")
    med = out["mark"].median()
    return out[(out["mark"] > .6 * med) & (out["mark"] < 1.6 * med)]


def annual(p, kind, start):
    best = p.groupby("year")["mark"].agg("min" if kind == "time" else "max")
    years = range(int(best.index.min()), LAST + 1)
    s = best.reindex(years)
    s = s.cummin() if kind == "time" else s.cummax()
    return s.ffill()[lambda x: x.index >= start]


events, series = [], []
for e in META["events"]:
    if not e.get("comparable") or not e.get("wiki_men"):
        continue
    kind = e["kind"]
    same = e["wiki_men"] == e["wiki_women"]
    m = marks(e["wiki_men"], "M", kind, not same)
    w = marks(e["wiki_women"], "W", kind, not same)
    if m is None or w is None:
        print("skip", e["event"]); continue
    start = e["women_first_record_year"]
    if e["event"] in ("Pole vault", "Triple jump"):
        start = e["women_official_year"]      # sparse pre-official marks would fake a catch-up
    sm, sw = annual(m, kind, start), annual(w, kind, start)
    df = pd.DataFrame({"men": sm, "women": sw}).dropna()
    df["ratio"] = df.men / df.women if kind == "time" else df.women / df.men
    df["event"], df["sport"], df["kind"] = e["event"], e["sport"], kind
    df["t"] = df.index - start
    series.append(df.reset_index().rename(columns={"index": "year"}))
    events.append({"event": e["event"], "sport": e["sport"], "kind": kind, "start": start,
                   "official": e.get("women_official_year"), "olympic_w": e.get("olympic_women"),
                   "olympic_m": e.get("olympic_men"), "doping_note": e.get("doping_note", ""),
                   "first_ratio": round(float(df.ratio.iloc[0]), 4), "now_ratio": round(float(df.ratio.iloc[-1]), 4),
                   "n_records_m": int(len(m)), "n_records_w": int(len(w))})

S = pd.concat(series)
S.to_csv(ROOT / "output" / "record_series.csv", index=False)
ev = pd.DataFrame(events)
ev.to_csv(ROOT / "output" / "events.csv", index=False)
pd.set_option("display.width", 220)
print(ev[["event", "sport", "start", "first_ratio", "now_ratio", "n_records_m", "n_records_w"]].to_string())

# ── Marathon majors: winning times by year ──
def winners(title, combined=False):
    out = []
    for head, df in W.tables(title):
        if DROP.search(head):
            continue
        yc = W.pick(df, "year", "date")
        if combined:
            tcols = [c for c in df.columns if str(c).lower().startswith("time")]
            if len(tcols) < 2 or yc is None:
                continue
            for y, a, b in zip(df[yc], df[tcols[0]], df[tcols[1]]):
                out.append((W.parse_year(y), W.parse_time(a), "M"))
                out.append((W.parse_year(y), W.parse_time(b), "W"))
            break
        sex = "W" if WOMEN.search(head) else ("M" if MEN.search(head) else None)
        tc = W.pick(df, "time")
        if sex and tc is not None and yc is not None:
            out += [(W.parse_year(y), W.parse_time(t), sex) for y, t in zip(df[yc], df[tc])]
    d = pd.DataFrame(out, columns=["year", "secs", "sex"]).dropna()
    d = d[(d.secs > 7000) & (d.secs < 20000)]          # drop non-times and short-course oddities
    return d.groupby(["year", "sex"]).secs.min().unstack()

maj = []
for x in META["world_marathon_majors"]:
    combined = x["race"].split()[0] in ("Berlin", "Chicago")
    w = winners(x["wiki"], combined)
    w["race"] = x["race"]
    maj.append(w.reset_index())
MJ = pd.concat(maj)
MJ.to_csv(ROOT / "output" / "marathon_majors.csv", index=False)
print(MJ.groupby("race").agg(first=("year", "min"), last=("year", "max"), n=("W", "count")))
