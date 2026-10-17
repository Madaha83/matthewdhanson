"""Step 5: write the small JSON file the website's charts read."""
from pathlib import Path
import json
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT.parents[1] / "OneDrive" / "Documents" / "Personal" / "Personal Website" / "personal-site"

r = json.loads((ROOT / "output" / "results.json").read_text())
ml = json.loads((ROOT / "output" / "ml.json").read_text())

# Long participation series (2000 onward) for the growth chart
df = pd.read_parquet(ROOT / "data" / "entries.parquet", columns=["Name", "Sex", "Year", "Raw", "Tested"])
d = df[df.Raw & df.Tested & df.Year.between(2000, 2025)].drop_duplicates(["Name", "Year"])
pl = d.groupby(["Year", "Sex"]).size().unstack()
participation = [{"year": int(y), "women": int(row.F), "men": int(row.M)} for y, row in pl.iterrows()]

out = {
    "meta": r["meta"],
    "participation": participation,
    "trend": r["trend"],
    "depth_matched": r["depth_matched"],
    "depth_summary": r["depth_summary"],
    "cell_model": r["cell_model"],
    "careers": {k: r["careers"][k] for k in ("lifters", "entries", "coef", "curve")},
    "robustness": r["robustness"],
    "ml": {k: ml[k] for k in ("n_train", "n_test", "mean_model", "elite_model", "baseline_r2",
                              "perm_importance", "shap_mean_abs", "adjusted_by_year")},
}
path = SITE / "strength-data.json"
path.write_text(json.dumps(out, separators=(",", ":")))
print(path, path.stat().st_size, "bytes")
