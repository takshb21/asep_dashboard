import pandas as pd
import streamlit as st


import plotly.express as px
import plotly.graph_objects as go


# ─────────────────────────────────────────────
# DARK THEME DESIGN TOKENS
# ─────────────────────────────────────────────
BG_MAIN      = "#0D1117"   # page background
BG_CARD      = "#161B22"   # chart / card background
BG_SURFACE   = "#1C2333"   # slightly lighter surface
BORDER       = "#30363D"   # subtle border
ACCENT_BLUE  = "#58A6FF"   # bright blue for lines/accents
ACCENT_TEAL  = "#3BCEAC"   # teal for pass/positive
ACCENT_AMBER = "#F0B429"   # amber for secondary line
TEXT_PRIMARY = "#E6EDF3"   # main text
TEXT_MUTED   = "#FFFFFF"   # captions / axis labels
GRID_COLOR   = "#21262D"   # chart gridlines

# Gauge / traffic light
GREEN  = "#2EA043"         # satisfactory  0 – 1.8
YELLOW = "#F0B429"         # developing    1.8 – 2.0
RED    = "#F85149"         # poor          2.0 – 2.5

FONT_FAMILY = "Montserrat, sans-serif"

def merge_both_df(principle_preception_df, educator_detail_df):
    # Find columns in the second DF that already exist in the first (excluding 'TEA ID')
    cols_to_drop = educator_detail_df.columns.intersection(principle_preception_df.columns).drop('TEA ID')
    
    # Merge while excluding those columns from the second DF
    return principle_preception_df.merge(
        educator_detail_df.drop(columns=cols_to_drop), 
        on='TEA ID', 
        how='inner'
    )

# ─────────────────────────────────────────────
# BASE PLOTLY LAYOUT (dark)
# ─────────────────────────────────────────────
def base_layout(title: str, xtitle: str = "", ytitle: str = "") -> dict:
    return dict(
        title=dict(
            text=f"<b>{title}</b>",
            font=dict(family=FONT_FAMILY, size=17, color=TEXT_PRIMARY),
            x=0.03,
        ),
        xaxis=dict(
            title=dict(text=f"<b>{xtitle}</b>", font=dict(family=FONT_FAMILY, size=12, color=TEXT_MUTED)),
            tickfont=dict(family=FONT_FAMILY, size=11, color=TEXT_MUTED),
            gridcolor=GRID_COLOR,
            linecolor=BORDER,
            showgrid=True,
            zeroline=False,
        ),
        yaxis=dict(
            title=dict(text=f"<b>{ytitle}</b>", font=dict(family=FONT_FAMILY, size=12, color=TEXT_MUTED)),
            tickfont=dict(family=FONT_FAMILY, size=11, color=TEXT_MUTED),
            gridcolor=GRID_COLOR,
            linecolor=BORDER,
            showgrid=True,
            zeroline=False,
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor=BG_CARD,
        font=dict(family=FONT_FAMILY, color=TEXT_PRIMARY),
        margin=dict(l=60, r=30, t=70, b=60),
        hoverlabel=dict(
            bgcolor=BG_SURFACE,
            font_color=TEXT_PRIMARY,
            font_family=FONT_FAMILY,
            bordercolor=BORDER,
        ),
    )

# ─────────────────────────────────────────────
# BASE PLOTLY LAYOUT (dark)
# ─────────────────────────────────────────────
def base_layout(title: str, xtitle: str = "", ytitle: str = "") -> dict:
    return dict(
        title=dict(
            text=f"<b>{title}</b>",
            font=dict(family=FONT_FAMILY, size=17, color=TEXT_PRIMARY),
            x=0.03,
        ),
        xaxis=dict(
            title=dict(text=f"<b>{xtitle}</b>", font=dict(family=FONT_FAMILY, size=12, color=TEXT_MUTED)),
            tickfont=dict(family=FONT_FAMILY, size=11, color=TEXT_MUTED),
            gridcolor=GRID_COLOR,
            linecolor=BORDER,
            showgrid=True,
            zeroline=False,
        ),
        yaxis=dict(
            title=dict(text=f"<b>{ytitle}</b>", font=dict(family=FONT_FAMILY, size=12, color=TEXT_MUTED)),
            tickfont=dict(family=FONT_FAMILY, size=11, color=TEXT_MUTED),
            gridcolor=GRID_COLOR,
            linecolor=BORDER,
            showgrid=True,
            zeroline=False,
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor=BG_CARD,
        font=dict(family=FONT_FAMILY, color=TEXT_PRIMARY),
        margin=dict(l=60, r=30, t=70, b=60),
        hoverlabel=dict(
            bgcolor=BG_SURFACE,
            font_color=TEXT_PRIMARY,
            font_family=FONT_FAMILY,
            bordercolor=BORDER,
        ),
    )

def get_asep_consolidated_data(merged_df):
    """
        Consolidates data per teacher:
        - Keeps the EARLIEST (oldest) Employment Date.
    """
    merged_df['Employment Date'] = pd.to_datetime(merged_df['Employment Date'], dayfirst=True)

    # 2. Sort the dataframe by TEA ID and then by date (ascending)
    # This puts the most recent date at the bottom for each ID
    df1_sorted = merged_df.sort_values(by=['TEA ID', 'Employment Date'], ascending=False)

    # 3. Drop duplicates, keeping only the 'last' occurrence for each TEA ID
    df_latest = df1_sorted.drop_duplicates(subset='TEA ID', keep='last')

    # Optional: Reset the index for a clean dataframe
    df_latest = df_latest.reset_index(drop=True)

    return df_latest

# def filter_by_asep_six_year_window(df, report_year):
#     """
#     Checks if the LATEST certification is within the 6-year window.
#     """
#     cutoff_year = report_year - 6
    
#     # Extract year from the latest certification found in the previous step
#     df['cert_year'] = df['Certification Date'].dt.year
    
#     # Filter for the 6-year window
#     mask = (df['cert_year'] >= cutoff_year) & (df['cert_year'] <= report_year)
    
#     return df[mask].drop(columns=['cert_year'])



# def first_year_status(df, selected_year):
#     temp_list = []
#     for year in selected_year:
#         target_emp_date = pd.Timestamp(year=year - 1, month=9, day=1)

#         consider_year = df[df['Employment Date'] == target_emp_date]
#         # temp_df = df[df['Employment Date'] == year]
#         temp_list.append(consider_year)

#     final_ready_df = pd.concat(temp_list, ignore_index=True)

#     return final_ready_df

def first_year_status(df, selected_year):
    target_emp_date = pd.Timestamp(year=selected_year - 1, month=9, day=1)

    final_ready_df = df[df['Employment Date'] == target_emp_date].reset_index(drop=True)

    return final_ready_df

def verify_certificate(df):
    df = df[df['Certification Type'].isin(['Standard', 'Intern','Probationary', 'Enhanced Standared'])]
    return df

def missing_required_sections(df):
    target_columns = [
        'Planning', 
        'Instruction', 
        'Learning Environment', 
        'Professional Practices and Responsibilities'
    ]

    # Drop rows where any of these columns have NaN/None
    return df.dropna(subset=target_columns)

def remove_duplicates(df):
    """If a Teacher work in multiple campus in same time it will give score of highest one also use this after merging both the dataset"""
    df['Employment Year'] = df['Employment Date'].dt.year

    merged_cleaned = df.sort_values(
        by=['TEA ID', 'Employment Year', 'Overall'], 
        ascending=[True, True, False]
    ).drop_duplicates(
        subset=['TEA ID', 'Employment Year'], 
        keep='first'
    )
    return merged_cleaned

def chapter_4_chart(df, years_checked):
    MET_COLOR     = "#1B8720"   # green  – score >= 50
    MISSED_COLOR  = "#FF1708"   # red    – score <  50
    # TARGET        = 50

    # ── Chapter 5–style binary threshold ────────────────────────────────
    TARGET_C4 = 2.0
    MET_COLOR_C4    = MET_COLOR    # reuse the same green used in Ch.5
    MISSED_COLOR_C4 = MISSED_COLOR # reuse the same red used in Ch.5

    

    def _c4_color(v):
        return MET_COLOR_C4 if v >= TARGET_C4 else MISSED_COLOR_C4

    def _c4_bar_colors(series):
        return [_c4_color(v) for v in series]

    # ══════════════════════════════════════════
    # CHART 1 — Radar Chart (dark theme, line/fill green/red based on avg)
    # ══════════════════════════════════════════
    st.markdown("---")
    st.subheader("📊 Indicator 2: Principal Appraisal")
    st.caption(
        "🟢 Green = Overall average ≥ 2.0 (Satisfactory)  |  🔴 Red = Below 2.0. "
        "Radar chart comparing average scores across six principal appraisal domains."
    )

    categories = [
        "Planning",
        "Instruction",
        "Learning Environment",
        "Professional Practices and Responsibilities",
        "Students with Disabilities",
        "English Language Learners",
    ]
    values = [df[c].mean() for c in categories]
    radar_avg = sum(values) / len(values)
    radar_color = _c4_color(radar_avg)
    radar_fill = "rgba(46,204,113,0.15)" if radar_avg >= TARGET_C4 else "rgba(231,76,60,0.15)"

    fig_radar = go.Figure()
    fig_radar.add_trace(
        go.Scatterpolar(
            r=values + [values[0]],
            theta=categories + [categories[0]],
            fill="toself",
            name="Appraisal Score",
            line=dict(color=radar_color, width=2.5),
            fillcolor=radar_fill,
            hovertemplate="<b>%{theta}</b><br>Score: %{r:.2f}<extra></extra>",
        )
    )
    fig_radar.update_layout(
        polar=dict(
            bgcolor="black",
            radialaxis=dict(
                visible=True,
                range=[0, max(values) + 0.4],
                tickfont=dict(size=10, family=FONT_FAMILY, color=TEXT_MUTED),
                gridcolor=GRID_COLOR,
                linecolor=BORDER,
            ),
            angularaxis=dict(
                tickfont=dict(size=11, family=FONT_FAMILY, color=TEXT_PRIMARY),
                linecolor=BORDER,
            ),
        ),
        showlegend=False,
        title=dict(
            text="<b>Principal Appraisal — Domain Performance Overview</b>",
            font=dict(family=FONT_FAMILY, size=17, color=TEXT_PRIMARY),
            x=0.03,
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family=FONT_FAMILY, color=TEXT_PRIMARY),
        margin=dict(t=80, b=40),
        height=480,
    )
    st.plotly_chart(fig_radar, use_container_width=True)

    # ══════════════════════════════════════════
    # CHART 2 — Bar Chart (UNCHANGED — kept as original traffic-light style)
    # ══════════════════════════════════════════
    st.markdown("---")
    st.subheader("📈 Average Overall Score by Certification Grade Level")
    st.caption(
        "Bars are color-coded by performance band: "
        "🔴 Needs Improvement (< 1.8)  🟡 Developing (1.8 – 2.0) 🟢 Satisfactory  (≥ 2.0). "
        "Dashed lines mark the band boundaries."
    )

    grade_df = (
        df.groupby("Certification Area Grade Level")["Overall"]
        .mean()
        .reset_index()
        .sort_values("Overall")
    )
    grade_df.columns = ["Grade Level", "Average Score"]

    def score_color(v):
        if v >= 2.0:
            return GREEN
        elif v >= 1.8:
            return YELLOW
        else:
            return RED

    bar_colors = [score_color(v) for v in grade_df["Average Score"]]

    fig_bar = go.Figure(
        go.Bar(
            x=grade_df["Grade Level"],
            y=grade_df["Average Score"],
            marker=dict(
                color=bar_colors,
                line=dict(color=BG_MAIN, width=1.5),
                opacity=0.9,
            ),
            text=grade_df["Average Score"].round(2),
            textposition="outside",
            textfont=dict(family=FONT_FAMILY, size=11, color=TEXT_PRIMARY),
            hovertemplate="<b>%{x}</b><br>Avg Score: %{y:.2f}<extra></extra>",
        )
    )
    layout_bar = base_layout(
        "Average Appraisal Score by Certification Grade Level",
        xtitle="Certification Grade Level",
        ytitle="Average Overall Score",
    )
    layout_bar["yaxis"]["range"] = [0, grade_df["Average Score"].max() + 0.45]

    fig_bar.add_hline(
        y=1.8,
        line=dict(color=RED, dash="dash", width=1.8),
        annotation_text="",
        annotation_position="top left",
        annotation_font=dict(family=FONT_FAMILY, size=10, color=RED),
    )
    fig_bar.add_hline(
        y=2.0,
        line=dict(color=YELLOW, dash="dash", width=1.8),
        annotation_text="",
        annotation_position="top right",
        annotation_font=dict(family=FONT_FAMILY, size=10, color=YELLOW),
    )
    fig_bar.update_layout(**layout_bar, height=430)
    st.plotly_chart(fig_bar, use_container_width=True)

    # ══════════════════════════════════════════
    # CHART 3 — Gauge (Ch.5 binary theme) + Donut (ORIGINAL dark theme, UNCHANGED)
    # ══════════════════════════════════════════
    st.markdown("---")
    overall_avg = round(df["Overall"].mean(), 2)
    col1, col2 = st.columns(2)

    with col1:
        # st.subheader("🎯 Overall Average Score")
        # st.caption(
        #     "🟢 Green = Met Standard (≥ 2.0)  |  🔴 Red = Did Not Meet (< 2.0). "
        #     "Needle shows the overall cohort average."
        # )

        # gauge_color = _c4_color(overall_avg)

        # fig_gauge = go.Figure(
        #     go.Indicator(
        #         mode="gauge+number",
        #         value=overall_avg,
        #         number=dict(
        #             font=dict(size=52, color="white"),
        #         ),
        #         domain={"x": [0, 1], "y": [0, 1]},
        #         gauge={
        #             "axis": {"range": [0, 2.5], "tickwidth": 1, "tickcolor": "darkblue"},
        #             "bar": {"color": gauge_color},
        #             "bgcolor": "white",
        #             "borderwidth": 2,
        #             "bordercolor": "gray",
        #             "steps": [
        #                 {"range": [0, 2.0],   "color": "#000000"},
        #                 {"range": [2.0, 2.5], "color": "#000000"},
        #             ],
        #         },
        #     )
        # )
        # fig_gauge.update_layout(height=300, margin=dict(t=30, b=10))
        # st.plotly_chart(fig_gauge, use_container_width=True)

        survey_data = chapter_4_survey_summary(df, years_checked)
        total_valid_surveys, surveys_meeting_standard = survey_data['total_valid_surveys'], survey_data['surveys_meeting_standard']
        if total_valid_surveys > 0:
            pct_meeting_standard = round((surveys_meeting_standard / total_valid_surveys) * 100, 2)
        else:
            pct_meeting_standard = 0

        st.caption(
            "🟢 Green = 70% or more surveys meeting standard (Overall ≥ 2.0)  |  "
            "🔴 Red = Below 70%. "
            f"({surveys_meeting_standard} of {total_valid_surveys} surveys met standard)"
        )

        gauge_color = GREEN if pct_meeting_standard >= 70 else RED

        fig_gauge = go.Figure(
            go.Indicator(
                mode="gauge+number",
                value=pct_meeting_standard,
                number=dict(
                    font=dict(size=52, color="white"),
                    suffix="%",
                ),
                domain={"x": [0, 1], "y": [0, 1]},
                gauge={
                    "axis": {"range": [0, 100], "tickwidth": 1, "tickcolor": "darkblue"},
                    "bar": {"color": gauge_color},
                    "bgcolor": "white",
                    "borderwidth": 2,
                    "bordercolor": "gray",
                    "steps": [
                        {"range": [0, 70],   "color": "#000000"},
                        {"range": [70, 100], "color": "#000000"},
                    ],
                },
            )
        )
        fig_gauge.update_layout(height=300, margin=dict(t=30, b=10))
        st.plotly_chart(fig_gauge, use_container_width=True)

    with col2:
        st.subheader("🥧 Score Distribution by Race / Ethnicity")
        st.caption(
            "Donut chart showing average principal appraisal scores proportionally "
            "by demographic group. Hover over each slice for exact values. "
            "The center displays the overall cohort average."
        )

        ethnicity_df = (
            df.groupby("Race/Ethnicity")["Overall"].mean().round(2).reset_index()
        )
        # Dark-friendly vivid palette
        palette = [
            ACCENT_BLUE, ACCENT_TEAL, "#F63228", ACCENT_AMBER,
            "#BC8CFF", "#FF7B72", "#56D364",
        ]

        fig_donut = go.Figure(
            go.Pie(
                labels=ethnicity_df["Race/Ethnicity"],
                values=ethnicity_df["Overall"],
                hole=0.48,
                marker=dict(
                    colors=palette[: len(ethnicity_df)],
                    line=dict(color=BG_MAIN, width=2.5),
                ),
                textinfo="label+percent",
                textfont=dict(family=FONT_FAMILY, size=11, color=TEXT_PRIMARY),
                hovertemplate=(
                    "<b>%{label}</b><br>Avg Score: %{value:.2f}<br>Share: %{percent}<extra></extra>"
                ),
            )
        )
        fig_donut.update_layout(
            title=dict(
                text="<b>Avg Appraisal Score by Race / Ethnicity</b>",
                font=dict(family=FONT_FAMILY, size=15, color=TEXT_PRIMARY),
                x=0.03,
            ),
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(family=FONT_FAMILY, color=TEXT_PRIMARY),
            legend=dict(
                orientation="v",
                font=dict(family=FONT_FAMILY, size=10, color=TEXT_MUTED),
                bgcolor="rgba(0,0,0,0)",
            ),
            annotations=[
                dict(
                    text=f"<b>{overall_avg}</b><br><span style='font-size:11px'>Overall</span>",
                    x=0.5, y=0.5,
                    font=dict(size=18, family=FONT_FAMILY, color=TEXT_PRIMARY),
                    showarrow=False,
                )
            ],
            height=400,
            margin=dict(t=60, b=20, l=10, r=10),
        )
        st.plotly_chart(fig_donut, use_container_width=True)


# ─────────────────────────────────────────────
# PRINCIPAL PERCEPTIONS TAB
# ─────────────────────────────────────────────
@st.cache_data
def prepare_chapter_4(principal_df, educator_df):
    merged = merge_both_df(principal_df, educator_df)
    merged = get_asep_consolidated_data(merged)
    merged = verify_certificate(merged)
    merged = missing_required_sections(merged)
    merged = remove_duplicates(merged)
    return merged


def chapter_4_group_aggregration(filtered_copy_df, current_year):
    aggregated_dfs = []
    total_records = 0  # now represents UNIQUE TEA ID count, not row count
    years_checked = 0
    combined_df = pd.DataFrame(columns=filtered_copy_df.columns)

    # Keep aggregating while unique TEA ID group size is <= 10, up to 3 years back
    while total_records <= 10 and years_checked < 3:
        year_df = first_year_status(filtered_copy_df, current_year)

        if not year_df.empty:
            aggregated_dfs.append(year_df)
            combined_df = pd.concat(aggregated_dfs, ignore_index=True)
            total_records = combined_df['TEA ID'].nunique()  

        current_year -= 1
        years_checked += 1

    if aggregated_dfs:
        filtered_copy_df = pd.concat(aggregated_dfs, ignore_index=True)
    else:
        filtered_copy_df = pd.DataFrame(columns=filtered_copy_df.columns)

    return filtered_copy_df, years_checked, total_records

def chapter_4_survey_summary(df, years_checked):
    total_valid_surveys = df['TEA ID'].nunique()
    surveys_meeting_standard = df[df['Overall'] >= 2.00]['TEA ID'].nunique()
    # No data / small group exception
    if total_valid_surveys == 0 or total_valid_surveys < 10:
        return {
            "total_valid_surveys": total_valid_surveys,
            "surveys_meeting_standard": surveys_meeting_standard,
            "no_of_year_taken": years_checked,
            "overall_score": None,
            "value": "<blank>"
        }

    # Calculate percentage meeting standard
    overall_score = round(
        (surveys_meeting_standard / total_valid_surveys) * 100,
        2
    )

    # Determine whether the current data meets the standard
    # Replace 50 with the actual ASEP performance threshold if different
    meets_standard = overall_score >= 50

    if meets_standard:
        value = 1

    elif years_checked >= 3:
        # Current year failed and data exists for the two most recent
        # prior actionable years
        value = -1

    else:
        # Current year failed, but historical data is not sufficient
        # to determine two prior years
        value = 0

    return {
        "total_valid_surveys": total_valid_surveys,
        "surveys_meeting_standard": surveys_meeting_standard,
        "no_of_year_taken": years_checked,
        "overall_score": overall_score,
        "value": value
    }


def principal_perceptions(principal_perception_df, educator_details_df):
    # 1. Handle the initial session state before preprocessing
    merged = prepare_chapter_4(principal_perception_df, educator_details_df)

    available_cohort_options = sorted(merged["Admission Cohort"].unique().astype(int).tolist())
    available_employment_options = sorted(merged['Employment Date'].dt.year.astype(int).unique().tolist())

    if "chapter_4_cohort_filter" not in st.session_state:
        st.session_state.chapter_4_cohort_filter = available_cohort_options  # Or [2019, 2020, 2021] depending on your default target
        
    if "chapter_4_gender_filter" not in st.session_state:
        st.session_state.chapter_4_gender_filter = "All"

    if "chapter_4_employment_date" not in st.session_state:
        st.session_state.chapter_4_employment_date = available_employment_options


    # # ── Filters ──
    st.subheader("🔍 Filter Options")
    filter_col1, filter_col2, filter_col3 = st.columns(3)
    
    with filter_col1:
        gender_selected = st.selectbox(
            "Gender",
            options=["All"] + sorted(merged["Gender"].unique().tolist()),
            key="chapter_4_gender_select",
        )
        st.session_state.chapter_4_gender_filter = gender_selected

    with filter_col2:
        employment_date_selected = st.selectbox(
            "Employment Date",
            options=available_employment_options,
            # default=st.session_state.chapter_4_employment_date,
            key="chapter_4_emp_date_select"
        )

        if employment_date_selected != st.session_state.chapter_4_employment_date:
            st.session_state.chapter_4_employment_date = employment_date_selected
            

    filtered_copy_df = merged.copy()
    if gender_selected != "All":
        filtered_copy_df = filtered_copy_df[filtered_copy_df["Gender"] == gender_selected]


    filtered_copy_df, years_checked, total_records = chapter_4_group_aggregration(filtered_copy_df, employment_date_selected)
    # if years_checked > 1 and total_records > 0:
    st.info(
        f"ℹ️ **Small Group Aggregation Applied:** Initial cohort was under 10. "
        f"Aggregated data across {years_checked} consecutive years. "
        f"Total evaluation sample size: **{total_records}**."
    )

    

    if total_records != 0:
        chapter_4_chart(filtered_copy_df, years_checked)
    else:
        st.info('Select Other Year No Record Found')

    return merged, years_checked