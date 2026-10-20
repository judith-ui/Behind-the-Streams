"""Main entry point for the Behind the Streams Streamlit dashboard."""

# Import Streamlit and the shared data paths, survey categories, and calculations.
import streamlit as st
from utils.constants import BASE, DATA_PATH, AGE_LABELS, GENDER_LABELS, FREQ_LABELS, DURATION_LABELS
from utils.io import load_data
from utils.prep import weighted_share
from utils.viz import apply_site_style

# Import each dashboard section so the narrative remains modular and maintainable.
from sections.intro import render_intro
from sections.overview import render_overview
from sections.deep_dives import render_generations, render_duration, render_payment, render_geography
from sections.conclusions import render_conclusions


# Configure the browser tab, page layout, and shared visual theme.
st.set_page_config(
    page_title="Behind the Streams | Hadopi Survey",
    page_icon="🎧",
    layout="wide",
)
apply_site_style()

# Introduce the research question and the official Hadopi data source.
render_intro()


# Stop with a helpful message if the prepared CSV is not yet available.
if not DATA_PATH.exists():
    st.error("Clean data not found. Run `python prepare_data.py` first.")
    st.stop()

# Load the data and display an understandable error if the CSV cannot be read.
# The modification time allows Streamlit's cache to refresh when the file changes.
try:
    df = load_data(str(DATA_PATH), DATA_PATH.stat().st_mtime)
except Exception as exc:
    st.error(f"Could not load clean data: {exc}")
    st.stop()


# Let readers explore the survey by age and gender using the sidebar.
with st.sidebar:
    st.image("assets/behind_the_streams_logo.png", use_container_width=True)
    st.header("Explore the survey")
    selected_ages = st.multiselect(
        "Age groups",
        list(AGE_LABELS.values()),
        default=list(AGE_LABELS.values()),
    )
    selected_genders = st.multiselect(
        "Gender",
        list(GENDER_LABELS.values()),
        default=list(GENDER_LABELS.values()),
    )
    st.caption("Percentages are survey-weighted. Counts are unweighted.")

# Apply the selected filters before calculating any results or drawing charts.
subset = df.loc[
    df["age_group"].isin(selected_ages)
    & df["gender"].isin(selected_genders)
].copy()

# Avoid calculations on an empty respondent selection.
if subset.empty:
    st.warning("No respondents match these filters. Select at least one age group and one gender.")
    st.stop()


# Identify valid Q3 respondents for the response-count indicator.
frequency_valid = subset.loc[
    subset["valid_weight"] & subset["Q3"].isin(FREQ_LABELS.keys())
]

# Compute daily listening using the first two Q3 frequency categories.
# Each weighted percentage uses valid responses to its own survey question.
daily = weighted_share(
    subset.loc[subset["Q3"].isin(FREQ_LABELS.keys())],
    "Q3",
    set(list(FREQ_LABELS)[:2]),
)

# Compute the share reporting two or more hours per day among valid Q4 answers.
duration = weighted_share(
    subset.loc[subset["Q4"].isin(DURATION_LABELS.keys())],
    "Q4",
    set(list(DURATION_LABELS)[2:]),
)


# Render the story in order: overview, generations, duration, payment, and region.
render_overview(subset, frequency_valid, daily, duration)
age_df = render_generations(subset)
render_duration(subset, duration)
intent_valid = render_payment(subset)
render_geography(subset)

# Finish with connected insights, methodological checks, and the final takeaway.
render_conclusions(subset, age_df, intent_valid, frequency_valid, daily, duration)
