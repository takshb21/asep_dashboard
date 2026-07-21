import pandas as pd 
import numpy as np 
import plotly.graph_objects as go
import streamlit as st
import plotly.express as px

def process_chapter_6_records(df):
    df = df.copy()
    
    # 1. Keep only CLIN and INT
    df = df[df['Assignment Type'].isin(['CLIN', 'INT'])]
    
    # Convert dates to datetime
    df['Assignment Begin Date'] = pd.to_datetime(df['Assignment Begin Date'])
    df['Assignment End Date'] = pd.to_datetime(df['Assignment End Date'])
    
    # 2. Determine the ASEP Reporting Year based on End Date
    df['filter_year'] = df['Assignment End Date'].apply(
        lambda x: f"{x.year}-{x.year + 1}" if x.month >= 9 else f"{x.year - 1}-{x.year}"
    )
    
    # 3. Apply the 2025-2026 "Start Date" rule for CLIN clinical experience
    # If the reporting year is 2025-2026 (or later), the assignment MUST have started on or after 9/1/2024 mentioned in ASEP p.23 (ASEP Accountability Indicator 4a last sentence)
    cutoff_date = pd.to_datetime('2024-09-01')
    
    # Filter out records that violate the rule
    invalid_old_records = (df['filter_year'] == '2025-2026') & (df['Assignment Begin Date'] < cutoff_date) & (df['Assignment Type'] == 'CLIN')
    df = df[~invalid_old_records]
    
    return df


def indicator_4a_calculate(df):
    # Create a copy so you don't accidentally modify the original df in unexpected ways
    df = df.copy()
    
    # 1. Check if it's already a timedelta. If it's still a string ('O'), convert it.
    if df['Duration Hours'].dtype == 'O':
        df['Duration Hours'] = pd.to_timedelta(df['Duration Hours'] + ':00')
    
    # 2. Filter using the correct 'hh:mm:ss' format
    df = df[df['Duration Hours'] >= pd.to_timedelta('00:45:00')]
    
    # df['Duration Hours'] = df['Duration Hours'].astype(str).str.split().str[-1]
    
    # output = df.groupby(['Candidate TEA ID'])['Assignment Type'].count().reset_index()
    summary_df =  df.groupby(['Candidate TEA ID', 'Assignment Type']).size().reset_index(name='Observation Count')

    conditions = [
        (summary_df['Assignment Type'] == 'INT') & (summary_df['Observation Count'] >= 5),
        (summary_df['Assignment Type'] == 'CLIN') & (summary_df['Observation Count'] >= 4)
    ]

    # Step 3: Assign 'Y' if they meet the condition, otherwise 'N'
    summary_df['Meet Minimum Requirement?'] = np.select(conditions, ['Y', 'Y'], default='N')

    total_candidates = len(summary_df) 
    
    # Count how many of those rows have a 'Y'
    met_requirement = (summary_df['Meet Minimum Requirement?'] == 'Y').sum()

    # Return the dataframe alongside the two numbers
    return summary_df, met_requirement, total_candidates


def _parse_duration_to_hours(duration_str):
    """Converts 'H:MM' or 'HH:MM' string to decimal hours. Returns None if unparseable."""
    if pd.isna(duration_str):
        return None
    try:
        s = str(duration_str).strip()
        parts = s.split(":")
        if len(parts) == 2:
            hours, minutes = int(parts[0]), int(parts[1])
            return hours + minutes / 60
        return float(s)  # fallback if already numeric
    except (ValueError, TypeError):
        return None

def group_size_calculate(df, id_col="Candidate TEA ID"):
    return df[id_col].nunique()


def shift_academic_year(academic_year_str, steps_back):
    """
    Steps an academic-year string like '2025-2026' backward by `steps_back` years.
    shift_academic_year('2025-2026', 1) -> '2024-2025'
    shift_academic_year('2025-2026', 2) -> '2023-2024'
    """
    start_year = int(academic_year_str.split('-')[0])
    new_start = start_year - steps_back
    return f"{new_start}-{new_start + 1}"

def indicator_4b_small_group_aggregation(df, year_filter):

    combined_df = pd.DataFrame(columns=df.columns)
    year_taken = []

    for i in range(3):
        target_year = shift_academic_year(year_filter, i)
        year_data = df[df["filter_year"] == target_year]
        combined_df = pd.concat([combined_df, year_data])
        year_taken.append(target_year)
        if group_size_calculate(combined_df) >= 10:
            break

    return combined_df, year_taken


def indicator_4b_calculate(df, id_col="Candidate TEA ID", points_col="Total Points", threshold=22):
    working_df = df.dropna(subset=[points_col])

    candidate_avg_points = working_df.groupby(id_col)[points_col].mean().reset_index()
    candidate_avg_points = candidate_avg_points.rename(columns={points_col: "Average Total Points"})
    candidate_avg_points["Within Acceptable Values"] = candidate_avg_points["Average Total Points"] <= threshold

    total_surveys = candidate_avg_points.shape[0]
    within_acceptable_values = int(candidate_avg_points["Within Acceptable Values"].sum())

    result_dict = {
        "Number of candidates' scores within acceptable values": within_acceptable_values,
        "Total number of survey responses": total_surveys,
    }

    return result_dict, candidate_avg_points

def field_supervision(observation_data):
    df = process_chapter_6_records(observation_data)

    available_year_options = df['filter_year'].unique().tolist()

    
    if "chapter_6_year_filter" not in st.session_state:
        st.session_state.chapter_6_year_filter = available_year_options

    if "chapter_6_experience_model_setting" not in st.session_state:
        st.session_state.chapter_6_experience_model_setting = "All"

    # ── Filters ──
    st.header("Indicator 4a")
    st.subheader("🔍 Filter Options")
    filter_col1, filter_col2, filter_col3 = st.columns(3)

    with filter_col1:
        year_selected = st.selectbox(
            "Year Filter",
            options=available_year_options,
            key="chapter_6_year_filter_select",
        )
        st.session_state.chapter_6_year_filter = year_selected

    with filter_col2:
        experience_model_selected = st.selectbox(
            "Experience Model",
            options=["All"] + sorted(df["Experience Model"].dropna().unique().tolist()),
            key="chapter_4_experience_model_list",
        )
        st.session_state.chapter_6_experience_model_setting = experience_model_selected

    filtered_copy_df = df.copy()
    if year_selected:
        filtered_copy_df = filtered_copy_df[filtered_copy_df["filter_year"] == st.session_state.chapter_6_year_filter]
    if experience_model_selected != "All":
        filtered_copy_df = filtered_copy_df[filtered_copy_df["Experience Model"] == experience_model_selected]


    result_df, num_met_req, num_total_exp = indicator_4a_calculate(filtered_copy_df)
    
    plot_indicator_4a(filtered_copy_df, num_met_req, num_total_exp)

    # Indicator 4b
    # Check the individual level data
    # Chekc what toal points are taken as there are 3 people also so which point to consider
    st.header("Indicator 4b")

    st.write(filtered_copy_df['Candidate TEA ID'].nunique())

    exp_filtered_df = df.copy()
    if experience_model_selected != "All":
        exp_filtered_df = exp_filtered_df[exp_filtered_df["Experience Model"] == experience_model_selected]

    agg_df, year_taken = indicator_4b_small_group_aggregation(exp_filtered_df, st.session_state.chapter_6_year_filter)

    if len(year_taken) > 1:
        st.caption(f"⚠️ Small sample size — aggregated years: {', '.join(year_taken)} (n = {group_size_calculate(agg_df)})")

    indicator_4b_results, candidate_level_df = indicator_4b_calculate(agg_df)

    # st.write(indicator_4b_results)
    # st.write(candidate_level_df)
    # st.write(year_taken)

    plot_indicator_4b(indicator_4b_results, candidate_level_df)

    return df

# def plot_indicator_4a(result_df: pd.DataFrame, num_met_req: int, num_total_exp: int):
#     """
#     Renders 3 charts summarizing Indicator 4A (ASEP Chapter 6):
#       1. Donut chart: overall Met vs Not Met requirement
#       2. Gauge chart: % compliance
#       3. Bar chart: average visit duration (hours) by Assignment Type
#     """

#     not_met = num_total_exp - num_met_req
#     pct_met = round((num_met_req / num_total_exp) * 100, 1) if num_total_exp else 0

#     # st.subheader("Indicator 4A — Overview")

#     col1, col2, col3 = st.columns(3)

#     # ---------- Chart 1: Donut chart (Met vs Not Met) ----------
#     with col1:
#         donut_fig = go.Figure(
#             data=[go.Pie(
#                 labels=["Met Requirement", "Not Met"],
#                 values=[num_met_req, not_met],
#                 hole=0.55,
#                 marker=dict(colors=["#2E7D32", "#C62828"]),
#                 textinfo="label+value+percent",
#             )]
#         )
#         donut_fig.update_layout(
#             title="Met vs Not Met",
#             showlegend=True,
#             margin=dict(t=50, b=0, l=0, r=0),
#         )
#         st.plotly_chart(donut_fig, use_container_width=True)

#     # ---------- Chart 2: Gauge chart (% compliance) ----------
#     with col2:
#         gauge_fig = go.Figure(
#             go.Indicator(
#                 mode="gauge+number",
#                 value=pct_met,
#                 number={"suffix": "%"},
#                 title={"text": "Compliance Rate"},
#                 gauge={
#                     "axis": {"range": [0, 100]},
#                     "bar": {"color": "#1565C0"},
#                     "steps": [
#                         {"range": [0, 50], "color": "#FFCDD2"},
#                         {"range": [50, 80], "color": "#FFF9C4"},
#                         {"range": [80, 100], "color": "#C8E6C9"},
#                     ],
#                 },
#             )
#         )
#         gauge_fig.update_layout(margin=dict(t=50, b=0, l=0, r=0))
#         st.plotly_chart(gauge_fig, use_container_width=True)

#     # ---------- Chart 3: Average Duration by Assignment Type ----------
#     with col3:
#         if "Assignment Type" in result_df.columns and "Duration Hours" in result_df.columns:
#             temp_df = result_df.copy()
#             temp_df["Duration_Decimal"] = temp_df["Duration Hours"].apply(_parse_duration_to_hours)
#             temp_df = temp_df.dropna(subset=["Duration_Decimal"])

#             avg_duration = (
#                 temp_df.groupby("Assignment Type")["Duration_Decimal"]
#                 .mean()
#                 .round(2)
#                 .sort_values(ascending=False)
#             )

#             if not avg_duration.empty:
#                 bar_fig = go.Figure(
#                     data=[go.Bar(
#                         x=avg_duration.index,
#                         y=avg_duration.values,
#                         text=avg_duration.values,
#                         texttemplate="%{text:.2f} hrs",
#                         textposition="outside",
#                         marker_color="#1565C0",
#                     )]
#                 )
#                 bar_fig.update_layout(
#                     title="Avg Duration by Assignment Type",
#                     xaxis_title="Assignment Type",
#                     yaxis_title="Avg Duration (Hrs)",
#                     margin=dict(t=50, b=0, l=0, r=0),
#                 )
#                 st.plotly_chart(bar_fig, use_container_width=True)
#             else:
#                 st.caption("No valid duration data found to compute averages.")
#         else:
#             st.caption(
#                 "Columns 'Assignment Type' and/or 'Duration Hours' not found. "
#                 f"Available columns: {list(result_df.columns)}"
#             )


# def plot_indicator_4b(result_dict, candidate_df):
#     # st.subheader("📊 Indicator 4b Charts")

#     percent_met = round(
#         (result_dict["Number of candidates' scores within acceptable values"] /
#          result_dict["Total number of survey responses"]) * 100
#     ) if result_dict["Total number of survey responses"] > 0 else 0

#     chart_col1, chart_col2, chart_col3 = st.columns(3)

#     with chart_col1:
#         pie_df = pd.DataFrame({
#             "Status": ["Within Acceptable Values", "Not Within Acceptable Values"],
#             "Count": [
#                 result_dict["Number of candidates' scores within acceptable values"],
#                 result_dict["Total number of survey responses"] - result_dict["Number of candidates' scores within acceptable values"]
#             ]
#         })
#         fig_pie = px.pie(
#             pie_df, names="Status", values="Count",
#             title="Candidates Meeting Standard",
#             color="Status",
#             color_discrete_map={
#                 "Within Acceptable Values": "#2ecc71",
#                 "Not Within Acceptable Values": "#e74c3c"
#             }
#         )
#         st.plotly_chart(fig_pie, use_container_width=True)

#     with chart_col2:
#         fig_hist = px.histogram(
#             candidate_df, x="Average Total Points", nbins=15,
#             title="Distribution of Average Total Points",
#             color_discrete_sequence=["#3498db"]
#         )
#         fig_hist.add_vline(x=22, line_dash="dash", line_color="red")
#         st.plotly_chart(fig_hist, use_container_width=True)

#     with chart_col3:
#         fig_gauge = go.Figure(go.Indicator(
#             mode="gauge+number",
#             value=percent_met,
#             title={"text": "Indicator 4b %"},
#             gauge={
#                 "axis": {"range": [0, 100]},
#                 "bar": {"color": "black"},
#                 "steps": [
#                     {"range": [0, 70], "color": "#e74c3c"},
#                     {"range": [70, 100], "color": "#2ecc71"},
#                 ],
#             }
#         ))
#         st.plotly_chart(fig_gauge, use_container_width=True)
















DURATION_TARGET_HRS = 45 / 60  # 0.75 hrs = 45 minutes
PCT_TARGET_4B = 90
# ══════════════════════════════════════════
# THEME VARIABLES — Dark Theme (shared across chapters)
# ══════════════════════════════════════════
BG_MAIN      = "#0E1117"   # main page/app background (deep black-navy)
BG_SURFACE   = "#000000"   # card/chart surface background (slightly lighter than main)
TEXT_PRIMARY = "#FAFAFA"   # main readable text (titles, values) — near-white
TEXT_MUTED   = "#9CA3AF"   # secondary/muted text (axis ticks, captions) — light gray
GRID_COLOR   = "#2A2E37"   # gridlines — subtle, low-contrast against BG_SURFACE
BORDER       = "#3A3F4B"   # borders/outlines around chart elements — mid gray

FONT_FAMILY  = "Segoe UI, Helvetica, Arial, sans-serif"

# Accent colors (used for non-binary/informational charts, e.g. radar line default, histogram bars)
ACCENT_BLUE  = "#58A6FF"
ACCENT_TEAL  = "#39D2C0"
ACCENT_AMBER = "#F0B429"

# Binary threshold colors (Met / Not Met — used across Ch.4, 5, 6)
MET_COLOR    =  "#1B8720"  # green
MISSED_COLOR = "#FF1708"   # red

GREEN  = MET_COLOR
RED    = MISSED_COLOR
YELLOW = "#F1C40F"         # used only where a 3-band system still applies (e.g. Ch.4 bar chart)


def plot_indicator_4a(result_df: pd.DataFrame, num_met_req: int, num_total_exp: int):
    """
    Renders 3 charts summarizing Indicator 4A (ASEP Chapter 6):
      1. Donut chart: overall Met vs Not Met requirement
      2. Gauge chart: % compliance
      3. Bar chart: average visit duration (hours) by Assignment Type
         🟢 Green = avg duration ≥ 45 min  |  🔴 Red = below 45 min
    """

    not_met = num_total_exp - num_met_req
    pct_met = round((num_met_req / num_total_exp) * 100, 1) if num_total_exp else 0

    col1, col2 = st.columns(2)

    # ---------- Chart 1: Donut chart (Met vs Not Met) ----------
    with col1:
        st.caption("🟢 Met Requirement  |  🔴 Not Met")
        donut_fig = go.Figure(
            data=[go.Pie(
                labels=["Met Requirement", "Not Met"],
                values=[num_met_req, not_met],
                hole=0.55,
                marker=dict(colors=[MET_COLOR, MISSED_COLOR], line=dict(color=BG_MAIN, width=2)),
                textinfo="label+value+percent",
                textfont=dict(family=FONT_FAMILY, size=11, color="black"),
            )]
        )
        donut_fig.update_layout(
            title=dict(text="Quality of Field Supervision: Met vs Not Met", font=dict(family=FONT_FAMILY, color=TEXT_PRIMARY)),
            showlegend=True,
            legend=dict(font=dict(family=FONT_FAMILY, color=TEXT_MUTED), bgcolor="rgba(0,0,0,0)"),
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(family=FONT_FAMILY, color=TEXT_PRIMARY),
            height=380,
            margin=dict(t=50, b=0, l=0, r=0),
        )
        st.plotly_chart(donut_fig, use_container_width=True)

    # # ---------- Chart 2: Gauge chart (% compliance) ----------
    # with col2:
    #     st.caption("Overall compliance rate (Met Requirement ÷ Total Expected)")
    #     gauge_color = MET_COLOR if pct_met >= 80 else MISSED_COLOR
    #     gauge_fig = go.Figure(
    #         go.Indicator(
    #             mode="gauge+number",
    #             value=pct_met,
    #             number={"suffix": "%", "font": dict(family=FONT_FAMILY, size=44, color="white")},
    #             title={"text": "Compliance Rate", "font": dict(family=FONT_FAMILY, color=TEXT_PRIMARY)},
    #             gauge={
    #                 "axis": {"range": [0, 100], "tickfont": dict(family=FONT_FAMILY, color=TEXT_MUTED), "tickcolor": BORDER},
    #                 "bar": {"color": gauge_color},
    #                 "bgcolor": BG_SURFACE,
    #                 "borderwidth": 2,
    #                 "bordercolor": BORDER,
    #                 "steps": [
    #                     {"range": [0, 100], "color": BG_SURFACE},
    #                 ],
    #             },
    #         )
    #     )
    #     gauge_fig.update_layout(
    #         paper_bgcolor="rgba(0,0,0,0)",
    #         font=dict(family=FONT_FAMILY, color=TEXT_PRIMARY),
    #         margin=dict(t=50, b=0, l=0, r=0),
    #     )
    #     st.plotly_chart(gauge_fig, use_container_width=True)

    # ---------- Chart 3: Average Duration by Assignment Type ----------
    with col2:
        st.caption("🟢 Green = avg duration ≥ 45 min  |  🔴 Red = below 45 min")
        if "Assignment Type" in result_df.columns and "Duration Hours" in result_df.columns:
            temp_df = result_df.copy()
            temp_df["Duration_Decimal"] = temp_df["Duration Hours"].apply(_parse_duration_to_hours)
            temp_df = temp_df.dropna(subset=["Duration_Decimal"])

            avg_duration = (
                temp_df.groupby("Assignment Type")["Duration_Decimal"]
                .mean()
                .round(2)
                .sort_values(ascending=False)
            )

            if not avg_duration.empty:
                bar_colors = [
                    MET_COLOR if v >= DURATION_TARGET_HRS else MISSED_COLOR
                    for v in avg_duration.values
                ]
                status_labels = [
                    "✓" if v >= DURATION_TARGET_HRS else "✗"
                    for v in avg_duration.values
                ]

                bar_fig = go.Figure(
                    data=[go.Bar(
                        x=avg_duration.index,
                        y=avg_duration.values,
                        text=[f"{v:.2f} hrs" for v, s in zip(avg_duration.values, status_labels)],
                        textposition="outside",
                        textfont=dict(family=FONT_FAMILY, size=12, color=TEXT_PRIMARY),
                        marker=dict(
                            color=bar_colors,
                            line=dict(color=BG_MAIN, width=2),
                            opacity=0.9,
                        ),
                        width=0.55,
                        hovertemplate="<b>%{x}</b><br>Avg Duration: %{y:.2f} hrs<extra></extra>",
                    )]
                )

                bar_fig.add_hline(
                    y=DURATION_TARGET_HRS,
                    line=dict(color="black", dash="dash", width=1.8),
                    annotation_text="Target: 45 min",
                    annotation_position="top left",
                    annotation_font=dict(family=FONT_FAMILY, size=11, color=TEXT_MUTED),
                )

                bar_fig.update_layout(
                    title=dict(
                        text="<b>Avg Duration by Assignment Type</b>",
                        font=dict(family=FONT_FAMILY, size=16, color=TEXT_PRIMARY),
                        x=0.02,
                    ),
                    xaxis=dict(
                        title="Assignment Type",
                        tickfont=dict(family=FONT_FAMILY, size=11, color=TEXT_MUTED),
                        gridcolor=GRID_COLOR,
                        linecolor=BORDER,
                        showgrid=False,
                    ),
                    yaxis=dict(
                        title="Avg Duration (Hrs)",
                        tickfont=dict(family=FONT_FAMILY, color=TEXT_MUTED),
                        gridcolor=GRID_COLOR,
                        linecolor=BORDER,
                        range=[0, avg_duration.values.max() + 0.35],
                    ),
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(family=FONT_FAMILY, color=TEXT_PRIMARY),
                    bargap=0.35,
                    height=380,
                    margin=dict(t=60, b=20, l=10, r=10),
                    showlegend=False,
                )
                st.plotly_chart(bar_fig, use_container_width=True)
            else:
                st.caption("No valid duration data found to compute averages.")
        else:
            st.caption(
                "Columns 'Assignment Type' and/or 'Duration Hours' not found. "
                f"Available columns: {list(result_df.columns)}"
            )


def plot_indicator_4b(result_dict, candidate_df):
    """
    Renders 3 charts for Indicator 4B (ASEP Chapter 6):
      1. Pie chart: candidates within acceptable values
      2. Histogram: distribution of average total points
      3. Gauge: % candidates meeting standard
         🟢 Green = ≥ 90%  |  🔴 Red = below 90%
    """

    percent_met = round(
        (result_dict["Number of candidates' scores within acceptable values"] /
         result_dict["Total number of survey responses"]) * 100
    ) if result_dict["Total number of survey responses"] > 0 else 0

    chart_col1, chart_col2, chart_col3 = st.columns(3)

    with chart_col1:
        st.caption("🟢 Within Acceptable Values (≤ 22)  |  🔴 Not Within")

        met_count = result_dict["Number of candidates' scores within acceptable values"]
        total_count = result_dict["Total number of survey responses"]
        not_met_count = total_count - met_count
        pct_met_display = round((met_count / total_count) * 100, 1) if total_count else 0

        fig_pie = go.Figure(
            go.Pie(
                labels=["Within Acceptable Values", "Not Within Acceptable Values"],
                values=[met_count, not_met_count],
                hole=0.6,
                marker=dict(
                    colors=[MET_COLOR, MISSED_COLOR],
                    line=dict(color=BG_MAIN, width=3),
                ),
                textinfo="percent",
                textfont=dict(family=FONT_FAMILY, size=14, color="black"),
                pull=[0.03, 0.03],
                hovertemplate="<b>%{label}</b><br>Candidates: %{value}<br>Share: %{percent}<extra></extra>",
                rotation=90,
            )
        )

        fig_pie.update_layout(
            title=dict(
                text="<b>Candidates Meeting Standard</b>",
                font=dict(family=FONT_FAMILY, size=16, color=TEXT_PRIMARY),
                x=0.02,
            ),
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom", y=-0.15,
                xanchor="center", x=0.5,
                font=dict(family=FONT_FAMILY, size=11, color=TEXT_MUTED),
                bgcolor="rgba(0,0,0,0)",
            ),
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(family=FONT_FAMILY, color=TEXT_PRIMARY),
            height=380,
            margin=dict(t=60, b=40, l=10, r=10),
            annotations=[
                dict(
                    text=f"<b>{pct_met_display}%</b><br><span style='font-size:11px;color:{TEXT_MUTED}'>Meeting Standard</span>",
                    x=0.5, y=0.5,
                    font=dict(size=24, family=FONT_FAMILY, color="white"),
                    showarrow=False,
                ),
                dict(
                    text=f"n = {total_count}",
                    x=0.5, y=1.08,
                    xanchor="center",
                    font=dict(size=11, family=FONT_FAMILY, color=TEXT_MUTED),
                    showarrow=False,
                ),
            ],
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    with chart_col2:
        st.caption("🟢 Green = ≤ 22 points (Acceptable)  |  🔴 Red = > 22 points")

        import numpy as np

        data = candidate_df["Average Total Points"].dropna()
        dot_colors = [MET_COLOR if v <= 22 else MISSED_COLOR for v in data]

        # jitter for the dots so they don't overlap on one line
        np.random.seed(42)
        y_jitter = np.random.uniform(-0.15, 0.15, size=len(data))

        fig_dist = go.Figure()

        # ── Box plot for spread ──
        fig_dist.add_trace(
            go.Box(
                x=data,
                y=[0] * len(data),
                orientation="h",
                boxpoints=False,
                marker=dict(color=ACCENT_BLUE),
                line=dict(color=TEXT_MUTED, width=1.5),
                fillcolor="rgba(255,255,255,0.05)",
                name="Spread",
                showlegend=False,
            )
        )

        # ── Individual candidate dots ──
        fig_dist.add_trace(
            go.Scatter(
                x=data,
                y=y_jitter,
                mode="markers",
                marker=dict(
                    color=dot_colors,
                    size=9,
                    line=dict(color=BG_MAIN, width=1),
                    opacity=0.85,
                ),
                name="Candidates",
                hovertemplate="Avg Points: %{x:.1f}<extra></extra>",
                showlegend=False,
            )
        )

        fig_dist.add_vline(
            x=22,
            line=dict(color=TEXT_PRIMARY, dash="dash", width=1.8),
            annotation_text="Target: ≤ 22",
            annotation_font=dict(family=FONT_FAMILY, size=10, color=TEXT_PRIMARY),
        )

        fig_dist.update_layout(
            title=dict(text="Candidate Average Total Points", font=dict(family=FONT_FAMILY, color=TEXT_PRIMARY)),
            xaxis=dict(title="Average Total Points", tickfont=dict(family=FONT_FAMILY, color=TEXT_MUTED),
                       gridcolor=GRID_COLOR, linecolor=BORDER),
            yaxis=dict(visible=False, range=[-0.5, 0.5]),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family=FONT_FAMILY, color=TEXT_PRIMARY),
            height=350,
            margin=dict(t=50, b=20, l=10, r=10),
        )
        st.plotly_chart(fig_dist, use_container_width=True)


    with chart_col3:
        st.caption("🟢 Green = ≥ 90%  |  🔴 Red = below 90%")
        gauge_color = MET_COLOR if percent_met >= PCT_TARGET_4B else MISSED_COLOR

        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=percent_met,
            number={"suffix": "%", "font": dict(family=FONT_FAMILY, size=48, color="white")},
            delta={
                "reference": PCT_TARGET_4B,
                "increasing": {"color": MET_COLOR},
                "decreasing": {"color": MISSED_COLOR},
                "font": dict(family=FONT_FAMILY, size=14),
            },
            title={
                "text": "<b>Indicator 4b — % Meeting Standard</b>",
                "font": dict(family=FONT_FAMILY, size=15, color=TEXT_PRIMARY),
            },
            domain={"x": [0, 1], "y": [0, 1]},
            gauge={
                "axis": {
                    "range": [0, 100],
                    "tickvals": [0, 25, 50, 75, 90, 100],
                    "tickfont": dict(family=FONT_FAMILY, size=10, color=TEXT_MUTED),
                    "tickcolor": BORDER,
                },
                "bar": {"color": gauge_color, "thickness": 0.28},
                "bgcolor": BG_SURFACE,
                "borderwidth": 2,
                "bordercolor": BORDER,
                "steps": [
                    {"range": [0, PCT_TARGET_4B], "color": "rgba(231,76,60,0.15)"},
                    {"range": [PCT_TARGET_4B, 100], "color": "rgba(46,204,113,0.15)"},
                ],
                "threshold": {
                    "line": {"color": "white", "width": 3},
                    "thickness": 0.85,
                    "value": PCT_TARGET_4B,
                },
            }
        ))

        fig_gauge.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(family=FONT_FAMILY, color=TEXT_PRIMARY),
            height=320,
            margin=dict(t=60, b=20, l=30, r=30),
            annotations=[
                dict(
                    text="Target: 90%",
                    x=0.5, y=-0.05,
                    xref="paper", yref="paper",
                    xanchor="center",
                    font=dict(size=11, family=FONT_FAMILY, color=TEXT_MUTED),
                    showarrow=False,
                ),
            ],
        )
        st.plotly_chart(fig_gauge, use_container_width=True)