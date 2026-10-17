"""Step 3: has the sex gap narrowed because more women compete?

A. Yearly trends with bootstrap confidence intervals.
B. Depth-matched gap: compare women and men drawn from equally sized pools,
   which removes the statistical advantage of a bigger field.
C. Country-year model: how elite performance scales with field size, by sex,
   and how much of the gap's change field growth accounts for.
D. Career growth curves (mixed-effects model) by sex.
Writes output/results.json for the website.
"""
from pathlib import Path
import json
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output"
rng = np.random.default_rng(2026)
YEARS = range(2012, 2026)         # raw lifting became the main stage around 2012 (see robustness)
TOPK = 10
B = 300

df = pd.read_parquet(ROOT / "data" / "entries.parquet")
df["Strength"] = df["TotalKg"] / df["BodyweightKg"] ** (2 / 3)


def best_per_year(d):
    return d.sort_values("Strength", ascending=False).drop_duplicates(["Name", "Year"])


main = best_per_year(df[df["Raw"] & df["Tested"]])
res = {"meta": {"source": "OpenPowerlifting bulk data, updated 2026-10-09",
                "rows_full_power": int(len(df)),
                "rows_main": int(len(main)),
                "lifters_main": int(main["Name"].nunique()),
                "years": [min(YEARS), max(YEARS)], "topk": TOPK, "boot": B,
                "ci_note": "Bootstrap intervals for extreme statistics (top 10, p99) are approximate."}}

# ── A. Yearly participation and performance ──
part, trend = [], []
for y in YEARS:
    f = main.loc[(main.Year == y) & main.Female, "Strength"].to_numpy()
    m = main.loc[(main.Year == y) & ~main.Female, "Strength"].to_numpy()
    part.append({"year": y, "women": int(len(f)), "men": int(len(m))})
    row = {"year": y}
    for name, fn in [("median", np.median),
                     ("p99", lambda a: np.quantile(a, .99)),
                     ("top", lambda a: np.sort(a)[-TOPK:].mean())]:
        r = fn(f) / fn(m)
        boots = [fn(rng.choice(f, len(f))) / fn(rng.choice(m, len(m))) for _ in range(B)]
        row[name] = [round(r, 4), round(np.quantile(boots, .025), 4), round(np.quantile(boots, .975), 4)]
        row[name + "_f"] = round(float(fn(f)), 2)
        row[name + "_m"] = round(float(fn(m)), 2)
    trend.append(row)
res["participation"] = part
res["trend"] = trend

# ── B. Depth-matched gap ──
# For each year, draw men's pools the size of the women's field (and both
# sexes at a fixed size) and recompute the elite ratio.
FIXED = 400
dm = []
for y in YEARS:
    f = main.loc[(main.Year == y) & main.Female, "Strength"].to_numpy()
    m = main.loc[(main.Year == y) & ~main.Female, "Strength"].to_numpy()
    top = lambda a: np.sort(a)[-TOPK:].mean()
    matched = [top(f) / top(rng.choice(m, len(f), replace=False)) for _ in range(B)]
    row = {"year": y, "observed": round(top(f) / top(m), 4),
           "matched": [round(np.mean(matched), 4), round(np.quantile(matched, .025), 4), round(np.quantile(matched, .975), 4)]}
    if len(f) >= FIXED:
        fixed = [top(rng.choice(f, FIXED, replace=False)) / top(rng.choice(m, FIXED, replace=False)) for _ in range(B)]
        row["fixed"] = [round(np.mean(fixed), 4), round(np.quantile(fixed, .025), 4), round(np.quantile(fixed, .975), 4)]
    dm.append(row)
res["depth_matched"] = dm
first, last = dm[0], dm[-1]
tr = {r["year"]: r for r in trend}
y0, y1 = first["year"], last["year"]
obs = last["observed"] - first["observed"]
res["depth_summary"] = {
    "from": y0, "to": y1,
    "observed_top10": round(obs, 4),
    "matched_to_women_n": round(last["matched"][0] - first["matched"][0], 4),
    "fixed_pool": round(last["fixed"][0] - first["fixed"][0], 4),
    "p99": round(tr[y1]["p99"][0] - tr[y0]["p99"][0], 4),
    "median": round(tr[y1]["median"][0] - tr[y0]["median"][0], 4),
}
for k in ["matched_to_women_n", "fixed_pool", "p99"]:
    res["depth_summary"]["share_" + k] = round(1 - res["depth_summary"][k] / obs, 3)
res["meta"]["fixed_pool"] = FIXED

# ── C. Country-year cells: elite strength vs field size ──
cells = (main[main.Year.between(2005, 2025)]
         .groupby(["Country", "Year", "Sex"])["Strength"]
         .agg(n="size", top=lambda s: s.nlargest(5).mean()).reset_index())
cells = cells[cells.n >= 30].copy()
cells["logn"] = np.log(cells.n)
cells["female"] = (cells.Sex == "F").astype(int)
cells["logtop"] = np.log(cells["top"])
FORM = "logtop ~ female * C(Year) + female:logn + logn + C(Country)"
mod = smf.ols(FORM, data=cells).fit(cov_type="cluster", cov_kwds={"groups": cells["Country"]})
pick = ["logn", "female:logn"]
res["cell_model"] = {
    "formula": FORM, "min_n": 30,
    "n_cells": int(len(cells)), "n_countries": int(cells.Country.nunique()), "r2": round(mod.rsquared, 3),
    "coef": {k: [round(mod.params[k], 4), round(mod.bse[k], 4), float(f"{mod.pvalues[k]:.2g}")] for k in pick},
}
# Note: a USA-only decomposition and an extreme-value benchmark were tried and
# dropped after methods review: within one country, women's field size rises
# almost in lockstep with calendar time, so depth and trend cannot be separated.

# Scatter data: field size vs elite strength, by sex (USA + other large countries)
sc = cells[cells.Country.isin(cells.groupby("Country").n.sum().nlargest(8).index)]
res["cells_scatter"] = [{"c": r.Country, "y": int(r.Year), "s": r.Sex, "n": int(r.n), "top": round(r.top, 2)}
                        for r in sc.itertuples()]

# ── D. Career growth curves ──
# Lifters with 3+ raw tested meets who started 2012 or later; first 5 years.
car = df[df["Raw"] & df["Tested"] & df.FirstYear.between(2012, 2020)].copy()   # cohorts observable for 4+ years
car = car[car.CareerYears <= 4]
cnt = car.groupby("Name").size()
car = car[car.Name.isin(cnt[cnt >= 3].index)]
ids = car.Name.drop_duplicates().sample(n=min(30000, car.Name.nunique()), random_state=1)
car = car[car.Name.isin(ids)].sort_values(["Name", "Date"]).copy()
car["female"] = car.Female.astype(int)
car["t"] = car.CareerYears
car["t2"] = car.t ** 2
car["logS"] = np.log(car.Strength)
a0 = car.groupby("Name")["Age"].transform(lambda s: s.iloc[0])
car["age_missing"] = a0.isna().astype(int)
car["age0"] = a0.fillna(a0.median()) - 25
mm = smf.mixedlm("logS ~ female * (t + t2) + age0 + I(age0**2) + age_missing", car, groups=car["Name"],
                 re_formula="~t").fit(method="lbfgs")
fe = mm.fe_params
grid = np.round(np.arange(0, 4.01, .25), 2)
curve = []
for s, fem in [("F", 1), ("M", 0)]:
    base = fe["Intercept"] + fe["female"] * fem
    for t in grid:
        v = base + (fe["t"] + fe["female:t"] * fem) * t + (fe["t2"] + fe["female:t2"] * fem) * t * t
        curve.append({"sex": s, "t": float(t), "pct": round((np.exp(v - base) - 1) * 100, 2)})
res["careers"] = {"lifters": int(car.Name.nunique()), "entries": int(len(car)),
                  "coef": {k: [round(fe[k], 4), round(mm.bse_fe[k], 4), float(f"{mm.pvalues[k]:.2g}")]
                           for k in ["female", "t", "female:t", "t2", "female:t2"]},
                  "curve": curve}

# ── Robustness: other divisions ──
rob = []
for label, mask in [("Raw, tested", df.Raw & df.Tested), ("Strict raw (no wraps), tested", df.RawStrict & df.Tested), ("Raw, untested", df.Raw & ~df.Tested),
                    ("Equipped, tested", ~df.Raw & df.Tested), ("Equipped, untested", ~df.Raw & ~df.Tested)]:
    b_ = best_per_year(df[mask])
    for y in range(1985, 2026):
        f = b_.loc[(b_.Year == y) & b_.Female, "Strength"]
        m = b_.loc[(b_.Year == y) & ~b_.Female, "Strength"]
        if len(f) >= 50 and len(m) >= 50:
            rob.append({"div": label, "year": y, "nf": int(len(f)), "nm": int(len(m)),
                        "top": round(f.nlargest(TOPK).mean() / m.nlargest(TOPK).mean(), 4),
                        "median": round(f.median() / m.median(), 4)})
res["robustness"] = rob

(OUT / "results.json").write_text(json.dumps(res, indent=1))
print(json.dumps({k: res[k] for k in ["meta", "depth_summary", "cell_model"]}, indent=1))
print(res["careers"]["coef"], [c for c in res["careers"]["curve"] if c["t"] in (1, 2, 3, 4)])
print("depth matched (first/last):", dm[0], dm[-1], sep="\n")
