import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import datetime
from saveData import load_data, save_data

if "data_loaded" not in st.session_state:
    load_data()
    st.session_state.dataloaded = True

st.title("Spendings sheet")

# Initialize session state for spendings
if "spendings" not in st.session_state:
    st.session_state.spendings = []
if "currency" not in st.session_state:
    st.session_state.currency = "EUR"
if "income" not in st.session_state:
    st.session_state.income = []
if "custom_pages" not in st.session_state:
    st.session_state.custom_pages = []

# steamlit doesnt have a built in modal, so here's a workaround.
if "show_add_page_modal" not in st.session_state:
    st.session_state.show_add_page_modal = False

if st.sidebar.button("Add Page"):
    st.session_state.show_add_page_modal = True

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

pages = (
    ["Spendings Summary"] + 
    [f"Spendings {year}" for year in years] + 
    ["Work Income"] + 
    st.session_state.custom_pages
    )
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
            save_data()
            st.success("Data saved!")
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


elif page in st.session_state.custom_pages:
    st.header(page)
    # You can use the same form and table logic as for year pages,
    # or customize as needed for each custom page.
    with st.form(f"custom_spending_form_{page}"):
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
                    "year": "Custom",
                    "month": month,
                    "currency": currency,
                    "notes": notes,
                    "custom_page": page
                }
            )
            save_data()
            st.success("Data saved!")

    # Display spendings for this custom page
    df = pd.DataFrame(st.session_state.spendings)
    df_custom = df[df.get("custom_page", "") == page]
    st.subheader(f"Spendings for {page}")
    st.dataframe(df_custom)

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
            save_data()
            st.success("Data saved!")

    # Display spendings for the selected year
    if st.session_state.spendings:
        df = pd.DataFrame(st.session_state.spendings)
        selected_currency = st.selectbox("Show currency", ["EUR", "IDR", "HUF", "SGD"], index=0)
        df_year = df[(df["year"] == year_page) & (df["currency"] == selected_currency)]
        st.subheader(f"Spendings for {year_page}")
        st.dataframe(df_year)

        # Option to delete by index
        st.write("Delete a record by index:")
        if "delete_mode" not in st.session_state:
            st.session_state.delete_mode = False
        if st.button("Delete by Index"):
            st.session_state.delete_mode = True

        if st.session_state.delete_mode and not df_year.empty:
            idx_to_delete = st.number_input(
                "Enter the index number to delete",
                min_value=0,
                max_value=len(df_year)-1,
                step=1,
                key="delete_idx_input"
            )
            if st.button("Confirm Delete", key="confirm_delete_btn"):
                if 0 <= idx_to_delete < len(df_year):
                    original_idx = df_year.index[idx_to_delete]
                    st.session_state.spendings.pop(original_idx)
                    save_data()
                    st.session_state.delete_mode = False
                    st.rerun()
                else:
                    st.warning("Invalid index selected.")
            if st.button("Cancel", key="cancel_delete_btn"):
                st.session_state.delete_mode = False
    else:
        st.info("No spendings entered yet.")