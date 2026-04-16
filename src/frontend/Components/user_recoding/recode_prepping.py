import streamlit as st
import io
import math
from src.backend.file_extract.PDF_implementation import PDFHandler1
from src.backend.sav.spss_match_processor import SPSSMatchProcessor


def _render_recode_prepping(Q4_file):
    """Extract arguments from Q4 PDF file and prepare recode settings"""
    pdf_handler = PDFHandler1()
    Q4_file.seek(0)
    
    name2_pages = pdf_handler.find_pages_with_text(Q4_file, f"{st.session_state.name2} Arguments")
    Q4_file.seek(0)
    name1_pages = pdf_handler.find_pages_with_text(Q4_file, f"{st.session_state.name1} Arguments")
    
    st.write(f"{st.session_state.name2} Arguments found on pages: {[p+1 for p in name2_pages]}")
    st.write(f"{st.session_state.name1} Arguments found on pages: {[p+1 for p in name1_pages]}")
    
    if name2_pages:
        Q4_file.seek(0)
        name2_pdf_bytes = pdf_handler.split_pdf_by_pages(Q4_file, name2_pages)
        st.session_state.name2_highlights = pdf_handler.extract_highlighted_statements(io.BytesIO(name2_pdf_bytes))
    else:
        st.warning("⚠️ No highlighted text found in name2 Arguments pages")

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


def _get_actual_values(column_name) -> list:
    """Get the actual unique values respondents used for a column from the dataframe"""
    df = st.session_state.sav_data['df']
    if column_name not in df.columns:
        return []
    return sorted(df[column_name].dropna().unique().tolist())


def _resolve_ranges(values: list, actual_values: list) -> tuple[int, int, int, int]:
    """
    Determine the best range1_start/end and range2_start/end given metadata
    values and actual response values.

    Logic:
    1. Check if any actual responses fall within values[0]-values[3] (or values[0]-values[1])
    2. If yes — use the metadata values as-is
    3. If no — derive ranges from actual responses:
       a. Fill any gaps in actual values to make contiguous
       b. Split down the middle (range1 = min to mid, range2 = mid+1 to max)
    """
    if not actual_values:
        if len(values) >= 4:
            return values[0], values[1], values[2], values[3]
        else:
            return values[0], values[0], values[1], values[1]

    if len(values) >= 4:
        range_min = values[0]
        range_max = values[3]
    else:
        range_min = values[0]
        range_max = values[1]

    any_in_range = any(range_min <= v <= range_max for v in actual_values)

    if any_in_range:
        if len(values) >= 4:
            return values[0], values[1], values[2], values[3]
        else:
            return values[0], values[0], values[1], values[1]

    min_val = int(min(actual_values))
    max_val = int(max(actual_values))

    expected_count = max_val - min_val + 1
    actual_set = set(int(v) for v in actual_values)

    if len(actual_set) < expected_count:
        contiguous = list(range(min_val, max_val + 1))
    else:
        contiguous = sorted(actual_set)

    mid_idx = math.floor((len(contiguous) - 1) / 2)
    mid_val = contiguous[mid_idx]

    range1_start = contiguous[0]
    range1_end = mid_val
    range2_start = contiguous[mid_idx + 1] if mid_idx + 1 < len(contiguous) else mid_val
    range2_end = contiguous[-1]

    return range1_start, range1_end, range2_start, range2_end


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
            actual_values = _get_actual_values(matched_column) if matched_column else []
            st.session_state.recode_settings[statement] = _create_recode_config(
                party='name1',
                matched_column=matched_column,
                values=values,
                favorable_becomes=1,
                unfavorable_becomes=2,
                actual_values=actual_values
            )


def _initialize_defense_recodes(processor: SPSSMatchProcessor):
    """Initialize recode settings for defense (name2) statements"""
    if not st.session_state.name2_highlights:
        return
    for statement in st.session_state.name2_highlights:
        if statement not in st.session_state.recode_settings:
            matched_column = processor._find_column(statement)
            values = _get_value_range(matched_column) if matched_column else None
            actual_values = _get_actual_values(matched_column) if matched_column else []
            st.session_state.recode_settings[statement] = _create_recode_config(
                party='name2',
                matched_column=matched_column,
                values=values,
                favorable_becomes=2,
                unfavorable_becomes=1,
                actual_values=actual_values
            )


def _initialize_neutral_recodes(processor: SPSSMatchProcessor):
    """Initialize recode settings for neutral/general questions"""
    general_questions = processor.get_all_general_questions()
    if not general_questions:
        print("⚠️ No general/neutral questions found in SAV file")
        return
    for column, label in general_questions:
        values = _get_value_range(column)
        actual_values = _get_actual_values(column)
        st.session_state.all_questions[label] = _create_recode_config(
            party='neutral',
            matched_column=column,
            values=values,
            favorable_becomes=1,
            unfavorable_becomes=2,
            include_label=True,
            label=label,
            actual_values=actual_values
        )


def _create_recode_config(
    party: str,
    matched_column: str,
    values: list,
    favorable_becomes: int,
    unfavorable_becomes: int,
    include_label: bool = False,
    label: str = None,
    actual_values: list = None
) -> dict:
    """Create a recode configuration dictionary"""
    if actual_values is None:
        actual_values = []

    is_continuous = (matched_column and values is None)
    
    config = {
        'party': party,
        'matched_column': matched_column,
        'sysmis_becomes': None  # default: system missing stays missing
    }
    
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
        r1s, r1e, r2s, r2e = _resolve_ranges(values, actual_values)
        config.update({
            'variable_type': 'categorical',
            'range1_start': r1s,
            'range1_end': r1e,
            'range1_becomes': favorable_becomes,
            'range2_start': r2s,
            'range2_end': r2e,
            'range2_becomes': unfavorable_becomes
        })
        if include_label:
            config['original_values'] = values
    elif values and len(values) >= 2 and include_label:
        r1s, r1e, r2s, r2e = _resolve_ranges(values, actual_values)
        config.update({
            'variable_type': 'categorical',
            'original_values': values,
            'range1_start': r1s,
            'range1_end': r1e,
            'range1_becomes': favorable_becomes,
            'range2_start': r2s,
            'range2_end': r2e,
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
        actual_values = _get_actual_values(matched_column)
        if values and len(values) >= 4:
            r1s, r1e, r2s, r2e = _resolve_ranges(values, actual_values)
            settings = st.session_state.recode_settings[statement]
            settings['matched_column'] = matched_column
            settings['range1_start'] = r1s
            settings['range1_end'] = r1e
            settings['range2_start'] = r2s
            settings['range2_end'] = r2e