import streamlit as st

from src.api import hive_sql


def get_page():
    st.title('Select unique hive commentators')
    st.write('Enter permlink to retrieve commentators on a post')
    st.write('Permlink is the end an url.')
    st.write('e.g.:')
    st.write('url: https://peakd.com/hive-13323/@splinterlands/splinterlands-community-engagement-challenge-favorite'
             '-strategies-sqkhvm')
    st.write('permlink: splinterlands-community-engagement-challenge-favorite-strategies-sqkhvm')

    permlinks = st.text_input('space separated permlinks')

    permlinks = [name.strip() for name in permlinks.split(' ') if name.strip()]
    if permlinks:
        with st.spinner('"Loading data... Please wait."'):
            authors = hive_sql.get_commentators(permlinks)
            if authors:
                authors_string = ' '.join(authors)

                # Display the list of authors
                st.write('### Unique Commenters:')
                st.write(authors)

                # Add a button to copy the list to the clipboard
                st.write('### Copy List to Clipboard:')
                st.text_area('space separated authors:', authors_string, height=100)
            else:
                st.write(f"### No authors found for '{permlinks}'")
