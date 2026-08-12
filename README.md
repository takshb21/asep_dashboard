# 📊 ASEP Metrics Dashboard

A Streamlit web application for calculating and visualizing **Alternative Student Educator Preparation (ASEP)** program metrics — built for tracking educator preparation program performance across multiple indicators (certification exams, principal perceptions, student growth, field supervision, teacher surveys) and rolling them up into a final **ASEP Index Score**.

---

## 🧭 Table of Contents

- [Overview](#-overview)
- [Pages](#-pages)
- [Datasets Required](#-datasets-required)
- [Getting Started](#-getting-started)
- [How to Use the App](#-how-to-use-the-app)
- [Project Structure](#-project-structure)
- [Tech Stack](#-tech-stack)
- [Contributing / Feedback](#-contributing--feedback)
- [Credits](#-credits)

---

## 📖 Overview

This dashboard automates the process of calculating ASEP compliance metrics for an Educator Preparation Program (EPP). Instead of manually combining reports from **I2I**, **ECOS**, and **ResultsAnalyzer**, users upload the raw exports directly, and the app:

1. Auto-detects and renames uploaded files based on their structure.
2. Merges and cleans the data per chapter/indicator.
3. Calculates each ASEP indicator (1a, 1b, 2, 3, 4a, 4b, 5).
4. Produces a weighted, demographic-broken-down **ASEP Index Score** with a visual gauge.

---

## 🗂️ Pages

| Page | Description |
|---|---|
| **📁 Data Management** | Upload raw dataset files. The app detects and renames each file automatically so the rest of the dashboard can recognize it. Includes a downloadable PDF guide and renamed-file download option. |
| **📊 Dashboard** | Tabbed view (Chapter 3–8) showing calculated metrics for each ASEP indicator, culminating in the combined ASEP Index Score in Chapter 8. |
| **ℹ️ About Us** | Info about the team, a description of each page, and a step-by-step navigation guide. |
| **💬 Feedback** | Embedded Microsoft Forms widget for reporting bugs, requesting features, or submitting general feedback. |

> The app opens on the **About Us** page by default so new users see the navigation guide first.

---

## 📋 Datasets Required

| Dataset | Source |
|---|---|
| **Educator Details** | I2I → EPP Employment and Retention → Educator Details |
| **Exam Roster** | ResultsAnalyzer → Texas Examinee Data → Examinee Roster |
| **Principal Perception** | I2I → EPP Perception Surveys → New Teacher Perceptions by Candidate (View by Academic Year) |
| **Student Growth** | I2I → EPP Student Growth → Average Student Growth by Candidate |
| **Observation** | ECOS → EPP → ASEP → Observations Report |
| **Finishers** | ECOS → ASEP → Maint Finishers |
| **New Teacher Survey** | I2I → EPP Perception Surveys → New Teacher Perceptions by Candidate |

**Which chapters need which files:**

| Chapter | Required Datasets |
|---|---|
| Chapter 3 | Exam Roster + Educator Details |
| Chapter 4 | Principal Perception + Educator Details |
| Chapter 5 | Educator Details + Student Growth |
| Chapter 6 | Observation + Finishers |
| Chapter 7 | Educator Details + New Teacher Survey |
| Chapter 8 | All datasets |

> ⚠️ **Note:** The Principal Perception dataset and New Teacher Survey dataset come from the *same* I2I report and look identical when exported. Rename them manually before uploading:
> - Principal Perception → `academic_year_principal_perceptions`
> - New Teacher Survey → `new_teacher_perceptions_by_candidate`

---

## 🚀 Getting Started

### Prerequisites
- Python 3.9+
- pip

### Installation

```bash
# Clone the repository
git clone https://github.com/takshb21/asep_dashboard.git
cd asep_dashboard

# (Recommended) Create a virtual environment
python -m venv venv
source venv/bin/activate      # macOS/Linux
venv\Scripts\activate         # Windows

# Install dependencies
pip install -r requirements.txt
```

### Run the App

```bash
streamlit run app.py
```

The app will open automatically in your browser at `http://localhost:8501`.

---

## 🧭 How to Use the App

1. **Go to Data Management** — Upload the required Excel/CSV files for the chapters you need.
2. **Rename before uploading if prompted** — Some files look identical when exported and must be renamed manually first.
3. **Confirm the files were recognized** — The page shows an arrow (➡️) mapping your original file name to the renamed name the app uses internally.
4. **Go to Dashboard** — Each Chapter tab auto-populates once its required datasets are uploaded. A tab showing a warning means a file is still missing.
5. **Check Chapter 8** — View the combined, weighted ASEP Index Score with a color-coded gauge (🟢 ≥85%, 🟡 80–85%, 🔴 <80%).
6. **Use Feedback** — Report issues or request changes anytime through the built-in form.

---

## 🗄️ Project Structure

```
.
├── app.py                          # Main Streamlit app (navigation, pages, ASEP score calculation)
├── utils/
│   ├── data_management.py          # File upload, renaming, and download helpers
│   ├── chapter_3_calculations.py   # Indicator 1a/1b: exam pass rate calculations
│   ├── chapter_4_calculations.py   # Indicator 2: principal perception survey calculations
│   ├── chapter_5_calculations.py   # Indicator 3: student growth calculations
│   ├── chapter_6_calculations.py   # Indicator 4a/4b: field supervision calculations
│   ├── chapter_7_calculations.py   # Indicator 5: new teacher survey calculations
│   └── dataset_download_info.pdf   # Step-by-step dataset download guide
├── images/
│   └── company_logo.png            # Logo shown on the About Us page
└── requirements.txt
```

---

## 💬 Contributing / Feedback

Found a bug or have a feature request? Use the **Feedback** page inside the app, or open an issue in this repository.

---

## 🎓 Credits

**Built by:**
- Taksh Beladiya
- Jeremy Martin
- Badgett Kevin
- Marder Michael P.
- Michelle Lowry

**Special thanks** to the **University of Texas at Arlington** for their partnership and support in making this project possible.
