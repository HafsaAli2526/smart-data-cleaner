import pandas as pd
import streamlit as st
import numpy as np
import re

from pipeline.utils import is_text_column
from pipeline.preprocess import parse_currency_value, parse_duration_to_minutes, split_year_range

def apply_pattern_transformers(df):
    df = df.copy()

    for col in df.columns:
        if not is_text_column(df[col]):
            continue

        sample = df[col].dropna().astype(str).head(30)

        if sample.empty:
            continue

        # currency-like
        if sample.str.contains(r"[$€£₹]|[0-9]+(?:\.[0-9]+)?[kmbKMB]", regex=True).any():
            transformed = df[col].apply(parse_currency_value)
            if transformed.notna().sum() / max(len(df), 1) > 0.4:
                if not pd.api.types.is_numeric_dtype(df[col]):
                    df[col] = transformed
                continue

        # duration-like
        if sample.str.contains(r"\d+\s*h|\d+\s*min|^\d{1,2}:\d{2}(?:\:\d{2})?$", regex=True).any():
            transformed = df[col].apply(parse_duration_to_minutes)
            if transformed.notna().sum() / max(len(df), 1) > 0.4:
                df[col] = transformed
                continue

        # year-like or year range
        if "year" in col.lower() or sample.str.match(r"^\(?\d{4}").any():
            year_pairs = df[col].apply(split_year_range)
            start_col = f"{col}_start"
            end_col = f"{col}_end"

            starts = year_pairs.apply(lambda x: x[0])
            ends = year_pairs.apply(lambda x: x[1])

            if starts.notna().sum() / max(len(df), 1) > 0.4:
                df[start_col] = starts
                df[end_col] = ends

    return df
