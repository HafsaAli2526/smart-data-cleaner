import pandas as pd
import streamlit as st
import numpy as np
import re

def cap_outliers_iqr(series):
    if not pd.api.types.is_numeric_dtype(series):
        return series

    clean = series.dropna()
    if clean.empty:
        return series

    q1 = clean.quantile(0.25)
    q3 = clean.quantile(0.75)
    iqr = q3 - q1

    if iqr == 0:
        return series

    lower = q1 - 1.5 * iqr
    upper = q3 + 1.5 * iqr

    return series.clip(lower=lower, upper=upper)

def remove_outliers_iqr(df, numeric_cols):
    df = df.copy()
    if not numeric_cols:
        return df

    mask = pd.Series(True, index=df.index)

    for col in numeric_cols:
        clean = df[col].dropna()
        if clean.empty:
            continue

        q1 = clean.quantile(0.25)
        q3 = clean.quantile(0.75)
        iqr = q3 - q1

        if iqr == 0:
            continue

        lower = q1 - 1.5 * iqr
        upper = q3 + 1.5 * iqr

        mask &= df[col].isna() | df[col].between(lower, upper)

    return df.loc[mask].copy()