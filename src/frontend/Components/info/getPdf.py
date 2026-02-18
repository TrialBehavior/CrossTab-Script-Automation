import streamlit as st
from src.backend.file_extract.PDF_implementation import PDFHandler1

def render_get_pdf():
    """
    Render the PDF upload component.
    
    Returns:
        None (updates session state with pdf_data)
    """
    pdf_handler = PDFHandler1()
    st.subheader("📄 Upload Q4 PDF")
    # File uploaders (store in temporary variables)
    uploaded_pdf = st.file_uploader("Upload Q4 PDF file", type="pdf", key="q4")

    if uploaded_pdf is None:
        st.session_state.pdf_data = None
    elif st.session_state.pdf_data is None or st.session_state.get('pdf_file_id') != uploaded_pdf.file_id:
        st.session_state.pdf_data = uploaded_pdf.read()
        if st.session_state.get('pdf_file_id') != uploaded_pdf.file_id:
            st.session_state.skip = False
        st.session_state.pdf_file_id = uploaded_pdf.file_id
        
        st.success(f"PDF uploaded: {uploaded_pdf.name}")