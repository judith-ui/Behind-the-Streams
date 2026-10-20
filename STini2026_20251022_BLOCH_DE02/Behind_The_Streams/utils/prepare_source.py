"""Prepare the original Hadopi survey file for the Streamlit dashboard."""

from pathlib import Path
import pandas as pd


# Locate the project directory and define the input and output data files.
# This assumes prepare_data.py is stored in a subfolder such as utils/.
BASE = Path(__file__).resolve().parents[1]
SOURCE = BASE / "data" / "hadopi-2020-musique-data.ods"
OUTPUT = BASE / "data" / "hadopi_clean.csv"


# Stop with a helpful error if the original survey file is unavailable.
if not SOURCE.exists():
    raise FileNotFoundError(
        f"Source file not found: {SOURCE}\n"
        "Place the original .ods file in the project's data/ folder."
    )


# Read the first worksheet of the Hadopi ODS file using the Calamine engine.
# Keep the original survey answers for traceability.
df = pd.read_excel(SOURCE, engine="calamine", sheet_name=0)
print("Original dataset dimensions:", df.shape)


# Remove only completely empty rows, then standardize column names.
# Individual missing survey answers are retained.
df = df.dropna(how="all").copy()
df.columns = df.columns.astype(str).str.strip()


# Treat explicit null markers and empty strings as missing values.
# A missing response should not be confused with a negative answer.
df = df.replace(["#NUL!", "#NULL!", ""], pd.NA)


# Confirm that the essential demographic, listening, and weight fields exist.
required = ["SEXE", "RAGE2", "Q3", "Q4", "poids"]
missing = [name for name in required if name not in df.columns]
if missing:
    raise ValueError(f"Required survey columns are missing: {missing}")


# Convert survey weights to numeric values, including comma-decimal strings.
# Flag missing, nonnumeric, zero, and negative weights for later checks.
df["poids"] = pd.to_numeric(
    df["poids"].astype("string").str.replace(",", ".", regex=False),
    errors="coerce",
)
df["poids_valide"] = df["poids"].notna() & df["poids"].gt(0)


# Report data quality diagnostics without automatically removing duplicates or respondents who were not asked every questionnaire item.
print("Dimensions after removing fully empty rows:", df.shape)
print(
    "Matching full rows:",
    int(df.drop(columns="poids_valide").duplicated().sum()),
)
print("Invalid survey weights:", int((~df["poids_valide"]).sum()))
print("Missing values in key columns:")
print(df[required].isna().sum().to_string())


# Inspect raw Q3 response categories before mapping them to English labels inside the Streamlit application.
print("\nRaw listening-frequency distribution (Q3):")
print(df["Q3"].value_counts(dropna=False).head(15).to_string())


# Export the prepared dataset as a UTF-8 CSV for efficient dashboard loading.
# The original ODS file remains unchanged.
df.to_csv(OUTPUT, index=False, encoding="utf-8-sig")
print(f"\nCleaned CSV exported to: {OUTPUT}")
