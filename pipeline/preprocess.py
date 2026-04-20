import numpy as np
import re
import pandas as pd

def preprocess_data(df):
    df = df.copy()

    df.replace(["", " ", "NA", "N/A", "null", "None"], np.nan, inplace=True)
    df.replace(r"^\s*$", np.nan, regex=True, inplace=True)
    df.replace("nan", np.nan, inplace=True)

    for col in df.columns:
        if df[col].dtype == "object":
            df[col] = df[col].str.strip()

    return df

def infer_column_type(series):
    series = series.dropna().astype(str)

    if len(series) == 0:
        return "unknown"

    total = len(series)

    num_count = 0
    float_count = 0
    bool_count = 0

    for val in series[:100]:
        v = val.strip().lower().replace(",", "")

        if v in ["true", "false", "yes", "no", "y", "n"]:
            bool_count += 1
            continue

        try:
            if "." in v:
                float(v)
                float_count += 1
            else:
                int(v)
                num_count += 1
        except:
            pass

    if (num_count + float_count) / total > 0.5:
        return "float" if float_count > 0 else "int"

    if bool_count / total > 0.7:
        return "bool"

    return "string"

def parse_currency_value(value):
    if pd.isna(value):
        return np.nan

    s = str(value).strip().lower()
    if s in ["", "na", "n/a", "null", "none", "unknown"]:
        return np.nan

    s = s.replace(",", "").replace("$", "").replace("€", "").replace("£", "").replace("₹", "")

    multiplier = 1
    if s.endswith("k"):
        multiplier = 1_000
        s = s[:-1]
    elif s.endswith("m"):
        multiplier = 1_000_000
        s = s[:-1]
    elif s.endswith("b"):
        multiplier = 1_000_000_000
        s = s[:-1]

    try:
        return float(s) * multiplier
    except ValueError:
        return np.nan

def parse_duration_to_minutes(value):
    if pd.isna(value):
        return np.nan

    s = str(value).strip().lower()
    if s in ["", "na", "n/a", "null", "none", "unknown"]:
        return np.nan

    # hh:mm:ss
    if re.match(r"^\d{1,2}:\d{2}(:\d{2})?$", s):
        parts = [int(p) for p in s.split(":")]
        if len(parts) == 2:
            return parts[0] * 60 + parts[1]
        if len(parts) == 3:
            return parts[0] * 60 + parts[1]

    hours = 0
    minutes = 0

    h_match = re.search(r"(\d+)\s*h", s)
    m_match = re.search(r"(\d+)\s*min", s)

    if h_match:
        hours = int(h_match.group(1))
    if m_match:
        minutes = int(m_match.group(1))

    if h_match or m_match:
        return hours * 60 + minutes

    # plain numeric minutes like "90"
    try:
        return float(s)
    except ValueError:
        return np.nan

def split_year_range(value):
    if pd.isna(value):
        return (np.nan, np.nan)

    s = str(value).strip()
    years = re.findall(r"\d{4}", s)

    if len(years) == 0:
        return (np.nan, np.nan)
    if len(years) == 1:
        y = int(years[0])
        return (y, y)

    return (int(years[0]), int(years[1]))