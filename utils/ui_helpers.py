import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

def page_container(content_func):
    st.container()
    content_func()

def show_transactions_grid(df, categories, key):
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=20)
    gb.configure_default_column(editable=True, filter=True, sortable=True)
    gb.configure_column(
        "Category",
        editable=True,
        cellEditor="agSelectCellEditor",
        cellEditorParams={"values": categories},
    )
    gb.configure_selection(selection_mode='multiple', use_checkbox=True)
    gb.configure_side_bar()
    grid_response = AgGrid(
        df,
        gridOptions=gb.build(),
        update_mode=GridUpdateMode.VALUE_CHANGED,
        allow_unsafe_jscode=True,
        key=key,
        height=500,
        fit_columns_on_grid_load=True,
    )
    return grid_response
