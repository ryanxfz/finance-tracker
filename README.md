# Finance Tracker
A simple Streamlit app to track my spendings. All features are tailored to my needs and preferences. All data is stored to the local disk in a `.csv` file.

## Features
- **Spendings Summary:** View monthly and yearly summaries of spendings with pie charts visualising the percentage of each spending categories. The categories are: Groceries, Leisure/Entertainment, Bills, Rent, Savings, Other.
- **Yearly Spendings:** Enter and view spendings for each year, organized by month in expandable tables.
- **Custom Pages:** Create and remove custom pages for special events or projects, and track spendings for each. This custom spending pages/group could then be appended into the spending list of a specific month/year. Example: Budapest 2025 Trip.
- **Work Income (Still a work in progress):** Track income sources and amounts per month/year. This value would then be taken into account into the spendings summary.
- **Spending performance (Still a work in progress):** Evaluate financial health based on the proportion of spending in each category.

## Setup
1. **Change to project directory**
```sh
   cd finance-tracker
```
2. **Create virtual environment**
```sh
   python -m venv venv
```
3. **Activate virtual environment**
```sh
   venv\Scripts\activate
```
4. **Install Requirements**<br>
You will require streamlit, pandas and matplotlib for this project.
```sh
   pip install -r requirements.txt
```
5. **Run the app**
```sh
   streamlit run app.py
```

test4