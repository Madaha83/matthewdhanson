"""Step 1: load the OpenPowerlifting bulk CSV and build tidy analysis tables.

Keeps full-power (squat, bench, deadlift) results with a valid total and
bodyweight, for men and women. Writes a compact parquet used by later steps.
"""
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = next((ROOT / "data").glob("openpowerlifting-*/openpowerlifting-*.csv"))
OUT = ROOT / "data" / "entries.parquet"

COLS = ["Name", "Sex", "Event", "Equipment", "Age", "BodyweightKg",
        "Best3SquatKg", "Best3BenchKg", "Best3DeadliftKg", "TotalKg", "Place",
        "Dots", "Tested", "Country", "Federation", "ParentFederation", "Date", "MeetName"]

df = pd.read_csv(RAW, usecols=COLS, dtype={"Tested": "string", "Place": "string"},
                 low_memory=False)
n0 = len(df)

df = df[(df["Event"] == "SBD") & df["Sex"].isin(["M", "F"])]
df = df[pd.to_numeric(df["Place"], errors="coerce").notna()]          # drop DQ / guest / no-show
for c in ["TotalKg", "BodyweightKg", "Best3SquatKg", "Best3BenchKg", "Best3DeadliftKg", "Dots"]:
    df = df[df[c].notna() & (df[c] > 0)]
df = df[(df["BodyweightKg"] >= 30) & (df["BodyweightKg"] <= 250)]

df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
df = df[df["Date"].notna()]
df["Year"] = df["Date"].dt.year.astype("int16")
df["Tested"] = df["Tested"].fillna("No").eq("Yes")
df["Raw"] = df["Equipment"].isin(["Raw", "Wraps"])      # no supportive suits or shirts
df["RawStrict"] = df["Equipment"].eq("Raw")
df["Female"] = df["Sex"].eq("F")

# Career variables per lifter (OpenPowerlifting disambiguates names with "#n")
df = df.sort_values(["Name", "Date"])
first = df.groupby("Name")["Date"].transform("min")
df["CareerYears"] = ((df["Date"] - first).dt.days / 365.25).astype("float32")
df["MeetNumber"] = df.groupby("Name").cumcount().astype("int16") + 1
df["FirstYear"] = df.groupby("Name")["Year"].transform("min").astype("int16")

keep = ["Name", "Sex", "Female", "Equipment", "Raw", "RawStrict", "Tested", "Age", "BodyweightKg",
        "Best3SquatKg", "Best3BenchKg", "Best3DeadliftKg", "TotalKg", "Dots",
        "Country", "Federation", "ParentFederation", "Date", "Year", "MeetName",
        "CareerYears", "MeetNumber", "FirstYear"]
df[keep].to_parquet(OUT, index=False)

print(f"rows read: {n0:,}  kept: {len(df):,}")
print(df.groupby(["Raw", "Tested", "Sex"]).size().unstack())
print("years:", df["Year"].min(), "-", df["Year"].max())
print("lifters:", df["Name"].nunique())
