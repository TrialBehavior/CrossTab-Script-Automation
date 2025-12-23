import streamlit as st
from src.frontend.Components.pdf_extractor import render_pdf_extractor
from src.frontend.Components.recode import render_recode_configurator
from src.frontend.Components.sav_processor import render_sav_processor
from src.frontend.Components.getName import render_name_input
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
if 'name1_highlights' not in st.session_state:
    st.session_state.name1_highlights = None
if 'name2_highlights' not in st.session_state:
    st.session_state.name2_highlights = None
if 'recode_settings' not in st.session_state:
    st.session_state.recode_settings = {}
if 'name1' not in st.session_state:
    st.session_state.name1 = "Plaintiff"
if 'name2' not in st.session_state:
    st.session_state.name2 = "Defense"
if 'getName_touched' not in st.session_state:
    st.session_state.getName_touched = False
# Component 2: PDF Extractor
render_name_input()
st.divider()
if(st.session_state.getName_touched == True):
    render_pdf_extractor()

# Component 3: Recode Configurator (only if statements extracted)
if (st.session_state.name1_highlights is not None and 
    st.session_state.name2_highlights is not None):
    st.divider()
    render_recode_configurator()

# Component 4: SAV Processor
st.divider()
render_sav_processor()
