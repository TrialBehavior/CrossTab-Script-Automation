import streamlit as st
from src.frontend.Components.user_recoding.recode_prepping import _get_value_range

def filter_unchanged_neutral_statements():
    """
    Filter neutral statements to find which ones were changed by the user.
    Stores changed neutral statements separately in st.session_state.changed_neutral.
    Keeps all neutral statements in recode_settings unchanged.
    """
    # Initialize changed_neutral list if it doesn't exist
    if 'changed_neutral' not in st.session_state:
        st.session_state.changed_neutral = []
    
    # Clear the list before repopulating
    st.session_state.changed_neutral = []
    
    # Get all statement keys as a list
    all_statements = list(st.session_state.recode_settings.keys())
    
    # Get neutral statements (everything from neutral_index onwards)
    neutral_statements = all_statements[st.session_state.neutral_index:]
    
    for statement in neutral_statements:
        settings = st.session_state.recode_settings[statement]
        
        # Only process neutral party statements
        if settings.get('party') != 'neutral':
            continue
        
        # Get the matched column to retrieve original values
        column = settings.get('matched_column')
        if column:
            original_values = _get_value_range(column)
            
            if original_values and len(original_values) >= 2:
                # Check if settings match the initial values we set
                is_unchanged = (
                    settings['range1_start'] == original_values[0] and
                    settings['range1_end'] == original_values[0] and
                    settings['range1_becomes'] == 1 and
                    settings['range2_start'] == original_values[1] and
                    settings['range2_end'] == original_values[1] and
                    settings['range2_becomes'] == 2
                )
                
                # If changed, add to the changed_neutral list
                if not is_unchanged:
                    st.session_state.changed_neutral.append(statement)