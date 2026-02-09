import streamlit as st
def _render_syntax_extract_button():
    """Render the syntax extract button component."""
    if st.button("Ready to Generate Syntax"):
        st.session_state.button['ready_to_syntax'] = True