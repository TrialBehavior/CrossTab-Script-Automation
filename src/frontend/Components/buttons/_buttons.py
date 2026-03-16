import streamlit as st

def _render_syntax_extract_button():
    """Render the syntax extract button component."""
    st.divider()
    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([2, 3, 2])
    with col2:
        if st.button(
            "⚖️ Generate SPSS Syntax",
            type="primary",
            use_container_width=True,
            key="generate_syntax_btn"
        ):
            st.session_state.button['ready_to_syntax'] = True

    st.markdown("<br>", unsafe_allow_html=True)