"""Step 4: machine learning.

Gradient-boosted trees predict a lifter's bodyweight-adjusted strength from
who they are (sex, age, bodyweight, experience) and the competitive context
(year, country, size of the same-sex field). Two models:
  - mean model (squared error): typical performance, explained with SHAP
  - elite model (95th-percentile quantile loss): what the strongest lifters
    in a given context reach
Train/test split is by lifter, so no one appears in both.
"""
from pathlib import Path
import json
import numpy as np
import pandas as pd
import shap
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.inspection import permutation_importance
from sklearn.metrics import r2_score, mean_absolute_error, mean_pinball_loss
from sklearn.model_selection import GroupShuffleSplit

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output"

df = pd.read_parquet(ROOT / "data" / "entries.parquet")
d = df[df.Raw & df.Tested & df.Year.between(2012, 2025)].copy()
d["Strength"] = d.TotalKg / d.BodyweightKg ** (2 / 3)
d = d.sort_values("Strength", ascending=False).drop_duplicates(["Name", "Year"])

d["Country"] = d.Country.fillna("Unknown")
fld = d.groupby(["Country", "Year", "Sex"]).Name.transform("size")
d["FieldSize"] = fld
d["WomenShare"] = d.groupby(["Country", "Year"]).Female.transform("mean")
top = d.Country.value_counts().index[:25]
d["CountryCat"] = pd.Categorical(np.where(d.Country.isin(top), d.Country, "Other"))
d["Age"] = d.Age.fillna(d.Age.median())

FEATS = ["Female", "Age", "BodyweightKg", "CareerYears", "MeetNumber", "Year",
         "FieldSize", "WomenShare", "CountryCat"]
LABEL = {"Female": "Sex (female)", "Age": "Age", "BodyweightKg": "Bodyweight", "CareerYears": "Years competing",
         "MeetNumber": "Meets completed", "Year": "Calendar year", "FieldSize": "Same-sex field size",
         "WomenShare": "Women's share of field", "CountryCat": "Country"}
X = d[FEATS].copy()
X["Female"] = X.Female.astype(int)
X["MeetNumber"] = X.MeetNumber.clip(upper=40)
CATS = list(X.CountryCat.cat.categories)
X["CountryCat"] = X.CountryCat.cat.codes.astype("int16")
y = np.log(d.Strength.to_numpy())

tr, te = next(GroupShuffleSplit(test_size=.2, random_state=7).split(X, y, d.Name))
Xtr, Xte, ytr, yte = X.iloc[tr], X.iloc[te], y[tr], y[te]

common = dict(categorical_features=["CountryCat"], max_iter=600, learning_rate=.06,
              max_leaf_nodes=63, min_samples_leaf=80, l2_regularization=1.0,
              early_stopping=True, validation_fraction=.1, random_state=7)
mean_m = HistGradientBoostingRegressor(**common).fit(Xtr, ytr)
q_m = HistGradientBoostingRegressor(loss="quantile", quantile=.95, **common).fit(Xtr, ytr)

pred = mean_m.predict(Xte)
res = {"n_train": int(len(tr)), "n_test": int(len(te)),
       "mean_model": {"r2": round(r2_score(yte, pred), 3),
                      "mae_pct": round(float(np.mean(np.abs(np.exp(pred) / np.exp(yte) - 1))) * 100, 1),
                      "iters": int(mean_m.n_iter_)},
       "elite_model": {"pinball": round(mean_pinball_loss(yte, q_m.predict(Xte), alpha=.95), 4),
                       "coverage": round(float(np.mean(yte <= q_m.predict(Xte))), 3),
                       "iters": int(q_m.n_iter_)}}

# Baseline: sex + bodyweight + age only, to show what context adds
base = HistGradientBoostingRegressor(**{**common, "categorical_features": None}).fit(Xtr[["Female", "Age", "BodyweightKg"]], ytr)
res["baseline_r2"] = round(r2_score(yte, base.predict(Xte[["Female", "Age", "BodyweightKg"]])), 3)

# Grouped permutation importance: shuffle related features together so that
# credit isn't split between correlated inputs (sex and bodyweight especially).
GROUPS = {"Sex & bodyweight": ["Female", "BodyweightKg"], "Age": ["Age"],
          "Experience (years, meets)": ["CareerYears", "MeetNumber"],
          "Calendar year": ["Year"], "Field (size, women's share)": ["FieldSize", "WomenShare"],
          "Country": ["CountryCat"]}
rng = np.random.default_rng(1)
s_idx = rng.choice(len(Xte), 40000, replace=False)
Xs_, ys_ = Xte.iloc[s_idx].reset_index(drop=True), yte[s_idx]
base_r2 = r2_score(ys_, mean_m.predict(Xs_))
gi = []
for name, cols in GROUPS.items():
    drops = []
    for rep in range(5):
        Xp = Xs_.copy()
        perm = rng.permutation(len(Xp))
        Xp[cols] = Xp[cols].to_numpy()[perm]
        drops.append(base_r2 - r2_score(ys_, mean_m.predict(Xp)))
    gi.append({"feature": name, "drop_r2": round(float(np.mean(drops)), 4)})
res["perm_importance"] = sorted(gi, key=lambda r: -r["drop_r2"])

# SHAP (individual features) kept for the methods appendix only
Xsh = Xs_.iloc[:4000]
sv = shap.TreeExplainer(mean_m).shap_values(Xsh)
res["shap_mean_abs"] = sorted([{"feature": LABEL[f], "value": round(float(np.abs(sv[:, i]).mean()), 4)}
                               for i, f in enumerate(FEATS)], key=lambda r: -r["value"])

# Composition-adjusted gap by year: take each sex's lifters as observed (age,
# bodyweight, experience, country, field) and set only the calendar year, for
# both the typical (mean) and elite (95th percentile) models.
samp = X.sample(60000, random_state=3)
adj = []
for yr in range(2012, 2026):
    Xy = samp.copy(); Xy["Year"] = yr
    row = {"year": yr}
    for name, mdl in (("typical", mean_m), ("elite", q_m)):
        p_ = np.exp(mdl.predict(Xy))
        f, m = p_[Xy.Female.to_numpy() == 1].mean(), p_[Xy.Female.to_numpy() == 0].mean()
        row[name] = round(float(f / m), 4); row[name + "_f"] = round(float(f), 2); row[name + "_m"] = round(float(m), 2)
    adj.append(row)
res["adjusted_by_year"] = adj

(OUT / "ml.json").write_text(json.dumps(res, indent=1))
print(json.dumps({k: v for k, v in res.items() if k != "adjusted_by_year"}, indent=1))
for r in adj: print(r)
