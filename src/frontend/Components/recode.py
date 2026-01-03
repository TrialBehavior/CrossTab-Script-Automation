"""Recode settings configuration component"""
import streamlit as st

def _render_recode_configurator():
    """
    Render the recode settings configuration UI.
    
    Allows users to configure recode ranges for each statement.
    """
    st.subheader("Configure Recode Settings Per Question")
    
    # name1 Questions
    if st.session_state.name1_highlights:
        st.write(f"**{st.session_state.name1} Questions:**")
        for i, statement in enumerate(st.session_state.name1_highlights, 1):
            _render_statement_config(statement, i, f"{st.session_state.name1}", "p")
    
    # name2 Questions
    if st.session_state.name2_highlights:
        st.write(f"**{st.session_state.name1} Questions:**")
        for i, statement in enumerate(st.session_state.name2_highlights, 1):
            _render_statement_config(statement, i, st.session_state.name2, "d")


def _render_statement_config(statement: str, index: int, category: str, prefix: str):
    """
    Render configuration UI for a single statement.
    
    Args:
        statement: The statement text
        index: Statement number (for UI labeling)
        category: 'name1' or 'name2'
        prefix: Key prefix ('p' or 'd')
    """
    with st.expander(f"{category} {index}: {statement[:60]}..."):
        st.write(f"**Full statement:** {statement}")
        st.divider()

        # First range
        st.write("**First Range:**")
        col1, col2, col3 = st.columns(3)
        with col1:
            r1_start = st.number_input(
                "Start",
                min_value=1,
                max_value=5,
                value=st.session_state.recode_settings[statement]['range1_start'],
                key=f"{prefix}_r1_start_{index}"
            )
            st.session_state.recode_settings[statement]['range1_start'] = r1_start
            
        with col2:
            r1_end = st.number_input(
                "End",
                min_value=1,
                max_value=5,
                value=st.session_state.recode_settings[statement]['range1_end'],
                key=f"{prefix}_r1_end_{index}"
            )
            st.session_state.recode_settings[statement]['range1_end'] = r1_end
            
        with col3:
            r1_becomes = st.selectbox(
                "Becomes",
                options=[1, 2],
                index=0 if st.session_state.recode_settings[statement]['range1_becomes'] == 1 else 1,
                key=f"{prefix}_r1_becomes_{index}"
            )
            st.session_state.recode_settings[statement]['range1_becomes'] = r1_becomes

        # Second range
        st.write("**Second Range:**")
        col4, col5, col6 = st.columns(3)
        with col4:
            r2_start = st.number_input(
                "Start",
                min_value=1,
                max_value=5,
                value=st.session_state.recode_settings[statement]['range2_start'],
                key=f"{prefix}_r2_start_{index}"
            )
            st.session_state.recode_settings[statement]['range2_start'] = r2_start
            
        with col5:
            r2_end = st.number_input(
                "End",
                min_value=1,
                max_value=5,
                value=st.session_state.recode_settings[statement]['range2_end'],
                key=f"{prefix}_r2_end_{index}"
            )
            st.session_state.recode_settings[statement]['range2_end'] = r2_end
            
        with col6:
            r2_becomes = st.selectbox(
                "Becomes",
                options=[1, 2],
                index=0 if st.session_state.recode_settings[statement]['range2_becomes'] == 1 else 1,
                key=f"{prefix}_r2_becomes_{index}"
            )
            st.session_state.recode_settings[statement]['range2_becomes'] = r2_becomes
        
        # Show preview of recode syntax
        st.code(
            f"recode ({r1_start} thru {r1_end}={r1_becomes}) ({r2_start} thru {r2_end}={r2_becomes})", 
            language="sql"
        )