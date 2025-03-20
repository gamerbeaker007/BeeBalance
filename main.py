import importlib
import logging
import sys

import streamlit as st
from st_pages import get_nav_from_toml, add_page_title

from src.pages import main_page, comments_list_page, top_holders_page, custom_queries_page, spl_metrics_page
from src.util import authentication


def reload_all():
    """Reload all imported modules. workaround for streamlit to load also changed modules"""
    for module_name in list(sys.modules.keys()):
        # Reload only modules that are not built-in and not part of the standard library
        if module_name.startswith("src"):
            importlib.reload(sys.modules[module_name])


reload_all()

st.set_page_config(page_title="Hive Bee Balanced", layout="wide")

nav = get_nav_from_toml('.streamlit/pages.toml')
pg = st.navigation(nav)

add_page_title(pg)

placeholder = st.empty()

# Configure logging globally
logging.basicConfig(
    level=logging.INFO,  # Set the logging level
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",  # Log format
    datefmt="%Y-%m-%d %H:%M:%S",  # Date format
)

# Set up session state to remember authentication
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

# Dynamically call the page-specific function based on the selected page
if pg.title == "Bee Balanced":
    with placeholder.container():
        main_page.get_page()
if pg.title == "Comments List":
    with placeholder.container():
        comments_list_page.get_page()
if pg.title == "Top Holders":
    with placeholder.container():
        authentication.get_page()
        top_holders_page.get_page()
if pg.title == "Custom Queries":
    with placeholder.container():
        authentication.get_page()
        custom_queries_page.get_page()
if pg.title == "SPL Metrics":
    with placeholder.container():
        spl_metrics_page.get_page()
