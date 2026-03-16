"""Recode settings configuration component"""
import streamlit as st


def _mark_touched(key: str):
    """Mark an expander as touched so it stays open after a rerun."""
    st.session_state[key] = True

def _render_recode_configurator():
    """
    Render the recode settings configuration UI.
    
    Allows users to configure recode ranges for each statement.
    """
    st.subheader("Configure Recode Settings Per Question")
    
    # name1 Questions
    if st.session_state.name1_highlights:
        st.write(f"**Highlighted {st.session_state.name1} Questions:**")
        for i, statement in enumerate(st.session_state.name1_highlights, 1):
            _render_statement_config(statement, i, f"{st.session_state.name1}", "p")
    
    # name2 Questions
    if st.session_state.name2_highlights:
        st.write(f"**Highlighted {st.session_state.name2} Questions:**")
        for i, statement in enumerate(st.session_state.name2_highlights, 1):
            _render_statement_config(statement, i, st.session_state.name2, "d")


def _render_statement_config(statement: str, index: int, category: str, prefix: str):
    """
    Render configuration UI for a single statement.
    """
    # touched_key is ONLY set to True via on_change callbacks below,
    # meaning the user actually changed a value. This is the only reliable
    # way to know the expander was opened — Streamlit registers widget keys
    # in session_state even for collapsed expanders, so key existence alone
    # is not a valid signal.
    touched_key = f"expander_touched_{prefix}_{index}"
    if touched_key not in st.session_state:
        st.session_state[touched_key] = False

    with st.expander(
        f"{category} {index}: {statement[:60]}...",
        expanded=st.session_state[touched_key]
    ):

        st.write(f"**Full statement:** {statement}")
        st.divider()
        
        settings = st.session_state.recode_settings[statement]
        is_neutral = settings.get('party') == 'neutral'
        
        # Initialize changed_neutral if it doesn't exist
        if 'changed_neutral' not in st.session_state:
            st.session_state.changed_neutral = []
        
        # Track if this neutral question was already marked as changed
        was_changed = statement in st.session_state.changed_neutral if is_neutral else False
        
        # Convert values to int to avoid type mismatches
        r1_start_val = int(settings['range1_start']) if settings['range1_start'] is not None else 1
        r1_end_val = int(settings['range1_end']) if settings['range1_end'] is not None else 2
        r2_start_val = int(settings['range2_start']) if settings['range2_start'] is not None else 3
        r2_end_val = int(settings['range2_end']) if settings['range2_end'] is not None else 4

        # First range
        st.write("**First Range:**")
        col1, col2, col3 = st.columns(3)
        with col1:
            r1_start = st.number_input(
                "Start",
                min_value=1,
                max_value=100,
                value=r1_start_val,
                key=f"{prefix}_r1_start_{index}",
                on_change=_mark_touched,
                args=(touched_key,)
            )
            st.session_state.recode_settings[statement]['range1_start'] = r1_start
            
        with col2:
            r1_end = st.number_input(
                "End",
                min_value=1,
                max_value=100,
                value=r1_end_val,
                key=f"{prefix}_r1_end_{index}",
                on_change=_mark_touched,
                args=(touched_key,)
            )
            st.session_state.recode_settings[statement]['range1_end'] = r1_end
            
        with col3:
            r1_becomes = st.selectbox(
                "Becomes",
                options=[st.session_state.name1, st.session_state.name2],
                index=0 if settings['range1_becomes'] == 1 else 1,
                key=f"{prefix}_r1_becomes_{index}",
                on_change=_mark_touched,
                args=(touched_key,)
            )
            st.session_state.recode_settings[statement]['range1_becomes'] = 1 if r1_becomes == st.session_state.name1 else 2

        # Second range
        st.write("**Second Range:**")
        col4, col5, col6 = st.columns(3)
        with col4:
            r2_start = st.number_input(
                "Start",
                min_value=1,
                max_value=100,
                value=r2_start_val,
                key=f"{prefix}_r2_start_{index}",
                on_change=_mark_touched,
                args=(touched_key,)
            )
            st.session_state.recode_settings[statement]['range2_start'] = r2_start
            
        with col5:
            r2_end = st.number_input(
                "End",
                min_value=1,
                max_value=100,
                value=r2_end_val,
                key=f"{prefix}_r2_end_{index}",
                on_change=_mark_touched,
                args=(touched_key,)
            )
            st.session_state.recode_settings[statement]['range2_end'] = r2_end
            
        with col6:
            r2_becomes = st.selectbox(
                "Becomes",
                options=[st.session_state.name1, st.session_state.name2],
                index=0 if settings['range2_becomes'] == 1 else 1,
                key=f"{prefix}_r2_becomes_{index}",
                on_change=_mark_touched,
                args=(touched_key,)
            )
            st.session_state.recode_settings[statement]['range2_becomes'] = 1 if r2_becomes == st.session_state.name1 else 2
        
        # Mark as changed if it's a neutral question and values changed
        if is_neutral:
            from src.frontend.Components.user_recoding.recode_prepping import _get_value_range
            column = settings.get('matched_column')
            if column:
                original_values = _get_value_range(column)
                if original_values and len(original_values) >= 2:
                    is_unchanged = (
                        r1_start == original_values[0] and
                        r1_end == original_values[0] and
                        settings['range1_becomes'] == 1 and
                        r2_start == original_values[1] and
                        r2_end == original_values[1] and
                        settings['range2_becomes'] == 2
                    )
                    
                    # Add to changed_neutral if changed
                    if not is_unchanged and statement not in st.session_state.changed_neutral:
                        st.session_state.changed_neutral.append(statement)
                    # Remove from changed_neutral if reverted back to original
                    elif is_unchanged and statement in st.session_state.changed_neutral:
                        st.session_state.changed_neutral.remove(statement)
        
        becomes1_label = settings['range1_becomes']
        becomes2_label = settings['range2_becomes']
        st.code(
            f"recode ({r1_start} thru {r1_end}={becomes1_label}) ({r2_start} thru {r2_end}={becomes2_label})",
            language="sql"
        )