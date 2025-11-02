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

def save_data():
    os.makedirs(DATA_DIR, exist_ok=True)
    pd.DataFrame(st.session_state.spendings).to_csv(os.path.join(DATA_DIR, "spendings.csv"), index=False)
    pd.DataFrame(st.session_state.income).to_csv(os.path.join(DATA_DIR, "income.csv"), index=False)