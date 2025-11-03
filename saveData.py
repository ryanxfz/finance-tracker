import os
import pandas as pd
import streamlit as st

DATA_DIR = "data"

def safe_read_csv(path):
    if not os.path.exists(path):
        return []
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

    # Custom pages
    custom_pages_path = os.path.join(DATA_DIR, "custom_pages.csv")
    if os.path.exists(custom_pages_path):
        df = pd.read_csv(custom_pages_path)
        st.session_state.custom_pages = df["page"].tolist() if not df.empty else []
    else:
        st.session_state.custom_pages = []

    st.session_state.custom_pages_spendings = {}
    for page in st.session_state.custom_pages:
        filename = f"{page}.csv"
        page_path = os.path.join(DATA_DIR, filename)
        st.session_state.custom_pages_spendings[page] = safe_read_csv(page_path)

def save_data():
    os.makedirs(DATA_DIR, exist_ok=True)
    pd.DataFrame(st.session_state.spendings).to_csv(os.path.join(DATA_DIR, "spendings.csv"), index=False)
    pd.DataFrame(st.session_state.income).to_csv(os.path.join(DATA_DIR, "income.csv"), index=False)
    pd.DataFrame({"page": st.session_state.custom_pages}).to_csv(os.path.join(DATA_DIR, "custom_pages.csv"), index=False)
    for page, entries in st.session_state.custom_pages_spendings.items():
        filename = f"{page}.csv"
        page_path = os.path.join(DATA_DIR, filename)
        pd.DataFrame(entries).to_csv(page_path, index=False)