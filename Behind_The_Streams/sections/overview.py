# Import libraries and shared project utilities for the dashboard overview.
import streamlit as st
import pandas as pd
import plotly.express as px
from utils.constants import *
from utils.prep import *
from utils.viz import apply_chart_style


def render_overview(subset, frequency_valid, daily, duration):
    """Introduce the survey sample and establish the listening-frequency baseline."""

    # Separate the introductory section from the dashboard's main indicators.
    st.markdown("---")
    st.markdown("### At a glance")

    # Summarize the selected sample and two key weighted listening indicators.
    # Counts are unweighted, while the listening percentages use survey weights.
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Respondents (unweighted)", f"{len(subset):,}")
    k2.metric("Valid frequency answers", f"{len(frequency_valid):,}")
    k3.metric(
        "Listen daily",
        f"{daily:.1f}%" if daily is not None else "N/A",
        help="Weighted share of valid Q3 respondents who listen several times a day or every day or almost every day."
    )
    k4.metric(
        "Listen 2+ hours/day",
        f"{duration:.1f}%" if duration is not None else "N/A",
        help="Weighted share of valid Q4 answers reporting at least two hours of daily listening. Q4 has its own eligible response base."
    )

    # Start the narrative with the broadest question before comparing audiences.
    st.markdown("---")
    st.markdown("### 1 : Music is a regular part of everyday life")
    st.caption("QUESTION: How often does music fit into everyday routines ?")
    st.write(
        "We begin with listening frequency to establish a starting point for the story. "
        "The Hadopi survey covers music and music videos across different formats and services, "
        "rather than Spotify activity alone."
    )

    # Calculate the weighted distribution of the six recognized Q3 categories.
    frequency_dist = weighted_distribution(
        subset,
        "frequency",
        list(FREQ_LABELS.values())
    )

    # Display a horizontal bar chart so response categories are easy to compare.
    fig1 = px.bar(
        frequency_dist,
        x="share",
        y="frequency",
        orientation="h",
        text="share",
        color_discrete_sequence=[GREEN],
        labels={
            "share": "Weighted share (%)",
            "frequency": "Listening frequency"
        }
    )

    # Show precise percentages and preserve the questionnaire's response order.
    fig1.update_traces(
        texttemplate="%{text:.1f}%",
        textposition="outside",
        cliponaxis=False
    )
    fig1.update_layout(
        yaxis=dict(
            categoryorder="array",
            categoryarray=list(reversed(list(FREQ_LABELS.values())))
        ),
        margin=dict(l=10, r=60, t=15, b=15),
        height=380
    )

    # Apply the same dark theme used throughout the Streamlit dashboard.
    fig1.update_layout(
        template="plotly_dark",
        paper_bgcolor=BG,
        plot_bgcolor=BG,
        font_color="#F0F6FC"
    )
    st.plotly_chart(apply_chart_style(fig1), use_container_width=True)

    # Explain why this overall percentage matters before exploring age differences.
    if daily is not None and not frequency_dist.empty:
        dominant = frequency_dist.loc[frequency_dist["share"].idxmax()]
        st.markdown(
            f"**What this reveals.** **{daily:.1f}%** of respondents with valid Q3 answers "
            f"listen to music at least daily (survey-weighted), and the most common single "
            f"answer is **{dominant['frequency'].lower()}** "
            f"(**{dominant['share']:.1f}%**). "
            "This gives us a useful starting point, but an overall percentage can hide "
            "very different habits across generations which is what we explore next."
        )

    # End the overview before the generational comparison section begins.
    st.markdown("---")
