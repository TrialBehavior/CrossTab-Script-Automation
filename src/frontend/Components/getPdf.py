import streamlit as st
from src.backend.file_extract.PDF_implementation import PDFHandler1

def render_get_pdf():
    """
    Render the PDF upload component.
    
    Returns:
        None (updates session state with pdf_data)
    """
    pdf_handler = PDFHandler1()
    st.subheader("📄 Upload Q4 PDF or DOCX")
    # File uploaders (store in temporary variables)
    uploaded_pdf = st.file_uploader("Upload Q4 PDF file", type="pdf", key="q4")
    uploaded_docx = st.file_uploader("Upload Q4 DOCX file", type="docx", key="q4_doc")
    # Process PDF upload
    if uploaded_pdf is not None:
        st.session_state.pdf_data = uploaded_pdf.read()
        st.success(f"PDF uploaded: {uploaded_pdf.name}")
    
    # Process DOCX upload and convert to PDF
    if uploaded_docx is not None:
        with st.spinner("Converting DOCX to PDF..."):
            pdf_bytes = pdf_handler.docx_to_pdf(uploaded_docx)
            st.session_state.pdf_data = pdf_bytes
        st.success(f"DOCX converted to PDF: {uploaded_docx.name}")