import streamlit as st
import pandas as pd
from datetime import datetime
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

from utils.file_io import load_json, save_json
from utils.parser import parse_csv
from utils.storage import (
    load_all_transactions,
    update_month_transactions,
    get_month_transactions,
    delete_month_transactions,
)
from config import CATEGORY_MAP_FILE, CATEGORY_STRUCTURE_FILE

category_memory = load_json(CATEGORY_MAP_FILE, {})
category_structure = load_json(CATEGORY_STRUCTURE_FILE, {})
categories_flat = [sub for subs in category_structure.values() for sub in subs]

def render_transactions():
    st.title("📁 Upload and Categorize Transactions")

    # Load all stored transactions (dict with keys as "YYYY-MM")
    all_transactions = load_all_transactions()

    # Extract available months and years from keys like "2025-06"
    months_years = sorted(all_transactions.keys(), reverse=True)
    years = sorted({m.split("-")[0] for m in months_years}, reverse=True)

    # Select Year dropdown
    current_year = str(datetime.now().year)
    selected_year = st.selectbox("Select Year", options=years if years else [current_year], index=0 if current_year not in years else years.index(current_year))

    # Filter months by selected year
    months_in_year = [m for m in months_years if m.startswith(selected_year)]
    month_names_map = {
        "01": "January", "02": "February", "03": "March", "04": "April",
        "05": "May", "06": "June", "07": "July", "08": "August",
        "09": "September", "10": "October", "11": "November", "12": "December"
    }
    months_options = [month_names_map.get(m.split("-")[1], m) + f" ({m})" for m in months_in_year]

    # Default month selection: current month if present else first
    current_month = datetime.now().strftime("%m")
    default_month_index = 0
    for idx, m in enumerate(months_in_year):
        if m.endswith(current_month):
            default_month_index = idx
            break

    selected_month_full = st.selectbox("Select Month", options=months_options if months_options else ["No months"], index=default_month_index if months_options else 0)
    
    # Extract actual "YYYY-MM" string from selected_month_full which has form "MonthName (YYYY-MM)"
    selected_month = None
    if months_options:
        # selected_month_full is like "June (2025-06)"
        selected_month = selected_month_full.split("(")[-1].replace(")", "")
    else:
        st.info("No transactions saved yet for the selected year.")

    # File uploader - unique key to avoid duplicate id error
    uploaded_files = st.file_uploader(
        "Upload CSV files (Credit/Debit). Filenames must contain 'credit' or 'debit'.",
        type=["csv"], accept_multiple_files=True, key="transaction_file_uploader"
    )

    if uploaded_files:
        all_dfs = []
        for file in uploaded_files:
            content = file.read().decode("utf-8")
            is_credit = "credit" in file.name.lower()
            df = parse_csv(content, is_credit=is_credit, memory=category_memory)
            all_dfs.append(df)
        if all_dfs:
            combined_df = pd.concat(all_dfs, ignore_index=True)
            # Save to current month based on selected_month or today if none
            save_month = selected_month if selected_month else datetime.now().strftime("%Y-%m")
            update_month_transactions(all_transactions, save_month, combined_df.to_dict(orient="records"))
            st.success(f"Saved {len(combined_df)} transactions for {save_month}.")

    # Load transactions for selected_month
    if selected_month and selected_month in all_transactions:
        df_month = pd.DataFrame(all_transactions[selected_month])
        if not df_month.empty:
            # Fix dates if needed
            if 'Date' in df_month.columns:
                df_month['Date'] = pd.to_datetime(df_month['Date'], errors='coerce')

            debit_df = df_month[df_month["Type"] == "Debit"].copy()
            credit_df = df_month[df_month["Type"] == "Credit"].copy()

            tabs = st.tabs(["💳 Debit Transactions", "💰 Credit Transactions"])

            def show_grid(data, label):
                gb = GridOptionsBuilder.from_dataframe(data)
                gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=20)
                gb.configure_default_column(editable=True, filter=True, sortable=True)
                gb.configure_column(
                    "Category",
                    editable=True,
                    cellEditor="agSelectCellEditor",
                    cellEditorParams={"values": categories_flat}
                )
                gb.configure_side_bar()
                grid_response = AgGrid(
                    data,
                    gridOptions=gb.build(),
                    update_mode=GridUpdateMode.VALUE_CHANGED,
                    allow_unsafe_jscode=True,
                    key=label,
                    height=500,
                    fit_columns_on_grid_load=True
                )
                return pd.DataFrame(grid_response["data"])

            with tabs[0]:
                updated_debit = show_grid(debit_df, "debit_grid")
                # Delete selected rows
                selected_rows = st.button("Delete Selected Debit Rows")
                if selected_rows:
                    selected = AgGrid(debit_df, enable_enterprise_modules=True).get('selected_rows')
                    if selected:
                        indexes_to_drop = [row['_selectedRowNodeInfo']['nodeRowIndex'] for row in selected]
                        debit_df.drop(debit_df.index[indexes_to_drop], inplace=True)
                        st.experimental_rerun()

            with tabs[1]:
                updated_credit = show_grid(credit_df, "credit_grid")
                selected_rows = st.button("Delete Selected Credit Rows")
                if selected_rows:
                    selected = AgGrid(credit_df, enable_enterprise_modules=True).get('selected_rows')
                    if selected:
                        indexes_to_drop = [row['_selectedRowNodeInfo']['nodeRowIndex'] for row in selected]
                        credit_df.drop(credit_df.index[indexes_to_drop], inplace=True)
                        st.experimental_rerun()

            # Combine and save back
            combined_updated = pd.concat([updated_debit, updated_credit], ignore_index=True)
            update_month_transactions(all_transactions, selected_month, combined_updated.to_dict(orient="records"))

            # Update category memory
            for _, row in combined_updated.iterrows():
                key = " ".join(str(row["Description"]).lower().split()[:2])
                category_memory[key] = row["Category"]
            save_json(CATEGORY_MAP_FILE, category_memory)

        else:
            st.info("No transactions available for the selected month.")

    # Option to delete all transactions for a month
    if selected_month:
        if st.button(f"🗑️ Delete all transactions for {selected_month}"):
            delete_month_transactions(all_transactions, selected_month)
            st.success(f"Deleted all transactions for {selected_month}.")

