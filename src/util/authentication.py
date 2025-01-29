import streamlit as st

# Load the secret from the secrets.toml file
SECRET_PASSWORD = st.secrets["general"]["password"]


def authenticate(password_input):
    """Authenticate the user by comparing the input with the secret password."""
    if password_input == SECRET_PASSWORD:
        st.session_state.authenticated = True


def get_page():
    col1, col2, col3 = st.columns([4, 1, 1])  # Adjust the ratios to control alignment
    if st.session_state.authenticated:
        with col3:
            st.button('🔓 Unlocked', key='auth_button', disabled=True)
    else:
        with col2:  # Center column for input and button
            password_input = st.text_input('Password:', type='password', label_visibility="collapsed")
        with col3:  # Center column for input and button
            if st.button('🔒 Authorize'):
                authenticate(password_input)
                st.rerun()
