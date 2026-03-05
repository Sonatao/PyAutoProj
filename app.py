import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="Excel Sorter & Duplicate Finder", layout="centered")

st.title("Excel Sorter & Duplicate Finder")
st.write("Upload an Excel file to begin.")

uploaded = st.file_uploader("Upload Excel File", type=["xlsx", "xls"])

if uploaded:
    # Force ALL columns and rows to be read as full strings
    df = pd.read_excel(uploaded, dtype=str)
    st.success("File loaded successfully")

    st.subheader("Sorting Options")
    sort_col = st.selectbox("Primary Sort Column", df.columns)
    order = st.selectbox("Sort Order", ["Ascending", "Descending"])

    st.subheader("Secondary Sort Options")
    enable_secondary = st.checkbox("Enable Secondary Sorting", value=True)
    secondary_col = st.selectbox("Secondary Sort Column", df.columns)

    st.subheader("Duplicate Detection")
    dup_col = st.selectbox("Duplicate Check Column", df.columns)

    if st.button("Run Processing"):
        ascending = order == "Ascending"

        # ---------------------------------------------------------
        # SECONDARY SORT LOGIC (only if enabled)
        # ---------------------------------------------------------
        if enable_secondary:

            # Special logic for Constituency Code (numeric-first)
            if secondary_col == "Constituency Code":
                df["_secondary_priority"] = df["Constituency Code"].str.match(r"^\d").apply(
                    lambda x: 0 if x else 1
                )
                secondary_sort_cols = ["_secondary_priority", "Constituency Code"]
                secondary_sort_order = [True, True]

            else:
                # Generic secondary sort for any other column
                df["_secondary_priority"] = 0  # no special priority
                secondary_sort_cols = [secondary_col]
                secondary_sort_order = [True]

        else:
            # No secondary sorting
            df["_secondary_priority"] = 0
            secondary_sort_cols = []
            secondary_sort_order = []

        # ---------------------------------------------------------
        # MAIN SORT: primary + optional secondary
        # ---------------------------------------------------------
        sort_columns = [sort_col] + secondary_sort_cols
        sort_orders = [ascending] + secondary_sort_order

        sorted_df = df.sort_values(
            by=sort_columns,
            ascending=sort_orders
        ).drop(columns=["_secondary_priority"])

        # ---------------------------------------------------------
        # DUPLICATES SORT: same logic
        # ---------------------------------------------------------
        dup_df = df[df[dup_col].duplicated(keep=False)]

        dup_sorted = dup_df.sort_values(
            by=[dup_col] + secondary_sort_cols,
            ascending=[ascending] + secondary_sort_order
        ).drop(columns=["_secondary_priority"])

        st.success("Processing complete")

        def to_excel_bytes(dataframe):
            buffer = BytesIO()
            dataframe.to_excel(buffer, index=False)
            buffer.seek(0)
            return buffer

        st.download_button(
            "Download Sorted File",
            data=to_excel_bytes(sorted_df),
            file_name="sorted_output.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        st.download_button(
            "Download Duplicates File",
            data=to_excel_bytes(dup_sorted),
            file_name="duplicates_output.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )