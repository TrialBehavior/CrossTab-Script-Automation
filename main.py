import streamlit as st
from src.frontend.Components.user_recoding.recode_prepping import _render_recode_prepping
from src.frontend.Components.user_recoding.plaintiff_defense_recode import _render_recode_configurator
from src.frontend.Components.sav_processor import render_sav_processor
from src.frontend.Components.info.getName import render_name_input
from src.frontend.Components.info.getPdf import render_get_pdf
from src.frontend.Components.info.getSav import render_get_sav
from src.frontend.Components.buttons._buttons import _render_syntax_extract_button
from src.frontend.Components.user_recoding.neutral_question_selector import _render_neutral_question_selector
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
if 'neutral_index' not in st.session_state:
    st.session_state.neutral_index = 0

if 'all_questions' not in st.session_state:
    st.session_state.all_questions = {}
if 'selected_neutral_questions' not in st.session_state:
    st.session_state.selected_neutral_questions = {}

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

if 'button' not in st.session_state:
    st.session_state.button = {
        'ready_to_syntax': False
    }

# Component 1: Get Name
render_name_input()
st.divider()

# Component 2: Get PDF / DOC
if st.session_state.getName_touched:
    render_get_pdf()

# Component 3: Get SAV file and extract labels
if (st.session_state.pdf_data is not None and st.session_state.name1 is not None and st.session_state.name2 is not None):
    render_get_sav()

# Component 3.5: pdf_extractor and populate all question database
if st.session_state.sav_data is not None:
    st.divider()
    _render_recode_prepping(io.BytesIO(st.session_state.pdf_data))

# Component 4: Recode For Plaintiff, Defense, and Neutral
if st.session_state.name1_highlights and st.session_state.name2_highlights:
    st.divider()
    _render_recode_configurator()
    _render_neutral_question_selector()
    _render_syntax_extract_button()

# Component 5: Generate SPSS Recode Syntax
if st.session_state.button['ready_to_syntax']:
    # Prepare selected neutral questions for syntax generation
    # prepare_neutral_questions_for_syntax()
    
    st.divider()
    st.subheader("Generating SPSS Recode Syntax...")
    render_sav_processor()