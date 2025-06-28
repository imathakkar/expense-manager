import streamlit as st
import pandas as pd
import os
from datetime import datetime
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
from utils.file_io import load_json, save_json
from utils.parser import parse_csv
from config import CATEGORY_MAP_FILE, CATEGORY_STRUCTURE_FILE

EXPORTS_DIR = "data/exports"
os.makedirs(EXPORTS_DIR, exist_ok=True)

category_memory = load_json(CATEGORY_MAP_FILE, {})
category_structure = load_json(CATEGORY_STRUCTURE_FILE, {})
categories_flat = [sub for subs in category_structure.values() for sub in subs]

def show_grid(data: pd.DataFrame, key: str):
    data["Delete"] = False  # Add Delete column
    gb = GridOptionsBuilder.from_dataframe(data)
    gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=20)
    gb.configure_default_column(editable=True, filter=True, sortable=True, resizable=True)
    gb.configure_column(
        "Category",
        editable=True,
        cellEditor="agSelectCellEditor",
        cellEditorParams={"values": categories_flat},
        minWidth=180,
        maxWidth=300,
        flex=1,
    )
    gb.configure_column("Delete", editable=True, headerCheckboxSelection=True)
    for col in data.columns:
        if col not in ["Category", "Delete"]:
            gb.configure_column(col, flex=1, minWidth=120)
    gb.configure_side_bar()

    grid_response = AgGrid(
        data,
        gridOptions=gb.build(),
        update_mode=GridUpdateMode.VALUE_CHANGED,
        allow_unsafe_jscode=True,
        key=key,
        height=700,
        fit_columns_on_grid_load=True,
        theme="material",
    )
    return pd.DataFrame(grid_response["data"])

def render_transactions():
    st.title("📁 Upload and Categorize Transactions")

    uploaded_files = st.file_uploader(
        "Upload CSVs",
        type=["csv"],
        accept_multiple_files=True,
        key="upload_transactions"
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
            st.session_state["combined_df"] = combined_df

    if "combined_df" in st.session_state and not st.session_state["combined_df"].empty:
        df = st.session_state["combined_df"]
        df["Year"] = df["Date"].dt.year.astype(str)
        df["MonthNum"] = df["Date"].dt.month

        current_year = str(datetime.now().year)
        current_month_num = datetime.now().month

        years = sorted(df["Year"].unique(), reverse=True)
        default_year_index = years.index(current_year) if current_year in years else 0

        col1, col2 = st.columns([1, 1])
        with col1:
            selected_year = st.selectbox("Select Year", years, index=default_year_index)
        with col2:
            months = df[df["Year"] == selected_year]["MonthNum"].unique()
            months_sorted = sorted(months)
            month_name_map = {m: datetime(1900, m, 1).strftime('%B') for m in months_sorted}
            default_month_index = months_sorted.index(current_month_num) if current_month_num in months_sorted else 0
            selected_month = st.selectbox(
                "Select Month",
                options=months_sorted,
                format_func=lambda x: month_name_map[x],
                index=default_month_index
            )

        filtered_df = df[(df["Year"] == selected_year) & (df["MonthNum"] == selected_month)]
        debit_df = filtered_df[filtered_df["Type"] == "Debit"].copy()
        credit_df = filtered_df[filtered_df["Type"] == "Credit"].copy()

        hidden_cols = ["Year", "MonthNum", "Type"]
        debit_df_display = debit_df.drop(columns=hidden_cols, errors="ignore")
        credit_df_display = credit_df.drop(columns=hidden_cols, errors="ignore")

        tabs = st.tabs(["💳 Debit", "💰 Credit"])

        with tabs[0]:
            st.markdown("### Debit Transactions")
            updated_debit = show_grid(debit_df_display, "debit")
            if st.button("🗑 Delete Selected (Debit)"):
                to_delete = updated_debit[updated_debit["Delete"] == True]
                st.session_state["combined_df"] = st.session_state["combined_df"].drop(
                    st.session_state["combined_df"].index[
                        st.session_state["combined_df"].apply(
                            lambda row: any(
                                (row["Date"] == d["Date"]) and
                                (row["Amount"] == d["Amount"]) and
                                (row["Description"] == d["Description"])
                                for _, d in to_delete.iterrows()
                            ), axis=1
                        )
                    ]
                )
                st.success(f"Deleted {len(to_delete)} debit transaction(s).")
                st.rerun()

        with tabs[1]:
            st.markdown("### Credit Transactions")
            updated_credit = show_grid(credit_df_display, "credit")
            if st.button("🗑 Delete Selected (Credit)"):
                to_delete = updated_credit[updated_credit["Delete"] == True]
                st.session_state["combined_df"] = st.session_state["combined_df"].drop(
                    st.session_state["combined_df"].index[
                        st.session_state["combined_df"].apply(
                            lambda row: any(
                                (row["Date"] == d["Date"]) and
                                (row["Amount"] == d["Amount"]) and
                                (row["Description"] == d["Description"])
                                for _, d in to_delete.iterrows()
                            ), axis=1
                        )
                    ]
                )
                st.success(f"Deleted {len(to_delete)} credit transaction(s).")
                st.rerun()

        combined_updated = pd.concat([updated_debit, updated_credit])
        for _, row in combined_updated.iterrows():
            mask = (
                (st.session_state["combined_df"]["Date"] == row["Date"]) &
                (st.session_state["combined_df"]["Description"] == row["Description"]) &
                (st.session_state["combined_df"]["Amount"] == row["Amount"])
            )
            st.session_state["combined_df"].loc[mask, "Category"] = row["Category"]

            key = " ".join(row["Description"].lower().split()[:2])
            category_memory[key] = row["Category"]

        save_json(CATEGORY_MAP_FILE, category_memory)

        st.markdown("### 💾 Save Transactions")
        save_filename = f"{selected_year}-{selected_month:02d}_transactions.csv"
        if st.button("📥 Save to File"):
            path = os.path.join(EXPORTS_DIR, save_filename)
            filtered_df.drop(columns=["Year", "MonthNum"], errors="ignore").to_csv(path, index=False)
            st.success(f"Saved as `{save_filename}` in `data/exports/` folder")

    st.markdown("---")
    st.markdown("### 📂 Saved Files")

    saved_files = sorted([f for f in os.listdir(EXPORTS_DIR) if f.endswith(".csv")])
    if saved_files:
        for fname in saved_files:
            file_path = os.path.join(EXPORTS_DIR, fname)
            col1, col2, col3 = st.columns([3, 2, 1])
            col1.write(fname)
            with open(file_path, "rb") as f:
                col2.download_button("⬇️ Download", f.read(), file_name=fname, mime="text/csv", key=f"dl_{fname}")
            if col3.button("🗑️ Delete", key=f"del_{fname}"):
                os.remove(file_path)
                st.warning(f"Deleted `{fname}`")
                st.rerun()
    else:
        st.info("No saved export files found.")
