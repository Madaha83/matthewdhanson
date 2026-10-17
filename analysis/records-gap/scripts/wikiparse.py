"""Helpers to turn cached Wikipedia tables into tidy (year, mark) series."""
from pathlib import Path
import io, json, re, urllib.parse
import pandas as pd
from bs4 import BeautifulSoup

CACHE = Path(__file__).resolve().parents[1] / "data" / "wiki"


def load(title):
    p = CACHE / (urllib.parse.quote(title.replace(" ", "_"), safe="") + ".json")
    return json.loads(p.read_text(encoding="utf-8"))


EXCLUDED_ROW = re.compile(r"#(?:ffd0bd|fec|fef6e7|cef6f5)\b", re.I)


def tables(title):
    """Return [(headings, DataFrame)] for every wikitable, with the h2/h3/h4 path above it."""
    soup = BeautifulSoup(load(title)["html"], "lxml")
    out, path = [], {}
    for node in soup.find_all(["h2", "h3", "h4", "table"]):
        if node.name in ("h2", "h3", "h4"):
            lvl = int(node.name[1])
            path = {k: v for k, v in path.items() if k < lvl}
            path[lvl] = node.get_text(" ", strip=True)
            continue
        if "wikitable" not in (node.get("class") or []):
            continue
        for sup in node.find_all("sup"):
            sup.decompose()
        # Wikipedia marks rescinded / unratified / pending records only by row colour
        for tr in node.find_all("tr"):
            st = (tr.get("style") or "") + " " + " ".join((c.get("style") or "") for c in tr.find_all(["td", "th"])[:2])
            if EXCLUDED_ROW.search(st):
                tr.decompose()
        try:
            df = pd.read_html(io.StringIO(str(node)))[0]
        except ValueError:
            continue
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = [" ".join(dict.fromkeys(str(c) for c in col)) for col in df.columns]
        out.append((" > ".join(path[k] for k in sorted(path)), df))
    return out


TIME_RE = re.compile(r"(\d+(?::\d{1,2}){0,2}(?:\.\d+)?)")


def parse_time(s):
    """'2:01:39' -> 7299.0 s; '1:40.91' -> 100.91; '9.58' -> 9.58. Returns None if unparseable."""
    if not isinstance(s, str):
        s = str(s)
    s = s.replace(" ", "").replace(" ", "").replace(",", ".")
    m = TIME_RE.search(s)
    if not m:
        return None
    parts = [float(x) for x in m.group(1).split(":")]
    v = 0.0
    for x in parts:
        v = v * 60 + x
    return v


DIST_RE = re.compile(r"(\d+(?:\.\d+)?)\s*m\b")


def parse_distance(s):
    """'6.26 m (20 ft 6 in)' -> 6.26"""
    if not isinstance(s, str):
        s = str(s)
    m = DIST_RE.search(s.replace(",", "."))
    if m:
        return float(m.group(1))
    try:
        return float(s.split()[0])
    except (ValueError, IndexError):
        return None


YEAR_RE = re.compile(r"\b(18[6-9]\d|19\d\d|20[0-2]\d)\b")


def parse_year(s):
    m = YEAR_RE.search(str(s))
    return int(m.group(1)) if m else None


def pick(df, *names):
    for n in names:
        for c in df.columns:
            if str(c).strip().lower().startswith(n):
                return c
    return None


def progression(df, kind):
    """Extract (year, mark) rows from a record-progression table."""
    mc = pick(df, "time", "mark", "height", "distance", "result", "record")
    dc = pick(df, "date", "year")
    if mc is None or dc is None:
        return None
    parse = parse_time if kind == "time" else parse_distance
    rows = []
    for m, d in zip(df[mc], df[dc]):
        v, y = parse(m), parse_year(d)
        if v and y:
            rows.append((y, v))
    return pd.DataFrame(rows, columns=["year", "mark"]) if rows else None
