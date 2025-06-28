import streamlit as st
import pandas as pd
from datetime import datetime
from config import DASHBOARD_DATA_FILE, CATEGORY_STRUCTURE_FILE
from utils.file_io import load_json, save_json

dashboard_data = load_json(DASHBOARD_DATA_FILE, {})
category_structure = load_json(CATEGORY_STRUCTURE_FILE, {})

def render_dashboard():
    st.title("📊 Financial Dashboard")
    month_options = list(dashboard_data.keys())
    current_month = datetime.now().strftime("%Y-%m")

    selected_month = st.selectbox("Select a month", ["Create New Dashboard"] + month_options)
    if selected_month == "Create New Dashboard":
        with st.form("create_dashboard_form"):
            new_month = st.text_input("New Month (e.g. 2025-07)", value=current_month)
            if st.form_submit_button("Create"):
                if new_month not in dashboard_data:
                    flat_cats = [sub for subs in category_structure.values() for sub in subs]
                    dashboard_data[new_month] = {
                        "income": {cat: 0.0 for cat in flat_cats},
                        "balances": {}
                    }
                    save_json(DASHBOARD_DATA_FILE, dashboard_data)
                    st.rerun()
    elif selected_month:
        tabs = st.tabs(["Overview", "Income & Balances", "Expense Overview"])
        data = dashboard_data[selected_month]

        with tabs[0]:
            st.subheader("Overview")
            income_total = sum(data["income"].values())
            balance_total = sum(data["balances"].values())
            outstanding = income_total - balance_total
            c1, c2, c3 = st.columns(3)
            c1.metric("Income", f"${income_total:,.2f}")
            c2.metric("Balance", f"${balance_total:,.2f}")
            c3.metric("Outstanding", f"${outstanding:,.2f}")

        with tabs[1]:
            st.subheader("Income and Balances")
            with st.form("edit_form"):
                col1, col2 = st.columns(2)
                for cat in data["income"]:
                    data["income"][cat] = st.number_input(cat, value=data["income"][cat], step=100.0, key=f"inc_{cat}")
                for acc in data["balances"]:
                    data["balances"][acc] = st.number_input(acc, value=data["balances"][acc], step=100.0, key=f"bal_{acc}")
                if st.form_submit_button("Save"):
                    save_json(DASHBOARD_DATA_FILE, dashboard_data)

        with tabs[2]:
            st.subheader("Expense Overview")
            st.info("Upload and categorize transactions in the 'Transactions' tab to view breakdown.")