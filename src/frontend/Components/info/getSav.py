"""SAV file processing UI component"""
import streamlit as st
import pyreadstat
import tempfile
import os
from src.backend.sav.spss_match_processor import SPSSMatchProcessor


def render_get_sav():
    """Render the SAV file upload component."""
    st.subheader("📊 Upload SAV/SPSS File")
    #a little scuff but basically check is the first time uploading sav file, if so, run the processor and set skip to false, 
    uploaded_sav = st.file_uploader("Upload SAV/SPSS file", type="sav", key="sav")

    if uploaded_sav is None:
        st.session_state.sav_data = None
    elif st.session_state.sav_data is None or st.session_state.sav_data.get('file_id') != uploaded_sav.file_id:
        with st.spinner("Processing SAV file..."):
            st.session_state.sav_data = SPSSMatchProcessor.get_essentials_from_sav(uploaded_sav, st.session_state.name1, st.session_state.name2)
            if st.session_state.sav_data.get('file_id') != uploaded_sav.file_id:
                st.session_state.skip = False
            st.session_state.sav_data['file_id'] = uploaded_sav.file_id
        st.success(f"SAV file uploaded: {uploaded_sav.name}")