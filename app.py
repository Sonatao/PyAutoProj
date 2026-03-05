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
    sort_col = st.selectbox("Sort Column", df.columns)
    order = st.selectbox("Sort Order", ["Ascending", "Descending"])

    st.subheader("Duplicate Detection")
    dup_col = st.selectbox("Duplicate Check Column", df.columns)

    if st.button("Run Processing"):
        ascending = order == "Ascending"

        # ---------------------------------------------------------
        # SECONDARY SORT LOGIC:
        # Create helper column: 0 if Constituency Code starts with a number, else 1
        # This ensures numeric-prefixed codes always rise to the top *within each group*
        # ---------------------------------------------------------
        df["_cc_priority"] = df["Constituency Code"].str.match(r"^\d").apply(lambda x: 0 if x else 1)

        # ---------------------------------------------------------
        # MAIN SORT:
        # 1. Primary sort column (user choice)
        # 2. Secondary: numeric-prefixed Constituency Codes first
        # 3. Tertiary: alphabetical Constituency Code
        # ---------------------------------------------------------
        sorted_df = df.sort_values(
            by=[sort_col, "_cc_priority", "Constituency Code"],
            ascending=[ascending, True, True]
        ).drop(columns=["_cc_priority"])

        # ---------------------------------------------------------
        # DUPLICATES SORT:
        # Apply the same group-aware numeric-first logic
        # ---------------------------------------------------------
        duplicates_df = (
            df[df[dup_col].duplicated(keep=False)]
            .sort_values(
                by=[dup_col, "_cc_priority", "Constituency Code"],
                ascending=[ascending, True, True]
            )
            .drop(columns=["_cc_priority"])
        )

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
            data=to_excel_bytes(duplicates_df),
            file_name="duplicates_output.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )