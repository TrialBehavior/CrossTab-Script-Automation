"""SAV file processing UI component - UPDATED for refactored architecture"""
import streamlit as st
from src.backend.sav.spss_syntax import SPSSSyntaxGenerator, RecodeResult


def render_sav_processor():
    """
    Render the SAV file processor component.
    
    Handles SAV file processing and results display.
    Uses data already loaded in session state.
    """
    st.subheader("📊 SPSS Syntax Generator")
    
    # Check if everything is ready
    if not _has_extracted_statements():
        st.warning("⚠️ Please extract Q4 arguments first")
        return
    
    if 'sav_data' not in st.session_state or st.session_state.sav_data is None:
        st.warning("⚠️ Please upload SAV file first")
        return
    
    # Generate syntax from already loaded data
    _generate_and_display_syntax()


def _has_extracted_statements() -> bool:
    """Check if statements have been extracted from Q4 PDF"""
    return (st.session_state.name1_highlights is not None and 
            st.session_state.name2_highlights is not None)


def _generate_and_display_syntax():
    """
    Generate SPSS syntax from session state data.
    """
    try:
        # Get SAV data from session state
        sav_data = st.session_state.sav_data
        
        # Create syntax generator with the NEW refactored class
        syntax_generator = SPSSSyntaxGenerator(
            sav_labels=sav_data['sav_labels'],
            name1=st.session_state.name1,
            name2=st.session_state.name2
        )
        
        # Generate script
        result: RecodeResult = syntax_generator.generate_recode_script(
            name1_questions=st.session_state.name1_highlights,
            name2_questions=st.session_state.name2_highlights,
            recode_settings=st.session_state.recode_settings
        )
        
        # Display results
        _display_results(result)
        
    except Exception as e:
        st.error(f"❌ Error generating syntax: {str(e)}")
        st.exception(e)


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