import streamlit as st
import io
from src.backend.file_extract.PDF_abstract import PDFProcessor
from src.backend.file_extract.PDF_implementation import PDFHandler1

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
    
    # Find pages with name1 and name2 arguments
    name2_pages = pdf_handler.find_pages_with_text(Q4_file, f"{st.session_state.name2} Arguments")
    Q4_file.seek(0)
    name1_pages = pdf_handler.find_pages_with_text(Q4_file, f"{st.session_state.name1} Arguments")
    
    st.write(f"🔵 {st.session_state.name2} Arguments found on pages: {[p+1 for p in name2_pages]}")
    st.write(f"🔴 {st.session_state.name1} Arguments found on pages: {[p+1 for p in name1_pages]}")
    
    # Extract name2 highlights
    if name2_pages:
        Q4_file.seek(0)
        name2_pdf_bytes = pdf_handler.split_pdf_by_pages(Q4_file, name2_pages)
        st.session_state.name2_highlights = pdf_handler.extract_highlighted_statements(io.BytesIO(name2_pdf_bytes))
    else:
        st.warning("⚠️ No highlighted text found in name2 Arguments pages")

    # Extract name1 highlights
    if name1_pages:
        Q4_file.seek(0)
        name1_pdf_bytes = pdf_handler.split_pdf_by_pages(Q4_file, name1_pages)
        st.session_state.name1_highlights = pdf_handler.extract_highlighted_statements(io.BytesIO(name1_pdf_bytes))
    else:
        st.warning("⚠️ No highlighted text found in name1 Arguments pages")
        
    if not name2_pages and not name1_pages:
        st.warning("⚠️ Neither name2 Arguments nor name1 Arguments found in PDF")
    
    # Initialize default recode settings
    _initialize_recode_settings()


def _initialize_recode_settings():
    """Initialize default recode settings for extracted statements"""
    # Initialize for name1 statements
    if st.session_state.name1_highlights:
        for statement in st.session_state.name1_highlights:
            if statement not in st.session_state.recode_settings:
                st.session_state.recode_settings[statement] = {
                    'range1_start': 1,
                    'range1_end': 2,
                    'range1_becomes': 1,
                    'range2_start': 3,
                    'range2_end': 4,
                    'range2_becomes': 2
                }
    
    # Initialize for name2 statements
    if st.session_state.name2_highlights:
        for statement in st.session_state.name2_highlights:
            if statement not in st.session_state.recode_settings:
                st.session_state.recode_settings[statement] = {
                    'range1_start': 1,
                    'range1_end': 2,
                    'range1_becomes': 2,
                    'range2_start': 3,
                    'range2_end': 4,
                    'range2_becomes': 1
                }