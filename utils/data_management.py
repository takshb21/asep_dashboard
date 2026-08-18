# ─────────────────────────────────────────────
# FILE PROCESSING
# ─────────────────────────────────────────────
import pandas as pd
import streamlit as st
import io

import re

# ─────────────────────────────────────────────
# FINISHER FILE DETECTION + READING
# ─────────────────────────────────────────────
FINISHER_COLUMNS = [
    'TEA ID',
    'SSN',
    'First Name',
    'Middle Name',
    'Last Name',
    'Cert Code',
    'Cert Description',
    'Program Type',
    'Gender',
    'Ethnicity',
    'Status',
]


def is_finisher_file(uploaded_file) -> bool:
    """Peek at the file's real header row (row 3, i.e. skiprows=2) to see
    if it matches the SBEC ASEP Finisher schema."""
    uploaded_file.seek(0)
    try:
        if uploaded_file.name.lower().endswith('.csv'):
            df_check = pd.read_csv(uploaded_file, skiprows=2, nrows=0)
        else:
            df_check = pd.read_excel(uploaded_file, skiprows=2, nrows=0, engine='calamine')
    except Exception:
        uploaded_file.seek(0)
        return False
    uploaded_file.seek(0)
    cols_check = sorted([str(c).strip() for c in df_check.columns])
    return cols_check == sorted(FINISHER_COLUMNS)


def read_finisher_file(uploaded_file) -> pd.DataFrame:
    """Extracts 'Data year' from row 1 and parses the table starting after
    the header row (skiprows=2), same logic as your standalone script."""
    is_csv = uploaded_file.name.lower().endswith('.csv')

    # 1. Extract the year from the first cell of row 1
    uploaded_file.seek(0)
    if is_csv:
        header_text_df = pd.read_csv(uploaded_file, nrows=1, header=None)
    else:
        header_text_df = pd.read_excel(uploaded_file, nrows=1, header=None, engine='calamine')

    first_cell_value = str(header_text_df.iloc[0, 0])
    year_match = re.search(r'(\d{4})', first_cell_value, re.IGNORECASE)
    data_year = int(year_match.group(1)) if year_match else None

    # 2. Read the actual table (headers on row 3 -> skiprows=2)
    uploaded_file.seek(0)
    if is_csv:
        df = pd.read_csv(uploaded_file, skiprows=2)
    else:
        df = pd.read_excel(uploaded_file, skiprows=2, engine='calamine')

    df.columns = [str(col).strip() for col in df.columns]

    if 'TEA ID' in df.columns:
        df = df[df['TEA ID'].notna()].copy()

    # 3. Tag each row with its source year
    df['Data year'] = data_year
    return df


def process_and_rename_file(uploaded_file):
    index_name = [
        'Field Supervisor Last Name',
        'Field Supervisor First Name',
        'Assignment Begin Date',
        'Candidate TEA ID',
        'Candidate Last Name',
        'Candidate First Name',
        'Visit Date',
        'Duration Hours',
        'Comments',
        'Field Supervisor TEA ID',
        'Assignment Type',
        'Experience Model',
        'Assignment End Date',
        'Observation Setting',
        'Total Points',
    ]

    uploaded_file.seek(0)

    # 0. Finisher files: special layout (year in row1, header on row3),
    #    and multiple year-files roll up into one combined dataset.
    if is_finisher_file(uploaded_file):
        df = read_finisher_file(uploaded_file)
        new_name = 'main_finisher_data'
        return new_name, df

    # Read the file based on extension
    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file, skiprows=10)
        df.columns = index_name
    else:
        df = pd.read_excel(uploaded_file, skipfooter=2, engine='calamine')

    # Convert DataFrame columns to a sorted list for reliable comparison
    cols = sorted([str(col).strip() for col in df.columns])

    # 1. Handle Manual Collisions First (Same columns in both files)
    if 'principal_perceptions' in uploaded_file.name.lower():
        new_name = 'principal_perceptions'
    elif 'teacher_perceptions' in uploaded_file.name.lower():
        new_name = 'teacher_perceptions'

    # 2. Schema-Based Auto-Matching for all other unique datasets
    elif cols == sorted([
        'TEA ID',
        'Employment Date',
        'Certification Type',
        'Name',
        'Race/Ethnicity',
        'Gender',
        'Certification Date',
        'Position',
        'District',
        'Campus',
        'Title I Designation',
        'Certification Grade Level',
        'Certification Subject Area',
        'Teaching Grade Level',
        'Teaching Subject Area',
    ]):
        new_name = 'educator_details_with_emp_start_date'

    elif cols == sorted([
        'TEA ID',
        'First Name',
        'Last Name',
        'Finisher Year',
        'Gender',
        'Race/ Ethnicity',
        'Certification Area Grade Level',
        'Year of Teaching',
        'Data Year',
        'Overall Student Growth Score',
        'Mathematics Student Growth Score',
        'Mathematics N',
        'English/ Reading Student Growth Score',
        'English/ Reading N',
    ]):
        new_name = 'academic_year_average_student_growth_by_candidate'

    elif cols == sorted([
        'Examinee Name',
        'TEAID',
        'Exam Name',
        'Exam Code',
        'Exam Version',
        'Exam Date',
        'P/F Status',
        'Reporting Type',
        'Score Report Finder',
    ]):
        new_name = 'exam_roaster_data'

    elif cols == sorted(index_name):
        new_name = 'observation_df'

    # 3. Fallback to original name if schema is unrecognized
    else:
        new_name = uploaded_file.name

    return new_name, df


# ─────────────────────────────────────────────
# GROUPING / MERGING LOGIC
# ─────────────────────────────────────────────
def get_grouped_dataframes():
    """Processes all uploaded files, then groups by output name. Any name
    with more than one file behind it (e.g. multiple Finisher-list years)
    gets concatenated into a single combined DataFrame."""
    uploaded_files = st.session_state.get("uploaded_files", [])
    grouped = {}
    for uploaded_file in uploaded_files:
        new_name, df = process_and_rename_file(uploaded_file)
        grouped.setdefault(new_name, []).append(df)

    merged = {}
    for name, dfs in grouped.items():
        merged[name] = pd.concat(dfs, ignore_index=True) if len(dfs) > 1 else dfs[0]
    return merged


# ─────────────────────────────────────────────
# DATA MANAGEMENT PAGE
# ─────────────────────────────────────────────
def show_old_new_file():
    uploaded_files = st.session_state.get("uploaded_files", [])
    if not uploaded_files:
        st.write("Upload your Files First")
    else:
        for uploaded_file in uploaded_files:
            new_name, _ = process_and_rename_file(uploaded_file)
            col1, col2, col3 = st.columns([4, 1, 4])
            with col1:
                st.info(f"{uploaded_file.name}")
            with col2:
                st.markdown(
                    "<h2 style='text-align:center;margin-top:-10px;color:#E6EDF3;'>→</h2>",
                    unsafe_allow_html=True,
                )
            with col3:
                st.success(f"{new_name}")


def download_new_file():
    uploaded_files = st.session_state.get("uploaded_files", [])
    if uploaded_files:
        st.subheader("Download file")
        grouped = get_grouped_dataframes()  # merges same-name files (e.g. Finisher years)
        for idx, (new_name, df) in enumerate(grouped.items()):
            buffer = io.BytesIO()
            file_name = new_name if new_name.endswith(('.csv', '.xlsx')) else f"{new_name}.csv"
            if file_name.endswith(".csv"):
                csv_data = df.to_csv(index=False).encode("utf-8")
                st.download_button(
                    label=f"Download {file_name}",
                    data=csv_data,
                    file_name=file_name,
                    mime="text/csv",
                    key=f"dl_{idx}_{file_name}",
                )
            else:
                with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
                    df.to_excel(writer, index=False, sheet_name="Sheet1")
                st.download_button(
                    label=f"Download {file_name}",
                    data=buffer.getvalue(),
                    file_name=file_name,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key=f"dl_{idx}_{file_name}",
                )
