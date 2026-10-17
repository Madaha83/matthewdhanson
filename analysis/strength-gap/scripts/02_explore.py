"""Step 2: participation and performance trends by sex (exploratory printout)."""
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
df = pd.read_parquet(ROOT / "data" / "entries.parquet")
d = df[df["Raw"] & df["Tested"]].copy()
# Allometric strength: total scaled by bodyweight^(2/3), comparable across sizes
d["Strength"] = d["TotalKg"] / d["BodyweightKg"] ** (2 / 3)

best = (d.sort_values("Strength", ascending=False)
          .drop_duplicates(["Name", "Year"]))          # each lifter's best result per year
g = best.groupby(["Year", "Sex"])
t = pd.DataFrame({
    "lifters": g.size(),
    "median": g["Strength"].median(),
    "p99": g["Strength"].quantile(.99),
    "top10": g["Strength"].apply(lambda s: s.nlargest(10).mean()),
}).unstack("Sex")
t = t[t[("lifters", "F")] >= 20]
for k in ["median", "p99", "top10"]:
    t[(k, "ratio")] = t[(k, "F")] / t[(k, "M")]
pd.set_option("display.width", 200)
print(t.round(3).to_string())
print("\nBodyweight medians:", best.groupby("Sex")["BodyweightKg"].median().to_dict())
print("Countries (raw tested):", d["Country"].value_counts().head(12).to_dict())
print("Federations:", d["Federation"].value_counts().head(12).to_dict())
