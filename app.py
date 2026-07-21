import streamlit as st
import pandas as pd
import io
import plotly.express as px
import plotly.graph_objects as go
from utils.data_management import show_old_new_file, download_new_file, process_and_rename_file
from utils.chapter_4_calculations import principal_perceptions, first_year_status, chapter_4_chart, merge_both_df, get_asep_consolidated_data, remove_duplicates, missing_required_sections, chapter_4_group_aggregration, chapter_4_survey_summary
from utils.chapter_5_calculations import verify_certificate, student_growth, chapter_5_summary
from utils.chapter_3_calculations import exam_pass_rate, indicator_1a_data, indicator_1b_data, calculate_asep_indicator_1a
from utils.chapter_6_calculations import process_chapter_6_records, indicator_4a_calculate, plot_indicator_4a, plot_indicator_4b, field_supervision

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


# ─────────────────────────────────────────────
# INJECT DARK CSS
# ─────────────────────────────────────────────
DARK_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700&display=swap');

/* ── root background ── */
html, body, [data-testid="stAppViewContainer"],
[data-testid="stHeader"], [data-testid="stSidebar"] {
    background-color: #0D1117 !important;
    color: #E6EDF3 !important;
    font-family: 'Montserrat', sans-serif !important;
}

/* sidebar */
[data-testid="stSidebar"] {
    background-color: #161B22 !important;
    border-right: 1px solid #30363D;
}

/* main content wrapper */
[data-testid="block-container"] { background-color: #0D1117 !important; }

/* ── typography ── */
h1, h2, h3, h4, h5, h6,
.stMarkdown p, .stCaption,
[data-testid="stMetricLabel"],
[data-testid="stMetricValue"],
[data-testid="stMetricDelta"] {
    color: #E6EDF3 !important;
    font-family: 'Montserrat', sans-serif !important;
}

.stCaption { color: #8B949E !important; }

/* ── metric cards ── */
[data-testid="metric-container"] {
    background-color: #161B22 !important;
    border: 1px solid #30363D !important;
    border-radius: 10px !important;
    padding: 16px !important;
}
[data-testid="stMetricLabel"] { font-weight: 600 !important; }

/* ── divider ── */
hr { border-color: #30363D !important; }

/* ── tabs ── */
[data-baseweb="tab-list"] { background-color: #161B22 !important; border-bottom: 1px solid #30363D; }
[data-baseweb="tab"] { color: #8B949E !important; font-family: 'Montserrat', sans-serif !important; }
[aria-selected="true"] { color: #58A6FF !important; border-bottom: 2px solid #58A6FF !important; }

/* ── selectbox / multiselect ── */
[data-baseweb="select"] > div {
    background-color: #161B22 !important;
    border: 1px solid #30363D !important;
    color: #E6EDF3 !important;
    font-family: 'Montserrat', sans-serif !important;
}

/* ── buttons ── */
.stDownloadButton > button, .stButton > button {
    background-color: #1F6FEB !important;
    color: white !important;
    border: none !important;
    border-radius: 6px !important;
    font-family: 'Montserrat', sans-serif !important;
    font-weight: 600 !important;
}
.stDownloadButton > button:hover, .stButton > button:hover {
    background-color: #388BFD !important;
}

/* ── file uploader ── */
[data-testid="stFileUploader"] {
    background-color: #161B22 !important;
    border: 1px dashed #30363D !important;
    border-radius: 8px !important;
}

/* ── info / success / warning boxes ── */
[data-testid="stAlert"] { border-radius: 8px !important; }

/* plotly chart transparent bg */
.js-plotly-plot .plotly { background: transparent !important; }
</style>
"""

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
def sidebar_data():
    uploaded_files = st.sidebar.file_uploader(
        "Upload data", accept_multiple_files=True, label_visibility="visible"
    )
    st.session_state.uploaded_files = uploaded_files




def Data_Management():
    st.title("Data Management")
    show_old_new_file()
    download_new_file()










indicator_1a_pedagogy = [
    "PPR EC-12",
    "PPR EC-4",
    "PPR 8-12",
    "PPR EC-6",
    "PPR 4-8"
]

indicator_1b_content = [
    "Physical Education EC-12",
    "Principal",
    "Core Sub EC-6 Science",
    "Core Sub EC-6 Soc Studies",
    "Core Sub EC-6 ELAR/STR",
    "Core Sub EC-6 Math",
    "Core Sub EC-6 FA/Hlth/PE",
    "ESL Supp",
    "Generalist EC-4",
    "History 8-12",
    "Generalist EC-6",
    "Mathematics 7-12",
    "Music EC-12",
    "Generalist 4-8",
    "ELAR/Soc Studies 4-8",
    "ELAR 7-12",
    "Art All Level",
    "Reading Specialist",
    "Core Sub EC-6 ELAR",
    "BTLPT - Spanish",
    "Science of Teaching Reading",
    "Bilingual Education Supp",
    "Science 4-8",
    "History 7-12",
    "TOPT-Spanish",
    "Bilingual Generalist EC-4",
    "Special Education EC-12",
    "School Counselor",
    "Social Studies 7-12",
    "Bilingual Generalist EC-6",
    "SPED SP EC-12",
    "Superintendent",
    "ESL/Generalist EC-6",
    "Art EC-12",
    "ELAR 8-12",
    "Mathematics/Science 4-8",
    "Life Science 8-12",
    "Physics/Math 7-12",
    "Mathematics 8-12",
    "Science 7-12",
    "Superintendent Parts I-II",
    "TX PACT: ELAR 4-8",
    "Life Science 7-12",
    "PHYSICAL EDUCATION EC-12",
    "Special Education Supp",
    "Principal Pilot",
    "TX PACT: EAS (Subtest III: Math)",
    "TX PACT: EAS (Subtest II: Writing)",
    "TX PACT: EAS (Subtest I Reading)",
    "Chemistry 7-12",
    "TX PACT: Music EC-12",
    "TX PACT: Social Studies 7-12",
    "Spanish 6-12",
    "TX PACT: ELAR 7-12",
    "TX PACT: Mathematics 4-8",
    "Social Studies 4-8",
    "LOTE-Spanish EC-12",
    "Speech 7-12",
    "Master Reading Teacher",
    "Speech 8-12",
    "ELAR 4-8",
    "Journalism 8-12",
    "TX PACT: Health EC 12",
    "Theatre EC-12",
    "TX PACT: Art EC-12",
    "Mathematics 4-8",
    "Social Studies 8-12",
    "Physical Science 8-12",
    "Master Tech Teacher EC-12",
    "TX PACT: Theatre EC-12",
    "Core Sub 4-8 Soc Studies",
    "Core Sub 4-8 Science",
    "Core Sub 4-8 ELAR",
    "Core Sub 4-8 Math",
    "Chemistry 8-12",
    "Physical Science 6-12",
    "TX PACT: History 7-12",
    "Science 8-12",
    "TX PACT: Physics 7-12",
    "TX PACT: Mathematics 7-12",
    "TX PACT: Life Science 7-12",
    "Gifted and Talented Supp",
    "TX PACT: Science 4-8",
    "TOPT-French",
    "French 6-12",
    "TX PACT: LOTE Spanish EC-12",
    "TX PACT: Physical Ed EC-12",
    "LOTE-French EC-12",
    "German 6-12",
    "TX PACT: Core Subjects 4-8",
    "TX PACT: Computer Science 8-12",
    "TX PACT: Chemistry 7–12",
    "TX PACT: Speech 7-12"
]

        

@st.cache_data
def prepare_chapter_7(new_teacher_survey_df, educator_df):
    merged = merge_both_df(new_teacher_survey_df, educator_df)
    merged = get_asep_consolidated_data(merged)
    merged = verify_certificate(merged)
    merged = missing_required_sections(merged)
    merged = remove_duplicates(merged)
    return merged

def new_teacher(new_teacher_survey_df, educator_details_df):
    merged = prepare_chapter_7(new_teacher_survey_df, educator_details_df)

    available_cohort_options = sorted(merged["Admission Cohort"].unique().astype(int).tolist())
    available_employment_options = sorted(merged['Employment Date'].dt.year.astype(int).unique().tolist())

    if "chapter_7_cohort_filter" not in st.session_state:
        st.session_state.chapter_7_cohort_filter = available_cohort_options  # Or [2019, 2020, 2021] depending on your default target
        
    if "chapter_7_gender_filter" not in st.session_state:
        st.session_state.chapter_7_gender_filter = "All"

    if "chapter_7_employment_date" not in st.session_state:
        st.session_state.chapter_7_employment_date = available_employment_options


    # # ── Filters ──
    st.subheader("🔍 Filter Options")
    filter_col1, filter_col2, filter_col3 = st.columns(3)
    
    with filter_col1:
        gender_selected = st.selectbox(
            "Gender",
            options=["All"] + sorted(merged["Gender"].unique().tolist()),
            key="chapter_7_gender_select",
        )
        st.session_state.chapter_7_gender_filter = gender_selected

    with filter_col2:
        admission_cohort = st.multiselect(
            "Admission Cohort Year",
            options=available_cohort_options,
            default=st.session_state.chapter_7_cohort_filter,
            key="chapter_7_cohort_select",
        )
        
        # If the user changes selection, trigger a rerun so the preprocessor runs with new years
        if admission_cohort != st.session_state.chapter_7_cohort_filter:
            st.session_state.chapter_7_cohort_filter = admission_cohort
            # st.rerun()

    with filter_col3:
        employment_date_selected = st.selectbox(
            "Employment Date",
            options=available_employment_options,
            # default=st.session_state.chapter_7_employment_date,
            key="chapter_7_emp_date_select"
        )

        if employment_date_selected != st.session_state.chapter_7_employment_date:
            st.session_state.chapter_7_employment_date = employment_date_selected

    filtered_copy_df = merged.copy()
    if gender_selected != "All":
        filtered_copy_df = filtered_copy_df[filtered_copy_df["Gender"] == gender_selected]
    if admission_cohort:
        filtered_copy_df = filtered_copy_df[filtered_copy_df["Admission Cohort"].isin(admission_cohort)]
    filtered_copy_df = first_year_status(filtered_copy_df, st.session_state.chapter_7_employment_date)


    filtered_copy_df, years_checked, total_records = chapter_4_group_aggregration(filtered_copy_df, employment_date_selected)
    # if years_checked > 1 and total_records > 0:
    st.info(
        f"ℹ️ **Small Group Aggregation Applied:** Initial cohort was under 10. "
        f"Aggregated data across {years_checked} consecutive years. "
        f"Total evaluation sample size: **{total_records}**."
    )

    # st.write('len of filtered data is ', len(filtered_copy_df))
    if total_records != 0:
        chapter_4_chart(filtered_copy_df, 0)
    else:
        st.info('Select Other Year No Record Found')

    return merged












def asep_index_score(first_two_attempt_data_1a_data, first_two_attempt_data_1b_data, principal_dataset, teacher_survey_dataset, student_growth_data, field_supervision_dataset, principal_year_total):
    year_filter = 2023  
    content_pedagogy_tests_name = "All" # Also can choose All if needed

    columns = [
        "ASEP Measure", 
        "All", 
        "Female", 
        "Male", 
        "African American", 
        "Hispanic / Latino", 
        "Other", 
        "White"
    ]
    asep_df = pd.DataFrame(columns=columns)

    # For Chapter3: indicator 1a
    combined_df_1a, year_taken_1a = indicator_1a_data(first_two_attempt_data_1a_data, year_filter=year_filter)

    # st.write(year_taken_1a)

    asep_df.loc[len(asep_df)] = [
        "1a: Certification examination results for pedagogy tests ", # ASEP Measure
        calculate_asep_indicator_1a(combined_df_1a, year_taken_1a)['year_taken'],                              # All
        calculate_asep_indicator_1a(combined_df_1a[combined_df_1a['Gender'] == 'Female'], year_taken_1a)['year_taken'],                              # Female
        calculate_asep_indicator_1a(combined_df_1a[combined_df_1a['Gender'] == 'Male'], year_taken_1a)['year_taken'],                              # Male
        calculate_asep_indicator_1a(combined_df_1a[combined_df_1a['Race/Ethnicity'] == 'Black - African American'], year_taken_1a)['year_taken'],                              # African American
        calculate_asep_indicator_1a(combined_df_1a[combined_df_1a['Race/Ethnicity'] == 'Hispanic - Latino'], year_taken_1a)['year_taken'],                              # Hispanic / Latino
        calculate_asep_indicator_1a(combined_df_1a[~combined_df_1a['Race/Ethnicity'].isin(['Black - African American', 'Hispanic - Latino', 'White'])], year_taken_1a)['year_taken'],                              # Other
        calculate_asep_indicator_1a(combined_df_1a[combined_df_1a['Race/Ethnicity'] == 'White'], year_taken_1a)['year_taken']                               # White
    ]

    # # For Chapter3: indicator 1b
    # combined_df_1b, year_taken = indicator_1b_data(first_two_attempt_data_1b_data, year_filter=year_filter, exam_name_filter=content_pedagogy_tests_name)

    # asep_df.loc[len(asep_df)] = [
    #     "1b: Certification examination results for content pedagogy tests ", # ASEP Measure
    #     calculate_asep_indicator_1a(combined_df_1b)['Indicator 1a Pass Rate (%)'],                              # All
    #     calculate_asep_indicator_1a(combined_df_1b[combined_df_1b['Gender'] == 'Female'])['Indicator 1a Pass Rate (%)'],                              # Female
    #     calculate_asep_indicator_1a(combined_df_1b[combined_df_1b['Gender'] == 'Male'])['Indicator 1a Pass Rate (%)'],                              # Male
    #     calculate_asep_indicator_1a(combined_df_1b[combined_df_1b['Race/Ethnicity'] == 'Black - African American'])['Indicator 1a Pass Rate (%)'],                              # African American
    #     calculate_asep_indicator_1a(combined_df_1b[combined_df_1b['Race/Ethnicity'] == 'Hispanic - Latino'])['Indicator 1a Pass Rate (%)'],                              # Hispanic / Latino
    #     calculate_asep_indicator_1a(combined_df_1b[~combined_df_1b['Race/Ethnicity'].isin(['Black - African American', 'Hispanic - Latino', 'White'])])['Indicator 1a Pass Rate (%)'],                              # Other
    #     calculate_asep_indicator_1a(combined_df_1b[combined_df_1b['Race/Ethnicity'] == 'White'])['Indicator 1a Pass Rate (%)']                               # White
    # ]

    
    # For Chapter 4:  Score should be 70% to sufficiently prepared 

    filtered_copy_df, years_checked, total_records = chapter_4_group_aggregration(principal_dataset, year_filter)

    asep_df.loc[len(asep_df)] = [
    "Chapter 4 – Appraisal of First-Year Teachers by Administrators (Principal Survey)", # ASEP Measure
    chapter_4_survey_summary(filtered_copy_df, principal_year_total)['value'],                              # All
    chapter_4_survey_summary(filtered_copy_df[filtered_copy_df['Gender'] == 'Female'], principal_year_total)['value'],                              # Female
    chapter_4_survey_summary(filtered_copy_df[filtered_copy_df['Gender'] == 'Male'], principal_year_total)['value'],                              # Male
    chapter_4_survey_summary(filtered_copy_df[filtered_copy_df['Race/Ethnicity'] == 'Black - African American'], principal_year_total)['value'],                              # African American
    chapter_4_survey_summary(filtered_copy_df[filtered_copy_df['Race/Ethnicity'] == 'Hispanic - Latino'], principal_year_total)['value'],                              # Hispanic / Latino
    chapter_4_survey_summary(filtered_copy_df[~filtered_copy_df['Race/Ethnicity'].isin(['Black - African American', 'Hispanic - Latino', 'White'])], principal_year_total)['value'],                              # Other
    chapter_4_survey_summary(filtered_copy_df[filtered_copy_df['Race/Ethnicity'] == 'White'], principal_year_total)['value']                               # White
    ]


    # For Chapter 5: 2024-2025 and 2025-2026 academic years, the performance standard shall be 60%, 2026-2027 academic year, the performance standard shall be 65%, 2027-2028 academic year, the performance standard shall be 70%

    student_growth_data = student_growth_data[student_growth_data["Data Year"] == year_filter]

    asep_df.loc[len(asep_df)] = [
    "Chapter 5 – Improvement in Student Achievement of Students Taught by Beginning Teachers", # ASEP Measure
    chapter_5_summary(student_growth_data)['pct_meeting_standard'],                              # All
    chapter_5_summary(student_growth_data[student_growth_data['Gender_x'] == 'Female'])['pct_meeting_standard'],                              # Female
    chapter_5_summary(student_growth_data[student_growth_data['Gender_x'] == 'Male'])['pct_meeting_standard'],                              # Male
    chapter_5_summary(student_growth_data[student_growth_data['Race/Ethnicity'] == 'Black - African American'])['pct_meeting_standard'],                              # African American
    chapter_5_summary(student_growth_data[student_growth_data['Race/Ethnicity'] == 'Hispanic - Latino'])['pct_meeting_standard'],                              # Hispanic / Latino
    chapter_5_summary(student_growth_data[~student_growth_data['Race/Ethnicity'].isin(['Black - African American', 'Hispanic - Latino', 'White'])])['pct_meeting_standard'],                              # Other
    chapter_5_summary(student_growth_data[student_growth_data['Race/Ethnicity'] == 'White'])['pct_meeting_standard']                               # White
    ]


    # For Chapter 6: Indicator 4a = 95% 19 TAC §229.4(a)(4)

    # Dynamically build the academic year string (e.g., 2026 -> "2025-2026")
    target_academic_year = f"{int(year_filter) - 1}-{year_filter}"

    field_supervision_dataset = field_supervision_dataset[field_supervision_dataset["filter_year"] == target_academic_year]

    # asep_df.loc[len(asep_df)] = [
    # "4a: Frequency and duration of field observations ", # ASEP Measure
    # field_supervision_dataset(field_supervision_dataset)['pct_meeting_standard'],                              # All
    # field_supervision_dataset(field_supervision_dataset[field_supervision_dataset['Gender_x'] == 'Female'])['pct_meeting_standard'],                              # Female
    # field_supervision_dataset(field_supervision_dataset[field_supervision_dataset['Gender_x'] == 'Male'])['pct_meeting_standard'],                              # Male
    # field_supervision_dataset(field_supervision_dataset[field_supervision_dataset['Race/Ethnicity'] == 'Black - African American'])['pct_meeting_standard'],                              # African American
    # field_supervision_dataset(field_supervision_dataset[field_supervision_dataset['Race/Ethnicity'] == 'Hispanic - Latino'])['pct_meeting_standard'],                              # Hispanic / Latino
    # field_supervision_dataset(field_supervision_dataset[~field_supervision_dataset['Race/Ethnicity'].isin(['Black - African American', 'Hispanic - Latino', 'White'])])['pct_meeting_standard'],                              # Other
    # field_supervision_dataset(field_supervision_dataset[field_supervision_dataset['Race/Ethnicity'] == 'White'])['pct_meeting_standard']                               # White
    # ]



    # For Chapter 7:  Score should be 70% to sufficiently prepared 

    filtered_copy_df, years_checked, total_records = chapter_4_group_aggregration(teacher_survey_dataset, year_filter)

    asep_df.loc[len(asep_df)] = [
    "Chapter 7 – Evaluation of Educator Preparation Programs by Teachers (Teacher Survey) ", # ASEP Measure
    chapter_4_survey_summary(filtered_copy_df, principal_year_total)['value'],                              # All
    chapter_4_survey_summary(filtered_copy_df[filtered_copy_df['Gender'] == 'Female'], principal_year_total)['value'],                              # Female
    chapter_4_survey_summary(filtered_copy_df[filtered_copy_df['Gender'] == 'Male'], principal_year_total)['value'],                              # Male
    chapter_4_survey_summary(filtered_copy_df[filtered_copy_df['Race/Ethnicity'] == 'Black - African American'], principal_year_total)['value'],                              # African American
    chapter_4_survey_summary(filtered_copy_df[filtered_copy_df['Race/Ethnicity'] == 'Hispanic - Latino'], principal_year_total)['value'],                              # Hispanic / Latino
    chapter_4_survey_summary(filtered_copy_df[~filtered_copy_df['Race/Ethnicity'].isin(['Black - African American', 'Hispanic - Latino', 'White'])], principal_year_total)['value'],                              # Other
    chapter_4_survey_summary(filtered_copy_df[filtered_copy_df['Race/Ethnicity'] == 'White'], principal_year_total)['value']                               # White
    ]

    st.table(asep_df)




# ─────────────────────────────────────────────
# STUDENT GROWTH TAB
# ─────────────────────────────────────────────
def student_growth_tab(df):
    st.subheader("📚 Indicator 3: Student Growth")
    


# ─────────────────────────────────────────────
# EXAM PASS RATE TAB
# ─────────────────────────────────────────────
def exam_pass_rate_tab(df):
    st.subheader("🏆 Indicator 1: Certification Exam Pass Rates")
    


# ─────────────────────────────────────────────
# DASHBOARD PAGE
# ─────────────────────────────────────────────
def Dashboard():
    st.title("📊 ASEP Metrics Dashboard")
    st.caption(
        "Alternative Student Educator Preparation (ASEP) program metrics — "
        "Certification Pass Rates · Principal Appraisals · Student Growth"
    )

    if not st.session_state.get("uploaded_files"):
        st.warning("Please upload Excel files in the Data Management page first.")
        return

    data = {"principal_perception": None, "educator_details": None, "student_growth": None, "new_teacher_survey": None, "exam_roaster": None, "observation_data": None}
    for uploaded_file in st.session_state.uploaded_files:
        new_name, df = process_and_rename_file(uploaded_file)
        if new_name == "academic_year_principle_perceptions":
            data["principal_perception"] = df
        elif new_name == "educator_details_with_emp_start_date":
            data["educator_details"] = df
        elif new_name == "academic_year_average_student_growth_by_candidate":
            data["student_growth"] = df
        elif new_name == 'new_teacher_perceptions_by_candidate':
            data['new_teacher_survey'] = df
        elif new_name == 'exam_roaster_data':
            data['exam_roaster'] = df
        elif new_name == 'observation_df':
            data['observation_data'] = df

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
        ["Chapter 3", "Chapter 4", "Chapter 5", "Chapter 6", "Chapter 7", "Chapter 8"]
    )
    first_two_attempt_data_1a_data = None 
    first_two_attempt_data_1b_data = None
    principal_dataset = None
    teacher_survey_dataset = None
    field_supervision_dataset = None
    principal_year_total = None
    
    with tab1:
        if data["exam_roaster"] is not None and data['educator_details'] is not None:
            first_two_attempt_data_1a_data, first_two_attempt_data_1b_data, _ = exam_pass_rate(data["exam_roaster"], data["educator_details"])
        else:
            if data["exam_roaster"] is not None:
                st.info("⚠️ Please upload a Educator Details file first.")
            elif data['educator_details'] is not None:
                st.info("⚠️ Please upload a Examinee Roster file first.")


    with tab2:
        if data["principal_perception"] is not None and data['educator_details'] is not None:
            principal_dataset, principal_year_total = principal_perceptions(data["principal_perception"], data["educator_details"])
        else:
            if data["principal_perception"] is not None:
                st.info("⚠️ Please upload a Educator Details file first.")
            elif data['educator_details'] is not None:
                st.info("⚠️ Please upload a Principal Perceptions file first.")

            

    with tab3:
        if data["educator_details"] is not None and data['student_growth'] is not None:
            student_growth_data = student_growth(data["educator_details"], data["student_growth"])
        else:
            if data["educator_details"] is not None:
                st.info("⚠️ Please upload a Student Growth file first.")
            elif data['student_growth'] is not None:
                st.info("⚠️ Please upload a Educator Details file first.")

    with tab4:
        if data['observation_data'] is not None:
            field_supervision_dataset = field_supervision(data['observation_data'])
        else:
            st.info("⚠️ Please upload a Observations Data file first.")

    with tab5:
        if data["new_teacher_survey"] is not None and data['educator_details'] is not None:
            teacher_survey_dataset = new_teacher(data["new_teacher_survey"], data["educator_details"])
        else:
            if data["new_teacher_survey"] is not None:
                st.info("⚠️ Please upload a Educator Details file first.")
            elif data['educator_details'] is not None:
                st.info("⚠️ Please upload a New Teacher Survey file first.")

    with tab6:
        if first_two_attempt_data_1a_data is not None and first_two_attempt_data_1b_data is not None and principal_dataset is not None and teacher_survey_dataset is not None and student_growth_data is not None and field_supervision_dataset is not None and principal_year_total is not None:
            asep_index_score(first_two_attempt_data_1a_data, first_two_attempt_data_1b_data, principal_dataset, teacher_survey_dataset, student_growth_data, field_supervision_dataset, principal_year_total)
            
            # You can now calculate cumulative logic, merge files, or perform 
            # ASEP index score math using these dataframes here.
        else:
            st.info("⚠️ Please ensure the required files are uploaded to populate this tab.")
    


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────
def main():
    st.set_page_config(
        page_title="ASEP Metrics Dashboard",
        layout="wide",
        initial_sidebar_state="expanded",
    )


    sidebar_data()
    pg = st.navigation([Data_Management, Dashboard])
    pg.run()


main()
