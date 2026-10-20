# Load and prepare the Hadopi survey data for the Streamlit dashboard.
import pandas as pd
import streamlit as st
from utils.constants import *


# Cache the prepared DataFrame to avoid repeating the same transformations
# whenever users interact with dashboard filters.
@st.cache_data(show_spinner=False)
def load_data(path: str, modified_time: float) -> pd.DataFrame:
    """Read the cleaned CSV, standardize survey answers, and validate weights."""

    # Read the cleaned dataset while allowing Pandas to inspect column types fully.
    # The modified_time argument changes the cache key when the CSV is updated.
    df = pd.read_csv(path, low_memory=False)

    # Stop early if any column required for the core listening analysis is missing.
    expected = {"SEXE", "RAGE2", "Q3", "Q4", "poids"}
    missing = expected.difference(df.columns)
    if missing:
        raise ValueError(f"Required columns are missing: {sorted(missing)}")

    # The survey stores written answers rather than numeric response codes.
    # Remove surrounding spaces to ensure accurate category matching.
    for col in ["SEXE", "RAGE2", "Q3", "Q4"]:
        df[col] = df[col].astype("string").str.strip()

    # Convert survey weights to numbers, accepting either commas or decimal points.
    # Unrecognized entries become missing values instead of causing an error.
    df["poids"] = pd.to_numeric(
        df["poids"].astype("string").str.replace(",", ".", regex=False),
        errors="coerce",
    )

    # Create readable English labels for demographic and listening variables.
    # Keep the original Hadopi columns unchanged for traceability.
    df["age_group"] = df["RAGE2"].map(AGE_LABELS)
    df["gender"] = df["SEXE"].map(GENDER_LABELS)
    df["frequency"] = df["Q3"].map(FREQ_LABELS)
    df["duration"] = df["Q4"].map(DURATION_LABELS)

    # Q51 measures stated future subscription intention, not actual subscriptions.
    # If it is absent, create a missing-value column for consistent downstream use.
    if "Q51" in df.columns:
        df["Q51"] = df["Q51"].astype("string").str.strip()
        intent_map = {
            "Certainement": "Definitely",
            "Probablement": "Probably",
            "Probablement pas": "Probably not",
            "Certainement pas": "Definitely not",
        }
        df["subscription_intent"] = df["Q51"].map(intent_map)
    else:
        df["subscription_intent"] = pd.Series(
            pd.NA, index=df.index, dtype="string"
        )

    # Translate the Hadopi regional codes for the geographic visualization.
    # Retain a consistent region column even if REG13 is unavailable.
    if "REG13" in df.columns:
        df["REG13"] = df["REG13"].astype("string").str.strip()
        df["region"] = df["REG13"].map(REGION_LABELS)
    else:
        df["region"] = pd.Series(pd.NA, index=df.index, dtype="string")

    # Flag respondents with non-missing, strictly positive survey weights.
    # Subsequent weighted calculations use this flag to select valid records.
    df["valid_weight"] = df["poids"].notna() & (df["poids"] > 0)

    # Return the prepared data for filtering, charts, and quality checks.
    return df
