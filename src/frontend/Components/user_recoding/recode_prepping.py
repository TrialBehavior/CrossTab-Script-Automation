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
    
    _initialize_recode_settings()


def _get_value_range(column_name):
    """Extract the actual value range for a question from SAV metadata"""
    meta = st.session_state.sav_data['meta']
    
    if column_name in meta.variable_value_labels:
        values = sorted(meta.variable_value_labels[column_name].keys())
        return values
    return None


def _initialize_recode_settings():
    """Initialize recode settings for all statements"""
    processor = SPSSMatchProcessor(
        sav_labels=st.session_state.sav_data['sav_labels'],
        name1=st.session_state.name1,
        name2=st.session_state.name2
    )
    
    _initialize_plaintiff_recodes(processor)
    _initialize_defense_recodes(processor)
    _initialize_neutral_recodes(processor)


def _initialize_plaintiff_recodes(processor: SPSSMatchProcessor):
    """Initialize recode settings for plaintiff (name1) statements"""
    if not st.session_state.name1_highlights:
        return
    
    for statement in st.session_state.name1_highlights:
        if statement not in st.session_state.recode_settings:
            matched_column = processor._find_column(statement)
            values = _get_value_range(matched_column) if matched_column else None
            
            st.session_state.recode_settings[statement] = _create_recode_config(
                party='name1',
                matched_column=matched_column,
                values=values,
                favorable_becomes=1,
                unfavorable_becomes=2
            )


def _initialize_defense_recodes(processor: SPSSMatchProcessor):
    """Initialize recode settings for defense (name2) statements"""
    if not st.session_state.name2_highlights:
        return
    
    for statement in st.session_state.name2_highlights:
        if statement not in st.session_state.recode_settings:
            matched_column = processor._find_column(statement)
            values = _get_value_range(matched_column) if matched_column else None
            
            st.session_state.recode_settings[statement] = _create_recode_config(
                party='name2',
                matched_column=matched_column,
                values=values,
                favorable_becomes=2,
                unfavorable_becomes=1
            )


def _initialize_neutral_recodes(processor: SPSSMatchProcessor):
    """Initialize recode settings for neutral/general questions"""
    general_questions = processor.get_all_general_questions()
    if not general_questions:
        print("⚠️ No general/neutral questions found in SAV file")
        return
    
    for column, label in general_questions:
        values = _get_value_range(column)
        
        st.session_state.all_questions[label] = _create_recode_config(
            party='neutral',
            matched_column=column,
            values=values,
            favorable_becomes=1,
            unfavorable_becomes=2,
            include_label=True,
            label=label
        )


def _create_recode_config(
    party: str,
    matched_column: str,
    values: list,
    favorable_becomes: int,
    unfavorable_becomes: int,
    include_label: bool = False,
    label: str = None
) -> dict:
    """Create a recode configuration dictionary"""
    is_continuous = (matched_column and values is None)
    
    config = {'party': party, 'matched_column': matched_column}
    
    if include_label:
        config['column'] = matched_column
        config['label'] = label
    
    if is_continuous:
        config.update({
            'variable_type': 'continuous',
            'range1_operator': '<=',
            'range1_value': 50,
            'range1_becomes': favorable_becomes,
            'range2_operator': '>',
            'range2_value': 50,
            'range2_becomes': unfavorable_becomes
        })
    elif values and len(values) >= 4:
        config.update({
            'variable_type': 'categorical',
            'range1_start': values[0],
            'range1_end': values[1],
            'range1_becomes': favorable_becomes,
            'range2_start': values[2],
            'range2_end': values[3],
            'range2_becomes': unfavorable_becomes
        })
        if include_label:
            config['original_values'] = values
    elif values and len(values) >= 2 and include_label:
        config.update({
            'variable_type': 'categorical',
            'original_values': values,
            'range1_start': values[0],
            'range1_end': values[0],
            'range1_becomes': favorable_becomes,
            'range2_start': values[1],
            'range2_end': values[1],
            'range2_becomes': unfavorable_becomes
        })
    else:
        config.update({
            'variable_type': 'unknown',
            'range1_start': None,
            'range1_end': None,
            'range1_becomes': favorable_becomes,
            'range2_start': None,
            'range2_end': None,
            'range2_becomes': unfavorable_becomes
        })
    
    return config


def update_recode_with_match(statement, matched_column):
    """Update recode settings once a statement is matched to a column"""
    if statement in st.session_state.recode_settings:
        values = _get_value_range(matched_column)
        
        if values and len(values) >= 4:
            settings = st.session_state.recode_settings[statement]
            settings['matched_column'] = matched_column
            settings['range1_start'] = values[0]
            settings['range1_end'] = values[1]
            settings['range2_start'] = values[2]
            settings['range2_end'] = values[3]