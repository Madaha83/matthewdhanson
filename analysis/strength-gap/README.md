# Did more competition close the strength gap?

Analysis behind the research showcase at
[matthewdhanson.com/strength](https://matthewdhanson.com/strength).

Using every full-meet result in the public [OpenPowerlifting](https://www.openpowerlifting.org)
database, it asks whether women's strength grew faster than men's as women's participation
expanded, and how much of the narrowing is explained by a bigger talent pool.

## Reproduce

1. Download `openpowerlifting-latest.zip` from the
   [OpenPowerlifting bulk data page](https://openpowerlifting.gitlab.io/opl-csv/bulk-csv.html)
   and unzip it into `data/` (the raw data is not committed).
2. Create an environment and install `pandas pyarrow numpy scipy scikit-learn statsmodels shap`.
3. Run the scripts in order:

| Script | What it does |
|---|---|
| `scripts/01_prepare.py` | Cleans full-power results and builds career variables |
| `scripts/02_explore.py` | Yearly participation and performance by sex |
| `scripts/03_models.py` | Bootstrapped trends, equal-field comparisons, country-year model, mixed-effects career curves, robustness by division |
| `scripts/04_ml.py` | Gradient-boosted models (mean and 95th-percentile), grouped permutation importance, SHAP, composition-adjusted gap |
| `scripts/05_export.py` | Writes the compact JSON the website's charts read |

`output/` holds the model results used on the site.

## Key choices

- Main sample: drug-tested federations, raw lifting (no suits or shirts), 2012–2025.
- Strength measure: total ÷ bodyweight^(2/3), each lifter's best meet per year.
- Train/test split for machine learning is by lifter.

Limitations are listed at the end of the published page.
