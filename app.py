import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import datetime
from saveData import load_data, save_data

if "data_loaded" not in st.session_state:
    load_data()
    st.session_state.dataloaded = True

# session states
if "spendings" not in st.session_state:
    st.session_state.spendings = []
if "currency" not in st.session_state:
    st.session_state.currency = "EUR"
if "income" not in st.session_state:
    st.session_state.income = []
if "custom_pages" not in st.session_state:
    st.session_state.custom_pages = []
if "custom_pages_spendings" not in st.session_state:
    st.session_state.custom_pages_spendings = {}

# constants
CURRENT_YEAR = datetime.datetime.now().year
YEAR_RANGE = list(range(2022, CURRENT_YEAR + 1))
MONTHS = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
]
SPENDING_CATEGORIES = [
    "Groceries",
    "Leisure/Entertainment",
    "Bills",
    "Wohnung",
    "Other"
]
PAGES = (
    ["Spendings Summary"] + 
    [f"Spendings {year}" for year in YEAR_RANGE] + 
    ["Income"] + 
    st.session_state.custom_pages
    )
INCOME_SOURCES = ["Family", "Work", "Other"]
CURRENCIES = ["EUR", "IDR", "SGD", "HUF"] # eventually with external currency exchange API

page = st.sidebar.selectbox("Select Page", PAGES)

with st.sidebar.expander("Add custom Page"):
    if "page_added_success" in st.session_state:
        st.success(st.session_state.page_added_success)
        del st.session_state.page_added_success
    st.markdown("### Enter new custom page name")
    new_page_name = st.text_input("Custom page name", key="new_custom_page_name")
    if st.button("Add new page", key="add_new_page"):
        if new_page_name not in st.session_state.custom_pages:
            st.session_state.custom_pages.append(new_page_name)
            save_data()
            st.session_state.page_added_success = f"Page successfully added: {new_page_name}"
            st.rerun()
        else:
            st.error("Page name already exists, pick another name")

with st.sidebar.expander("Remove Custom Page"):
    if "page_removed_success" in st.session_state:
        st.success(st.session_state.page_removed_success)
        del st.session_state.page_removed_success
    page_to_remove = st.selectbox("Select custom page to remove", st.session_state.custom_pages, key="remove_custom_page_select")
    if st.session_state.custom_pages == []:
        st.write("No custom pages available to delete")
    else:
        if st.button("Remove Page", key="remove_custom_page_btn"):
            st.session_state.custom_pages.remove(page_to_remove)
            save_data()
            st.session_state.page_removed_success = f"Removed custom page: {page_to_remove}"
            st.rerun()

if page == "Spendings Summary":
    st.header("Spendings Summary")
    if st.session_state.spendings:
        df = pd.DataFrame(st.session_state.spendings)
        selected_currency = st.selectbox("Show Currency", CURRENCIES, index=0)
        df_filtered = df[df["currency"] == selected_currency]
        pivot = pd.pivot_table(
            df_filtered,
            values="amount",
            index="month",
            columns="year",
            aggfunc="sum",
            fill_value=0
        )
        pivot = pivot.reindex(MONTHS)
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

elif page == "Income":
    st.header("Income")
    with st.form("income_form"):
        year = st.selectbox("Year", YEAR_RANGE)
        month = st.selectbox("Month", MONTHS)
        source = st.selectbox("Income source", INCOME_SOURCES)
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
        pivot_income = pivot_income.reindex(MONTHS)
        st.dataframe(pivot_income.style.format("{:,.2f}"))
    else:
        st.info("No income records entered yet.")

# for custom pages
elif page in st.session_state.custom_pages:
    st.header(page)
    if page not in st.session_state.custom_pages_spendings:
        st.session_state.custom_pages_spendings[page] = []
    
    with st.form(f"custom_spending_form_{page}"):
        currency = st.selectbox("Currency", CURRENCIES, index=0)
        amount = st.number_input("Amount Spent", min_value=0.0, format="%.2f")
        notes = st.text_input("Notes for this spending")
        submit = st.form_submit_button("Add Spending")
        if submit and amount > 0:
            st.session_state.custom_pages_spendings[page].append(
                {
                    "currency": currency,
                    "amount": amount,
                    "notes": notes,
                }
            )
            save_data()
            st.success("Data saved!")
    
    df_custom_pages = pd.DataFrame(st.session_state.custom_pages_spendings[page])
    st.subheader(f"Spendings for {page}")
    st.dataframe(df_custom_pages)

    if not df_custom_pages.empty and "amount" in df_custom_pages.columns:
        total = df_custom_pages["amount"].sum()
        st.markdown(f"**Total Spendings:** {total:,.2f}")

    st.markdown("## Add where you want this spendings to be appended to: ")
    with st.form("spending_form"):
        month = st.selectbox("Month", MONTHS)
        year = st.selectbox("Year", YEAR_RANGE)
        category = st.selectbox("Category", SPENDING_CATEGORIES)
        submit = st.form_submit_button("Append spendings to the selected month and year")
        if submit and st.session_state.custom_pages_spendings[page]:
            st.session_state.spendings.append(
                {
                    "amount": total,
                    "category": category,
                    "year": year,
                    "month": month,
                    "currency": currency,
                    "notes": notes,
                }
            )
            save_data()
            st.success(f"Data appended to {str(month)} {str(year)}")

# for every year
else:
    year_page = int(page.split(" ")[1])
    st.header(f"Spendings for {year_page}")
    with st.form("spending_form"):
        month = st.selectbox("Month", MONTHS)
        currency = st.selectbox("Currency", CURRENCIES, index=0)
        amount = st.number_input("Amount Spent", min_value=0.0, format="%.2f")
        category = st.selectbox("Category", SPENDING_CATEGORIES)
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
        selected_currency = st.selectbox("Show currency", CURRENCIES, index=0)
        df_year = df[(df["year"] == year_page) & (df["currency"] == selected_currency)]
        st.subheader(f"Spendings for {year_page}")
    
        for month in MONTHS:
            df_month = df_year[df_year["month"] == month]
            df_without_month = df_month.drop(columns=["month"]) # dont have to include the month again in the table, since it's already determined in the expander
            with st.expander(f"{month} ({len(df_month)})"):
                if not df_month.empty:
                    st.dataframe(df_without_month)
                else:
                    st.info(f"No spendings entered for {month}.")
                month_total = df_month[df_month["category"] != "Savings"]["amount"].sum()
                st.markdown(f"Total Spending in {month}: €{str(round(month_total,2))}")
        
        # pie chart:
        st.subheader(f"Spending Proportions for {year_page}")
        proportions = df_year.groupby("category")["amount"].sum()
        if not proportions.empty:
            fig, ax = plt.subplots()
            ax.pie(proportions, labels=proportions.index, autopct="%1.1f%%")
            st.pyplot(fig)
        else:
            st.info("No spendings entered for selected year and currency.")

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

        if st.session_state.spendings and st.session_state.income:
            df_spendings = pd.DataFrame(st.session_state.spendings)
            df_income = pd.DataFrame(st.session_state.income)
            savings_per_month = []
            for month in MONTHS:
                income_this_month = df_income[
                    (df_income["year"] == year_page) &
                    (df_income["month"] == month )
                ]["amount"].sum()

                spendings_this_month = df_spendings[
                    (df_spendings["year"] == year_page) &
                    (df_spendings["month"] == month ) &
                    (df_spendings["category"] != "Savings")
                ]["amount"].sum()

                savings = income_this_month - spendings_this_month

                # Only append if savings > 0 and not already present
                already_saved = any(
                    (s.get("year") == year_page and s.get("month") == month and s.get("currency") == selected_currency and s.get("category") == "Savings")
                    for s in st.session_state.spendings
                )
                if savings > 0 and not already_saved:
                    st.session_state.spendings.append({
                        "amount": savings,
                        "category": "Savings",
                        "year": year_page,
                        "month": month,
                        "currency": selected_currency,
                        "notes": st.markdown("*Auto calculated*")
                    })
                    save_data()

            df_display = pd.DataFrame(st.session_state.spendings)
            st.subheader(f"Spending Proportions for {year_page} (including Automated Savings)")
            proportions = df_display[
                (df_display["year"] == year_page) & (df_display["currency"] == selected_currency)
            ].groupby("category")["amount"].sum()
            if not proportions.empty:
                fig, ax = plt.subplots()
                ax.pie(proportions, labels=proportions.index, autopct="%1.1f%%")
                st.pyplot(fig)
            else:
                st.info("No spendings entered for selected year and currency.")
        else:
            st.info("No spendings entered yet.")