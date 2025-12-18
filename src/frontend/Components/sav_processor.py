"""SAV file processing UI component"""
import streamlit as st
import pyreadstat
import tempfile
import os
from src.backend.sav.sav_abstract import RecodeResult
from src.backend.sav.sav_handler import SavHandler


def render_sav_processor():
    """
    Render the SAV file processor component.
    
    Handles SAV file upload, processing, and results display.
    """
    st.subheader("📊 SPSS Syntax Generator")
    
    # Check if Q4 has been extracted
    if not _has_extracted_statements():
        st.warning("⚠️ Please extract Q4 arguments first before uploading SAV file")
        return
    
    # SAV file uploader
    sav_file = st.file_uploader("Upload SAV/SPSS file", type="sav", key="sav")
    
    if sav_file is not None:
        _process_sav_file(sav_file)


def _has_extracted_statements() -> bool:
    """Check if statements have been extracted from Q4 PDF"""
    return (st.session_state.plaintiff_highlights is not None and 
            st.session_state.defense_highlights is not None)


def _process_sav_file(sav_file):
    """
    Process the uploaded SAV file and generate SPSS syntax.
    
    Args:
        sav_file: Uploaded SAV file
    """
    # Save to temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix='.sav') as tmp_file:
        tmp_file.write(sav_file.read())
        tmp_path = tmp_file.name
    
    try:
        # Read SAV file
        df, meta = pyreadstat.read_sav(tmp_path)
        
        # Create SAV handler and generate script
        sav_handler = SavHandler(list(meta.column_names_to_labels.items()))
        
        result: RecodeResult = sav_handler.generate_recode_script(
            plaintiff_questions=st.session_state.plaintiff_highlights,
            defense_questions=st.session_state.defense_highlights,
            recode_settings=st.session_state.recode_settings
        )
        
        # Display results
        _display_results(result)
        
    finally:
        # Clean up temporary file
        os.unlink(tmp_path)


def _display_results(result: RecodeResult):
    """
    Display the processing results.
    
    Args:
        result: RecodeResult containing script and matches
    """
    # Show statistics
    st.info(
        f"✅ Matched: {len(result.matched)} statements | "
        f"❌ Unmatched: {len(result.unmatched)} statements"
    )
    
    # Display generated SPSS syntax
    st.subheader("Generated SPSS Syntax")
    st.code(result.script, language="sql")
    
    # Download button
    st.download_button(
        label="📥 Download SPSS Syntax",
        data=result.script,
        file_name="recode_syntax.sps",
        mime="text/plain",
        type="primary"
    )
    
    # Display unmatched statements
    if result.unmatched:
        _display_unmatched_statements(result.unmatched)
    
    # Optional: Show matched statements
    _display_matched_statements(result.matched)


def _display_unmatched_statements(unmatched: list[tuple[str, str]]):
    """Display statements that couldn't be matched"""
    st.subheader("❌ Statements Not Found in SAV File")
    st.write(
        f"These {len(unmatched)} highlighted statements couldn't be matched "
        f"to any variable labels:"
    )
    
    for side, statement in unmatched:
        with st.expander(f"[{side}] {statement[:80]}..."):
            st.write(statement)


def _display_matched_statements(matched: list[tuple[str, str]]):
    """Display successfully matched statements"""
    with st.expander(f"✅ Show {len(matched)} Matched Statements"):
        for side, statement in matched:
            st.write(f"**[{side}]** {statement}")