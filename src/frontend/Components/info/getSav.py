"""SAV file processing UI component"""
import streamlit as st
import pyreadstat
import tempfile
import os
from src.backend.sav.spss_match_processor import SPSSMatchProcessor


def render_get_sav():
    """Render the SAV file upload component."""
    st.subheader("📊 Upload SAV/SPSS File")

    uploaded_sav = st.file_uploader("Upload SAV/SPSS file", type="sav", key="sav")

    if uploaded_sav is None:
        st.session_state.sav_data = None
    elif st.session_state.sav_data is None or st.session_state.sav_data.get('file_id') != uploaded_sav.file_id:
        # Check file_id BEFORE overwriting sav_data so we don't lose the comparison
        is_new_file = (
            st.session_state.sav_data is None or
            st.session_state.sav_data.get('file_id') != uploaded_sav.file_id
        )
        with st.spinner("Processing SAV file..."):
            st.session_state.sav_data = SPSSMatchProcessor.get_essentials_from_sav(
                uploaded_sav, st.session_state.name1, st.session_state.name2
            )
            st.session_state.sav_data['file_id'] = uploaded_sav.file_id

        if is_new_file:
            st.session_state.skip = False

        st.success(f"SAV file uploaded: {uploaded_sav.name}")