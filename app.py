import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import datetime
import os

st.title("Spendings sheet")

# Initialize session state for spendings
if "spendings" not in st.session_state:
    st.session_state.spendings = []
if "currency" not in st.session_state:
    st.session_state.currency = "EUR"
if "income" not in st.session_state:
    st.session_state.income = []
if "fixed_costs" not in st.session_state:
    st.session_state.fixed_costs = {}

current_year = datetime.datetime.now().year
years = list(range(2022, current_year + 1))
months = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
]
categories = [
    "Groceries",
    "Leisure/Entertainment",
    "Bills",
    "Wohnung",
    "Other",
    "Savings"
]

pages = ["Spendings Summary"] + [f"Spendings {year}" for year in years] + ["Work Income"]
page = st.sidebar.selectbox("Select Page", pages)

if page == "Spendings Summary":
    st.header("Spendings Summary")
    if st.session_state.spendings:
        df = pd.DataFrame(st.session_state.spendings)
        selected_currency = st.selectbox("Show Currency", ["EUR", "IDR", "HUF", "SGD"], index=0)
        df_filtered = df[df["currency"] == selected_currency]
        pivot = pd.pivot_table(
            df_filtered,
            values="amount",
            index="month",
            columns="year",
            aggfunc="sum",
            fill_value=0
        )
        pivot = pivot.reindex(months)
        st.dataframe(pivot.style.format("{:,.2f}"))
        st.subheader("Spending Proportions")
        proportions = df_filtered.groupby("category")["amount"].sum()
        if not proportions.empty:
            fig, ax = plt.subplots()
            ax.pie(proportions, labels=proportions.index, autopct="%1.1f%%")
            st.pyplot(fig)
        else:
            st.info("No spendings entered for selected currency.")
    else:
        st.info("No spendings entered yet.")

elif page == "Work Income":
    st.header("Work Income")
    with st.form("work_income_form"):
        year = st.selectbox("Year", years)
        month = st.selectbox("Month", months)
        source = st.text_input("Income source")
        amount = st.number_input("Earned amount", min_value=0.0, format="%.2f")
        submit = st.form_submit_button("Add income")
        if submit and amount > 0:
            st.session_state.income.append(
                {
                    "year": year,
                    "month": month,
                    "source": source,
                    "amount": amount
                }
            )
    if st.session_state.income:
        df_income = pd.DataFrame(st.session_state.income)
        st.subheader("Income Records")
        st.dataframe(df_income)
        st.subheader("Income Summary")
        pivot_income = pd.pivot_table(
            df_income,
            values="amount",
            index="month",
            columns="year",
            aggfunc="sum",
            fill_value=0
        )
        pivot_income = pivot_income.reindex(months)
        st.dataframe(pivot_income.style.format("{:,.2f}"))
    else:
        st.info("No income records entered yet.")

else:
    year_page = int(page.split(" ")[1])
    with st.form("spending_form"):
        st.markdown(f"**Year:** {year_page}")
        month = st.selectbox("Month", months)
        currency = st.selectbox("Currency", ["EUR", "IDR", "HUF", "SGD"], index=0)
        amount = st.number_input("Amount Spent", min_value=0.0, format="%.2f")
        category = st.selectbox("Category", categories)
        notes = st.text_input("Notes for this spending")
        submit = st.form_submit_button("Add Spending")
        if submit and amount > 0:
            st.session_state.spendings.append(
                {
                    "amount": amount,
                    "category": category,
                    "year": year_page,
                    "month": month,
                    "currency": currency,
                    "notes": notes,
                }
            )

    # Display spendings for the selected year
    if st.session_state.spendings:
        df = pd.DataFrame(st.session_state.spendings)
        selected_currency = st.selectbox("Show currency", ["EUR", "IDR", "HUF", "SGD"], index=0)
        df_year = df[(df["year"] == year_page) & (df["currency"] == selected_currency)]
        st.dataframe(df_year)
        st.subheader(f"Spending Proportions for {year_page}")
        proportions = df_year.groupby("category")["amount"].sum()
        if not proportions.empty:
            fig, ax = plt.subplots()
            ax.pie(proportions, labels=proportions.index, autopct="%1.1f%%")
            st.pyplot(fig)
        else:
            st.info("No spendings entered for selected year and currency.")
    else:
        st.info("No spendings entered yet.")


DATA_DIR = "data"

def load_data():
    # Spendings
    spendings_path = os.path.join(DATA_DIR, "spendings.csv")
    if os.path.exists(spendings_path):
        st.session_state.spendings = pd.read_csv(spendings_path).to_dict("records")
    else:
        st.session_state.spendings = []

    # Income
    income_path = os.path.join(DATA_DIR, "income.csv")
    if os.path.exists(income_path):
        st.session_state.income = pd.read_csv(income_path).to_dict("records")
    else:
        st.session_state.income = []

    # Fixed costs
    fixed_costs_path = os.path.join(DATA_DIR, "fixed_costs.csv")
    if os.path.exists(fixed_costs_path):
        df_fixed = pd.read_csv(fixed_costs_path)
        st.session_state.fixed_costs = {}
        for _, row in df_fixed.iterrows():
            year = int(row["year"])
            entry = row.drop("year").to_dict()
            if year not in st.session_state.fixed_costs:
                st.session_state.fixed_costs[year] = []
            st.session_state.fixed_costs[year].append(entry)
    else:
        st.session_state.fixed_costs = {}

def save_data():
    os.makedirs(DATA_DIR, exist_ok=True)
    pd.DataFrame(st.session_state.spendings).to_csv(os.path.join(DATA_DIR, "spendings.csv"), index=False)
    pd.DataFrame(st.session_state.income).to_csv(os.path.join(DATA_DIR, "income.csv"), index=False)
    fixed_rows = []
    for year, entries in st.session_state.fixed_costs.items():
        for entry in entries:
            row = {"year": year}
            row.update(entry)
            fixed_rows.append(row)
    pd.DataFrame(fixed_rows).to_csv(os.path.join(DATA_DIR, "fixed_costs.csv"), index=False)

# Load data at startup
if "data_loaded" not in st.session_state:
    load_data()
    st.session_state.data_loaded = True