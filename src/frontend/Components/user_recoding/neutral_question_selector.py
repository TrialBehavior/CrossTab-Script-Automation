"""Neutral question selector component"""
import streamlit as st
import pandas as pd
from src.frontend.Components.user_recoding.recode_prepping import (
    _get_value_range,
    _create_recode_config
)

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


def _render_sysmis_row(label: str, settings: dict):
    """Render the SYSMIS row — just a single Becomes dropdown defaulting to None"""
    if 'sysmis_becomes' not in settings:
        settings['sysmis_becomes'] = None
    st.write("**Missing Values (SYSMIS):**")
    _, col_sysmis = st.columns([2, 1])
    with col_sysmis:
        sysmis_becomes = st.selectbox(
            "Becomes",
            options=BECOMES_OPTIONS(),
            index=_value_to_becomes_index(settings['sysmis_becomes']),
            key=f"sysmis_becomes_{label}"
        )
        settings['sysmis_becomes'] = _becomes_to_value(sysmis_becomes)


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
        _render_sysmis_row(label, settings)


def _render_continuous_config(label: str, settings: dict):
    """Render UI for continuous variables with numeric comparisons"""
    st.write("**Continuous Variable Configuration:**")
    st.caption("This variable has numeric values (e.g., percentages, dollar amounts)")

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
        val1 = st.number_input("Value", value=float(settings['range1_value']), key=f"neutral_r1_val_{label}")
        settings['range1_value'] = val1
    with col3:
        becomes1 = st.selectbox(
            "Becomes",
            options=BECOMES_OPTIONS(),
            index=_value_to_becomes_index(settings['range1_becomes']),
            key=f"neutral_r1_becomes_{label}"
        )
        settings['range1_becomes'] = _becomes_to_value(becomes1)

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
        val2 = st.number_input("Value", value=float(settings['range2_value']), key=f"neutral_r2_val_{label}")
        settings['range2_value'] = val2
    with col6:
        becomes2 = st.selectbox(
            "Becomes",
            options=BECOMES_OPTIONS(),
            index=_value_to_becomes_index(settings['range2_becomes']),
            key=f"neutral_r2_becomes_{label}"
        )
        settings['range2_becomes'] = _becomes_to_value(becomes2)

    b1 = settings['range1_becomes'] if settings['range1_becomes'] is not None else 'None'
    b2 = settings['range2_becomes'] if settings['range2_becomes'] is not None else 'None'
    st.code(
        f"{settings['range1_operator']} {settings['range1_value']} → {b1} | "
        f"{settings['range2_operator']} {settings['range2_value']} → {b2}",
        language="text"
    )


def _render_categorical_config(label: str, settings: dict):
    """Render UI for categorical variables"""
    column = settings['matched_column']
    meta = st.session_state.sav_data['meta']
    value_labels = meta.variable_value_labels.get(column, {})
    original_values = settings.get('original_values', [])
    is_binary = len(original_values) == 2

    r1_start_val = int(settings['range1_start']) if settings['range1_start'] is not None else 1
    r1_end_val = int(settings['range1_end']) if settings['range1_end'] is not None else 1
    r2_start_val = int(settings['range2_start']) if settings['range2_start'] is not None else 2
    r2_end_val = int(settings['range2_end']) if settings['range2_end'] is not None else 2

    if is_binary:
        st.write("**First Range:**")
        col1, col2 = st.columns(2)
        with col1:
            options = [(val, f"{val} - {value_labels.get(val, 'Unknown')}") for val in original_values]
            selected_idx = next((i for i, (val, _) in enumerate(options) if val == r1_start_val), 0)
            selected = st.selectbox("Value", options=[lbl for _, lbl in options], index=selected_idx, key=f"neutral_r1_value_{label}")
            r1_value = options[[lbl for _, lbl in options].index(selected)][0]
            settings['range1_start'] = r1_value
            settings['range1_end'] = r1_value
        with col2:
            r1_becomes = st.selectbox("Becomes", options=BECOMES_OPTIONS(), index=_value_to_becomes_index(settings['range1_becomes']), key=f"neutral_r1_becomes_{label}")
            settings['range1_becomes'] = _becomes_to_value(r1_becomes)

        st.write("**Second Range:**")
        col3, col4 = st.columns(2)
        with col3:
            options = [(val, f"{val} - {value_labels.get(val, 'Unknown')}") for val in original_values]
            selected_idx = next((i for i, (val, _) in enumerate(options) if val == r2_start_val), 1)
            selected = st.selectbox("Value", options=[lbl for _, lbl in options], index=selected_idx, key=f"neutral_r2_value_{label}")
            r2_value = options[[lbl for _, lbl in options].index(selected)][0]
            settings['range2_start'] = r2_value
            settings['range2_end'] = r2_value
        with col4:
            r2_becomes = st.selectbox("Becomes", options=BECOMES_OPTIONS(), index=_value_to_becomes_index(settings['range2_becomes']), key=f"neutral_r2_becomes_{label}")
            settings['range2_becomes'] = _becomes_to_value(r2_becomes)

        b1 = settings['range1_becomes'] if settings['range1_becomes'] is not None else 'None'
        b2 = settings['range2_becomes'] if settings['range2_becomes'] is not None else 'None'
        st.code(f"recode ({settings['range1_start']}={b1}) ({settings['range2_start']}={b2})", language="sql")

    else:
        st.write("**First Range:**")
        col1, col2, col3 = st.columns(3)
        with col1:
            options = [(val, f"{val} - {value_labels.get(val, 'Unknown')}") for val in original_values]
            selected_idx = next((i for i, (val, _) in enumerate(options) if val == r1_start_val), 0)
            selected = st.selectbox("Start", options=[lbl for _, lbl in options], index=selected_idx, key=f"neutral_r1_start_{label}")
            settings['range1_start'] = options[[lbl for _, lbl in options].index(selected)][0]
        with col2:
            options = [(val, f"{val} - {value_labels.get(val, 'Unknown')}") for val in original_values]
            selected_idx = next((i for i, (val, _) in enumerate(options) if val == r1_end_val), 0)
            selected = st.selectbox("End", options=[lbl for _, lbl in options], index=selected_idx, key=f"neutral_r1_end_{label}")
            settings['range1_end'] = options[[lbl for _, lbl in options].index(selected)][0]
        with col3:
            r1_becomes = st.selectbox("Becomes", options=BECOMES_OPTIONS(), index=_value_to_becomes_index(settings['range1_becomes']), key=f"neutral_r1_becomes_{label}")
            settings['range1_becomes'] = _becomes_to_value(r1_becomes)

        st.write("**Second Range:**")
        col4, col5, col6 = st.columns(3)
        with col4:
            options = [(val, f"{val} - {value_labels.get(val, 'Unknown')}") for val in original_values]
            selected_idx = next((i for i, (val, _) in enumerate(options) if val == r2_start_val), 1)
            selected = st.selectbox("Start", options=[lbl for _, lbl in options], index=selected_idx, key=f"neutral_r2_start_{label}")
            settings['range2_start'] = options[[lbl for _, lbl in options].index(selected)][0]
        with col5:
            options = [(val, f"{val} - {value_labels.get(val, 'Unknown')}") for val in original_values]
            selected_idx = next((i for i, (val, _) in enumerate(options) if val == r2_end_val), 1)
            selected = st.selectbox("End", options=[lbl for _, lbl in options], index=selected_idx, key=f"neutral_r2_end_{label}")
            settings['range2_end'] = options[[lbl for _, lbl in options].index(selected)][0]
        with col6:
            r2_becomes = st.selectbox("Becomes", options=BECOMES_OPTIONS(), index=_value_to_becomes_index(settings['range2_becomes']), key=f"neutral_r2_becomes_{label}")
            settings['range2_becomes'] = _becomes_to_value(r2_becomes)

        b1 = settings['range1_becomes'] if settings['range1_becomes'] is not None else 'None'
        b2 = settings['range2_becomes'] if settings['range2_becomes'] is not None else 'None'
        st.code(
            f"recode ({settings['range1_start']} thru {settings['range1_end']}={b1}) "
            f"({settings['range2_start']} thru {settings['range2_end']}={b2})",
            language="sql"
        )


def _render_neutral_question_selector():
    """Render the neutral question search and selection UI."""
    if 'sav_data' not in st.session_state or st.session_state.sav_data is None:
        st.warning("⚠️ Please upload SAV file first")
        return

    st.subheader("🔍 Select Neutral Questions")
    st.caption("Search and configure neutral/demographic questions for analysis")

    columns = [column for column, label in st.session_state.sav_data['sav_labels']]
    labels = [label for column, label in st.session_state.sav_data['sav_labels']]
    df_labels = pd.DataFrame({"Column": columns, "Label": labels})

    search_input = st.text_input("Search questions", key="neutral_search_input", placeholder="Type to search labels...")

    if search_input:
        filtered_df = df_labels[df_labels['Label'].str.contains(search_input, case=False, na=False)]
        filtered_df = filtered_df.drop_duplicates(subset='Label')

        for idx, row in filtered_df.iterrows():
            is_selected = row['Label'] in st.session_state.recode_settings

            checkbox = st.checkbox(
                f"**{row['Label']}** (`{row['Column']}`)",
                value=is_selected,
                key=f"neutral_checkbox_{row['Column']}"
            )

            if checkbox and not is_selected:
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
                st.rerun()
            elif not checkbox and is_selected:
                if st.session_state.recode_settings[row['Label']].get('party') == 'neutral':
                    del st.session_state.recode_settings[row['Label']]
                    st.rerun()

            if checkbox and row['Label'] in st.session_state.recode_settings:
                settings = st.session_state.recode_settings[row['Label']]
                if settings.get('party') == 'neutral':
                    _render_neutral_question_config(row['Label'], settings)