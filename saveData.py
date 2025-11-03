import os
import pandas as pd
import streamlit as st

DATA_DIR = "data"

def safe_read_csv(path):
    try:
        df = pd.read_csv(path)
        if df.empty:
            return []
        return df.to_dict("records")
    except pd.errors.EmptyDataError:
        return []

def load_data():
    # Spendings
    spendings_path = os.path.join(DATA_DIR, "spendings.csv")
    st.session_state.spendings = safe_read_csv(spendings_path)

    # Income
    income_path = os.path.join(DATA_DIR, "income.csv")
    st.session_state.income = safe_read_csv(income_path)

    #custom pages
    custom_pages_spendings_path = os.path.join(DATA_DIR, "custom_pages_spendings.csv")
    if os.path.exists(custom_pages_spendings_path):
        df = pd.read_csv(custom_pages_spendings_path)
        custom_dict = {}
        if not df.empty:
            for page in df["custom_page"].unique():
                custom_dict[page] = df[df["custom_page"] == page].drop("custom_page", axis=1).to_dict("records")
        st.session_state.custom_pages_spendings = custom_dict
    else:
        st.session_state.custom_pages_spendings = {}

def save_data():
    os.makedirs(DATA_DIR, exist_ok=True)

    pd.DataFrame(st.session_state.spendings).to_csv(os.path.join(DATA_DIR, "spendings.csv"), index=False)

    pd.DataFrame(st.session_state.income).to_csv(os.path.join(DATA_DIR, "income.csv"), index=False)

    custom_rows = []
    for page, entries in st.session_state.custom_pages_spendings.items():
        for entry in entries:
            row = {"custom_page": page}
            row.update(entry)
            custom_rows.append(row)
    pd.DataFrame(custom_rows).to_csv(os.path.join(DATA_DIR, "custom_pages_spendings.csv"), index=False)
