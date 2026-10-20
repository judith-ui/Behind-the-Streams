# Build the introduction to the Behind the Streams data storytelling project.
import streamlit as st
from utils.constants import BASE


def render_intro():
    """Present the project, research question, data source, and personal motivation."""

    # Display the dashboard title and project logo side by side.
    col_title, col_logo = st.columns(
        [5, 1],
        vertical_alignment="center",
        gap="large",
    )

    with col_title:
        st.title("🎧 BEHIND THE STREAMS")

    with col_logo:
        st.image(
            BASE / "assets" / "behind_the_streams_logo.png",
            width="stretch",
        )

    # Introduce the topic and acknowledge the origin and date of the survey.
    st.markdown("## Understanding Music Listening Habits in France")
    st.caption(
        "Source: [Hadopi, Online Music Listening Practices Survey (2020)]"
        "(https://www.data.gouv.fr/datasets/pratiques-decoute-de-musique-en-ligne-2020). "
        "Survey fieldwork: late 2019; publication: 2020. "
        "Results describe survey respondents, not today's streaming activity."
    )

    # State the guiding question that connects the listening and payment analyses.
    st.markdown("### The Question Behind the Data")
    st.markdown(
        "**How do listening habits vary across generations, and does frequent "
        "listening go hand in hand with an intention to pay for a music subscription ?**"
    )

    # Explain the analytical journey without suggesting the survey tracks Spotify users.
    st.write(
        "Using survey responses from 2,200 participants, this dashboard explores "
        "how often people listen, how much time they spend listening, and whether "
        "they would consider a paid music service. Interactive comparisons by age, "
        "gender, and region help reveal patterns that an overall average can hide."
    )

    # Share the motivation behind the project in a concise portfolio-friendly voice.
    st.markdown("### Why I Chose This Project")
    st.write(
        "Music has always been part of my daily life, from discovering artists "
        "to attending concerts and sharing recommendations with family. "
        "As someone interested in working with data in the music industry, "
        "I wanted to connect a personal passion with practical analytical skills. "
        "This project gave me the opportunity to turn public survey data into "
        "an interactive story, while learning to question what the numbers "
        "can and cannot tell us."
    )
