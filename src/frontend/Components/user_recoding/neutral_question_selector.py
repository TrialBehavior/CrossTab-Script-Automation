"""Neutral question selector component"""
import streamlit as st
import pandas as pd
from src.frontend.Components.user_recoding.recode_prepping import (
    _get_value_range,
    _create_recode_config
)
def _render_neutral_question_config(label: str, settings: dict):
    """Render configuration UI for a neutral question"""
    variable_type = settings.get('variable_type', 'categorical')
    
    with st.expander(f"⚙️ {label}", expanded=True):
        if variable_type == 'continuous':
            _render_continuous_config(label, settings)
        elif variable_type == 'categorical':
            _render_categorical_config(label, settings)
        else:
            st.warning("⚠️ Could not determine variable type")


def _render_continuous_config(label: str, settings: dict):
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
            key=f"neutral_r1_op_{label}"
        )
        settings['range1_operator'] = op1
    
    with col2:
        val1 = st.number_input(
            "Value",
            value=float(settings['range1_value']),
            key=f"neutral_r1_val_{label}"
        )
        settings['range1_value'] = val1
    
    with col3:
        becomes1 = st.selectbox(
            "Becomes",
            options=[1, 2],
            index=0 if settings['range1_becomes'] == 1 else 1,
            key=f"neutral_r1_becomes_{label}"
        )
        settings['range1_becomes'] = becomes1
    
    # Second range
    st.write("**Second Range:**")
    col4, col5, col6 = st.columns([1, 2, 1])
    
    with col4:
        op2 = st.selectbox(
            "Operator",
            options=['<', '<=', '=', '>=', '>'],
            index=['<', '<=', '=', '>=', '>'].index(settings['range2_operator']),
            key=f"neutral_r2_op_{label}"
        )
        settings['range2_operator'] = op2
    
    with col5:
        val2 = st.number_input(
            "Value",
            value=float(settings['range2_value']),
            key=f"neutral_r2_val_{label}"
        )
        settings['range2_value'] = val2
    
    with col6:
        becomes2 = st.selectbox(
            "Becomes",
            options=[1, 2],
            index=0 if settings['range2_becomes'] == 1 else 1,
            key=f"neutral_r2_becomes_{label}"
        )
        settings['range2_becomes'] = becomes2
    
    # Show preview
    st.code(
        f"{settings['range1_operator']} {settings['range1_value']} → {settings['range1_becomes']} | "
        f"{settings['range2_operator']} {settings['range2_value']} → {settings['range2_becomes']}",
        language="text"
    )


def _render_categorical_config(label: str, settings: dict):
    """Render UI for categorical variables"""
    # Get the original values and their labels
    column = settings['matched_column']
    meta = st.session_state.sav_data['meta']
    value_labels = meta.variable_value_labels.get(column, {})
    original_values = settings.get('original_values', [])
    
    # Determine if this is a simple 2-choice question
    is_binary = len(original_values) == 2
    
    # Convert values to int
    r1_start_val = int(settings['range1_start']) if settings['range1_start'] is not None else 1
    r1_end_val = int(settings['range1_end']) if settings['range1_end'] is not None else 1
    r2_start_val = int(settings['range2_start']) if settings['range2_start'] is not None else 2
    r2_end_val = int(settings['range2_end']) if settings['range2_end'] is not None else 2
    
    if is_binary:
        # Simple binary choice - just show "Value" and "Becomes"
        st.write("**First Range:**")
        col1, col2 = st.columns(2)
        with col1:
            # Show dropdown with value labels
            options = [(val, f"{val} - {value_labels.get(val, 'Unknown')}") for val in original_values]
            selected_idx = next((i for i, (val, _) in enumerate(options) if val == r1_start_val), 0)
            
            selected = st.selectbox(
                "Value",
                options=[label for val, label in options],
                index=selected_idx,
                key=f"neutral_r1_value_{label}"
            )
            # Extract the numeric value from selection
            r1_value = options[[label for val, label in options].index(selected)][0]
            settings['range1_start'] = r1_value
            settings['range1_end'] = r1_value
            
        with col2:
            r1_becomes = st.selectbox(
                "Becomes",
                options=[1, 2],
                index=0 if settings['range1_becomes'] == 1 else 1,
                key=f"neutral_r1_becomes_{label}"
            )
            settings['range1_becomes'] = r1_becomes

        # Second range
        st.write("**Second Range:**")
        col3, col4 = st.columns(2)
        with col3:
            options = [(val, f"{val} - {value_labels.get(val, 'Unknown')}") for val in original_values]
            selected_idx = next((i for i, (val, _) in enumerate(options) if val == r2_start_val), 1)
            
            selected = st.selectbox(
                "Value",
                options=[label for val, label in options],
                index=selected_idx,
                key=f"neutral_r2_value_{label}"
            )
            r2_value = options[[label for val, label in options].index(selected)][0]
            settings['range2_start'] = r2_value
            settings['range2_end'] = r2_value
            
        with col4:
            r2_becomes = st.selectbox(
                "Becomes",
                options=[1, 2],
                index=0 if settings['range2_becomes'] == 1 else 1,
                key=f"neutral_r2_becomes_{label}"
            )
            settings['range2_becomes'] = r2_becomes
        
        # Show preview
        st.code(
            f"recode ({settings['range1_start']}={r1_becomes}) ({settings['range2_start']}={r2_becomes})", 
            language="sql"
        )
        
    else:
        # Multi-choice question - show Start, End, Becomes
        # First range
        st.write("**First Range:**")
        col1, col2, col3 = st.columns(3)
        with col1:
            # Show dropdown with value labels for start
            options = [(val, f"{val} - {value_labels.get(val, 'Unknown')}") for val in original_values]
            selected_idx = next((i for i, (val, _) in enumerate(options) if val == r1_start_val), 0)
            
            selected = st.selectbox(
                "Start",
                options=[label for val, label in options],
                index=selected_idx,
                key=f"neutral_r1_start_{label}"
            )
            r1_start = options[[label for val, label in options].index(selected)][0]
            settings['range1_start'] = r1_start
            
        with col2:
            options = [(val, f"{val} - {value_labels.get(val, 'Unknown')}") for val in original_values]
            selected_idx = next((i for i, (val, _) in enumerate(options) if val == r1_end_val), 0)
            
            selected = st.selectbox(
                "End",
                options=[label for val, label in options],
                index=selected_idx,
                key=f"neutral_r1_end_{label}"
            )
            r1_end = options[[label for val, label in options].index(selected)][0]
            settings['range1_end'] = r1_end
            
        with col3:
            r1_becomes = st.selectbox(
                "Becomes",
                options=[1, 2],
                index=0 if settings['range1_becomes'] == 1 else 1,
                key=f"neutral_r1_becomes_{label}"
            )
            settings['range1_becomes'] = r1_becomes

        # Second range
        st.write("**Second Range:**")
        col4, col5, col6 = st.columns(3)
        with col4:
            options = [(val, f"{val} - {value_labels.get(val, 'Unknown')}") for val in original_values]
            selected_idx = next((i for i, (val, _) in enumerate(options) if val == r2_start_val), 1)
            
            selected = st.selectbox(
                "Start",
                options=[label for val, label in options],
                index=selected_idx,
                key=f"neutral_r2_start_{label}"
            )
            r2_start = options[[label for val, label in options].index(selected)][0]
            settings['range2_start'] = r2_start
            
        with col5:
            options = [(val, f"{val} - {value_labels.get(val, 'Unknown')}") for val in original_values]
            selected_idx = next((i for i, (val, _) in enumerate(options) if val == r2_end_val), 1)
            
            selected = st.selectbox(
                "End",
                options=[label for val, label in options],
                index=selected_idx,
                key=f"neutral_r2_end_{label}"
            )
            r2_end = options[[label for val, label in options].index(selected)][0]
            settings['range2_end'] = r2_end
            
        with col6:
            r2_becomes = st.selectbox(
                "Becomes",
                options=[1, 2],
                index=0 if settings['range2_becomes'] == 1 else 1,
                key=f"neutral_r2_becomes_{label}"
            )
            settings['range2_becomes'] = r2_becomes
        
        # Show preview
        st.code(
            f"recode ({settings['range1_start']} thru {settings['range1_end']}={settings['range1_becomes']}) "
            f"({settings['range2_start']} thru {settings['range2_end']}={settings['range2_becomes']})", 
            language="sql"
        )

def _render_neutral_question_selector():
    """
    Render the neutral question search and selection UI.
    
    Allows users to search for neutral/general questions and configure their recode settings.
    Assumes st.session_state.sav_data is already loaded.
    """
    if 'sav_data' not in st.session_state or st.session_state.sav_data is None:
        st.warning("⚠️ Please upload SAV file first")
        return
    
    st.subheader("🔍 Select Neutral Questions")
    st.caption("Search and configure neutral/demographic questions for analysis")
    
    # Extract labels for searching
    columns = [column for column, label in st.session_state.sav_data['sav_labels']]
    labels = [label for column, label in st.session_state.sav_data['sav_labels']]
    
    df_labels = pd.DataFrame({"Column": columns, "Label": labels})
    
    # Search input
    search_input = st.text_input(
        "Search questions",
        key="neutral_search_input",
        placeholder="Type to search labels..."
    )
    
    if search_input:
        filtered_df = df_labels[df_labels['Label'].str.contains(search_input, case=False, na=False)]
        
        # Display checkboxes for each result
        for idx, row in filtered_df.iterrows():
            is_selected = row['Label'] in st.session_state.recode_settings
            
            checkbox = st.checkbox(
                f"**{row['Label']}** (`{row['Column']}`)",
                value=is_selected,
                key=f"neutral_checkbox_{row['Column']}"
            )
            
            # Add or remove from recode_settings based on checkbox state
            if checkbox and not is_selected:
                # Create recode config for this question
                values = _get_value_range(row['Column'])
                st.session_state.recode_settings[row['Label']] = _create_recode_config(
                    party='neutral',
                    matched_column=row['Column'],
                    values=values,
                    favorable_becomes=1,
                    unfavorable_becomes=2,
                    include_label=True,
                    label=row['Label']
                )
            elif not checkbox and is_selected:
                # Only remove if it's a neutral question
                if st.session_state.recode_settings[row['Label']].get('party') == 'neutral':
                    del st.session_state.recode_settings[row['Label']]
            
            # If checked, show configuration block immediately below
            if checkbox and row['Label'] in st.session_state.recode_settings:
                settings = st.session_state.recode_settings[row['Label']]
                if settings.get('party') == 'neutral':  # Only show config for neutral questions
                    _render_neutral_question_config(row['Label'], settings)


