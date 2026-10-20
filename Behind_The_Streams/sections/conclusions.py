# Import libraries and utility functions
import streamlit as st
import pandas as pd
import plotly.express as px
from utils.constants import *
from utils.prep import *
from utils.viz import apply_chart_style


def render_conclusions(subset, age_df, intent_valid, frequency_valid, daily, duration):
    """Present key findings, data quality, and the final takeaway."""

    # Highlight generational differences in daily listening
    st.markdown("### Connecting the findings")

    if not age_df.empty and len(age_df) >= 2:
        hi = age_df.loc[age_df["Daily listeners (%)"].idxmax()]
        lo = age_df.loc[age_df["Daily listeners (%)"].idxmin()]

        st.markdown(
            f"**Key insight : Listening habits differ across generations.** "
            f"Daily listening reaches **{hi['Daily listeners (%)']:.1f}%** "
            f"among respondents aged **{hi['Age group']}**, compared with "
            f"**{lo['Daily listeners (%)']:.1f}%** among those aged "
            f"**{lo['Age group']}**. "
            f"This represents a difference of "
            f"**{hi['Daily listeners (%)'] - lo['Daily listeners (%)']:.1f} "
            f"percentage points**."
        )

    # Explain why comparing age groups matters
    st.write(
        "**Why it matters:** An overall listening percentage can hide "
        "important differences between audiences. Comparing generations "
        "helps us understand how music habits vary, without assuming "
        "that age itself causes these behaviors."
    )

    # Connect listening frequency with the broader story
    st.markdown("### Interpretation and limitations")

    if daily is not None:
        st.markdown(
            f"**Looking beyond the average:** "
            f"**{daily:.1f}%** of respondents with valid frequency answers "
            f"listen daily, based on survey-weighted results. "
            f"But this figure is only the starting point: listening "
            f"duration and subscription intention reveal other aspects "
            f"of music consumption."
        )

    # Introduce the data quality analysis
    st.markdown("### Data Quality  Can We Trust the Comparisons ?")

    st.write(
        "Before interpreting the results, it is important to understand "
        "which respondents answered each question. Some questions were "
        "only asked to specific groups, meaning that missing answers "
        "do not necessarily indicate data collection errors."
    )

    # Define the survey variables used in the quality report
    quality_columns = {
        "Age group (RAGE2)": "age_group",
        "Gender (SEXE)": "gender",
        "Listening frequency (Q3)": "frequency",
        "Listening duration (Q4)": "duration",
        "Subscription intention (Q51)": "subscription_intent",
        "Region (REG13)": "region",
    }

    # Calculate the number of recognized and missing answers
    quality_rows = []

    for label, mapped_col in quality_columns.items():
        valid_count = int(subset[mapped_col].notna().sum())

        quality_rows.append({
            "Survey field": label,
            "Recognized answers": valid_count,
            "Missing / unrecognized / not asked": len(subset) - valid_count,
            "Valid share (%)": 100 * valid_count / len(subset),
        })

    # Convert the quality results into a DataFrame
    quality_df = pd.DataFrame(quality_rows)

    # Create the response coverage chart
    fig_quality = px.bar(
        quality_df,
        x="Valid share (%)",
        y="Survey field",
        orientation="h",
        text="Valid share (%)",
        color_discrete_sequence=[PURPLE],
        hover_data=[
            "Recognized answers",
            "Missing / unrecognized / not asked"
        ],
        title="Answer coverage by survey question",
    )

    # Format the labels, axes, and chart layout
    fig_quality.update_traces(
        texttemplate="%{text:.1f}%",
        textposition="outside",
        cliponaxis=False
    )

    fig_quality.update_xaxes(
        range=[0, 108],
        title="Recognized responses (% of selected respondents)"
    )

    fig_quality.update_layout(
        yaxis=dict(autorange="reversed"),
        margin=dict(l=10, r=35, t=55, b=15),
        height=340
    )

    # Apply the dark dashboard theme
    fig_quality.update_layout(
        template="plotly_dark",
        paper_bgcolor=BG,
        plot_bgcolor=BG,
        font_color="#F0F6FC"
    )

    # Display the data quality chart
    st.plotly_chart(
        apply_chart_style(fig_quality),
        use_container_width=True
    )

    # Explain how response coverage should be interpreted
    st.caption(
        "Response coverage is calculated using unweighted counts. "
        "Missing responses may result from questionnaire routing, "
        "empty answers, or unrecognized categories. They should not "
        "automatically be treated as data quality failures."
    )

    # Display three data quality indicators
    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Valid survey weights",
        f"{int(subset['valid_weight'].sum()):,} / {len(subset):,}"
    )

    c2.metric(
        "Full-row duplicates",
        f"{int(subset.drop(columns=['valid_weight'], errors='ignore').duplicated().sum()):,}",
        help=(
            "Identical rows after mapping do not necessarily represent "
            "duplicate respondents, since no unique participant ID "
            "has been validated."
        )
    )

    c3.metric(
        "Valid Q51 responses",
        f"{len(intent_valid):,}",
        help=(
            "Unweighted number of valid subscription intention responses. "
            "This question may be skipped depending on survey routing."
        )
    )

    # Provide detailed quality checks and methodological explanations
    with st.expander(
        "Detailed quality checks and methodology",
        expanded=False
    ):

        # Display the complete response coverage table
        st.dataframe(
            quality_df,
            use_container_width=True,
            hide_index=True
        )

        # Report invalid weights and valid question responses
        st.write(
            f"Missing, nonpositive or nonnumeric weights: "
            f"**{int((~subset['valid_weight']).sum()):,}**"
        )

        st.write(
            f"Valid frequency responses with positive weights: "
            f"**{len(frequency_valid):,}**"
        )

        st.write(
            f"Valid subscription intention responses with positive weights: "
            f"**{len(intent_valid):,}**"
        )

        # Document the statistical method and limitations
        st.markdown("""
    **Method.** All analytical percentages use survey weights:
    `100 × sum(weights for selected answers) / sum(weights for valid answers)`.
    Each question uses its own valid response base, and age comparisons
    use valid responses within each age group. Respondent counts remain
    unweighted.

    **Missing responses.** Some respondents were not asked every question.
    For example, missing answers to Q4 or Q51 may result from the survey
    design rather than missing information. These cases are not treated
    as refusals.

    **Duplicates.** Identical rows are reported as a diagnostic only.
    Different people can provide identical answers, so matching rows
    are not automatically removed.

    **Study limitations.** The survey was conducted in late 2019 and
    published in 2020. It measures self-reported music listening habits
    across services, not actual Spotify activity. The findings describe
    associations rather than causal relationships. Estimates based on
    small subgroups should be interpreted cautiously, and confidence
    intervals are not calculated.
    """)

        # Allow users to export the data quality results
        st.download_button(
            "Download quality report (CSV)",
            data=quality_df.to_csv(index=False).encode("utf-8-sig"),
            file_name="behind_the_streams_data_quality.csv",
            mime="text/csv",
        )

    # Display the final storytelling conclusion
    st.markdown("## Final Takeaway : More Listening, More Paying ?")

    conclusion = []

    # Summarize the generational differences
    if len(age_df) >= 2:
        high = age_df.loc[age_df["Daily listeners (%)"].idxmax()]
        low = age_df.loc[age_df["Daily listeners (%)"].idxmin()]

        conclusion.append(
            f"Music is part of everyday life, but listening habits "
            f"are far from identical across generations: "
            f"**{high['Age group']}** respondents have a daily listening "
            f"rate of **{high['Daily listeners (%)']:.1f}%**, compared with "
            f"**{low['Daily listeners (%)']:.1f}%** for "
            f"**{low['Age group']}** respondents."
        )
    else:
        conclusion.append(
            "Music is part of everyday life, but listening habits "
            "cannot be described by a single pattern."
        )

    # Show how listening duration adds another perspective
    if duration is not None:
        conclusion.append(
            f"Frequency is only one part of musical engagement: "
            f"**{duration:.1f}%** of respondents with valid duration "
            f"answers report listening for at least two hours a day."
        )
    else:
        conclusion.append(
            "Listening frequency and listening duration reveal "
            "different aspects of musical engagement."
        )

    # Calculate the positive subscription intention rate
    positive = (
        weighted_share(
            intent_valid,
            "subscription_intent",
            {"Definitely", "Probably"}
        )
        if not intent_valid.empty
        else None
    )

    # Connect listening behavior with willingness to pay
    if positive is not None:
        conclusion.append(
            f"Yet listening frequently does not automatically translate "
            f"into a willingness to pay: **{positive:.1f}%** of respondents "
            f"with valid Q51 answers express a positive intention "
            f"to subscribe to a paid music service."
        )
    else:
        conclusion.append(
            "Listening frequently and being willing to pay are "
            "different behaviors, although subscription intention "
            "cannot be estimated for the current selection."
        )

    # End with the geographic perspective and survey limitations
    conclusion.append(
        "Regional comparisons add another perspective to the story, "
        "but these findings reflect self-reported habits from 2019 "
        "and should not be interpreted as causal effects or "
        "a description of today's streaming market."
    )

    # Display the four concluding statements
    st.markdown("  \n\n".join(conclusion))

    # Credit the original data source
    st.caption(
        "Data source: Hadopi / data.gouv.fr  "
        "Pratiques d’écoute de musique en ligne (2020)."
    )
