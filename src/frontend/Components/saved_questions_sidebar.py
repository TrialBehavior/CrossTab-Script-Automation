"""
Sidebar panel showing all saved/checkmarked neutral questions.
Renders a persistent list with remove buttons.
Call render_saved_questions_sidebar() once in main.py — Streamlit will keep it in the sidebar.
"""
import streamlit as st


def process_pending_sidebar_deletions():
    """
    Apply any pending sidebar deletions before the app renders.
    Call this at the very top of main.py, before render_saved_questions_sidebar().
    """
    if st.session_state.get('_sidebar_pending_delete'):
        label = st.session_state._sidebar_pending_delete
        if label in st.session_state.get('recode_settings', {}):
            del st.session_state.recode_settings[label]
        if label in st.session_state.get('all_questions', {}):
            st.session_state.all_questions[label]['selected'] = False
        st.session_state._sidebar_pending_delete = None


def render_saved_questions_sidebar():
    """
    Render a persistent sidebar panel listing all saved neutral questions.
    Each entry has an X button to remove it from recode_settings.
    """
    with st.sidebar:
        st.subheader("🗂️ Saved Neutral Questions")

        recode_settings = st.session_state.get('recode_settings', {})

        # Filter to only neutral questions
        neutral_questions = [
            label for label, settings in recode_settings.items()
            if settings.get('party') == 'neutral'
        ]

        if not neutral_questions:
            st.caption("No neutral questions saved yet.")
            return

        st.caption(f"{len(neutral_questions)} question(s) saved")
        st.divider()

        for label in neutral_questions:
            col1, col2 = st.columns([0.85, 0.15])

            with col1:
                display_label = label if len(label) <= 60 else label[:57] + "..."
                st.write(display_label)

            with col2:
                if st.button("✕", key=f"sidebar_remove_{label}", help="Remove question", type="tertiary"):
                    # Stage the deletion — it will be applied at the top of the next rerun
                    st.session_state._sidebar_pending_delete = label
                    st.rerun()

            st.divider()