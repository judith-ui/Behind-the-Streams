import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.constants import *
from utils.prep import *
from utils.viz import apply_chart_style

# Compare listening habits between age groups.
def render_generations(subset):
    st.markdown("<div class='story-transition'> Next question → Do generations share the same listening habits ?</div>", unsafe_allow_html=True)
    st.markdown("### 2 : Listening every day: a generational comparison")
    st.caption("QUESTION: How different are daily listening habits across generations ?")
    st.write("Daily listening combines 'several times a day' and 'every day or almost every day'. Each age group's denominator includes its valid, weighted frequency responses.")
    # Calculate the weighted daily-listening rate for each age group.
    age_df = weighted_age_table(subset)
    if not age_df.empty:
        # Show daily listening rates in an age-group bar chart.
        fig2 = px.bar(age_df, x="Age group", y="Daily listeners (%)", text="Daily listeners (%)", hover_data=["Valid responses"], color_discrete_sequence=[GREEN], category_orders={"Age group": list(AGE_LABELS.values())})
        fig2.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
        fig2.update_yaxes(range=[0, 105], title="Daily listeners (weighted %)")
        fig2.update_layout(margin=dict(l=10, r=15, t=15, b=15))
        fig2.update_layout(template="plotly_dark", paper_bgcolor=BG, plot_bgcolor=BG, font_color="#F0F6FC")
        st.plotly_chart(apply_chart_style(fig2), use_container_width=True)
        # Identify the age groups with the strongest and weakest daily listening rates.
        if len(age_df) >= 2:
            oldest_or_low = age_df.loc[age_df["Daily listeners (%)"].idxmin()]
            youngest_or_high = age_df.loc[age_df["Daily listeners (%)"].idxmax()]
            st.markdown(
                f"**What the chart tells us.** **{youngest_or_high['Age group']}** has the highest "
                f"daily-listening rate in this selection (**{youngest_or_high['Daily listeners (%)']:.1f}%**), "
                f"versus **{oldest_or_low['Age group']}** (**{oldest_or_low['Daily listeners (%)']:.1f}%**). "
                f"The gap is **{youngest_or_high['Daily listeners (%)'] - oldest_or_low['Daily listeners (%)']:.1f} percentage points**. "
                "This is a group difference, not proof that age itself causes listening behavior."
            )
    else:
        st.info("No eligible age-group responses for the selected filters.")

    st.markdown("---")
    st.markdown("<div class='story-transition'>Look closer → Two people may both be non-daily listeners, but one listens weekly and the other never listens.</div>", unsafe_allow_html=True)
    st.markdown("### Deep dive : Which listening habits define each generation ?")
    st.caption("INTERACTIVE HEATMAP  :  Weighted percentage-point difference from the selected population's average")
    st.write(
        "The previous chart groups all daily listeners together. This heatmap goes deeper: "
        "it compares **all six listening-frequency categories** across age groups. "
        "Green means an answer is more common within that age group than in the currently selected population; "
        "pink means it is less common. Each cell represents a **percentage-point difference**, not a percentage of people."
    )

    # Keep respondents with a valid survey weight, age group, and frequency response.
    heat_base = subset.loc[
        subset["valid_weight"] & subset["age_group"].notna() & subset["frequency"].notna()
    ].copy()
    # Keep age groups in the same order across visualizations.
    heat_age_order = [a for a in AGE_LABELS.values() if a in heat_base["age_group"].unique()]
    heat_freq_order = list(FREQ_LABELS.values())
    if len(heat_age_order) >= 2 and not heat_base.empty:
        # Calculate the reference distribution for the selected population.
        overall = weighted_distribution(heat_base, "frequency", heat_freq_order).set_index("frequency")["share"]
        matrix_rows, details = [], []
        # Compare each sufficiently large age group with this benchmark.
        for age in heat_age_order:
            age_base = heat_base.loc[heat_base["age_group"] == age]
            if len(age_base) < 30:
                continue  # Avoid interpreting very small subgroup samples.
            group_dist = weighted_distribution(age_base, "frequency", heat_freq_order).set_index("frequency")["share"]
            for freq in heat_freq_order:
                share = float(group_dist.loc[freq])
                benchmark = float(overall.loc[freq])
                details.append({"Age group": age, "Listening frequency": freq,
                                "Difference (pp)": share - benchmark,
                                "Within age group (%)": share,
                                "Selected population (%)": benchmark,
                                "Valid age-group responses": len(age_base)})
        # Collect percentage-point differences in a DataFrame.
        heat_df = pd.DataFrame(details)
        if not heat_df.empty:
            # Reshape comparisons into the age-by-frequency heatmap matrix.
            heat_display = heat_df.pivot(index="Age group", columns="Listening frequency", values="Difference (pp)")
            heat_display = heat_display.reindex(columns=heat_freq_order)
            age_display = [a for a in heat_age_order if a in heat_display.index]
            heat_display = heat_display.reindex(age_display)
            # Keep the heatmap color scale balanced around zero.
            max_abs = max(5.0, float(heat_df["Difference (pp)"].abs().max()))
            # Visualize over- and under-represented listening frequencies.
            heat_fig = px.imshow(
                heat_display,
                color_continuous_scale=[[0, RED], [0.5, "#372B52"], [1, GREEN]],
                color_continuous_midpoint=0,
                range_color=[-max_abs, max_abs],
                text_auto=".1f",
                labels={"x": "Listening frequency", "y": "Age group", "color": "Difference (pp)"},
                aspect="auto",
            )
            # Add age-group percentages to interactive hover information.
            heat_fig.update_traces(
                customdata=heat_df.pivot(index="Age group", columns="Listening frequency", values="Within age group (%)").reindex(index=age_display, columns=heat_freq_order).to_numpy(),
                hovertemplate="Age group: %{y}<br>Listening frequency: %{x}<br>Difference: %{z:+.1f} pp<br>Within age group: %{customdata:.1f}%<extra></extra>",
                textfont={"size": 11},
            )
            heat_fig.update_layout(
                template="plotly_dark", paper_bgcolor=BG, plot_bgcolor=BG,
                font_color="#F0F6FC", height=390,
                margin=dict(l=10, r=15, t=45, b=90),
                xaxis=dict(tickangle=-24),
                coloraxis_colorbar=dict(title="Difference<br>(pp)"),
            )
            st.plotly_chart(apply_chart_style(heat_fig), use_container_width=True)
            # Highlight the strongest positive and negative differences in the current selection.
            peak_row = heat_df.loc[heat_df["Difference (pp)"].idxmax()]
            low_row = heat_df.loc[heat_df["Difference (pp)"].idxmin()]
            st.markdown(
                f"**What the heatmap reveals.** Relative to the selected respondents' average, "
                f"**{peak_row['Age group']}** is most overrepresented in **{peak_row['Listening frequency'].lower()}** "
                f"(**+{peak_row['Difference (pp)']:.1f} percentage points**). "
                f"The largest negative difference occurs for **{low_row['Age group']}** in "
                f"**{low_row['Listening frequency'].lower()}** "
                f"(**{low_row['Difference (pp)']:.1f} points**). "
                "Unlike the daily-listener bar chart, the heatmap also shows which less-frequent categories are comparatively common or rare. These differences are descriptive, not causal effects."
            )
            st.caption(
                "Benchmark: valid Q3 respondents within the current age and gender filters. "
                "Each cell compares the within-age weighted share with that benchmark. "
                "Age groups with fewer than 30 valid responses are excluded."
            )
        else:
            st.info("Not enough valid responses per age group to display the heatmap (minimum 30).")
    else:
        st.info("Select at least two age groups with valid frequency answers to compare their listening patterns.")
    st.markdown("---")

    # Return the age comparison for reuse in the conclusion.
    return age_df

# Measure listening duration separately from listening frequency.
def render_duration(subset, duration):
    st.markdown("<div class='story-transition'>A new dimension → Listening often is not necessarily the same as spending many hours listening.</div>", unsafe_allow_html=True)
    st.markdown("### 3 : Frequency is not the same as listening time")
    st.caption("QUESTION: Does listening longer tell the same story as listening often?")
    st.write("Q4 records listening-time categories, not exact hours. Percentages are calculated among valid Q4 respondents in each age group.")
    # Calculate the weighted duration distribution within each age group.
    rows = []
    for age in AGE_LABELS.values():
        group = subset.loc[(subset["age_group"] == age) & subset["valid_weight"] & subset["Q4"].isin(DURATION_LABELS.keys())]
        total = group["poids"].sum()
        if total > 0:
            for code, label in DURATION_LABELS.items():
                weight = group.loc[group["Q4"] == code, "poids"].sum()
                rows.append({"Age group": age, "Listening time": label, "Share (%)": 100 * weight / total, "Valid responses": len(group)})
    # Prepare the age-by-duration data for a stacked bar chart.
    duration_df = pd.DataFrame(rows)
    if not duration_df.empty:
        # Draw a stacked comparison of listening-time categories.
        fig3 = px.bar(duration_df, x="Age group", y="Share (%)", color="Listening time", color_discrete_map=DURATION_COLORS, barmode="stack", hover_data=["Valid responses"], category_orders={"Age group": list(AGE_LABELS.values()), "Listening time": list(DURATION_LABELS.values())}, labels={"Share (%)": "Weighted share within age group (%)"})
        fig3.update_layout(margin=dict(l=10, r=10, t=15, b=15), legend_title_text="Daily listening time")
        fig3.update_layout(template="plotly_dark", paper_bgcolor=BG, plot_bgcolor=BG, font_color="#F0F6FC")
        st.plotly_chart(apply_chart_style(fig3), use_container_width=True)
        if duration is not None:
            st.markdown(
                f"**What the chart tells us.** Among respondents with a valid listening-duration "
                f"answer, **{duration:.1f}%** report at least two hours a day (weighted). "
                "Each column shows the *composition* of listening time within one age group. "
                "This adds nuance to the previous chart: how often someone listens and how long "
                "they listen are different dimensions of engagement. Because Q4 has its own eligible-answer base, "
                "we should not treat its percentages as if they describe every respondent in Q3."
            )
    else:
        st.info("No valid daily-listening-time responses for these filters.")

    st.markdown("---")

# Investigate whether frequent listening aligns with stated subscription intention.
def render_payment(subset):
    st.markdown("<div class='story-transition'>From use to value → Now that we know how respondents listen, would they consider paying for access ?</div>", unsafe_allow_html=True)
    st.markdown("### 4 : Does interest in music translate into willingness to pay ?")
    st.write("**The next question in our story:** After exploring how often and how long people listen, we ask whether musical engagement goes hand in hand with a willingness to subscribe.")
    st.write("The survey asks about **future subscription intention (Q51)**. These answers are **not** a measure of actual free or paid membership. The question applies only to respondents who were asked it.")
    # Preserve the natural ordering of the four Q51 response options.
    INTENT_ORDER = ["Definitely", "Probably", "Probably not", "Definitely not"]
    # Select recognized Q51 answers with valid survey weights.
    intent_valid = subset.loc[subset["valid_weight"] & subset["subscription_intent"].isin(INTENT_ORDER)]
    if intent_valid.empty:
        st.info("Q51 has no eligible responses under the current filters. Try selecting all ages and genders. If it remains empty, inspect the raw Q51 response labels in the CSV.")
    else:
        # Calculate the weighted response distribution for Q51.
        intent_dist = weighted_distribution(intent_valid, "subscription_intent", INTENT_ORDER)
        # Show how positive and negative intentions are distributed.
        chart = px.bar(intent_dist, x="subscription_intent", y="share", text="share",
                       category_orders={"subscription_intent": INTENT_ORDER},
                       color="subscription_intent", color_discrete_map={
                           "Definitely": GREEN, "Probably": "#36B995",
                           "Probably not": "#FB7185", "Definitely not": "#CE4257"},
                       labels={"subscription_intent": "Subscription intention", "share": "Weighted share of valid Q51 responses (%)"})
        chart.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
        chart.update_layout(showlegend=False, margin=dict(l=10, r=10, t=20, b=10), yaxis_range=[0, 105])
        chart.update_layout(template="plotly_dark", paper_bgcolor=BG, plot_bgcolor=BG, font_color="#F0F6FC")
        st.plotly_chart(apply_chart_style(chart), use_container_width=True)
        # Combine definite and probable interest into one positive-intention estimate.
        willing = weighted_share(intent_valid, "subscription_intent", {"Definitely", "Probably"})
        st.info(f"**{willing:.1f}%** of eligible respondents with valid Q51 answers say they would definitely or probably consider subscribing. Base: **{len(intent_valid):,} unweighted valid Q51 answers**. This is stated intention, not observed purchasing behavior.")
        st.markdown(
            f"**What the chart tells us.** **{willing:.1f}%** of eligible respondents with valid answers "
            "say they would definitely or probably consider subscribing. This denominator "
            "only includes respondents who answered Q51; it must not be confused with the "
            "whole survey sample or the share of current paying subscribers."
        )
        # Calculate positive subscription intention separately for each age group.
        age_intent = []
        for age in AGE_LABELS.values():
            g = intent_valid.loc[intent_valid["age_group"] == age]
            if len(g) >= 30:
                value = weighted_share(g, "subscription_intent", {"Definitely", "Probably"})
                if value is not None:
                    age_intent.append({"Age group": age, "Likely to subscribe (%)": value, "Valid answers": len(g)})
        if age_intent:
            st.markdown("**Subscription intention by age** (groups with at least 30 valid responses)")
            # Visualize differences in subscription intention by age.
            fig4 = px.bar(pd.DataFrame(age_intent), x="Age group", y="Likely to subscribe (%)", text="Likely to subscribe (%)", hover_data=["Valid answers"], color_discrete_sequence=[GREEN])
            fig4.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
            fig4.update_yaxes(range=[0, 105])
            fig4.update_layout(template="plotly_dark", paper_bgcolor=BG, plot_bgcolor=BG, font_color="#F0F6FC")
            st.plotly_chart(apply_chart_style(fig4), use_container_width=True)
            age_intent_df = pd.DataFrame(age_intent)
            peak = age_intent_df.loc[age_intent_df["Likely to subscribe (%)"].idxmax()]
            st.markdown(
                f"**Why the comparison matters.** In the selected population, **{peak['Age group']}** "
                f"shows the strongest stated subscription interest (**{peak['Likely to subscribe (%)']:.1f}%**). "
                "This comparison helps us see whether frequent listening and subscription interest follow the same pattern. "
                "Interpret small groups cautiously."
            )

    st.markdown("---")
    st.markdown("<div class='story-transition'>Beyond a yes/no split → Positive and negative answers also differ in strength.</div>", unsafe_allow_html=True)
    st.markdown("### 5 : Subscription decisions: the full spectrum")
    st.caption("ADVANCED CHART : Diverging weighted response distribution by age")
    st.write(
        "A single willingness-to-pay percentage hides *how strongly* people agree or disagree. "
        "This chart separates **definitely / probably** from **probably not / definitely not**. "
        "The left side represents reluctance; the right side represents openness to subscribing."
    )

    # Each age group's four categories sum to 100% among valid Q51 responses.
    import plotly.graph_objects as go
    # Use consistent colors to distinguish reluctance and openness.
    DIVERGING_COLORS = {
        "Definitely not": "#CE4257", "Probably not": RED,
        "Probably": "#36B995", "Definitely": GREEN,
    }
    # Build four-category weighted distributions for eligible age groups.
    valid_age_intent = []
    for age in AGE_LABELS.values():
        age_valid = intent_valid.loc[intent_valid["age_group"] == age]
        if len(age_valid) >= 30 and age_valid["poids"].sum() > 0:
            denom = age_valid["poids"].sum()
            item = {"Age group": age, "Valid Q51 answers": len(age_valid)}
            for label in INTENT_ORDER:
                item[label] = 100.0 * age_valid.loc[age_valid["subscription_intent"] == label, "poids"].sum() / denom
            valid_age_intent.append(item)

    # Display a diverging Likert chart when enough valid answers exist.
    if valid_age_intent:
        divergent_df = pd.DataFrame(valid_age_intent)
        divergent_fig = go.Figure()
        # The sign encodes response direction; plotted values are percentages.
        # Place negative response categories to the left of zero.
        for response in ["Definitely not", "Probably not", "Probably", "Definitely"]:
            sign = -1 if response in {"Definitely not", "Probably not"} else 1
            plotted = divergent_df[response] * sign
            divergent_fig.add_bar(
                name=response,
                x=plotted,
                y=divergent_df["Age group"],
                orientation="h",
                marker_color=DIVERGING_COLORS[response],
                customdata=divergent_df[[response, "Valid Q51 answers"]].to_numpy(),
                hovertemplate=("Age: %{y}<br>Response: " + response +
                               "<br>Weighted share: %{customdata[0]:.1f}%" +
                               "<br>Valid responses: %{customdata[1]}<extra></extra>"),
            )
        divergent_fig.update_layout(
            barmode="relative", template="plotly_dark", paper_bgcolor=BG, plot_bgcolor=BG,
            font_color="#F0F6FC", height=440,
            xaxis=dict(title="Reluctant ← Weighted response share (%) → Willing",
                       range=[-105, 105], ticksuffix="%", tickvals=[-100, -50, 0, 50, 100],
                       ticktext=["100%", "50%", "0%", "50%", "100%"]),
            yaxis=dict(title="Age group", categoryorder="array",
                       categoryarray=list(reversed(list(AGE_LABELS.values())))),
            legend=dict(orientation="h", y=1.16, x=0),
            margin=dict(l=5, r=5, t=70, b=20),
        )
        # Mark the separation between negative and positive answers.
        divergent_fig.add_vline(x=0, line_width=1, line_color="#DDE5E7")
        st.plotly_chart(apply_chart_style(divergent_fig), use_container_width=True)
        strongest = divergent_df.loc[(divergent_df["Definitely"] + divergent_df["Probably"]).idxmax()]
        st.markdown(
            f"**What the chart tells us.** Among respondents eligible for Q51, "
            f"**{strongest['Age group']}** has the highest combined positive intention "
            f"(**{strongest['Definitely'] + strongest['Probably']:.1f}%**). "
            "The red side reveals how much resistance is firm versus tentative, while the green side "
            "shows how much openness is confident versus uncertain. This adds interpretation that a single "
            "positive-share bar cannot provide. These are declared intentions, not actual subscriptions."
        )
        st.caption("Each age bar sums to 100% across four valid Q51 categories; at least 30 unweighted eligible answers per displayed age group. Negative positions mean reluctance, not negative percentages.")
    else:
        st.info("The selected filters contain no age groups with at least 30 valid subscription-intention answers.")

    st.markdown("---")
    st.markdown("<div class='story-transition'>Bring the evidence together → Do the groups that listen most regularly also express the strongest willingness to subscribe ?</div>", unsafe_allow_html=True)
    st.markdown("### 6 : Listening versus paying: are they the same audience ?")
    st.caption("ADVANCED CHART : Bubble scatter plot on a COMMON respondent base")
    st.write(
        "To compare two behaviors fairly, we retain only respondents who answered **both** "
        "listening frequency (Q3) and subscription intention (Q51), with valid weights. "
        "Each bubble represents an age group. Bubble size reflects its **unweighted common-base sample size**."
    )
    # Compare Q3 and Q51 only among respondents with valid answers to both.
    common_base = subset.loc[
        subset["valid_weight"]
        & subset["Q3"].isin(FREQ_LABELS.keys())
        & subset["subscription_intent"].isin(INTENT_ORDER)
        & subset["age_group"].notna()
    ].copy()
    # Calculate daily-listening and subscription-intention rates on this common base.
    bubble_rows = []
    for age in AGE_LABELS.values():
        g = common_base.loc[common_base["age_group"] == age]
        if len(g) >= 30 and g["poids"].sum() > 0:
            daily_rate = weighted_share(g, "Q3", set(list(FREQ_LABELS.keys())[:2]))
            positive_rate = weighted_share(g, "subscription_intent", {"Definitely", "Probably"})
            if daily_rate is not None and positive_rate is not None:
                bubble_rows.append({
                    "Age group": age, "Daily listening (%)": daily_rate,
                    "Likely to subscribe (%)": positive_rate,
                    "Common-base respondents": len(g),
                })
    bubble_df = pd.DataFrame(bubble_rows)
    if not bubble_df.empty:
        # Explicit traces avoid Plotly Express generated hover/title metadata.
        # Create explicit bubbles so labels and tooltips remain predictable.
        bubble_fig = go.Figure()
        # Scale bubble sizes based on unweighted respondent counts.
        max_n = max(bubble_df["Common-base respondents"].max(), 1)
        for _, bubble in bubble_df.iterrows():
            bubble_size = 18 + 35 * (bubble["Common-base respondents"] / max_n) ** 0.5
            bubble_fig.add_trace(go.Scatter(
                x=[float(bubble["Daily listening (%)"])],
                y=[float(bubble["Likely to subscribe (%)"])],
                mode="markers+text",
                name=str(bubble["Age group"]),
                text=[str(bubble["Age group"])],
                textposition="top center",
                textfont=dict(color=LIGHT, size=12),
                marker=dict(
                    size=bubble_size,
                    color=AGE_COLORS[str(bubble["Age group"])],
                    opacity=0.83,
                    line=dict(color=LIGHT, width=1),
                ),
                customdata=[[int(bubble["Common-base respondents"])]],
                hovertemplate=(
                    "<b>%{fullData.name}</b><br>"
                    "Daily listeners: %{x:.1f}%<br>"
                    "Positive subscription intention: %{y:.1f}%<br>"
                    "Valid respondents: %{customdata[0]}<extra></extra>"
                ),
            ))
        # Show both weighted percentages on clearly labeled axes.
        bubble_fig.update_layout(
            title=None,
            height=500,
            xaxis=dict(title="Daily listeners on common base (weighted %)", range=[0, 100]),
            yaxis=dict(title="Positive subscription intention on common base (weighted %)", range=[0, 100]),
            legend=dict(title="Age group"),
            margin=dict(l=10, r=15, t=35, b=20),
        )
        st.plotly_chart(apply_chart_style(bubble_fig), use_container_width=True)
        # Compare the top listening group and the top subscription-intention group.
        if len(bubble_df) > 1:
            most_frequent = bubble_df.loc[bubble_df["Daily listening (%)"].idxmax()]
            most_willing = bubble_df.loc[bubble_df["Likely to subscribe (%)"].idxmax()]
            st.markdown(
                f"**What the chart tells us.** On the common Q3–Q51 response base, "
                f"**{most_frequent['Age group']}** has the highest daily-listening rate "
                f"(**{most_frequent['Daily listening (%)']:.1f}%**), while "
                f"**{most_willing['Age group']}** shows the highest positive subscription intention "
                f"(**{most_willing['Likely to subscribe (%)']:.1f}%**). "
                "Comparing the points is useful for spotting similarities or mismatches between listening and payment interest. "
                "However, five aggregated age points cannot establish individual-level relationships or causality."
            )
        else:
            st.info("Only one age group passes the sample-size threshold. A relationship between groups cannot be assessed.")
        st.caption("Important: This is descriptive, with at most five age-group points. No trend line or causal claim is warranted. Q51 was asked only to eligible respondents, so these rates can differ from the full Q3 sample.")
    else:
        st.info("No selected age group has at least 30 respondents with valid answers to both questions.")

    st.markdown("---")
    # Return valid Q51 data for the quality report and conclusions.
    return intent_valid

# Explore how weighted daily listening varies between French regions.
def render_geography(subset):
    st.markdown("<div class='story-transition'>Add place to the story → After age-based differences, we can also ask whether daily listening varies across French regions.</div>", unsafe_allow_html=True)
    st.markdown("### 7 : A geographic lens: where is daily listening strongest ?")
    st.caption("MAP VIEW : Regional comparison using survey-weighted daily-listening rates")
    st.write(
        "This map shifts from demographic groups to **French regions**. Each point represents one region's "
        "weighted share of daily listeners (Q3), while bubble size shows the **unweighted number of valid regional responses**. "
        "Because the survey is not designed as a regional census, the map should be read as an exploratory comparison."
    )
    # Select valid Q3 responses with region labels and positive weights.
    region_base = subset.loc[
        subset["valid_weight"] & subset["Q3"].isin(FREQ_LABELS.keys()) & subset["region"].notna()
    ].copy()
    # Compute regional estimates, excluding groups with fewer than 30 responses.
    region_rows = []
    for region_name in REGION_COORDS:
        rg = region_base.loc[region_base["region"] == region_name]
        if len(rg) >= 30 and rg["poids"].sum() > 0:
            daily_region = weighted_share(rg, "Q3", set(list(FREQ_LABELS.keys())[:2]))
            if daily_region is not None:
                region_rows.append({
                    "Region": region_name,
                    "Daily listeners (%)": daily_region,
                    "Valid responses": len(rg),
                    "lat": REGION_COORDS[region_name]["lat"],
                    "lon": REGION_COORDS[region_name]["lon"],
                })
    # Prepare coordinates, weighted rates, and respondent counts for the map.
    region_df = pd.DataFrame(region_rows)
    if not region_df.empty:
        # Display proportional bubbles at approximate regional positions.
        map_fig = px.scatter_geo(
            region_df,
            lat="lat",
            lon="lon",
            size="Valid responses",
            color="Daily listeners (%)",
            hover_name="Region",
            hover_data={"Daily listeners (%)": ":.1f", "Valid responses": True, "lat": False, "lon": False},
            size_max=35,
            color_continuous_scale=[[0.0, RED], [0.5, PURPLE], [1.0, GREEN]],
            labels={"Daily listeners (%)": "Daily listeners (weighted %)"},
            projection="natural earth",
        )
        map_fig.update_traces(marker=dict(line=dict(color="#F2F5F9", width=0.8), opacity=0.9))
        # Focus the geographic chart on mainland France.
        map_fig.update_geos(
            scope="europe",
            center=dict(lat=46.5, lon=2.5),
            lataxis_range=[41.0, 51.8],
            lonaxis_range=[-5.8, 9.8],
            showland=True,
            landcolor="#16202A",
            showocean=True,
            oceancolor="#0A0F14",
            showcountries=True,
            countrycolor="#5C6B7A",
            showsubunits=True,
            subunitcolor="#293241",
            resolution=50,
            bgcolor=BG,
        )
        map_fig.update_layout(
            template="plotly_dark",
            paper_bgcolor=BG,
            plot_bgcolor=BG,
            font_color="#F0F6FC",
            height=520,
            margin=dict(l=10, r=10, t=20, b=10),
            coloraxis_colorbar=dict(title="Daily listeners (%)"),
        )
        st.plotly_chart(apply_chart_style(map_fig), use_container_width=True)
        # Describe the regional extremes with the current filter selection.
        highest_region = region_df.loc[region_df["Daily listeners (%)"].idxmax()]
        lowest_region = region_df.loc[region_df["Daily listeners (%)"].idxmin()]
        st.markdown(
            f"**What the map tells us.** Among regions with at least 30 valid Q3 responses, **{highest_region['Region']}** "
            f"shows the highest weighted daily-listening rate (**{highest_region['Daily listeners (%)']:.1f}%**), while "
            f"**{lowest_region['Region']}** shows the lowest (**{lowest_region['Daily listeners (%)']:.1f}%**). "
            "This adds a geographic perspective to our story, but subgroup sizes and the survey design limit what we can infer about each region."
        )
        st.caption("Map note: region bubbles are positioned at approximate regional centers. Regions with fewer than 30 valid Q3 answers are hidden to avoid overinterpreting small bases.")
    else:
        st.info("No region reaches the minimum of 30 valid Q3 responses under the current filters. Try broader filters to display the regional map.")

