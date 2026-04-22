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
                data.append([cell.text for cell in row.cells])
            tables.append(pd.DataFrame(data[1:], columns=data[0]))

        return pd.concat(tables, ignore_index=True) if tables else pd.DataFrame()

    else:
        st.error("Unsupported file format")
        return None
    