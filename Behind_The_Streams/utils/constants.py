"""Shared file paths, chart colors, survey labels, and map coordinates."""

from pathlib import Path

# Locate the project root from this file inside the utils/ directory.
BASE = Path(__file__).resolve().parents[1]

# Point to the cleaned dataset used by the Streamlit application.
DATA_PATH = BASE / "data" / "hadopi_clean.csv"

# Define the dashboard's dark theme and primary chart colors.
GREEN = "#177A39"
PURPLE = "#6F0C8D"
RED = "#9B071D"
LIGHT = "#F2F5F9"
MUTED = "#B4C1CE"
BG = "#0D1117"

# Personal visual inspiration: green evokes Spotify, purple Deezer, and red other music/video services. These are not official brand colors.
PALETTE = [GREEN, PURPLE, RED]

# Assign consistent colors to the six daily listening-duration categories.
# The warmer shades are a design choice, not a numerical scale of risk.
DURATION_COLORS = {
    "Under 1 hour": "#D3D928",
    "1–2 hours": "#DB9722",
    "2–3 hours": "#D7591E",
    "3–4 hours": "#B93836",
    "4–6 hours": "#FF0000",
    "Over 6 hours": "#E14963",
}

# Keep age-group colors consistent across charts such as the bubble plot.
AGE_COLORS = {
    "15–24": GREEN,
    "25–34": "#A78BFA",
    "35–49": "#EF476F",
    "50–64": "#8B5CF6",
    "65+": "#36B995",
}

# Translate the original age codes into reader-friendly categories.
AGE_LABELS = {
    "De15a24ans": "15–24",
    "De25a34ans1": "25–34",
    "De35a49ans1": "35–49",
    "De50a64ans1": "50–64",
    "De65aPlus": "65+",
}

# Translate the gender responses used as dashboard filters.
GENDER_LABELS = {
    "Un homme": "Men",
    "Une femme": "Women",
}

# Translate Q3 responses while preserving the original frequency order.
FREQ_LABELS = {
    "Plusieurs fois par jour": "Several times a day",
    "Tous les jours ou presque": "Every day or almost every day",
    "1 à 5 fois par semaine": "1–5 times a week",
    "1 à 3 fois par mois": "1–3 times a month",
    "Moins souvent": "Less often",
    "Jamais": "Never",
}

# Translate Q4 duration categories; the survey gives ranges, not exact hours.
DURATION_LABELS = {
    "Moins de 1 heure / jour": "Under 1 hour",
    "Entre 1 et 2 heures / jour": "1–2 hours",
    "Entre 2 et 3 heures / jour": "2–3 hours",
    "Entre 3 et 4 heures / jour": "3–4 hours",
    "Entre 4 et 6 heures / jour": "4–6 hours",
    "Plus de 6 heures /jour": "Over 6 hours",
}

# Match the survey's REG13 codes to modern, readable regional names.
# The main survey data has no observed Corsica category in this mapping.
REGION_LABELS = {
    "IleDeFrance1": "Île-de-France",
    "AuvergneRhoneAlpes": "Auvergne-Rhône-Alpes",
    "BourgogneFrancheComte": "Bourgogne-Franche-Comté",
    "Bretagne1": "Brittany",
    "CentreValDeLoire": "Centre-Val de Loire",
    "AlsaceChampagneArdenneLo": "Grand Est",
    "NordPasDeCalaisPicardie": "Hauts-de-France",
    "Normandie": "Normandy",
    "AquitaineLimousinPoitouC": "Nouvelle-Aquitaine",
    "LanguedicRoussillonMidiP": "Occitanie",
    "PaysDeLaLoire1": "Pays de la Loire",
    "ProvenceAlpesCoteDAzur": "Provence-Alpes-Côte d'Azur",
}

# Place each map bubble at a representative city within its region.
# These are approximate display positions, not official regional centroids.
REGION_COORDS = {
    "Île-de-France": {"lat": 48.8566, "lon": 2.3522},
    "Auvergne-Rhône-Alpes": {"lat": 45.7640, "lon": 4.8357},
    "Bourgogne-Franche-Comté": {"lat": 47.3220, "lon": 5.0415},
    "Brittany": {"lat": 48.1173, "lon": -1.6778},
    "Centre-Val de Loire": {"lat": 47.9029, "lon": 1.9093},
    "Grand Est": {"lat": 48.5734, "lon": 7.7521},
    "Hauts-de-France": {"lat": 50.6292, "lon": 3.0573},
    "Normandy": {"lat": 49.1829, "lon": -0.3707},
    "Nouvelle-Aquitaine": {"lat": 44.8378, "lon": -0.5792},
    "Occitanie": {"lat": 43.6047, "lon": 1.4442},
    "Pays de la Loire": {"lat": 47.2184, "lon": -1.5536},
    "Provence-Alpes-Côte d'Azur": {"lat": 43.2965, "lon": 5.3698},
}
