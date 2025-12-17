import streamlit as st
import io
from src.backend.pdf.PDF_abstract import PDFProcessor
from src.backend.pdf.PDF_implementation import PDFHandler1

def render_pdf_extractor():
    """
    Render the PDF extraction component.
    
    Args:
        pdf_handler: Instance of PDFHandler from backend
        
    Returns:
        None (updates session state)
    """
    pdf_handler = PDFHandler1()
    st.subheader("📄 Extract Highlighted Arguments from Q4 PDF")
    
    Q4_file = st.file_uploader("Upload Q4 PDF file", type="pdf", key="q4")
    
    if Q4_file is not None:
        if st.button("🔍 Extract Arguments", type="primary"):
            with st.spinner("Processing Q4 PDF..."):
                try:
                    _extract_arguments(Q4_file, pdf_handler)
                    st.success("✅ Arguments extracted successfully!")
                        
                except Exception as e:
                    st.error(f"❌ Error processing Q4 PDF: {str(e)}")
                    st.exception(e)
    else:
        st.info("👆 Please upload a Q4 PDF file to extract arguments")


def _extract_arguments(Q4_file, pdf_handler):
    """Extract arguments from Q4 PDF file"""
    Q4_file.seek(0)
    
    # Find pages with Defense and Plaintiff arguments
    defense_pages = pdf_handler.find_pages_with_text(Q4_file, "Defense Arguments")
    Q4_file.seek(0)
    plaintiff_pages = pdf_handler.find_pages_with_text(Q4_file, "Plaintiff Arguments")
    
    st.write(f"🔵 Defense Arguments found on pages: {[p+1 for p in defense_pages]}")
    st.write(f"🔴 Plaintiff Arguments found on pages: {[p+1 for p in plaintiff_pages]}")
    
    # Extract defense highlights
    if defense_pages:
        Q4_file.seek(0)
        defense_pdf_bytes = pdf_handler.split_pdf_by_pages(Q4_file, defense_pages)
        st.session_state.defense_highlights = pdf_handler.extract_highlighted_statements(io.BytesIO(defense_pdf_bytes))
    else:
        st.warning("⚠️ No highlighted text found in Defense Arguments pages")

    # Extract plaintiff highlights
    if plaintiff_pages:
        Q4_file.seek(0)
        plaintiff_pdf_bytes = pdf_handler.split_pdf_by_pages(Q4_file, plaintiff_pages)
        st.session_state.plaintiff_highlights = pdf_handler.extract_highlighted_statements(io.BytesIO(plaintiff_pdf_bytes))
    else:
        st.warning("⚠️ No highlighted text found in Plaintiff Arguments pages")
        
    if not defense_pages and not plaintiff_pages:
        st.warning("⚠️ Neither Defense Arguments nor Plaintiff Arguments found in PDF")
    
    # Initialize default recode settings
    _initialize_recode_settings()


def _initialize_recode_settings():
    """Initialize default recode settings for extracted statements"""
    # Initialize for plaintiff statements
    if st.session_state.plaintiff_highlights:
        for statement in st.session_state.plaintiff_highlights:
            if statement not in st.session_state.recode_settings:
                st.session_state.recode_settings[statement] = {
                    'range1_start': 1,
                    'range1_end': 2,
                    'range1_becomes': 1,
                    'range2_start': 3,
                    'range2_end': 4,
                    'range2_becomes': 2
                }
    
    # Initialize for defense statements
    if st.session_state.defense_highlights:
        for statement in st.session_state.defense_highlights:
            if statement not in st.session_state.recode_settings:
                st.session_state.recode_settings[statement] = {
                    'range1_start': 1,
                    'range1_end': 2,
                    'range1_becomes': 2,
                    'range2_start': 3,
                    'range2_end': 4,
                    'range2_becomes': 1
                }