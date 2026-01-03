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
    
    if uploaded_sav is not None:
        with st.spinner("Processing SAV file..."):
            essentials = SPSSMatchProcessor.get_essentials_from_sav(uploaded_sav,st.session_state.name1,st.session_state.name2)
            st.session_state.sav_data = essentials
        
        st.success(f"SAV file uploaded: {uploaded_sav.name}")