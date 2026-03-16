"""
Sidebar panel showing all saved/checkmarked neutral questions.
Renders a persistent list with remove buttons.
Call render_saved_questions_sidebar() once in main.py — Streamlit will keep it in the sidebar.
"""
import streamlit as st


def process_pending_sidebar_deletions():
    if st.session_state.get('_sidebar_pending_delete'):
        label = st.session_state._sidebar_pending_delete
        print(f"[SIDEBAR DELETE] Attempting to delete: ")

        if label in st.session_state.get('recode_settings', {}):
            settings = st.session_state.recode_settings[label]
            col = settings.get('matched_column') or settings.get('column')

            del st.session_state.recode_settings[label]

            if col:
                # Explicitly set checkbox to False so when it renders on the
                # next rerun it doesn't re-add the question back
                st.session_state[f"neutral_checkbox_{col}"] = False
        else:
            print(f"[SIDEBAR DELETE] Label not found in recode_settings!")

        if label in st.session_state.get('all_questions', {}):
            st.session_state.all_questions[label]['selected'] = False

        st.session_state._sidebar_pending_delete = None


def render_saved_questions_sidebar():
    with st.sidebar:
        st.subheader("🗂️ Saved Neutral Questions")

        recode_settings = st.session_state.get('recode_settings', {})

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
                    print(f"[SIDEBAR] X pressed for: ")
                    st.session_state._sidebar_pending_delete = label
                    st.rerun()

            st.divider()