import pandas as pd
import streamlit as st
import re


import pandas as pd
import streamlit as st
import re


def load_file(uploaded_file):
    file_name = uploaded_file.name.lower()

    # CSV
    if file_name.endswith(".csv"):
        return pd.read_csv(uploaded_file)

    # Excel
    elif file_name.endswith(".xlsx") or file_name.endswith(".xls"):
        return pd.read_excel(uploaded_file)

    # JSON
    elif file_name.endswith(".json"):
        return pd.read_json(uploaded_file)

    # TXT (basic)
    elif file_name.endswith(".txt"):
        return pd.read_csv(uploaded_file, delimiter=None, engine="python")

    # DOCX (tables)
    elif file_name.endswith(".docx"):
        from docx import Document

        doc = Document(uploaded_file)
        tables = []

        for table in doc.tables:
            data = []

            for row in table.rows:
                row_data = [cell.text.strip() for cell in row.cells]
                data.append(row_data)

            # Skip invalid tables
            if len(data) <= 1:
                continue

            header = data[0]

            # 🔥 FIX 1: make headers unique
            seen = {}
            new_header = []
            for col in header:
                if col in seen:
                    seen[col] += 1
                    new_header.append(f"{col}_{seen[col]}")
                else:
                    seen[col] = 0
                    new_header.append(col)

            # 🔥 FIX 2: normalize row length
            max_len = len(new_header)
            clean_rows = []

            for row in data[1:]:
                if len(row) < max_len:
                    row = row + [None] * (max_len - len(row))
                elif len(row) > max_len:
                    row = row[:max_len]
                clean_rows.append(row)

            try:
                df_table = pd.DataFrame(clean_rows, columns=new_header)
                tables.append(df_table)
            except:
                continue

        if tables:
            # 🔥 FIX 3: align columns safely
            return pd.concat(tables, ignore_index=True, sort=False)

        st.warning("⚠️ No valid tables found in DOCX file")
        return pd.DataFrame()

    else:
        st.error("Unsupported file format")
        return None
    