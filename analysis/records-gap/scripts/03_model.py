"""Step 3: catch-up curves.

For each event, model the women/men world-record ratio as rising from its
starting level toward a plateau:

    r(t) = a - (a - b) * exp(-t / tau)

t = years since women's records begin, a = plateau, b = starting ratio,
tau = catch-up time constant (95% of the catch-up is done after 3 * tau).
Uncertainty: moving-block bootstrap of residuals (records are serially
dependent, so independent resampling would be too optimistic).

Also: a pooled fit with one shared tau, a "frozen record" sensitivity check,
the recent-trend straight-line projection (the method behind the famous
1992 prediction), and the marathon-majors winners series.
"""
from pathlib import Path
import json
import numpy as np
import pandas as pd
from scipy.optimize import curve_fit, least_squares

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output"
S = pd.read_csv(OUT / "record_series.csv")
EV = pd.read_csv(OUT / "events.csv")
MJ = pd.read_csv(OUT / "marathon_majors.csv")
rng = np.random.default_rng(1992)
B, BLOCK = 150, 18

# Women's records that have stood since the 1980s-90s doping era (frozen series)
FROZEN = {"100 m", "200 m", "400 m", "800 m", "3000 m", "Long jump"}


def curve(t, a, b, tau, t0=0.0):
    """Flat at b until onset t0, then exponential approach to plateau a."""
    tt = np.clip(np.asarray(t, float) - t0, 0, None)
    return a - (a - b) * np.exp(-tt / tau)


def fit(t, r, step=2):
    """Grid-search the onset year t0; least squares for plateau, start level, tau."""
    best = None
    for t0 in np.arange(0, max(1, t.max() - 15), step):
        f = lambda tt, a, b, tau: curve(tt, a, b, tau, t0)
        b0 = r[t <= t0].mean() if (t <= t0).any() else r[0]
        try:
            p, _ = curve_fit(f, t, r, p0=[min(r.max() + .02, 1.1), b0, 10],
                             bounds=([.5, .3, .5], [1.3, 1.1, 150]), maxfev=5000)
        except RuntimeError:
            continue
        sse = float(np.sum((r - f(t, *p)) ** 2))
        if best is None or sse < best[0]:
            best = (sse, [*p, t0])
    return np.array(best[1])


def block_boot(t, r, p):
    res = r - curve(t, *p)
    n, out = len(r), []
    for _ in range(B):
        idx = np.concatenate([np.arange(s, s + BLOCK) for s in rng.integers(0, n - BLOCK + 1, n // BLOCK + 1)])[:n]
        try:
            out.append(fit(t, curve(t, *p) + res[idx]))
        except RuntimeError:
            pass
    return np.array(out)


def gain(g, col, kind):
    """Percent improvement in the standing record from 2000 to the latest year."""
    a = g.loc[g.year == 2000, col]
    if a.empty:
        return float("nan")
    a, b = float(a.iloc[0]), float(g[col].iloc[-1])
    return (a / b - 1) if kind == "time" else (b / a - 1)


rows, curves = [], []
for ev, g in S.groupby("event", sort=False):
    g = g.sort_values("t")
    t, r = g.t.to_numpy(float), g.ratio.to_numpy(float)
    p = fit(t, r)
    bs = block_boot(t, r, p)
    lo, hi = np.quantile(bs, [.025, .975], axis=0)
    # straight-line trend over the last 20 years and the implied year of parity
    last = g[g.year >= g.year.max() - 20]
    slope = np.polyfit(last.year, last.ratio, 1)[0]
    now = float(g.ratio.iloc[-1])
    parity = int(g.year.max() + (1 - now) / slope) if slope > 1e-6 else None
    e = EV.set_index("event").loc[ev]
    rows.append({
        "event": ev, "sport": e.sport, "start": int(e.start), "years": int(t.max()),
        "ratio_start": round(float(r[0]), 4), "ratio_now": round(now, 4),
        "plateau": round(float(p[0]), 4), "plateau_ci": [round(float(lo[0]), 4), round(float(hi[0]), 4)],
        "tau": round(float(p[2]), 1), "tau_ci": [round(float(lo[2]), 1), round(float(hi[2]), 1)],
        "years_to_95": round(float(3 * p[2]), 0),
        "onset_year": int(e.start + p[3]), "onset_ci": [int(e.start + lo[3]), int(e.start + hi[3])],
        "years_to_95_from_onset_ci": [round(float(3 * lo[2])), round(float(3 * hi[2]))],
        "plateau_below_parity": bool(hi[0] < 1),
        "slope_20y_per_decade": round(float(slope * 10), 4),
        "linear_parity_year": parity,
        "frozen": ev in FROZEN,
        "identified": bool(p[2] > 1 and hi[2] < 140 and lo[2] > .6),
        "n_changes_w": int((np.diff(g.women.to_numpy()) != 0).sum()),
        "gain_2000_m": round(gain(g, "men", e.kind), 4), "gain_2000_w": round(gain(g, "women", e.kind), 4),
    })
    curves.append({"event": ev, "sport": e.sport, "start": int(e.start),
                   "points": [[int(y), round(float(v), 4)] for y, v in zip(g.year, g.ratio)],
                   "fit": [[int(e.start + tt), round(float(curve(tt, *p)), 4)] for tt in range(0, int(t.max()) + 1)]})

R = pd.DataFrame(rows)
pd.set_option("display.width", 250)
print(R.drop(columns=["plateau_ci", "tau_ci"]).to_string())


# ── Pooled fit: event-specific start and plateau, one shared tau ──
ONSET = {r_["event"]: r_["onset_year"] - r_["start"] for r_ in rows}


def pooled(sub):
    evs = list(sub.event.unique())
    T = [np.clip(sub[sub.event == e].t.to_numpy(float) - ONSET[e.split("#")[0]], 0, None) for e in evs]
    Y = [sub[sub.event == e].ratio.to_numpy(float) for e in evs]
    def resid(x):
        tau = x[0]
        return np.concatenate([Y[i] - curve(T[i], x[1 + 2 * i], x[2 + 2 * i], tau) for i in range(len(evs))])
    x0 = [15] + sum([[Y[i].max() + .02, Y[i][0]] for i in range(len(evs))], [])
    lb = [.5] + [.5, .3] * len(evs); ub = [150] + [1.3, 1.1] * len(evs)
    sol = least_squares(resid, x0, bounds=(lb, ub))
    return sol.x[0], sol


IDENT = [r_["event"] for r_ in rows if r_["identified"]]
SI = S[S.event.isin(IDENT)]
tau_all, _ = pooled(SI)
tau_nofrozen, _ = pooled(SI[~SI.event.isin(FROZEN)])
# bootstrap over events for the shared tau (onsets taken as given)
evs = SI.event.unique()
taus = []
for _ in range(200):
    pick = rng.choice(evs, len(evs))
    sub = pd.concat([SI[SI.event == e].assign(event=f"{e}#{i}") for i, e in enumerate(pick)])
    taus.append(pooled(sub)[0])
pooled_res = {"tau": round(float(tau_all), 1), "tau_ci": [round(float(np.quantile(taus, .025)), 1), round(float(np.quantile(taus, .975)), 1)],
              "years_to_95": round(float(3 * tau_all)), "tau_without_frozen": round(float(tau_nofrozen), 1),
              "events_used": IDENT, "note": "Onset years taken as given from each event's own fit."}
print("pooled:", pooled_res)

# ── 1992-style projection for the marathon (data to 1992 only) ──
m = S[S.event == "Marathon"]
pre = m[(m.year >= 1963) & (m.year <= 1992)]
k, c = np.polyfit(pre.year, pre.ratio, 1)
whipp = {"fit_years": [1963, 1992], "slope_per_decade": round(float(k * 10), 4),
         "projected_parity_year": int(round((1 - c) / k)),
         "line": [[int(y), round(float(k * y + c), 4)] for y in range(1963, 2031)],
         "ratio_2026": round(float(m.ratio.iloc[-1]), 4)}
print("1992-style marathon projection:", {k_: v for k_, v in whipp.items() if k_ != "line"})

# ── Marathon majors: winners' speed ratio ──
MJ = MJ.dropna(subset=["M", "W"])
MJ["ratio"] = MJ.M / MJ.W
mj = MJ.groupby("year").ratio.agg(["mean", "count"]).reset_index()
mj = mj[mj["count"] >= 2]
mj_slope = np.polyfit(mj[mj.year >= 1990].year, mj[mj.year >= 1990]["mean"], 1)[0]
majors = {"by_year": [[int(y), round(float(v), 4), int(n)] for y, v, n in mj.itertuples(index=False)],
          "by_race": {race: [[int(y), round(float(v), 4)] for y, v in zip(g.year, g.ratio)] for race, g in MJ.groupby("race")},
          "slope_since_1990_per_decade": round(float(mj_slope * 10), 4)}
print("majors since 1990 slope/decade:", majors["slope_since_1990_per_decade"],
      "| mean 1985-89:", round(mj[mj.year.between(1985, 1989)]["mean"].mean(), 4),
      "| mean 2020-26:", round(mj[mj.year >= 2020]["mean"].mean(), 4))

json.dump({"events": rows, "curves": curves, "pooled": pooled_res, "whipp_ward": whipp, "majors": majors,
           "frozen": sorted(FROZEN), "boot": B, "block": BLOCK},
          open(OUT / "records_results.json", "w"), indent=1)
