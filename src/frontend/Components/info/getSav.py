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
        # Only wipe sav_data if we never had a file — don't clear it on
        # incidental reruns (e.g. sidebar delete) where uploader resets to None
        if st.session_state.sav_data is None:
            st.session_state.sav_data = None  # already None, no-op
        # If sav_data is already loaded, leave it alone
        return

    # A file is uploaded — process it only if it's new
    if st.session_state.sav_data is None or st.session_state.sav_data.get('file_id') != uploaded_sav.file_id:
        with st.spinner("Processing SAV file..."):
            st.session_state.sav_data = SPSSMatchProcessor.get_essentials_from_sav(
                uploaded_sav, st.session_state.name1, st.session_state.name2
            )
            st.session_state.sav_data['file_id'] = uploaded_sav.file_id
            st.session_state.skip = False

        st.success(f"SAV file uploaded: {uploaded_sav.name}")