# ─────────────────────────────────────────────
# FILE PROCESSING
# ─────────────────────────────────────────────
import pandas as pd
import streamlit as st
import io


def process_and_rename_file(uploaded_file):
    index_name = ['Field Supervisor Last Name', 'Field Supervisor First Name',
       'Assignment Begin Date', 'Candidate TEA ID', 'Candidate Last Name',
       'Candidate First Name', 'Visit Date', 'Duration Hours', 'Comments',
       'Field Supervisor TEA ID', 'Assignment Type', 'Experience Model',
       'Assignment End Date', 'Observation Setting', 'Total Points']
    
    uploaded_file.seek(0) 
    # df = pd.read_excel(uploaded_file, skipfooter= 2)

    # Check file extension to read correctly
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file, skiprows=10)
        df.columns = index_name
    else:
        df = pd.read_excel(uploaded_file, skipfooter=2)

    if uploaded_file.name == 'academic_year_principle_perceptions.xlsx':
        new_name = "academic_year_principle_perceptions"
    elif uploaded_file.name == 'educator_details_with_emp_start_date.xlsx':
        new_name = 'educator_details_with_emp_start_date'
    elif uploaded_file.name == 'academic_year_average_student_growth_by_candidate.xlsx':
        new_name = 'academic_year_average_student_growth_by_candidate'
    elif uploaded_file.name == 'new_teacher_perceptions_by_candidate.xlsx':
        new_name = 'new_teacher_perceptions_by_candidate'
    elif uploaded_file.name == 'Examinee Roster.xlsx':
        new_name = 'exam_roaster_data'
    elif uploaded_file.name == "epp_observations_report_134267067791026568.csv":
        new_name = "observation_df"
    else:
        new_name = uploaded_file.name

    return new_name, df

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
        for idx, uploaded_file in enumerate(uploaded_files):
            new_name, df = process_and_rename_file(uploaded_file)
            buffer = io.BytesIO()
            # Handle downloads based on file type
            if new_name.endswith(".csv"):
                csv_data = df.to_csv(index=False).encode("utf-8")
                st.download_button(
                    label=f"Download {new_name}",
                    data=csv_data,
                    file_name=new_name,
                    mime="text/csv",
                    key=f"dl_{idx}_{uploaded_file.name}",
                )
            else:
                with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
                    df.to_excel(writer, index=False, sheet_name="Sheet1")
                st.download_button(
                    label=f"Download {new_name}",
                    data=buffer.getvalue(),
                    file_name=new_name,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key=f"dl_{idx}_{uploaded_file.name}",
                )