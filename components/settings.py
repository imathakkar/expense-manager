import streamlit as st
from config import CATEGORY_STRUCTURE_FILE
from utils.file_io import load_json, save_json

category_structure = load_json(CATEGORY_STRUCTURE_FILE, {})

def render_settings():
    st.title("⚙️ Category Settings")

    st.markdown("### Edit Existing Categories")
    for parent in list(category_structure.keys()):
        with st.expander(f"{parent}"):
            subcats = category_structure[parent]
            updated = [st.text_input(f"{i+1}.", value=s, key=f"{parent}_{i}") for i, s in enumerate(subcats)]
            if st.button(f"Save {parent}", key=f"save_{parent}"):
                category_structure[parent] = updated
                save_json(CATEGORY_STRUCTURE_FILE, category_structure)
                st.success(f"Updated {parent}")
                st.experimental_rerun()

    st.markdown("---")
    if st.button("➕ Add New Parent Category"):
        with st.dialog("Add New Parent Category"):
            new_parent = st.text_input("New Parent Category Name", key="dlg_parent")
            new_subs = st.text_area("Enter subcategories (comma-separated)", key="dlg_subs")
            if st.button("Confirm Add Parent Category", key="dlg_submit"):
                if new_parent and new_subs:
                    subs_list = [s.strip() for s in new_subs.split(",") if s.strip()]
                    if new_parent not in category_structure:
                        category_structure[new_parent] = subs_list
                        save_json(CATEGORY_STRUCTURE_FILE, category_structure)
                        st.success(f"Added parent category: {new_parent}")
                        st.rerun()
                    else:
                        st.warning("Parent category already exists.")
                else:
                    st.warning("Please enter a name and at least one subcategory.")

    st.markdown("---")
    if st.button("➕ Add Subcategory"):
        with st.dialog("Add Subcategory"):
            parent_choice = st.selectbox("Select Parent Category", list(category_structure.keys()), key="dlg_parent_choice")
            new_subcat = st.text_input("New Subcategory Name", key="dlg_subcat")
            if st.button("Confirm Add Subcategory", key="dlg_confirm_subcat"):
                if new_subcat:
                    if new_subcat not in category_structure[parent_choice]:
                        category_structure[parent_choice].append(new_subcat)
                        save_json(CATEGORY_STRUCTURE_FILE, category_structure)
                        st.success(f"Added subcategory to {parent_choice}")
                        st.rerun()
                    else:
                        st.warning("Subcategory already exists under selected parent.")
                else:
                    st.warning("Please enter subcategory name.")