import io
from unittest.mock import MagicMock

import pandas as pd
import pytest
# Mock Streamlit functions for testing
import streamlit as st

from src.pages.custom_queries_subpages.upload_section import MAX_FILE_SIZE, detect_encoding, sanitize_csv, \
    get_import_section

# Simulated CSV files with different encodings and issues
CSV_UTF8 = "name,age\nAlice,30\nBob,25"
CSV_ISO8859 = "name,age\nÉlise,29\nJürgen,35".encode("ISO-8859-1")
CSV_WITH_FORMULA_INJECTION = "name,age\n=SUM(A1:A3),30\nBob,25"
EMPTY_CSV = ""
CVS_INVALID_COLUMNS = """
name, age, gender
aap ,  10
"""
CVS_MIXED_ROWS = """
name, age, gender
aap ,  10, Male
Apple, Yes, 10
"""


# ------------------------- #
# TESTS FOR ENCODING DETECTION
# ------------------------- #
def test_detect_encoding_utf8():
    file = io.BytesIO(CSV_UTF8.encode("utf-8"))
    assert detect_encoding(file) == "utf-8"


def test_detect_encoding_iso8859():
    file = io.BytesIO(CSV_ISO8859)
    assert detect_encoding(file) == "ISO-8859-1"


def test_detect_encoding_empty_file():
    file = io.BytesIO(EMPTY_CSV.encode("utf-8"))
    assert detect_encoding(file) is None  # Should return None or fail gracefully


# ------------------------- #
# TESTS FOR CSV SANITIZATION
# ------------------------- #
def test_sanitize_csv():
    df = pd.DataFrame({"name": ["=SUM(A1:A3)", "Bob"], "age": [30, 25]})
    sanitized_df = sanitize_csv(df)
    assert sanitized_df["name"][0] == "SUM(A1:A3)"  # The "=" should be removed
    assert sanitized_df["name"][1] == "Bob"  # Should remain unchanged


def test_sanitize_csv_no_change():
    df = pd.DataFrame({"name": ["Alice", "Bob"], "age": [30, 25]})
    sanitized_df = sanitize_csv(df)
    assert sanitized_df.equals(df)  # Should not modify clean data


# ------------------------- #
# TESTS FOR FILE UPLOAD HANDLING
# ------------------------- #
@pytest.mark.parametrize("csv_content, expected_valid", [
    (CSV_UTF8, True),  # Valid UTF-8 CSV
    (CSV_WITH_FORMULA_INJECTION, True),  # Should be sanitized successfully
    (EMPTY_CSV, False),  # Should fail with "file is empty"
    (CVS_INVALID_COLUMNS, True),
    (CVS_MIXED_ROWS, True),
])
def test_file_upload(csv_content, expected_valid, monkeypatch):
    """Mocks Streamlit UI behavior and tests file handling."""

    # Mock the file uploader return value
    uploaded_file = io.BytesIO(csv_content.encode("utf-8"))
    uploaded_file.size = len(csv_content.encode("utf-8"))

    # Patch Streamlit UI elements
    monkeypatch.setattr(st, "file_uploader", lambda *args, **kwargs: uploaded_file)
    monkeypatch.setattr(st, "error", MagicMock())
    monkeypatch.setattr(st, "success", MagicMock())

    # Call function and check result
    df = get_import_section()

    if expected_valid:
        assert not df.empty
        st.success.assert_called_once()  # Should show success message
    else:
        assert df.empty
        st.error.assert_called_once()  # Should show error message
