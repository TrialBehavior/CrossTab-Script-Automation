"""Recode settings configuration component"""
import streamlit as st

BECOMES_OPTIONS = lambda: [st.session_state.name1, st.session_state.name2, "None"]

def _becomes_to_value(becomes: str) -> int | None:
    if becomes == st.session_state.name1:
        return 1
    elif becomes == st.session_state.name2:
        return 2
    return None

def _value_to_becomes_index(value) -> int:
    if value == 1:
        return 0
    elif value == 2:
        return 1
    return 2  # None

def _mark_touched(key: str):
    st.session_state[key] = True

def _render_recode_configurator():
    st.subheader("Configure Recode Settings Per Question")
    
    if st.session_state.name1_highlights:
        st.write(f"**Highlighted {st.session_state.name1} Questions:**")
        for i, statement in enumerate(st.session_state.name1_highlights, 1):
            _render_statement_config(statement, i, f"{st.session_state.name1}", "p")
    
    if st.session_state.name2_highlights:
        st.write(f"**Highlighted {st.session_state.name2} Questions:**")
        for i, statement in enumerate(st.session_state.name2_highlights, 1):
            _render_statement_config(statement, i, st.session_state.name2, "d")


def _render_statement_config(statement: str, index: int, category: str, prefix: str):
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
        
        if 'changed_neutral' not in st.session_state:
            st.session_state.changed_neutral = []
        
        r1_start_val = int(settings['range1_start']) if settings['range1_start'] is not None else 1
        r1_end_val = int(settings['range1_end']) if settings['range1_end'] is not None else 2
        r2_start_val = int(settings['range2_start']) if settings['range2_start'] is not None else 3
        r2_end_val = int(settings['range2_end']) if settings['range2_end'] is not None else 4

        # First range
        st.write("**First Range:**")
        col1, col2, col3 = st.columns(3)
        with col1:
            r1_start = st.number_input(
                "Start", min_value=1, max_value=100, value=r1_start_val,
                key=f"{prefix}_r1_start_{index}",
                on_change=_mark_touched, args=(touched_key,)
            )
            settings['range1_start'] = r1_start
        with col2:
            r1_end = st.number_input(
                "End", min_value=1, max_value=100, value=r1_end_val,
                key=f"{prefix}_r1_end_{index}",
                on_change=_mark_touched, args=(touched_key,)
            )
            settings['range1_end'] = r1_end
        with col3:
            r1_becomes = st.selectbox(
                "Becomes", options=BECOMES_OPTIONS(),
                index=_value_to_becomes_index(settings['range1_becomes']),
                key=f"{prefix}_r1_becomes_{index}",
                on_change=_mark_touched, args=(touched_key,)
            )
            settings['range1_becomes'] = _becomes_to_value(r1_becomes)

        # Second range
        st.write("**Second Range:**")
        col4, col5, col6 = st.columns(3)
        with col4:
            r2_start = st.number_input(
                "Start", min_value=1, max_value=100, value=r2_start_val,
                key=f"{prefix}_r2_start_{index}",
                on_change=_mark_touched, args=(touched_key,)
            )
            settings['range2_start'] = r2_start
        with col5:
            r2_end = st.number_input(
                "End", min_value=1, max_value=100, value=r2_end_val,
                key=f"{prefix}_r2_end_{index}",
                on_change=_mark_touched, args=(touched_key,)
            )
            settings['range2_end'] = r2_end
        with col6:
            r2_becomes = st.selectbox(
                "Becomes", options=BECOMES_OPTIONS(),
                index=_value_to_becomes_index(settings['range2_becomes']),
                key=f"{prefix}_r2_becomes_{index}",
                on_change=_mark_touched, args=(touched_key,)
            )
            settings['range2_becomes'] = _becomes_to_value(r2_becomes)

        # System missing range
        st.write("**Missing Values (SYSMIS):**")
        sysmis_becomes = st.selectbox(
            "Becomes",
            options=BECOMES_OPTIONS(),
            index=_value_to_becomes_index(settings.get('sysmis_becomes')),
            key=f"{prefix}_sysmis_becomes_{index}",
            on_change=_mark_touched, args=(touched_key,)
        )
        settings['sysmis_becomes'] = _becomes_to_value(sysmis_becomes)

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
                    if not is_unchanged and statement not in st.session_state.changed_neutral:
                        st.session_state.changed_neutral.append(statement)
                    elif is_unchanged and statement in st.session_state.changed_neutral:
                        st.session_state.changed_neutral.remove(statement)

        b1 = settings['range1_becomes'] if settings['range1_becomes'] is not None else 'None'
        b2 = settings['range2_becomes'] if settings['range2_becomes'] is not None else 'None'
        sysmis_str = f" (SYSMIS={settings['sysmis_becomes']})" if settings.get('sysmis_becomes') is not None else ""
        st.code(
            f"recode ({r1_start} thru {r1_end}={b1}) ({r2_start} thru {r2_end}={b2}){sysmis_str}",
            language="sql"
        )