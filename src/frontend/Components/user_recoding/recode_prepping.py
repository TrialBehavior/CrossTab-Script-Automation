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
    """Initialize recode settings for all statements with actual SAV value ranges"""
    
    processor = SPSSMatchProcessor(
        sav_labels=st.session_state.sav_data['sav_labels'],
        name1=st.session_state.name1,
        name2=st.session_state.name2
    )
    
    general_questions = processor.get_all_general_questions()
    if not general_questions:
        print("⚠️ No general/neutral questions found in SAV file")
    
    # Initialize for name1 (plaintiff) statements
    if st.session_state.name1_highlights:
        for statement in st.session_state.name1_highlights:
            if statement not in st.session_state.recode_settings:
                matched_column = processor._find_column(statement)
                values = _get_value_range(matched_column) if matched_column else None
                
                # Determine if this is a categorical or continuous variable
                is_continuous = (matched_column and values is None)
                
                if is_continuous:
                    # Continuous variable - use numeric ranges
                    st.session_state.recode_settings[statement] = {
                        'party': 'name1',
                        'matched_column': matched_column,
                        'variable_type': 'continuous',
                        'range1_operator': '<=',
                        'range1_value': 50,
                        'range1_becomes': 1,
                        'range2_operator': '>',
                        'range2_value': 50,
                        'range2_becomes': 2
                    }
                elif values and len(values) >= 4:
                    # Categorical with 4+ values
                    st.session_state.recode_settings[statement] = {
                        'party': 'name1',
                        'matched_column': matched_column,
                        'variable_type': 'categorical',
                        'range1_start': values[0],
                        'range1_end': values[1],
                        'range1_becomes': 1,
                        'range2_start': values[2],
                        'range2_end': values[3],
                        'range2_becomes': 2
                    }
                else:
                    # No match or insufficient values
                    st.session_state.recode_settings[statement] = {
                        'party': 'name1',
                        'matched_column': matched_column,
                        'variable_type': 'unknown',
                        'range1_start': None,
                        'range1_end': None,
                        'range1_becomes': 1,
                        'range2_start': None,
                        'range2_end': None,
                        'range2_becomes': 2
                    }
    
    # Similar for name2 (defense) statements - just swap the becomes values
    if st.session_state.name2_highlights:
        for statement in st.session_state.name2_highlights:
            if statement not in st.session_state.recode_settings:
                matched_column = processor._find_column(statement)
                values = _get_value_range(matched_column) if matched_column else None
                
                is_continuous = (matched_column and values is None)
                
                if is_continuous:
                    st.session_state.recode_settings[statement] = {
                        'party': 'name2',
                        'matched_column': matched_column,
                        'variable_type': 'continuous',
                        'range1_operator': '<=',
                        'range1_value': 50,
                        'range1_becomes': 2,  # Defense
                        'range2_operator': '>',
                        'range2_value': 50,
                        'range2_becomes': 1
                    }
                elif values and len(values) >= 4:
                    st.session_state.recode_settings[statement] = {
                        'party': 'name2',
                        'matched_column': matched_column,
                        'variable_type': 'categorical',
                        'range1_start': values[0],
                        'range1_end': values[1],
                        'range1_becomes': 2,
                        'range2_start': values[2],
                        'range2_end': values[3],
                        'range2_becomes': 1
                    }
                else:
                    st.session_state.recode_settings[statement] = {
                        'party': 'name2',
                        'matched_column': matched_column,
                        'variable_type': 'unknown',
                        'range1_start': None,
                        'range1_end': None,
                        'range1_becomes': 2,
                        'range2_start': None,
                        'range2_end': None,
                        'range2_becomes': 1
                    }
    
    # Neutral questions
    st.session_state.neutral_index = len(st.session_state.recode_settings)
    st.session_state.neutral_questions = {}
    
    for column, label in general_questions:
        values = _get_value_range(column)
        is_continuous = (values is None)
        
        if is_continuous:
            # Continuous neutral variable
            st.session_state.neutral_questions[label] = {
                'column': column,
                'label': label,
                'variable_type': 'continuous',
                'range1_operator': '<=',
                'range1_value': 50,
                'range1_becomes': 1,
                'range2_operator': '>',
                'range2_value': 50,
                'range2_becomes': 2
            }
        elif values and len(values) >= 2:
            # Categorical neutral variable
            st.session_state.neutral_questions[label] = {
                'column': column,
                'label': label,
                'variable_type': 'categorical',
                'original_values': values,
                'range1_start': values[0],
                'range1_end': values[0],
                'range1_becomes': 1,
                'range2_start': values[1],
                'range2_end': values[1],
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
def _render_statement_config(statement: str, index: int, category: str, prefix: str):
    """Render configuration UI for a single statement"""
    
    settings = st.session_state.recode_settings[statement]
    variable_type = settings.get('variable_type', 'categorical')
    
    with st.expander(f"{category} {index}: {statement[:60]}..."):
        st.write(f"**Full statement:** {statement}")
        
        if settings.get('matched_column'):
            st.info(f"📊 Matched to column: `{settings['matched_column']}`")
        
        st.divider()
        
        if variable_type == 'continuous':
            _render_continuous_config(statement, index, prefix, settings)
        elif variable_type == 'categorical':
            _render_categorical_config(statement, index, prefix, settings)
        else:
            st.warning("⚠️ Could not determine variable type - no match found")


def _render_continuous_config(statement: str, index: int, prefix: str, settings: dict):
    """Render UI for continuous variables with numeric comparisons"""
    
    st.write("**Continuous Variable Configuration:**")
    st.caption("This variable has numeric values (e.g., percentages, dollar amounts)")
    
    # First range
    st.write("**First Range:**")
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        op1 = st.selectbox(
            "Operator",
            options=['<', '<=', '=', '>=', '>'],
            index=['<', '<=', '=', '>=', '>'].index(settings['range1_operator']),
            key=f"{prefix}_r1_op_{index}"
        )
        st.session_state.recode_settings[statement]['range1_operator'] = op1
    
    with col2:
        val1 = st.number_input(
            "Value",
            value=float(settings['range1_value']),
            key=f"{prefix}_r1_val_{index}"
        )
        st.session_state.recode_settings[statement]['range1_value'] = val1
    
    with col3:
        becomes1 = st.selectbox(
            "Becomes",
            options=[1, 2],
            index=0 if settings['range1_becomes'] == 1 else 1,
            key=f"{prefix}_r1_becomes_{index}"
        )
        st.session_state.recode_settings[statement]['range1_becomes'] = becomes1
    
    # Second range
    st.write("**Second Range:**")
    col4, col5, col6 = st.columns([1, 2, 1])
    
    with col4:
        op2 = st.selectbox(
            "Operator",
            options=['<', '<=', '=', '>=', '>'],
            index=['<', '<=', '=', '>=', '>'].index(settings['range2_operator']),
            key=f"{prefix}_r2_op_{index}"
        )
        st.session_state.recode_settings[statement]['range2_operator'] = op2
    
    with col5:
        val2 = st.number_input(
            "Value",
            value=float(settings['range2_value']),
            key=f"{prefix}_r2_val_{index}"
        )
        st.session_state.recode_settings[statement]['range2_value'] = val2
    
    with col6:
        becomes2 = st.selectbox(
            "Becomes",
            options=[1, 2],
            index=0 if settings['range2_becomes'] == 1 else 1,
            key=f"{prefix}_r2_becomes_{index}"
        )
        st.session_state.recode_settings[statement]['range2_becomes'] = becomes2
    
    # Show preview
    column = settings['matched_column']
    preview = _generate_continuous_preview(column, settings)
    st.code(preview, language="sql")


def _render_categorical_config(statement: str, index: int, prefix: str, settings: dict):
    """Render UI for categorical variables (existing logic)"""
    
    # First range
    st.write("**First Range:**")
    col1, col2, col3 = st.columns(3)
    with col1:
        r1_start = st.number_input(
            "Start",
            min_value=1,
            max_value=10,
            value=settings['range1_start'] if settings['range1_start'] else 1,
            key=f"{prefix}_r1_start_{index}"
        )
        st.session_state.recode_settings[statement]['range1_start'] = r1_start
        
    with col2:
        r1_end = st.number_input(
            "End",
            min_value=1,
            max_value=10,
            value=settings['range1_end'] if settings['range1_end'] else 2,
            key=f"{prefix}_r1_end_{index}"
        )
        st.session_state.recode_settings[statement]['range1_end'] = r1_end
        
    with col3:
        r1_becomes = st.selectbox(
            "Becomes",
            options=[1, 2],
            index=0 if settings['range1_becomes'] == 1 else 1,
            key=f"{prefix}_r1_becomes_{index}"
        )
        st.session_state.recode_settings[statement]['range1_becomes'] = r1_becomes

    # Second range (similar pattern)
    st.write("**Second Range:**")
    col4, col5, col6 = st.columns(3)
    with col4:
        r2_start = st.number_input(
            "Start",
            min_value=1,
            max_value=10,
            value=settings['range2_start'] if settings['range2_start'] else 3,
            key=f"{prefix}_r2_start_{index}"
        )
        st.session_state.recode_settings[statement]['range2_start'] = r2_start
        
    with col5:
        r2_end = st.number_input(
            "End",
            min_value=1,
            max_value=10,
            value=settings['range2_end'] if settings['range2_end'] else 4,
            key=f"{prefix}_r2_end_{index}"
        )
        st.session_state.recode_settings[statement]['range2_end'] = r2_end
        
    with col6:
        r2_becomes = st.selectbox(
            "Becomes",
            options=[1, 2],
            index=0 if settings['range2_becomes'] == 1 else 1,
            key=f"{prefix}_r2_becomes_{index}"
        )
        st.session_state.recode_settings[statement]['range2_becomes'] = r2_becomes
    
    # Show preview
    st.code(
        f"recode ({r1_start} thru {r1_end}={r1_becomes}) ({r2_start} thru {r2_end}={r2_becomes})", 
        language="sql"
    )


def _generate_continuous_preview(column: str, settings: dict) -> str:
    """Generate SPSS syntax preview for continuous variables"""
    op1 = settings['range1_operator']
    val1 = settings['range1_value']
    becomes1 = settings['range1_becomes']
    
    op2 = settings['range2_operator']
    val2 = settings['range2_value']
    becomes2 = settings['range2_becomes']
    
    # Convert operators to SPSS range syntax
    range1 = _operator_to_spss_range(op1, val1)
    range2 = _operator_to_spss_range(op2, val2)
    
    return f"recode {column} ({range1}={becomes1}) ({range2}={becomes2}) into {column}.r"


def _operator_to_spss_range(operator: str, value: float) -> str:
    """Convert operator and value to SPSS range syntax"""
    if operator == '<':
        return f"LOWEST thru {value - 0.01}"
    elif operator == '<=':
        return f"LOWEST thru {value}"
    elif operator == '=':
        return f"{value}"
    elif operator == '>=':
        return f"{value} thru HIGHEST"
    elif operator == '>':
        return f"{value + 0.01} thru HIGHEST"
    return str(value)