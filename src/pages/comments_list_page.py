import logging
import streamlit as st
from src.api import hive_sql

log = logging.getLogger("Main Page")


def get_page():
    st.title('Select unique hive commentators')
    st.markdown("""
    Enter permlink to retrieve commentators on a post <br>
    Permlink is the end an url.<br>
    
    e.g.:<br>
    url: https://peakd.com/hive-13323/@splinterlands/splinterlands-community-engagement-challenge-favorite-strategies-sqkhvm<br>
    permlink: splinterlands-community-engagement-challenge-favorite-strategies-sqkhvm
    """, unsafe_allow_html=True)

    permlinks = st.text_input('space separated permlinks')
    permlinks = [name.strip() for name in permlinks.split(' ') if name.strip()]
    if permlinks:
        log.info(f'Analysing commentators: {permlinks}')

        with st.spinner('Loading data... Please wait.'):
            authors = hive_sql.get_commentators(permlinks)
            if authors:
                authors_string = ' '.join(authors)

                # Display the list of authors
                st.write(f'### Unique Commenters: {len(authors)} (Depth 1)')

                # Add a button to copy the list to the clipboard
                st.write('### Copy List to Clipboard:')
                st.text_area('space separated authors:', authors_string, height=100)
            else:
                st.write(f"### No authors found for '{permlinks}'")
