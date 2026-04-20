import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import seaborn as sns
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pipeline.loader import load_file
from pipeline.preprocess import preprocess_data
from pipeline.transformers import apply_pattern_transformers
from pipeline.cleaner import (
    clean_data,
    auto_convert_types,
    smart_detect_column_types
)
from pipeline.outliers import cap_outliers_iqr, remove_outliers_iqr
from pipeline.utils import (
    data_quality_score,
    generate_suggestions,
    column_confidence,
    detect_patterns,
    load_pipeline_config,
    save_pipeline_config
)


st.set_page_config(page_title="CSV Cleaner", layout="wide")

# ===============================
# TITLE
# ===============================

st.title("📊 Smart CSV Cleaner & Analyzer")

# ===============================
# FILE UPLOAD
# ===============================

uploaded_file = st.file_uploader(
    "Upload your dataset",
    type=["csv", "xlsx", "xls", "json", "txt", "docx"],
    key="main_file_uploader"
)

if uploaded_file:

    df = load_file(uploaded_file)

    if df is None or df.empty:
        st.error("Could not load data properly.")
        st.stop()

    # Step 1: preprocess
    df = preprocess_data(df)
    df = apply_pattern_transformers(df)

    # Step 2: detect types
    col_types = smart_detect_column_types(df)

    # Step 3: auto convert
    df = auto_convert_types(df, col_types)

    st.info(f"Loaded file type: {uploaded_file.name.split('.')[-1].upper()}")
    
    st.subheader("🔍 Raw Data Preview")
    st.dataframe(df.astype(object).head())

    st.write("Detected dtypes:")
    st.write(df.dtypes)

    # -------------------------------
    # BASIC INFO
    # -------------------------------
    st.subheader("📌 Dataset Info")

    col1, col2 = st.columns(2)

    with col1:
        st.write("Shape:", df.shape)
        st.write("Duplicates:", df.duplicated().sum())

    with col2:
        st.write("Missing Values:")
        missing_percent = (df.isnull().sum() / len(df)) * 100
        st.write(pd.DataFrame({
            "Missing Count": df.isnull().sum(),
            "Missing %": missing_percent.round(2)
        }))

    st.subheader("📊 Data Quality Score")

    score = data_quality_score(df)

    st.metric(label="Quality Score", value=f"{score}%")

    if score > 80:
        st.success("High quality dataset ✅")
    elif score > 60:
        st.warning("Moderate quality dataset ⚠️")
    else:
        st.error("Low quality dataset ❌")

    # -------------------------------
    # COLUMN TYPES
    # -------------------------------

    st.subheader("📂 Column Types")
    st.json(col_types)

    st.subheader("🧠 Column Intelligence")

    for col in df.columns:
        col_data = df[col]

        info = {
            "dtype": str(col_data.dtype),
            "missing %": round(col_data.isnull().mean() * 100, 2),
            "unique": col_data.nunique()
        }

        if pd.api.types.is_numeric_dtype(col_data):
            info["skew"] = round(col_data.skew(), 2)

        st.write(f"🔹 {col}", info)

    st.subheader("📊 Column Confidence")

    for col in df.columns:
        score = column_confidence(df[col])
        st.write(f"{col}: {score}% numeric")

    st.subheader("🔍 Pattern Detection")

    for col in df.columns:
        pattern = detect_patterns(df[col])
        if pattern:
            st.info(f"{col} → detected pattern: {pattern}")

    st.subheader("🤖 Smart Suggestions")

    suggestions = generate_suggestions(df)

    if suggestions:
        for s in suggestions:
            st.warning(s)
    else:
        st.success("No major issues detected 🎉")
    
    # -------------------------------
    # USER CONTROLS
    # -------------------------------
    st.subheader("⚙️ Cleaning Options")

    drop_cols = st.multiselect(
        "Select columns to drop",
        df.columns
    )

    dup_cols = st.multiselect(
        "Select columns for duplicate detection",
        df.columns
    )
    
    null_strategy = st.selectbox(
        "Select null handling for numeric columns",
        ["Auto", "Mean", "Median"]
    )

    outlier_strategy = st.selectbox(
        "Outlier handling",
        ["None", "Cap with IQR", "Remove with IQR"]
    )

    apply_saved_pipeline = st.checkbox("Apply saved pipeline if available")


    pipeline_config = None
    if apply_saved_pipeline:
        pipeline_config = load_pipeline_config()
        if pipeline_config:
            drop_cols = pipeline_config.get("drop_cols", drop_cols)
            null_strategy = pipeline_config.get("null_strategy", null_strategy)
            outlier_strategy = pipeline_config.get("outlier_strategy", outlier_strategy)
            st.success("Saved pipeline loaded.")
        else:
            st.warning("No saved pipeline found.")

    # ===============================
    # CLEAN BUTTON
    # ===============================
    if st.button("🚀 Clean Data"):

        cleaned_df = clean_data(df, col_types, drop_cols, null_strategy, dup_cols)

        # Re-detect types after filling
        #new_col_types = smart_detect_column_types(cleaned_df)

        # 🔥 Recalculate column types after cleaning
        new_col_types = {
            "numerical": cleaned_df.select_dtypes(include=[np.number, "bool"]).columns.tolist(),
            "categorical": cleaned_df.select_dtypes(exclude=[np.number, "bool"]).columns.tolist()
        }

        # Re-apply conversions
        cleaned_df = auto_convert_types(cleaned_df, new_col_types)

        # Outlier handling
        if outlier_strategy == "Cap with IQR":
            for col in new_col_types["numerical"]:
                cleaned_df[col] = cap_outliers_iqr(cleaned_df[col])

        elif outlier_strategy == "Remove with IQR":
            cleaned_df = remove_outliers_iqr(cleaned_df, new_col_types["numerical"])
            cleaned_df.reset_index(drop=True, inplace=True)
            new_col_types = {
                "numerical": cleaned_df.select_dtypes(include=[np.number, "bool"]).columns.tolist(),
                "categorical": cleaned_df.select_dtypes(exclude=[np.number, "bool"]).columns.tolist()
            }

        # Save pipeline config
        pipeline_to_save = {
            "drop_cols": drop_cols,
            "null_strategy": null_strategy,
            "outlier_strategy": outlier_strategy
        }
        save_pipeline_config(pipeline_to_save)

        st.write("Column dtypes with type info:")
        for col in cleaned_df.columns:
            st.write(col, str(cleaned_df[col].dtype))

        valid_num_cols = [c for c in new_col_types["numerical"] if c in cleaned_df.columns]
        valid_cat_cols = [c for c in new_col_types["categorical"] if c in cleaned_df.columns]

        st.subheader("✅ Cleaned Data Preview")
        st.dataframe(cleaned_df.astype(object).head())

        st.subheader("📊 Numerical Statistics")
        if valid_num_cols:
            st.write(cleaned_df[valid_num_cols].describe())
        else:
            st.warning("No numerical columns available after cleaning.")

        st.subheader("📊 Categorical Summary")
        for col in valid_cat_cols[:3]:
            st.write(f"Top values in {col}")
            st.write(cleaned_df[col].value_counts().head())

        st.subheader("📈 Visualizations")

        for col in valid_num_cols[:2]:
            fig, ax = plt.subplots()
            cleaned_df[col].hist(ax=ax)
            ax.set_title(f"Distribution of {col}")
            st.pyplot(fig)

        for col in valid_cat_cols[:2]:
            fig, ax = plt.subplots()
            cleaned_df[col].value_counts().head(10).plot(kind="bar", ax=ax)
            ax.set_title(f"Top categories in {col}")
            st.pyplot(fig)

        csv = cleaned_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "⬇️ Download Cleaned Data",
            csv,
            "cleaned_data.csv",
            "text/csv"
        )

        