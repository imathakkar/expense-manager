import streamlit as st
from components.dashboard import render_dashboard
from components.transactions import render_transactions
from components.settings import render_settings

def apply_global_css():
    st.markdown("""
        <link href="https://fonts.googleapis.com/css2?family=Roboto&display=swap" rel="stylesheet">
        <style>
        .main > div {
            max-width: 1200px !important;
            margin-left: auto !important;
            margin-right: auto !important;
            padding: 20px 40px !important;
            font-family: 'Roboto', sans-serif !important;
            background-color: #fafafa !important;
        }
        .ag-root-wrapper, .ag-cell {
            font-size: 16px !important;
            font-family: 'Roboto', sans-serif !important;
            color: #212121 !important;
        }
        .ag-header-cell-label {
            font-weight: 600 !important;
            color: #424242 !important;
        }
        .ag-row:hover {
            background-color: #e0f7fa !important;
        }
        </style>
        """, unsafe_allow_html=True)

apply_global_css()

st.set_page_config(page_title="💼 Expense Manager", layout="wide")

st.sidebar.title("💼 Expense Manager")
menu = st.sidebar.radio("Navigate", ["📊 Dashboard", "📁 Transactions", "⚙️ Settings"])

if menu == "📊 Dashboard":
    render_dashboard()
elif menu == "📁 Transactions":
    render_transactions()
elif menu == "⚙️ Settings":
    render_settings()