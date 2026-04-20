import pandas as pd
import streamlit as st
import numpy as np
import re

from pipeline.utils import is_text_column
from pipeline.preprocess import infer_column_type

def clean_data(df, col_types, drop_cols, null_strategy, subset_cols=None):
    df = df.copy()

    # Drop columns
    df.drop(columns=drop_cols, errors="ignore", inplace=True)

    # Remove duplicates
    #df.drop_duplicates(inplace=True)
    df = remove_duplicates(df, subset_cols)

    # -------------------------
    # HANDLE NULLS
    # -------------------------
    for col in df.columns:
        # NUMERIC
        if null_strategy == "Auto":
            df[col] = smart_fill(df[col])

        elif pd.api.types.is_numeric_dtype(df[col]):
            if null_strategy == "Mean":
                df[col] = df[col].fillna(df[col].mean())
            elif null_strategy == "Median":
                df[col] = df[col].fillna(df[col].median())

        # STRING / CATEGORICAL
        elif is_text_column(df[col]):
            df[col] = df[col].fillna("Unknown")

    # -------------------------
    # NORMALIZE CATEGORICAL (SEPARATE LOOP)
    # -------------------------
    for col in df.columns:
        if is_text_column(df[col]):
            df[col] = df[col].astype("string").str.strip().str.lower()
    return df

def smart_fill(series):
    # Skip if no missing
    if series.isnull().sum() == 0:
        return series

    # -------------------------
    # NUMERIC
    # -------------------------
    if pd.api.types.is_numeric_dtype(series):

        # Handle edge case: all NaN
        if series.dropna().empty:
            return series

        skew = series.skew()

        # Highly skewed → median
        if abs(skew) > 1:
            return series.fillna(series.median())

        # Otherwise → mean
        return series.fillna(series.mean())

    # -------------------------
    # CATEGORICAL
    # -------------------------
    else:
        mode = series.mode()
        if not mode.empty:
            return series.fillna(mode[0])

        return series.fillna("Unknown")
    
def auto_convert_types(df, col_types):
    df = df.copy()

    for col in df.columns:

        # -------------------------
        # NUMERIC (from inference)
        # -------------------------
        if col in col_types["numerical"]:
            df[col] = df[col].astype(str).str.replace(",", "", regex=False)
            df[col] = pd.to_numeric(df[col], errors="coerce")
            continue

        # -------------------------
        # BOOLEAN
        # -------------------------
        elif col in col_types.get("boolean", []):
            df[col] = df[col].astype(str).str.lower()
            df[col] = df[col].map({
                "true": True,
                "false": False,
                "yes": True,
                "no": False,
                "y": True,
                "n": False
            })
            continue

        # -------------------------
        # FALLBACK NUMERIC DETECTION (FIXED)
        # -------------------------
        elif is_text_column(df[col]):

            temp = pd.to_numeric(
                df[col].astype(str).str.replace(",", ""),
                errors="coerce"
            )

            if len(df) > 0 and temp.notnull().sum() / len(df) > 0.5:
                df[col] = temp
                continue

            # -------------------------
            # STRING CLEAN (ONLY IF NOT NUMERIC)
            # -------------------------
            df[col] = df[col].str.strip().str.lower()

    return df

def smart_detect_column_types(df):
    col_types = {
        "numerical": [],
        "categorical": [],
        "boolean": []
    }

    for col in df.columns:
        col_type = infer_column_type(df[col])

        if col_type in ["int", "float"]:
            col_types["numerical"].append(col)
        elif col_type == "bool":
            col_types["boolean"].append(col)
        else:
            col_types["categorical"].append(col)

    return col_types

def remove_duplicates(df, subset_cols=None, keep="first"):
    df = df.copy()

    # Normalize text columns before duplicate check
    for col in df.columns:
        if df[col].dtype == "object":
            df[col] = df[col].astype(str).str.strip().str.lower()

    if subset_cols and len(subset_cols) > 0:
        df = df.drop_duplicates(subset=subset_cols, keep=keep)
    else:
        df = df.drop_duplicates(keep=keep)

    return df.reset_index(drop=True)

