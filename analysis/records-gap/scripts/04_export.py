"""Step 4: write the compact JSON the website's records page reads."""
from pathlib import Path
import json
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT.parents[1] / "OneDrive" / "Documents" / "Personal" / "Personal Website" / "personal-site"
R = json.loads((ROOT / "output" / "records_results.json").read_text())
S = pd.read_csv(ROOT / "output" / "record_series.csv")


def fmt_time(s):
    s = float(s)
    h, rem = divmod(s, 3600)
    m, sec = divmod(rem, 60)
    if h:
        return f"{int(h)}:{int(m):02d}:{sec:02.0f}"
    if m:
        return f"{int(m)}:{sec:05.2f}"
    return f"{sec:.2f}"


series = {}
for ev, g in S.groupby("event", sort=False):
    f = fmt_time if g.kind.iloc[0] == "time" else (lambda v: f"{float(v):.2f} m")
    series[ev] = [[int(r.year), f(r.men), f(r.women), round(float(r.ratio), 4)] for r in g.itertuples()]

out = {k: R[k] for k in ("events", "curves", "pooled", "whipp_ward", "majors", "frozen")}
out["series"] = series
path = SITE / "records-data.json"
path.write_text(json.dumps(out, separators=(",", ":")))
print(path.name, path.stat().st_size, "bytes")
