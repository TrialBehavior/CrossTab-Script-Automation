import streamlit as st
from src.frontend.Components.pdf_extractor import render_pdf_extractor
from src.frontend.Components.recode import render_recode_configurator
from src.frontend.Components.sav_processor import render_sav_processor

# Page configuration
st.set_page_config(
    page_title="Juror Information Extractor",
    page_icon="⚖️",
    layout="wide"
)

# Title
st.title("⚖️ Juror Information Extractor")
st.write("Upload a PDF to extract juror information")

# Initialize session state
if 'plaintiff_highlights' not in st.session_state:
    st.session_state.plaintiff_highlights = None
if 'defense_highlights' not in st.session_state:
    st.session_state.defense_highlights = None
if 'recode_settings' not in st.session_state:
    st.session_state.recode_settings = {}

# Component 1: PDF Extractor
st.divider()
render_pdf_extractor()

# Component 2: Recode Configurator (only if statements extracted)
if (st.session_state.plaintiff_highlights is not None and 
    st.session_state.defense_highlights is not None):
    st.divider()
    render_recode_configurator()

# Component 3: SAV Processor
st.divider()
render_sav_processor()
