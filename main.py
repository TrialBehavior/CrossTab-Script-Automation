import streamlit as st
from src.frontend.Components.recode_prepping import _render_recode_prepping
from src.frontend.Components.recode import _render_recode_configurator
# from src.frontend.Components.sav_processor import render_sav_processor
from src.frontend.Components.getName import render_name_input
from src.frontend.Components.getPdf import render_get_pdf
from src.frontend.Components.getSav import render_get_sav
import io

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
if 'pdf_data' not in st.session_state:
    st.session_state.pdf_data = None
if 'sav_data' not in st.session_state:
    st.session_state.sav_data = None
if 'name1' not in st.session_state:
    st.session_state.name1 = "Plaintiff"
if 'name2' not in st.session_state:
    st.session_state.name2 = "Defense"
if 'getName_touched' not in st.session_state:
    st.session_state.getName_touched = False
if 'sav_data' not in st.session_state:
    st.session_state.sav_data = None
# Component 1: Get Name
render_name_input()
st.divider()

#Component 2: Get PDF / DOC
if(st.session_state.getName_touched == True):
    render_get_pdf()
#Component 3: Get SAV / DOC 
if (st.session_state.pdf_data is not None and
    st.session_state.name1 is not None and 
    st.session_state.name2 is not None):
    render_get_sav()

# Component 3.5: pdf_extractor
#less of an actual ui and more just like a transition phrase between 3 and 4 where a lot of backend stuff occur and I want the actual components to be simply based on UI
if (st.session_state.sav_data is not None):
    st.divider()
    _render_recode_prepping(io.BytesIO(st.session_state.pdf_data))

# Component 5: Recode For Plaintiff And Defense
if (st.session_state.name1_highlights and st.session_state.name2_highlights):
    st.divider()
    _render_recode_configurator()

# render_sav_processor()
