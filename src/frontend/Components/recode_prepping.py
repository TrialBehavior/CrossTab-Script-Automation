import streamlit as st
import io
from src.backend.file_extract.PDF_implementation import PDFHandler1
from src.backend.sav.spss_match_processor import SPSSMatchProcessor

def _render_recode_prepping(Q4_file):
    """Extract arguments from Q4 PDF file and prepare recode settings"""
    pdf_handler = PDFHandler1()
    Q4_file.seek(0)
    
    # Find pages with name1 and name2 arguments
    name2_pages = pdf_handler.find_pages_with_text(Q4_file, f"{st.session_state.name2} Arguments")
    Q4_file.seek(0)
    name1_pages = pdf_handler.find_pages_with_text(Q4_file, f"{st.session_state.name1} Arguments")
    
    st.write(f"{st.session_state.name2} Arguments found on pages: {[p+1 for p in name2_pages]}")
    st.write(f"{st.session_state.name1} Arguments found on pages: {[p+1 for p in name1_pages]}")
    
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
    
    # Initialize recode settings with actual value ranges from SAV
    _initialize_recode_settings()


def _get_value_range(column_name):
    """
    Extract the actual value range for a question from SAV metadata.
    
    Args:
        column_name: The column name (e.g., "Plaaffs_3", "Q1")
        
    Returns:
        List of numeric values in order, or None if no value labels exist
    """
    meta = st.session_state.sav_data['meta']
    
    if column_name in meta.variable_value_labels:
        # Get the value codes and sort them
        values = sorted(meta.variable_value_labels[column_name].keys())
        return values
    return None


def _initialize_recode_settings():
    """Initialize recode settings for all statements (plaintiff, defense, and neutral)"""
    
    # Create SPSS processor to get general questions
    processor = SPSSMatchProcessor(
        sav_labels=st.session_state.sav_data['sav_labels'],
        name1=st.session_state.name1,
        name2=st.session_state.name2
    )
    
    # Get general/neutral questions
    general_questions = processor.get_all_general_questions()
    
    # Initialize for name1 (plaintiff) statements
    if st.session_state.name1_highlights:
        for statement in st.session_state.name1_highlights:
            if statement not in st.session_state.recode_settings:
                # For now, we'll match later, so just use default column
                # This will be updated when we do the actual matching
                st.session_state.recode_settings[statement] = {
                    'party': 'name1',
                    'matched_column': None,  # Will be filled during matching
                    'range1_start': None,
                    'range1_end': None,
                    'range1_becomes': 1,
                    'range2_start': None,
                    'range2_end': None,
                    'range2_becomes': 2
                }
    
    # Initialize for name2 (defense) statements
    if st.session_state.name2_highlights:
        for statement in st.session_state.name2_highlights:
            if statement not in st.session_state.recode_settings:
                st.session_state.recode_settings[statement] = {
                    'party': 'name2',
                    'matched_column': None,
                    'range1_start': None,
                    'range1_end': None,
                    'range1_becomes': 2,
                    'range2_start': None,
                    'range2_end': None,
                    'range2_becomes': 1
                }
    
    # Initialize for neutral/general questions
    for column, label in general_questions:
        if label not in st.session_state.recode_settings:
            values = _get_value_range(column)
            if values and len(values) >= 4:
                # Assume neutral questions don't get reversed
                st.session_state.recode_settings[label] = {
                    'party': 'neutral',
                    'matched_column': column,
                    'range1_start': values[0],
                    'range1_end': values[1],
                    'range1_becomes': 1,
                    'range2_start': values[2],
                    'range2_end': values[3],
                    'range2_becomes': 2
                }


def update_recode_with_match(statement, matched_column):
    """
    Update recode settings once a statement is matched to a column.
    
    Args:
        statement: The highlighted statement text
        matched_column: The SAV column it matched to
    """
    if statement in st.session_state.recode_settings:
        values = _get_value_range(matched_column)
        
        if values and len(values) >= 4:
            settings = st.session_state.recode_settings[statement]
            settings['matched_column'] = matched_column
            settings['range1_start'] = values[0]
            settings['range1_end'] = values[1]
            settings['range2_start'] = values[2]
            settings['range2_end'] = values[3]