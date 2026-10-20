# Statistical helpers for survey-weighted music listening analysis.
import pandas as pd
from utils.constants import *


def weighted_share(frame: pd.DataFrame, column: str, numerator_values: set) -> float | None:
    """Calculate a weighted percentage among valid answers to a survey question."""

    # Use only respondents with a valid survey weight and a non-missing answer.
    valid = frame.loc[frame["valid_weight"] & frame[column].notna()]

    # The denominator is the sum of valid survey weights, not the row count.
    total = valid["poids"].sum()
    if total <= 0:
        return None

    # Divide the weight of the selected answers by the total valid weight.
    return 100.0 * valid.loc[valid[column].isin(numerator_values), "poids"].sum() / total


def weighted_distribution(frame: pd.DataFrame, column: str, ordered_labels: list[str]) -> pd.DataFrame:
    """Return the weighted share of each recognized response category."""

    # Restrict the calculation to positive-weight respondents with known labels.
    valid = frame.loc[frame["valid_weight"] & frame[column].isin(ordered_labels)]

    # Sum weights by response and keep a consistent category order for charts.
    totals = valid.groupby(column, observed=True)["poids"].sum().reindex(ordered_labels, fill_value=0)

    # Calculate each category's share of total valid weight.
    # If the denominator is zero, return zero shares rather than dividing by zero.
    denominator = totals.sum()
    return pd.DataFrame({column: ordered_labels, "share": (totals / denominator * 100 if denominator > 0 else totals).values})


def weighted_age_table(frame: pd.DataFrame) -> pd.DataFrame:
    """Compare daily listening across age groups using valid Q3 responses."""

    # Build one result row per age group, following the order used in the dashboard.
    rows = []
    for age in AGE_LABELS.values():
        group = frame.loc[frame["age_group"] == age]

        # Keep respondents with a valid weight and recognized Q3 frequency answer.
        valid = group.loc[group["valid_weight"] & group["Q3"].isin(FREQ_LABELS)]
        denominator = valid["poids"].sum()

        if denominator > 0:
            # The first two Q3 categories represent daily or more frequent listening.
            daily = valid.loc[valid["Q3"].isin(list(FREQ_LABELS)[:2]), "poids"].sum()

            # Percentages are weighted; the sample-size tooltip is unweighted.
            rows.append({"Age group": age, "Daily listeners (%)": 100 * daily / denominator, "Valid responses": len(valid)})

    # Return a chart-ready table for the generational comparison.
    return pd.DataFrame(rows)
