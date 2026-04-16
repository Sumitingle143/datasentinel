import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO
from autofix import auto_fix
from validator import data_quality_report

st.set_page_config(page_title="DataSentinel Pro", layout="wide")

# ================= SESSION STATE =================
if "cleaned_df" not in st.session_state:
    st.session_state.cleaned_df = None

# ================= SIDEBAR =================
st.sidebar.title("⚙️ Settings")

theme = st.sidebar.radio("🎨 Theme", ["Light", "Dark"])

if theme == "Dark":
    st.markdown("""
    <style>
    body {background-color: #0E1117; color: white;}
    </style>
    """, unsafe_allow_html=True)

# ================= TITLE =================
st.title("🧠 DataSentinel Pro Dashboard")

# ================= FILE LOAD =================
def load_file(file):
    name = file.name.lower()

    if name.endswith(".xlsx") or name.endswith(".xls"):
        return pd.read_excel(file)

    encodings = ['utf-8', 'latin1', 'ISO-8859-1', 'cp1252']

    for enc in encodings:
        try:
            file.seek(0)
            return pd.read_csv(file, encoding=enc)
        except:
            continue

    raise ValueError("File not supported")

# ================= UPLOAD =================
file = st.file_uploader("📂 Upload Dataset", type=["csv","xlsx"])

if file:

    original_df = load_file(file)
    filtered_df = original_df.copy()

    st.success(f"✅ Loaded Dataset: {original_df.shape}")

    # ================= FILTER =================
    st.sidebar.subheader("🔍 Filters")

    selected_column = st.sidebar.selectbox("Select Column", filtered_df.columns)

    if filtered_df[selected_column].dtype == "object":
        unique_vals = filtered_df[selected_column].dropna().unique()
        selected_vals = st.sidebar.multiselect("Select Values", unique_vals)

        if selected_vals:
            filtered_df = filtered_df[filtered_df[selected_column].isin(selected_vals)]

    # ================= METRICS =================
    st.subheader("📊 Data Quality Metrics")

    report = data_quality_report(filtered_df)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Missing %", report["Missing %"])
    col2.metric("Duplicates %", report["Duplicate Rows %"])
    col3.metric("Negative %", report["Negative Values %"])
    col4.metric("Clean Score %", report["Clean Data Score %"])

    st.progress(int(report["Clean Data Score %"]))

    # ================= PREVIEW =================
    st.subheader("📄 Data Preview")

    selected_cols = st.multiselect(
        "Select Columns",
        filtered_df.columns,
        default=filtered_df.columns[:5]
    )

    st.dataframe(filtered_df[selected_cols].head(20))

    # ================= RAW BOXPLOT =================
    st.subheader("📦 Outliers (Before Cleaning)")

    num_cols = filtered_df.select_dtypes(include=np.number).columns

    if len(num_cols) > 0:
        col_choice_raw = st.selectbox("Raw Column", num_cols, key="raw_col")

        data_raw = filtered_df[col_choice_raw].dropna()

        if len(data_raw) > 0:
            fig_raw = plt.figure(figsize=(4,3))
            plt.boxplot(data_raw)
            plt.title(f"Raw: {col_choice_raw}")
            st.pyplot(fig_raw)

    # ================= CLEAN OPTIONS =================
    remove_outlier = st.checkbox("Handle Outliers (IQR Capping)")

    # ================= CLEAN BUTTON =================
    if st.button("🚀 Clean Data"):
        st.session_state.cleaned_df = auto_fix(filtered_df.copy(), remove_outlier)

    # ================= USE CLEANED =================
    if st.session_state.cleaned_df is not None:

        cleaned_df = st.session_state.cleaned_df

        st.subheader("✅ Cleaned Data")
        st.dataframe(cleaned_df.head(20))

        # ================= CLEANED BOXPLOT =================
        st.subheader("📦 Outliers (After Cleaning)")

        num_cols_clean = cleaned_df.select_dtypes(include=np.number).columns

        if len(num_cols_clean) > 0:
            col_choice_clean = st.selectbox("Cleaned Column", num_cols_clean, key="clean_col")

            data_clean = cleaned_df[col_choice_clean].dropna()

            if len(data_clean) > 0:
                fig_clean = plt.figure(figsize=(4,3))
                plt.boxplot(data_clean)
                plt.title(f"Cleaned: {col_choice_clean}")
                st.pyplot(fig_clean)

        # ================= IMPACT =================
        st.subheader("📉 Cleaning Impact")

        before = filtered_df.isnull().sum().sum()
        after = cleaned_df.isnull().sum().sum()

        fig2 = plt.figure(figsize=(4,3))
        plt.bar(["Before", "After"], [before, after])
        st.pyplot(fig2)

        # ================= DOWNLOAD =================
        output = BytesIO()
        cleaned_df.to_excel(output, index=False)
        output.seek(0)

        st.download_button(
            "📥 Download Cleaned Data",
            output,
            "cleaned_data.xlsx"
        )