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

        if 'changed_neutral' not in st.session_state:
            st.session_state.changed_neutral = []
        if 'sysmis_becomes' not in settings:
            settings['sysmis_becomes'] = None

        # Build display options from actual responses, remapped to metadata labels by position
        matched_column = settings.get('matched_column')
        display_values = []
        display_labels = {}

        if matched_column and st.session_state.sav_data:
            meta = st.session_state.sav_data['meta']
            df = st.session_state.sav_data['df']
            value_labels = meta.variable_value_labels.get(matched_column, {})
            original_values = sorted(value_labels.keys()) if value_labels else []

            if matched_column in df.columns:
                actual_responses = sorted(df[matched_column].dropna().unique().tolist())
            else:
                actual_responses = original_values

            if actual_responses and original_values and len(actual_responses) <= len(original_values):
                # Remap: actual response values get labels from metadata by position
                # e.g. actual=[1,2,3,4], metadata=[7,8,9,10] → 1="Disagree Strongly"
                display_values = actual_responses
                display_labels = {
                    actual_responses[i]: value_labels.get(original_values[i], str(actual_responses[i]))
                    for i in range(len(actual_responses))
                }
            elif actual_responses:
                display_values = actual_responses
                display_labels = {v: value_labels.get(v, str(v)) for v in actual_responses}
            else:
                display_values = original_values
                display_labels = {v: value_labels.get(v, str(v)) for v in original_values}

        use_dropdowns = len(display_values) >= 2

        def make_options():
            return [(val, f"{val} - {display_labels.get(val, str(val))}") for val in display_values]

        def val_to_idx(opts, target):
            return next((i for i, (v, _) in enumerate(opts) if v == target), 0)

        # ── First Range ──
        st.write("**First Range:**")
        col1, col2, col3 = st.columns(3)

        if use_dropdowns:
            opts = make_options()
            with col1:
                r1_start_sel = st.selectbox(
                    "Start", options=[lbl for _, lbl in opts],
                    index=val_to_idx(opts, settings.get('range1_start', display_values[0])),
                    key=f"{prefix}_r1_start_{index}",
                    on_change=_mark_touched, args=(touched_key,)
                )
                settings['range1_start'] = opts[[lbl for _, lbl in opts].index(r1_start_sel)][0]
            with col2:
                r1_end_sel = st.selectbox(
                    "End", options=[lbl for _, lbl in opts],
                    index=val_to_idx(opts, settings.get('range1_end', display_values[0])),
                    key=f"{prefix}_r1_end_{index}",
                    on_change=_mark_touched, args=(touched_key,)
                )
                settings['range1_end'] = opts[[lbl for _, lbl in opts].index(r1_end_sel)][0]
        else:
            r1_start_val = int(settings['range1_start']) if settings['range1_start'] is not None else 1
            r1_end_val = int(settings['range1_end']) if settings['range1_end'] is not None else 2
            with col1:
                settings['range1_start'] = st.number_input(
                    "Start", min_value=1, max_value=100, value=r1_start_val,
                    key=f"{prefix}_r1_start_{index}",
                    on_change=_mark_touched, args=(touched_key,)
                )
            with col2:
                settings['range1_end'] = st.number_input(
                    "End", min_value=1, max_value=100, value=r1_end_val,
                    key=f"{prefix}_r1_end_{index}",
                    on_change=_mark_touched, args=(touched_key,)
                )

        with col3:
            r1_becomes = st.selectbox(
                "Becomes", options=BECOMES_OPTIONS(),
                index=_value_to_becomes_index(settings['range1_becomes']),
                key=f"{prefix}_r1_becomes_{index}",
                on_change=_mark_touched, args=(touched_key,)
            )
            settings['range1_becomes'] = _becomes_to_value(r1_becomes)

        # ── Second Range ──
        st.write("**Second Range:**")
        col4, col5, col6 = st.columns(3)

        if use_dropdowns:
            opts = make_options()
            with col4:
                r2_start_sel = st.selectbox(
                    "Start", options=[lbl for _, lbl in opts],
                    index=val_to_idx(opts, settings.get('range2_start', display_values[-2] if len(display_values) >= 2 else display_values[0])),
                    key=f"{prefix}_r2_start_{index}",
                    on_change=_mark_touched, args=(touched_key,)
                )
                settings['range2_start'] = opts[[lbl for _, lbl in opts].index(r2_start_sel)][0]
            with col5:
                r2_end_sel = st.selectbox(
                    "End", options=[lbl for _, lbl in opts],
                    index=val_to_idx(opts, settings.get('range2_end', display_values[-1])),
                    key=f"{prefix}_r2_end_{index}",
                    on_change=_mark_touched, args=(touched_key,)
                )
                settings['range2_end'] = opts[[lbl for _, lbl in opts].index(r2_end_sel)][0]
        else:
            r2_start_val = int(settings['range2_start']) if settings['range2_start'] is not None else 3
            r2_end_val = int(settings['range2_end']) if settings['range2_end'] is not None else 4
            with col4:
                settings['range2_start'] = st.number_input(
                    "Start", min_value=1, max_value=100, value=r2_start_val,
                    key=f"{prefix}_r2_start_{index}",
                    on_change=_mark_touched, args=(touched_key,)
                )
            with col5:
                settings['range2_end'] = st.number_input(
                    "End", min_value=1, max_value=100, value=r2_end_val,
                    key=f"{prefix}_r2_end_{index}",
                    on_change=_mark_touched, args=(touched_key,)
                )

        with col6:
            r2_becomes = st.selectbox(
                "Becomes", options=BECOMES_OPTIONS(),
                index=_value_to_becomes_index(settings['range2_becomes']),
                key=f"{prefix}_r2_becomes_{index}",
                on_change=_mark_touched, args=(touched_key,)
            )
            settings['range2_becomes'] = _becomes_to_value(r2_becomes)

        # ── Missing Values (SYSMIS) ──
        st.write("**Missing Values (SYSMIS):**")
        _, col_sysmis = st.columns([2, 1])
        with col_sysmis:
            sysmis_becomes = st.selectbox(
                "Becomes", options=BECOMES_OPTIONS(),
                index=_value_to_becomes_index(settings.get('sysmis_becomes')),
                key=f"{prefix}_sysmis_becomes_{index}",
                on_change=_mark_touched, args=(touched_key,)
            )
            settings['sysmis_becomes'] = _becomes_to_value(sysmis_becomes)

        b1 = settings['range1_becomes'] if settings['range1_becomes'] is not None else 'None'
        b2 = settings['range2_becomes'] if settings['range2_becomes'] is not None else 'None'
        r1s = settings.get('range1_start', '')
        r1e = settings.get('range1_end', '')
        r2s = settings.get('range2_start', '')
        r2e = settings.get('range2_end', '')
        sysmis_str = f" (SYSMIS={settings['sysmis_becomes']})" if settings.get('sysmis_becomes') is not None else ""
        st.code(
            f"recode ({r1s} thru {r1e}={b1}) ({r2s} thru {r2e}={b2}){sysmis_str}",
            language="sql"
        )