"""Helper functions to prepare selected neutral questions for SPSS syntax generation"""
import streamlit as st


def prepare_neutral_questions_for_syntax():
    """
    Convert selected_neutral_questions into the format expected by recode_settings.
    
    This bridges the gap between:
    - selected_neutral_questions: {label: {column, variable_type, ranges...}}
    - recode_settings format: {question_text: {matched_column, variable_type, ranges...}}
    
    Only processes questions from selected_neutral_questions (user's selections).
    """
    if 'selected_neutral_questions' not in st.session_state:
        return
    
    # Process each selected neutral question
    for label, data in st.session_state.selected_neutral_questions.items():
        # Use the label as the question text key in recode_settings
        if label not in st.session_state.recode_settings:
            # Convert the data format
            settings = {
                'party': 'neutral',
                'matched_column': data['column'],
                'variable_type': data.get('variable_type', 'categorical')
            }
            
            # Add type-specific fields
            if data.get('variable_type') == 'continuous':
                settings.update({
                    'range1_operator': data.get('range1_operator', '<='),
                    'range1_value': data.get('range1_value', 50),
                    'range1_becomes': data.get('range1_becomes', 1),
                    'range2_operator': data.get('range2_operator', '>'),
                    'range2_value': data.get('range2_value', 50),
                    'range2_becomes': data.get('range2_becomes', 2)
                })
            elif data.get('variable_type') == 'binary':
                # Binary variables use simple mapping
                binary_map = data.get('binary_map', {})
                original_values = data.get('original_values', [])
                if len(original_values) >= 2:
                    settings.update({
                        'range1_start': original_values[0],
                        'range1_end': original_values[0],
                        'range1_becomes': binary_map.get(original_values[0], 1),
                        'range2_start': original_values[1],
                        'range2_end': original_values[1],
                        'range2_becomes': binary_map.get(original_values[1], 2)
                    })
            else:  # categorical
                settings.update({
                    'range1_start': data.get('range1_start', 1),
                    'range1_end': data.get('range1_end', 1),
                    'range1_becomes': data.get('range1_becomes', 1),
                    'range2_start': data.get('range2_start', 2),
                    'range2_end': data.get('range2_end', 2),
                    'range2_becomes': data.get('range2_becomes', 2)
                })
            
            st.session_state.recode_settings[label] = settings


def get_neutral_questions_for_syntax():
    """
    Get list of neutral question labels that should be included in syntax generation.
    
    Returns:
        List of question labels (strings) from selected_neutral_questions
    """
    if 'selected_neutral_questions' not in st.session_state:
        return []
    
    return list(st.session_state.selected_neutral_questions.keys())


def count_selected_neutral():
    """Get count of selected neutral questions"""
    if 'selected_neutral_questions' not in st.session_state:
        return 0
    return len(st.session_state.selected_neutral_questions)