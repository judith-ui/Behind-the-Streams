"""Shared visual styling for the Behind the Streams dashboard."""

import streamlit as st

from utils.constants import BG, LIGHT


def apply_chart_style(fig, height=None):
    """Apply a consistent dark appearance to every Plotly chart."""

    # Use the same background and typography across all visualizations.
    # Chart titles are displayed separately in Streamlit.
    fig.update_layout(
        title=None,
        template="plotly_dark",
        paper_bgcolor=BG,
        plot_bgcolor=BG,
        font=dict(color=LIGHT, size=18),
        legend=dict(font=dict(color=LIGHT)),
        hoverlabel=dict(bgcolor="#202735", font_color=LIGHT),
    )

    # Allow individual charts to override their height when necessary.
    if height is not None:
        fig.update_layout(height=height)

    return fig


def apply_site_style():
    """Apply the dashboard's dark theme and subtle music-inspired accents."""

    # Inject CSS to personalize Streamlit without changing its data or charts.
    st.markdown(
        """
        <style>
        /* Keep the top of the dashboard clean and reduce unused space. */
        [data-testid="stHeader"],
        [data-testid="stToolbar"] {
            display: none;
        }

        .block-container {
            padding-top: 1rem;
        }

        /* Set the main application and sidebar colors. */
        .stApp {
            background: #0D1117;
            color: #F0F6FC;
        }

        [data-testid="stSidebar"] {
            background: #171E25;
        }

        /* Improve text contrast on the dark background. */
        h1, h2, h3 {
            letter-spacing: -0.025em;
            color: #F2F5F9 !important;
        }

        p, .stMarkdown, [data-testid="stCaptionContainer"] {
            color: #E0E8F1;
        }

        [data-testid="stCaptionContainer"] {
            color: #B4C1CE !important;
        }

        [data-testid="stSidebar"] label {
            color: #F2F5F9 !important;
        }

        /* Highlight narrative explanations and transitions between charts. */
        .story-note {
            background: #171E2A;
            border-left: 4px solid #A78BFA;
            padding: 14px 18px;
            border-radius: 8px;
            color: #EAF0F6;
            margin: 12px 0 22px 0;
        }

        .story-transition {
            color: #D0BAFF;
            font-weight: 600;
            padding: 6px 0 14px 0;
        }

        /* Make KPI cards visually distinct and easy to scan. */
        div[data-testid="stMetric"] {
            background: #17221E;
            padding: 18px;
            border: 1px solid #2D4035;
            border-radius: 14px;
        }

        div[data-testid="stMetricValue"] {
            color: #1ED760;
        }

        /* Keep Streamlit information and warning boxes consistent. */
        [data-testid="stAlert"] {
            border-radius: 12px;
        }

        /* Add decorative musical notes that do not block user interaction. */
        [data-testid="stAppViewContainer"]::before,
        [data-testid="stAppViewContainer"]::after {
            position: fixed;
            pointer-events: none;
            z-index: 0;
            color: rgba(167, 139, 250, 0.09);
            font-family: Georgia, serif;
            font-size: 90px;
            line-height: 1;
        }

        [data-testid="stAppViewContainer"]::before {
            content: "♫";
            right: 1.4%;
            top: 22%;
            transform: rotate(-15deg);
        }

        [data-testid="stAppViewContainer"]::after {
            content: "♪";
            right: 3%;
            bottom: 9%;
            transform: rotate(12deg);
        }

        /* Keep the application content above decorative background elements. */
        [data-testid="stMainBlockContainer"] {
            position: relative;
            z-index: 1;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
