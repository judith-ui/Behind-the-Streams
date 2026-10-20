# 🎧 Behind the Streams

Behind the streams is an interactive Streamlit dashboard exploring how people in France listen to music, how habits vary by age, and whether frequent listening relates to stated willingness to subscribe.

## The story

Music has always been an important part of my daily life, from discovering new artists and attending concerts to sharing recommendations with my family. As someone interested in pursuing a career in data analytics within the music industry, I wanted to connect this personal passion with practical data analysis skills.

This project gave me the opportunity to transform a public survey dataset into an interactive story, explore meaningful patterns in music consumption, and understand both the insights and limitations of survey data

**Do generations in France listen to music differently, and does daily listening necessarily imply willingness to pay  ?**

We will base our research on three questions from the survey, questions 3, 4, and 51 which are, respectively :

**How often does a person listen to music ?**

**How much time does a person spend listening to music each day ?**

**Would the person consider subscribing to a paid music service ?**

1. **Who listens ?** Establish the overall distribution of music-listening frequency.
2. **Generational differences :** Compare daily listening and the full frequency mix by age.
3. **How long ?** Contrast frequent listening with daily listening duration.
4. **Willingness to pay :** Explore stated future paid-subscription intention by age ; compare Q3 and Q51 on the same respondent base.
5. **Geographical perspective :** Explore weighted daily-listening rates by French region.
6. **Key insights and data quality  :** Interpret results and acknowledge the limits of self-reported historical survey data.

The survey contains 2,200 respondents and 262 original columns. For the unfiltered dataset, the weighted figures are approximately 48.8% listening daily 30.4% listening for at least two hours, and 22.8% expressing positive future subscription intention. These have different valid response bases and must not be treated as a joint population. Respondent counts are unweighted ; percentages are survey-weighted.

## Run the app

How to run the app. Open the project on vs code and in a new terminal :

```bash
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Open the localhost URL, and you have access to the streamlit.

## Code structure

```text
app.py                       # Entry point, sidebar, filtering and section orchestration
sections/
  intro.py                    # Research question and context + logo
  overview.py                 # KPIs and overall frequency
  deep_dives.py               # Age, duration, payment and regional chart sections
  conclusions.py              # Findings, validation and caveats
utils/
  constants.py                # Survey category labels, region coordinates and colors
  io.py                       # Cached CSV loading and feature mapping
  prep.py                     # Weighted aggregation helpers
  prepare_source.py           # Raw ODS to cleaned CSV + validation diagnostics
  viz.py                      # Shared Plotly theme and subtle musical styling
assets/
  behind_the_streams_logo.png # The logo of the app
data/                         # Original ODS files and hadopi_clean.csv
prepare_data.py               # Command-line preparation entrypoint
requirements.txt
```

### Why these functions ?

- **`load_data()` + `@st.cache_data`:** Load the CSV file once and map the responses from the original French surveys to clear, understandable labels this avoids repetitive work whenever filters are adjusted.
- **`weighted_share()` **and `weighted_distribution()`**:** Ensure that the survey weights (`poids`) are applied correctly; calculate percentages based exclusively on the relevant responses for the specific question being analyzed.
- **`weighted_age_table()`:** Maintain consistency in intergenerational comparisons and ensure the denominator remains valid for each age group.
- **`apply_chart_style()`:** Keep all Plotly charts visually coherent and legible.
- `prepare_data.py`**:** Preserve the original responses while standardizing missing values, validating weights, and identifying duplicates and coverage. Unprovided responses may be a result of the questionnaire process itself and are not necessarily errors.

## Source and limitations

**Dataset License :**  Open Licence (Etalab).

**Data Provider :** Arcom (formerly Hadopi).

**Source :** [www.data.gouv.fr/datasets/pratiques-decoute-de-musique-en-ligne-2020 ?resource_id=75d359e9-e950-482a-9559-cfa96e3e94a7](https://www.data.gouv.fr/datasets/pratiques-decoute-de-musique-en-ligne-2020?resource_id=75d359e9-e950-482a-9559-cfa96e3e94a7)

Under the Open License, the dataset is available for reuse. The information has been cleaned and modified for visualization and educational analysis purposes. The origin of the data as well as the publisher who published it are clearly indicated.

The results highlight the distinctive traits of the study participants and do not represent snapshot data. Question 51 deals with intentional programs and not actual subscriptions; Comparisons between statistically adjusted groups are descriptive and do not prove cause and effect. The symbols on the maps represent an approximate position within the core regions, while assessments relating to limited subgroups should be taken with caution.

**Application logo :** Created by me using an online logo design tool.

**Author :** Judith BLOCH 20251022
