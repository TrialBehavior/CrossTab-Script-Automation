"""Recode settings neutral configuration component"""
import streamlit as st

def _render_neutral_recode_configurator():
    """
    Render a search interface for users to find and select neutral questions.
    Shows recode configurator only for selected questions.
    """
    st.subheader("🔍 Add Neutral Questions to Recode")
    
    # Get all available questions from SAV
    if 'sav_data' not in st.session_state or not st.session_state.sav_data:
        st.warning("⚠️ Please upload a SAV file first")
        return
    
    all_questions = st.session_state.sav_data['sav_labels']
    
    
    # Search bar - THAT'S IT, nothing else shows until you type
    search_query = st.text_input(
        "Type to search questions...",
        placeholder="e.g., 'age', 'gender', 'income'",
        label_visibility="collapsed"
    )
    
    # ONLY show results if user actually typed something (at least 2 chars)
    if not search_query or len(search_query.strip()) < 2:
        return  # Exit early - show nothing else
    
    # User typed something, so filter and display
    filtered_questions = _filter_questions(all_questions, search_query)
    
    if not filtered_questions:
        st.caption("No questions found")
        return
    
    st.caption(f"Found {len(filtered_questions)} question(s)")
    st.divider()
    
    # Show ONLY the filtered search results
    for i, (column, label) in enumerate(filtered_questions, 1):
        # Skip if already selected - FIXED LINE
        if st.session_state.all_questions.get(label, {}).get('selected', False):
            st.text(f"✓ {column}: {label[:100]}... (already added)")
            st.divider()
            continue
        
        # Skip plaintiff/defense questions
        if _is_party_question(column, label):
            continue
        
        # Show this result with Add button
        col1, col2 = st.columns([0.85, 0.15])
        
        with col1:
            st.text(f"{column}: {label[:100]}{'...' if len(label) > 100 else ''}")
        
        with col2:
            if st.button("➕", key=f"add_{i}", help="Add question"):
                _add_neutral_question(column, label)
                st.rerun()
        
        st.divider()


def _filter_questions(all_questions: list[tuple[str, str]], query: str) -> list[tuple[str, str]]:
    """Filter questions based on search query"""
    query_lower = query.lower()
    filtered = []
    
    for column, label in all_questions:
        if query_lower in column.lower() or query_lower in label.lower():
            filtered.append((column, label))
    
    return filtered


def _is_party_question(column: str, label: str) -> bool:
    """Check if question is a party-specific question"""
    col_lower = column.lower()
    label_lower = label.lower()
    
    name1_lower = st.session_state.name1.lower()
    name2_lower = st.session_state.name2.lower()
    
    party_patterns = ['plaaffs', 'defaffs', 'plaintiff', 'defense']
    
    return (
        name1_lower in col_lower or name1_lower in label_lower or
        name2_lower in col_lower or name2_lower in label_lower or
        any(pattern in col_lower for pattern in party_patterns)
    )


def _add_neutral_question(column: str, label: str):
    """Add a neutral question to the selected list"""
    meta = st.session_state.sav_data['meta']
    
    # Get value range
    values = None
    if column in meta.variable_value_labels:
        values = sorted(meta.variable_value_labels[column].keys())
    
    # Determine variable type
    is_continuous = (values is None)
    
    if is_continuous:
        st.session_state.all_questions[label] = {
            'column': column,
            'label': label,
            'variable_type': 'continuous',
            'selected': True,  # ADDED THIS LINE
            'range1_operator': '<=',
            'range1_value': 50.0,
            'range1_becomes': 1,
            'range2_operator': '>',
            'range2_value': 50.0,
            'range2_becomes': 2
        }
    elif values and len(values) == 2:
        st.session_state.all_questions[label] = {
            'column': column,
            'label': label,
            'variable_type': 'binary',
            'selected': True,  # ADDED THIS LINE
            'original_values': values,
            'binary_map': {
                values[0]: 1,
                values[1]: 2
            }
        }
    elif values and len(values) >= 2:
        st.session_state.all_questions[label] = {
            'column': column,
            'label': label,
            'variable_type': 'categorical',
            'selected': True,  # ADDED THIS LINE
            'original_values': values,
            'range1_start': values[0],
            'range1_end': values[0],
            'range1_becomes': 1,
            'range2_start': values[1],
            'range2_end': values[1],
            'range2_becomes': 2
        }


def _render_selected_neutral_question(label: str, index: int, data: dict):
    """Render a selected neutral question with remove button and configuration"""
    with st.container():
        col1, col2 = st.columns([0.9, 0.1])
        
        with col1:
            st.write(f"**{index}. [{data['column']}]** {label[:100]}{'...' if len(label) > 100 else ''}")
        
        with col2:
            if st.button("🗑️", key=f"remove_{index}", help="Remove this question"):
                del st.session_state.all_questions[label]
                st.rerun()
        
        variable_type = data.get('variable_type', 'unknown')
        
        if variable_type == 'continuous':
            _render_continuous_config(label, index, data)
        elif variable_type == 'binary':
            _render_binary_config(label, index, data)
        elif variable_type == 'categorical':
            _render_categorical_config(label, index, data)
        else:
            st.warning("⚠️ Unknown variable type")
        
        st.divider()


def _render_continuous_config(label: str, index: int, data: dict):
    """Render configuration for continuous variables"""
    st.caption("📊 Continuous variable")
    
    st.write("**First Range:**")
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        op1 = st.selectbox(
            "Operator",
            options=['<', '<=', '=', '>=', '>'],
            index=['<', '<=', '=', '>=', '>'].index(data['range1_operator']),
            key=f"neutral_cont_r1_op_{index}"
        )
        data['range1_operator'] = op1
    
    with col2:
        val1 = st.number_input(
            "Value",
            value=float(data['range1_value']),
            key=f"neutral_cont_r1_val_{index}"
        )
        data['range1_value'] = val1
    
    with col3:
        becomes1 = st.selectbox(
            "Becomes",
            options=[st.session_state.name1, st.session_state.name2],
            index=0 if data['range1_becomes'] == 1 else 1,
            key=f"neutral_cont_r1_becomes_{index}"
        )
        data['range1_becomes'] = 1 if becomes1 == st.session_state.name1 else 2
    
    st.write("**Second Range:**")
    col4, col5, col6 = st.columns([1, 2, 1])
    
    with col4:
        op2 = st.selectbox(
            "Operator",
            options=['<', '<=', '=', '>=', '>'],
            index=['<', '<=', '=', '>=', '>'].index(data['range2_operator']),
            key=f"neutral_cont_r2_op_{index}"
        )
        data['range2_operator'] = op2
    
    with col5:
        val2 = st.number_input(
            "Value",
            value=float(data['range2_value']),
            key=f"neutral_cont_r2_val_{index}"
        )
        data['range2_value'] = val2
    
    with col6:
        becomes2 = st.selectbox(
            "Becomes",
            options=[st.session_state.name1, st.session_state.name2],
            index=0 if data['range2_becomes'] == 1 else 1,
            key=f"neutral_cont_r2_becomes_{index}"
        )
        data['range2_becomes'] = 1 if becomes2 == st.session_state.name1 else 2
    
    preview = _generate_continuous_preview(data)
    st.code(preview, language="sql")


def _render_binary_config(label: str, index: int, data: dict):
    """Render configuration for binary variables"""
    st.caption("📊 Binary variable")
    
    meta = st.session_state.sav_data['meta']
    column = data['column']
    value_labels = meta.variable_value_labels.get(column, {})
    codes = data['original_values']
    binary_map = data['binary_map']
    
    col1, col2 = st.columns([0.7, 0.3])
    with col1:
        st.write(f"**{value_labels.get(codes[0], 'Option 1')}** (code {codes[0]})")
    with col2:
        choice1 = st.selectbox(
            "→",
            options=[st.session_state.name1, st.session_state.name2],
            index=0 if binary_map[codes[0]] == 1 else 1,
            key=f"neutral_bin_{index}_c1",
            label_visibility="collapsed"
        )
        binary_map[codes[0]] = 1 if choice1 == st.session_state.name1 else 2
    
    col3, col4 = st.columns([0.7, 0.3])
    with col3:
        st.write(f"**{value_labels.get(codes[1], 'Option 2')}** (code {codes[1]})")
    with col4:
        choice2 = st.selectbox(
            "→",
            options=[st.session_state.name1, st.session_state.name2],
            index=0 if binary_map[codes[1]] == 1 else 1,
            key=f"neutral_bin_{index}_c2",
            label_visibility="collapsed"
        )
        binary_map[codes[1]] = 1 if choice2 == st.session_state.name1 else 2
    
    becomes1 = st.session_state.name1 if binary_map[codes[0]] == 1 else st.session_state.name2
    becomes2 = st.session_state.name1 if binary_map[codes[1]] == 1 else st.session_state.name2
    st.code(f"recode {column} ({codes[0]}={becomes1}) ({codes[1]}={becomes2}).", language="sql")


def _render_categorical_config(label: str, index: int, data: dict):
    """Render configuration for categorical variables"""
    st.caption("📊 Categorical variable")
    
    original_values = data['original_values']
    min_val = int(min(original_values))
    max_val = int(max(original_values))
    
    st.write("**First Range:**")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        r1_start = st.number_input(
            "Start",
            min_value=min_val,
            max_value=max_val,
            value=int(data['range1_start']),
            key=f"neutral_cat_r1_start_{index}"
        )
        data['range1_start'] = r1_start
    
    with col2:
        r1_end = st.number_input(
            "End",
            min_value=min_val,
            max_value=max_val,
            value=int(data['range1_end']),
            key=f"neutral_cat_r1_end_{index}"
        )
        data['range1_end'] = r1_end
    
    with col3:
        becomes1 = st.selectbox(
            "Becomes",
            options=[st.session_state.name1, st.session_state.name2],
            index=0 if data['range1_becomes'] == 1 else 1,
            key=f"neutral_cat_r1_becomes_{index}"
        )
        data['range1_becomes'] = 1 if becomes1 == st.session_state.name1 else 2
    
    st.write("**Second Range:**")
    col4, col5, col6 = st.columns(3)
    
    with col4:
        r2_start = st.number_input(
            "Start",
            min_value=min_val,
            max_value=max_val,
            value=int(data['range2_start']),
            key=f"neutral_cat_r2_start_{index}"
        )
        data['range2_start'] = r2_start
    
    with col5:
        r2_end = st.number_input(
            "End",
            min_value=min_val,
            max_value=max_val,
            value=int(data['range2_end']),
            key=f"neutral_cat_r2_end_{index}"
        )
        data['range2_end'] = r2_end
    
    with col6:
        becomes2 = st.selectbox(
            "Becomes",
            options=[st.session_state.name1, st.session_state.name2],
            index=0 if data['range2_becomes'] == 1 else 1,
            key=f"neutral_cat_r2_becomes_{index}"
        )
        data['range2_becomes'] = 1 if becomes2 == st.session_state.name1 else 2
    
    becomes1_label = st.session_state.name1 if data['range1_becomes'] == 1 else st.session_state.name2
    becomes2_label = st.session_state.name1 if data['range2_becomes'] == 1 else st.session_state.name2
    st.code(
        f"recode ({r1_start} thru {r1_end}={becomes1_label}) ({r2_start} thru {r2_end}={becomes2_label})",
        language="sql"
    )


def _generate_continuous_preview(data: dict) -> str:
    """Generate SPSS syntax preview for continuous variables"""
    
    def operator_to_spss(op: str, val: float) -> str:
        if op == '<':
            return f"LOWEST thru {val - 0.01}"
        elif op == '<=':
            return f"LOWEST thru {val}"
        elif op == '=':
            return f"{val}"
        elif op == '>=':
            return f"{val} thru HIGHEST"
        elif op == '>':
            return f"{val + 0.01} thru HIGHEST"
        return str(val)
    
    range1 = operator_to_spss(data['range1_operator'], data['range1_value'])
    range2 = operator_to_spss(data['range2_operator'], data['range2_value'])
    
    becomes1 = st.session_state.name1 if data['range1_becomes'] == 1 else st.session_state.name2
    becomes2 = st.session_state.name1 if data['range2_becomes'] == 1 else st.session_state.name2
    
    return f"recode {data['column']} ({range1}={becomes1}) ({range2}={becomes2}) into {data['column']}.r"