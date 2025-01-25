import importlib
import sys

import streamlit as st
from st_pages import get_nav_from_toml, add_page_title

from src.pages import main_page, comments_list_page


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

# Dynamically call the page-specific function based on the selected page
if pg.title == "Bee Balanced":
    with placeholder.container():
        main_page.get_page()
if pg.title == "Comments List":
    with placeholder.container():
        comments_list_page.get_page()
