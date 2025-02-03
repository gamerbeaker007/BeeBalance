import chardet
import pandas as pd
import streamlit as st

MAX_FILE_SIZE_MB = 10
MAX_FILE_SIZE = MAX_FILE_SIZE_MB * 1024 * 1024


def sanitize_csv(df):
    for col in df.select_dtypes(include=["object", "string"]).columns:  # Only sanitize text columns
        df[col] = df[col].replace(r"^=", "", regex=True)  # Remove formula injection
    return df


def detect_encoding(file):
    raw_data = file.read(10000)
    result = chardet.detect(raw_data)
    file.seek(0)
    return result['encoding']


def hide_drag_and_drop():
    # Hide the drag & drop area
    st.markdown("""
        <style>
        .stFileUploader div[data-testid="stFileDropzone"] {
            display: none;
        }
        </style>
        """, unsafe_allow_html=True)


def get_import_section():
    with st.container():
        hide_drag_and_drop()
        uploaded_file = st.file_uploader("Upload CSV file", type=["csv"])

        if uploaded_file is not None:
            if uploaded_file.size > MAX_FILE_SIZE:
                st.error(f"❌ File too large! Max allowed: {MAX_FILE_SIZE_MB}MB.")
                st.stop()

            try:
                encoding = detect_encoding(uploaded_file)
                df = pd.read_csv(uploaded_file, encoding=encoding)
        
                df = sanitize_csv(df)  # Sanitize only string columns
        
                if df.empty:
                    st.error("❌ The uploaded file is empty. Please upload a valid CSV.")
                else:
                    st.success("✅ File uploaded successfully!")
                    return df
        
            except Exception as e:
                st.error(f"❌ Error processing file: {str(e)}")
        else:
            return pd.DataFrame()
