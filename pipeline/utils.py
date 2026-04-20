import pandas as pd
import streamlit as st
import numpy as np
import re
import json
import os

def column_confidence(series):
    total = len(series)
    numeric = pd.to_numeric(series, errors="coerce").notnull().sum()

    return round((numeric / total) * 100, 2)

def detect_patterns(series):
    if not is_text_column(series):
        return None

    sample = series.dropna().astype(str).head(20)

    if sample.str.contains(r"\$|€|₹").any():
        return "currency"

    if sample.str.match(r"^\(?\d{4}").any():
        return "year-like"

    if sample.str.contains(r"\d+h|\d+ min").any():
        return "duration"

    return None

def data_quality_score(df):
    total_cells = df.shape[0] * df.shape[1]
    missing = df.isnull().sum().sum()
    duplicates = df.duplicated().sum()

    completeness = 1 - (missing / total_cells)
    uniqueness = 1 - (duplicates / len(df))

    score = (completeness * 0.6 + uniqueness * 0.4) * 100

    return round(score, 2)

def generate_suggestions(df):
    suggestions = []

    for col in df.columns:
        missing_ratio = df[col].isnull().mean()

        if missing_ratio > 0.5:
            suggestions.append(f"⚠️ '{col}' has >50% missing values → consider dropping")

        if df[col].nunique() == 1:
            suggestions.append(f"⚠️ '{col}' has only one unique value → useless column")

        unique_ratio = df[col].nunique() / len(df)
        if unique_ratio > 0.9 and len(df) > 50:
            suggestions.append(f"ℹ️ '{col}' looks like ID → consider dropping")

    return suggestions

def save_pipeline_config(config, filepath="saved_pipeline.json"):
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)

def load_pipeline_config(filepath="saved_pipeline.json"):
    if not os.path.exists(filepath):
        return None

    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)        

def is_text_column(series):
    return (
        pd.api.types.is_string_dtype(series) or
        pd.api.types.is_object_dtype(series)
    )
