import pandas as pd
import streamlit as st

import plotly.express as px
import plotly.graph_objects as go
from utils.gauge import gauge

def chapter_5_data_preparation(educator_data, academic_growth_data):
    # educator_data = pd.read_excel(educator_data_path, skipfooter=2)

    # academic_growth_data = pd.read_excel(academic_growth_data_path, skipfooter=2)

    merged_growth_df = academic_growth_data.merge(
            educator_data, 
            on='TEA ID', 
            how='inner'
    )

    df1_sorted = merged_growth_df.sort_values(by=['TEA ID', 'Employment Date'], ascending=False)

    # 3. Drop duplicates, keeping only the 'last' occurrence for each TEA ID
    df_latest = df1_sorted.drop_duplicates(subset='TEA ID', keep='first')

    # Optional: Reset the index for a clean dataframe
    df_latest = df_latest.reset_index(drop=True)

    return df_latest

def verify_certificate(df):
    df = df[df['Certification Type'].isin(['Standard', 'Intern','Probationary', 'Enhanced Standared'])]
    return df

def eligible_window(df):
    df = df[df['Year of Teaching'] <= 3]
    return df

def student_minimum(df):
    filtered_df = df[~(df['Mathematics N'] <= 10) | (df['English/ Reading N'] <= 10)]
    return filtered_df

MET_COLOR     = "#1B8720"   # green  – score >= 50
MISSED_COLOR  = "#FF1708"   # red    – score <  50
TARGET        = 50
 
MET_LABEL    = "Met Standard (≥50)"
MISSED_LABEL = "Did Not Meet (<50)"
 
COLOR_MAP = {MET_LABEL: MET_COLOR, MISSED_LABEL: MISSED_COLOR}

def _asep_label(score: float) -> str:
    return MET_LABEL if score >= TARGET else MISSED_LABEL
 
# ── Helper: bar color list aligned to a value series ─────────────────────────
def _bar_colors(series: pd.Series) -> list:
    return [MET_COLOR if v >= TARGET else MISSED_COLOR for v in series]

# def chapter_5_chart(merge_data):
#     st.markdown("---")
#     df = merge_data.copy()

#     # 1. Calculate the average of Math and English/Reading scores
#     # axis=1 calculates row-wise. It safely averages the two, or takes the single available score if one is NaN.
#     df['Calculated Growth Score'] = df[['Mathematics Student Growth Score', 'English/ Reading Student Growth Score']].mean(axis=1)

#     # 2. Fill any remaining blanks with the original Overall Student Growth Score just in case, 
#     # then drop rows only if they are completely missing all three scores.
#     df['Calculated Growth Score'] = df['Calculated Growth Score'].fillna(df['Overall Student Growth Score'])
#     df = df.dropna(subset=['Calculated Growth Score'])

#     # 3. Create the compliance status flag
#     df['ASEP Standard'] = df['Calculated Growth Score'].apply(
#         lambda x: 'Met Standard (>50)' if x > 50 else 'Did Not Meet (<=50)'
#     )

#     # 4. Clean up Gender data (combine Gender_x and Gender_y to prevent gaps)
#     df['Gender'] = df['Gender_x'].fillna(df['Gender_y']).fillna('Unknown')

#     # --- DASHBOARD LAYOUT ---
#     col1, col2 = st.columns(2)
#     st.markdown("---")
#     col3, col4 = st.columns(2)
#     col5, col6 = st.columns(2)


#     # --- CHART 1: Overall Compliance Breakdown (With Gender Filter Applied) ---
#     with col1:
#         # st.subheader("Overall ASEP Compliance")
#         # fig1 = px.pie(
#         #     df, 
#         #     names='ASEP Standard', 
#         #     hole=0.4, 
#         #     color='ASEP Standard',
#         #     color_discrete_map={'Met Standard (>50)': "#72d188", 'Did Not Meet (<=50)': '#dc3545'}
#         # )
#         # st.plotly_chart(fig1, use_container_width=True)

#         st.subheader("Overall Average Score")
#         st.caption(
#             "Gauge bands: 🟢 Green = Satisfactory (50 - 100) "
#             "🔴 Red = Needs Improvement (0 – 49). "
#             "The line indicate overall average score."
#         )


#         if 'Calculated Growth Score' in df.columns:
#             avg_score = df['Calculated Growth Score'].mean()
#         else:
#             st.error("Column 'Calculated Growth Score' not found in DataFrame.")
#             return None

#         low_color = "#FF1708"
#         high_color = "#1B8720"
        
#         gauge_color = high_color if avg_score >= 50 else low_color

#         fig = go.Figure(
#                 go.Indicator(
#                     mode="gauge+number",
#                     value=avg_score,
#                     domain={"x": [0, 1], "y": [0, 1]},
#                     gauge={
#                         "axis": {
#                             "range": [0, 100],
#                             "tickwidth": 1,
#                             "tickcolor": "darkblue",
#                         },
#                         "bar": {"color": gauge_color},  # This changes dynamically
#                         "bgcolor": "white",
#                         "borderwidth": 2,
#                         "bordercolor": "gray",
#                         "steps": [
#                             {"range": [0, 50], "color": "#000000"},
#                             {"range": [50, 100], "color": "#000000"},
#                         ],
#                     },
#                 )
#             )

#         # 4. Render in Streamlit
#         st.plotly_chart(fig, use_container_width=True)
        

#     # --- CHART 2: Average Score by Certification Area Grade Level ---
#     with col2:
#         st.subheader("Avg Score by Certification Area")
#         # Group and calculate average
#         cert_avg = df.groupby('Certification Area Grade Level')['Calculated Growth Score'].mean().reset_index()
        
#         # Sort Ascending = True pushes the highest values to the TOP of a Plotly horizontal chart
#         cert_avg = cert_avg.sort_values(by='Calculated Growth Score', ascending=True)
        
#         fig2 = px.bar(
#             cert_avg,
#             x='Calculated Growth Score',
#             y='Certification Area Grade Level',
#             orientation='h', # This makes it a horizontal bar chart
#             color='Calculated Growth Score',
#             color_continuous_scale='Greens',
#             labels={'Calculated Growth Score': 'Avg Score', 'Certification Area Grade Level': ''}
#         )
        
#         # The threshold line is vertical (vline) because the scores are now on the X-axis
#         fig2.add_vline(x=50, line_dash="dash", line_color="red", annotation_text="Target: 50")
        
#         st.plotly_chart(fig2, use_container_width=True)


    
#     # --- CHART 3: Performance by Finisher Year (Stacked Bar) ---
#     with col3:
#         st.subheader("Compliance by Finisher Year")
#         cohort_counts = df.groupby(['Finisher Year', 'ASEP Standard']).size().reset_index(name='Count')
#         fig3 = px.bar(
#             cohort_counts, 
#             x='Finisher Year', 
#             y='Count', 
#             color='ASEP Standard',
#             barmode='group',
#             color_discrete_map={'Met Standard (>50)': '#28a745', 'Did Not Meet (<=50)': '#dc3545'}
#         )
#         st.plotly_chart(fig3, use_container_width=True)


#     # --- CHART 4: Average Score by Year of Teaching & Race/Ethnicity ---
#     # Breaking this into two clean sub-tabs within the 4th quadrant to avoid crowding
#     with col4:
#         tab1, tab2 = st.tabs(["📊 By Year of Teaching", "🧬 By Race / Ethnicity"])
        
#         with tab1:
#             st.write("### Avg Score by Year of Teaching")
#             # Ensure 'Year of Teaching' is treated well for sorting/averaging
#             teaching_year_avg = df.groupby('Year of Teaching')['Calculated Growth Score'].mean().reset_index()
#             teaching_year_avg = teaching_year_avg.sort_values(by='Year of Teaching')
            
#             fig4a = px.line(
#                 teaching_year_avg,
#                 x='Year of Teaching',
#                 y='Calculated Growth Score',
#                 markers=True,
#                 labels={'Calculated Growth Score': 'Avg Growth Score'}
#             )
#             fig4a.add_hline(y=50, line_dash="dash", line_color="red", annotation_text="Target: 50")
#             st.plotly_chart(fig4a, use_container_width=True)
            
#         with tab2:
#             st.write("### Avg Score by Race / Ethnicity")
#             # Standardize naming fallback just in case columns differ
#             df['Race_Group'] = df['Race/ Ethnicity'].fillna(df['Race/Ethnicity']).fillna('Unknown')
#             race_avg = df.groupby('Race_Group')['Calculated Growth Score'].mean().reset_index()
#             race_avg = race_avg.sort_values(by='Calculated Growth Score', ascending=False)
            
#             fig4b = px.bar(
#                 race_avg,
#                 x='Race_Group',
#                 y='Calculated Growth Score',
#                 color='Calculated Growth Score',
#                 color_continuous_scale='Purples',
#                 labels={'Race_Group': 'Race/Ethnicity', 'Calculated Growth Score': 'Avg Score'}
#             )
#             fig4b.add_hline(y=50, line_dash="dash", line_color="red")
#             st.plotly_chart(fig4b, use_container_width=True)
 
#     st.markdown("---")

#     with col5:
#         st.subheader("Students Achieving Target Growth (Score ≥ 50)")

#         required_cols = [
#                 "Mathematics Student Growth Score",
#                 "English/ Reading Student Growth Score",
#         ]
#         if not all(col in merge_data.columns for col in required_cols):
#             st.error(
#                 f"Missing required columns. Please ensure both {required_cols} exist."
#             )
#             return

#         # 2. Calculate the Growth Score (Average of Math and English/Reading)
#         merge_data["Calculated Growth Score"] = merge_data[required_cols].mean(
#             axis=1
#         )

#         # 3. Calculate total records and records matching the threshold (>= 50)
#         total_records = len(merge_data)
        
#         if total_records == 0:
#             st.warning("The provided DataFrame is empty.")
#             return

#         # Corrected filtering logic to get the true count of rows >= 50
#         count_above_or_equal_50 = len(
#             merge_data[merge_data["Calculated Growth Score"] >= 50]
#         )
#         count_below_50 = total_records - count_above_or_equal_50

#         # Compute percentages
#         pct_above_or_equal_50 = (count_above_or_equal_50 / total_records) * 100
#         pct_below_50 = (count_below_50 / total_records) * 100

#         # 4. Display a Summary Metric Card
#         st.metric(
#             label="",
#             value=f"{pct_above_or_equal_50:.1f}%",
#             delta=f"{count_above_or_equal_50} out of {total_records} students",
#             delta_color="normal",
#         )

#         # 5. Create a Donut Chart to visualize the distribution percentage
#         labels = ["Score ≥ 50 (Met Target)", "Score < 50 (Below Target)"]
#         values = [pct_above_or_equal_50, pct_below_50]
#         colors = ["#1B8720", "#FF1708"]  # Matching your green and red hex choices

#         fig = go.Figure(
#             data=[
#                 go.Pie(
#                     labels=labels,
#                     values=values,
#                     hole=0.5,  # Makes it a donut chart
#                     marker=dict(colors=colors),
#                     textinfo="percent+label",
#                     hoverinfo="label+value+percent",
#                 )
#             ]
#         )

#         # Style layout to be transparent and adapt nicely to Streamlit themes
#         fig.update_layout(
#             title={
#                 "text": "Growth Score Threshold Breakdown",
#                 "y": 0.95,
#                 "x": 0.5,
#                 "xanchor": "center",
#                 "yanchor": "top",
#             },
#             showlegend=False,
#             paper_bgcolor="rgba(0,0,0,0)",
#             plot_bgcolor="rgba(0,0,0,0)",
#             height=350,
#             margin=dict(l=20, r=20, t=60, b=20),
#         )

#         # Render chart in Streamlit
#         st.plotly_chart(fig, use_container_width=True)

def chapter_5_summary(df):
    score_cols = ["Mathematics Student Growth Score", "English/ Reading Student Growth Score"]

    temp = df.copy()
    temp["Calculated Growth Score"] = temp[score_cols].mean(axis=1)
    temp["Calculated Growth Score"] = temp["Calculated Growth Score"].fillna(
        temp["Overall Student Growth Score"]
    )
    temp = temp.dropna(subset=["Calculated Growth Score"])

    total_teachers_with_scores = len(temp)

    if total_teachers_with_scores == 0:
        return {
            "teachers_meeting_standard": 0,
            "total_teachers_with_scores": 0,
            "pct_meeting_standard": 0,
        }

    teachers_meeting_standard = len(temp[temp["Calculated Growth Score"] >= TARGET])
    pct_meeting_standard = (teachers_meeting_standard / total_teachers_with_scores) * 100
   
    return {
        "teachers_meeting_standard": teachers_meeting_standard,
        "total_teachers_with_scores": total_teachers_with_scores,
        "pct_meeting_standard": round(pct_meeting_standard, 2), 
    }

def get_asep_threshold(year_of_teaching):
    """
    Returns the ASEP Chapter 5 compliance threshold for a given reporting year.
    Returns None if the year is Report-Only (no threshold applies).
    """
    year_val = int(year_of_teaching)

    if year_val <= 2024:
        threshold = None
    elif year_val in [2025, 2026]:
        threshold = 60.0
    elif year_val == 2027:
        threshold = 65.0
    else:
        threshold = 70.0

    return threshold


def chapter_5_chart(merge_data, year_of_teaching):
    st.markdown("---")
    df = merge_data.copy()
 
    # ── 1. Calculated Growth Score ──────────────────────────────────────────
    score_cols = ["Mathematics Student Growth Score", "English/ Reading Student Growth Score"]
    df["Calculated Growth Score"] = df[score_cols].mean(axis=1)
    df["Calculated Growth Score"] = df["Calculated Growth Score"].fillna(df["Overall Student Growth Score"])
    df = df.dropna(subset=["Calculated Growth Score"])
 
    # ── 2. ASEP compliance flag ─────────────────────────────────────────────
    df["ASEP Standard"] = df["Calculated Growth Score"].apply(_asep_label)
 
    # ── 3. Gender fallback ──────────────────────────────────────────────────
    df["Gender"] = df["Gender_x"].fillna(df["Gender_y"]).fillna("Unknown")
 
    # ── Layout ──────────────────────────────────────────────────────────────
    col1, col2 = st.columns(2)
    st.markdown("---")
    col3, col4 = st.columns(2)
    col5, col6 = st.columns(2)
 
    # ════════════════════════════════════════════════════════════════════════
    # CHART 1 – Gauge: Overall Average Score
    # ════════════════════════════════════════════════════════════════════════
    with col1:
        st.subheader("Overall Average Growth Score")
        st.caption(
            "🟢 Green = Met Standard (≥ 50)  |  🔴 Red = Did Not Meet (< 50). "
            "Needle shows the overall average."
        )
 
        avg_score   = df["Calculated Growth Score"].mean()
        gauge_color = MET_COLOR if avg_score >= TARGET else MISSED_COLOR
 
        fig1 = go.Figure(
            go.Indicator(
                mode="gauge+number",
                value=avg_score,
                domain={"x": [0, 1], "y": [0, 1]},
                gauge={
                    "axis": {"range": [0, 100], "tickwidth": 1, "tickcolor": "darkblue"},
                    "bar": {"color": gauge_color},
                    "bgcolor": "white",
                    "borderwidth": 2,
                    "bordercolor": "gray",
                    "steps": [
                        {"range": [0, 50],  "color": "#000000"},
                        {"range": [50, 100], "color": "#000000"},
                    ],
                },
            )
        )
        fig1.update_layout(height=300, margin=dict(t=30, b=10))
        st.plotly_chart(fig1, use_container_width=True)
 
    # ════════════════════════════════════════════════════════════════════════
    # CHART 2 – Horizontal Bar: Avg Score by Certification Area Grade Level
    #           Each bar is green if avg >= 50, red otherwise
    # ════════════════════════════════════════════════════════════════════════
    with col2:
        st.subheader("Avg Score by Certification Area")
 
        cert_avg = (
            df.groupby("Certification Area Grade Level")["Calculated Growth Score"]
            .mean()
            .reset_index()
            .sort_values("Calculated Growth Score", ascending=True)
        )
 
        fig2 = go.Figure(
            go.Bar(
                x=cert_avg["Calculated Growth Score"],
                y=cert_avg["Certification Area Grade Level"],
                orientation="h",
                marker_color=_bar_colors(cert_avg["Calculated Growth Score"]),
                text=cert_avg["Calculated Growth Score"].round(1),
                textposition="outside",
            )
        )
        fig2.add_vline(x=TARGET, line_dash="dash", line_color="black",
                       annotation_text="Target: 50", annotation_position="top right")
        fig2.update_layout(
            xaxis_title="Avg Score",
            yaxis_title="",
            height=380,
            margin=dict(t=20, b=20),
        )
        st.plotly_chart(fig2, use_container_width=True)
 
    # ════════════════════════════════════════════════════════════════════════
    # CHART 3 – Grouped Bar: Met vs Did Not Meet by Finisher Year
    # ════════════════════════════════════════════════════════════════════════
    with col3:
        st.subheader("Compliance by Finisher Year")
 
        cohort_counts = (
            df.groupby(["Finisher Year", "ASEP Standard"])
            .size()
            .reset_index(name="Count")
        )
 
        fig3 = px.bar(
            cohort_counts,
            x="Finisher Year",
            y="Count",
            color="ASEP Standard",
            barmode="group",
            color_discrete_map=COLOR_MAP,
            text="Count",
        )
        fig3.update_traces(textposition="outside")
        fig3.update_layout(legend_title_text="ASEP Standard", margin=dict(t=20))
        st.plotly_chart(fig3, use_container_width=True)
 
    # ════════════════════════════════════════════════════════════════════════
    # CHART 4 – Tabs: By Year of Teaching  |  By Race / Ethnicity
    #           Line markers and bars colored green/red per value
    # ════════════════════════════════════════════════════════════════════════
    with col4:
        tab1, tab2 = st.tabs(["📊 By Year of Teaching", "🧬 By Race / Ethnicity"])
 
        with tab1:
            st.write("### Avg Score by Year of Teaching")
            yr_avg = (
                df.groupby("Year of Teaching")["Calculated Growth Score"]
                .mean()
                .reset_index()
                .sort_values("Year of Teaching")
            )
 
            fig4a = go.Figure()
            # Colored segments: green above 50, red below
            for i in range(len(yr_avg) - 1):
                seg = yr_avg.iloc[i : i + 2]
                mid = seg["Calculated Growth Score"].mean()
                fig4a.add_trace(
                    go.Scatter(
                        x=seg["Year of Teaching"],
                        y=seg["Calculated Growth Score"],
                        mode="lines",
                        line=dict(color=MET_COLOR if mid >= TARGET else MISSED_COLOR, width=3),
                        showlegend=False,
                    )
                )
            # Markers
            fig4a.add_trace(
                go.Scatter(
                    x=yr_avg["Year of Teaching"],
                    y=yr_avg["Calculated Growth Score"],
                    mode="markers+text",
                    marker=dict(
                        color=_bar_colors(yr_avg["Calculated Growth Score"]),
                        size=10,
                    ),
                    text=yr_avg["Calculated Growth Score"].round(1),
                    textposition="top center",
                    showlegend=False,
                )
            )
            fig4a.add_hline(y=TARGET, line_dash="dash", line_color="black",
                            annotation_text="Target: 50")
            fig4a.update_layout(
                xaxis_title="Year of Teaching",
                yaxis_title="Avg Growth Score",
                margin=dict(t=20),
            )
            st.plotly_chart(fig4a, use_container_width=True)
 
        with tab2:
            st.write("### Avg Score by Race / Ethnicity")
            df["Race_Group"] = (
                df.get("Race/ Ethnicity", pd.Series(dtype=str))
                .fillna(df.get("Race/Ethnicity", pd.Series(dtype=str)))
                .fillna("Unknown")
            )
            race_avg = (
                df.groupby("Race_Group")["Calculated Growth Score"]
                .mean()
                .reset_index()
                .sort_values("Calculated Growth Score", ascending=False)
            )
 
            fig4b = go.Figure(
                go.Bar(
                    x=race_avg["Race_Group"],
                    y=race_avg["Calculated Growth Score"],
                    marker_color=_bar_colors(race_avg["Calculated Growth Score"]),
                    text=race_avg["Calculated Growth Score"].round(1),
                    textposition="outside",
                )
            )
            fig4b.add_hline(y=TARGET, line_dash="dash", line_color="black",
                            annotation_text="Target: 50")
            fig4b.update_layout(
                xaxis_title="Race / Ethnicity",
                yaxis_title="Avg Score",
                margin=dict(t=20),
            )
            st.plotly_chart(fig4b, use_container_width=True)
 
    st.markdown("---")
 
    # ════════════════════════════════════════════════════════════════════════
    # CHART 5 – Donut + Metric: % Students Achieving Target Growth (≥ 50)
    # ════════════════════════════════════════════════════════════════════════
    with col5:
        st.subheader("Students Achieving Target Growth (Score ≥ 50)")
 
        required_cols = [
            "Mathematics Student Growth Score",
            "English/ Reading Student Growth Score",
        ]
        if not all(c in merge_data.columns for c in required_cols):
            st.error(f"Missing required columns: {required_cols}")
            return
 
        tmp = merge_data.copy()
        tmp["Calculated Growth Score"] = tmp[required_cols].mean(axis=1)
 
        total = len(tmp)
        if total == 0:
            st.warning("The provided DataFrame is empty.")
            return
 
        count_met = len(tmp[tmp["Calculated Growth Score"] >= TARGET])
        count_missed = total - count_met
        pct_met = (count_met   / total) * 100
        pct_missed = (count_missed / total) * 100
 
        st.metric(
            label="",
            value=f"{pct_met:.1f}%",
            delta=f"{count_met} out of {total} students met target",
            delta_color="normal",
        )
 
        fig5 = go.Figure(
            go.Pie(
                labels=[MET_LABEL, MISSED_LABEL],
                values=[pct_met, pct_missed],
                hole=0.5,
                marker=dict(colors=[MET_COLOR, MISSED_COLOR]),
                textinfo="percent+label",
                hoverinfo="label+value+percent",
            )
        )
        fig5.update_layout(
            title=dict(
                text="Growth Score Threshold Breakdown",
                y=0.95, x=0.5, xanchor="center", yanchor="top",
            ),
            showlegend=False,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            height=350,
            margin=dict(l=20, r=20, t=60, b=20),
        )
        st.plotly_chart(fig5, use_container_width=True)

    # ════════════════════════════════════════════════════════════════════════
    # CHART 6 – Gauge: % Teachers Meeting Individual Standard
    # ════════════════════════════════════════════════════════════════════════
    with col6:
        st.subheader("Teachers Meeting Individual Standard")

        summary = chapter_5_summary(merge_data)
        pct_met_individual = summary["pct_meeting_standard"]
        total_teachers = summary["total_teachers_with_scores"]
        teachers_met = summary["teachers_meeting_standard"]

        threshold = get_asep_threshold(year_of_teaching)

        if total_teachers == 0:
            st.warning("No teachers with valid growth scores found.")
        elif threshold is None:
            st.info(
                f"ℹ️ Year {int(year_of_teaching)} is **Report-Only** — no compliance "
                f"threshold applies. Current rate: **{pct_met_individual:.1f}%** "
                f"({teachers_met} of {total_teachers})."
            )
        else:
            st.caption(
                f"🟢 Green = Meets or exceeds threshold (≥ {threshold:.0f}%)  |  "
                f"🔴 Red = Below threshold. "
                f"({teachers_met} of {total_teachers} teachers met individual standard)"
            )

            gauge_color = MET_COLOR if pct_met_individual >= threshold else MISSED_COLOR

            fig6 = go.Figure(
                go.Indicator(
                    mode="gauge+number",
                    value=pct_met_individual,
                    number=dict(suffix="%"),
                    domain={"x": [0, 1], "y": [0, 1]},
                    gauge={
                        "axis": {"range": [0, 100], "tickwidth": 1, "tickcolor": "darkblue"},
                        "bar": {"color": gauge_color},
                        "bgcolor": "white",
                        "borderwidth": 2,
                        "bordercolor": "gray",
                        "steps": [
                            {"range": [0, threshold], "color": "#000000"},
                            {"range": [threshold, 100], "color": "#000000"},
                        ],
                        "threshold": {
                            "line": {"color": "white", "width": 3},
                            "thickness": 0.85,
                            "value": threshold,
                        },
                    },
                )
            )
                    
            fig6.update_layout(height=300, margin=dict(t=30, b=10))
            st.plotly_chart(fig6, use_container_width=True)
        

@st.cache_data
def prepare_chapter_5(educator_data, student_growth):
    df = chapter_5_data_preparation(educator_data, student_growth)
    df = verify_certificate(df)
    df = eligible_window(df)
    df = student_minimum(df)
    return df

def student_growth(educator_data, student_growth):
    # merge_data = chapter_5_data_preparation(educator_data, student_growth)
    # merge_data = verify_certificate(merge_data)
    # merge_data = eligible_window(merge_data)
    # merge_data = student_minimum(merge_data)
    merge_data = prepare_chapter_5(educator_data, student_growth)

    if "chapter_5_gender_filter" not in st.session_state:
        st.session_state.chapter_5_gender_filter = "All"

    available_year_of_teaching_options = sorted(merge_data['Data Year'].unique().tolist())

    if "chapter_5_data_year" not in st.session_state:
        st.session_state.chapter_5_data_year = available_year_of_teaching_options

    # # ── Filters ──
    st.subheader("🔍 Filter Options")
    filter_col1, filter_col2, filter_col3 = st.columns(3)
    
    with filter_col1:
        gender_selected = st.selectbox(
            "Gender",
            options=["All"] + sorted(merge_data["Gender_x"].unique().tolist()),
            key="chapter_5_gender_select",
        )
        st.session_state.chapter_5_gender_filter = gender_selected

    with filter_col2:
        data_year = st.selectbox(
            "Data Year",
            options = available_year_of_teaching_options,
            key="year_of_teaching"
        )
        if data_year != st.session_state.chapter_5_data_year:
            st.session_state.chapter_5_data_year = data_year

        
    filtered_copy_df = merge_data.copy()
    if gender_selected != "All":
        filtered_copy_df = filtered_copy_df[filtered_copy_df["Gender_x"] == gender_selected]
    filtered_copy_df = filtered_copy_df[filtered_copy_df["Data Year"] == st.session_state.chapter_5_data_year]

    chapter_5_chart(filtered_copy_df, data_year)

    return merge_data