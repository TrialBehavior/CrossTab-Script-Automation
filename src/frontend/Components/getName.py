"""Party name input component"""
import streamlit as st


def render_name_input():
    """
    Render the party name input component.
    
    Allows users to set custom names for both parties in the case.
    Updates session state with name1 and name2.
    """
    st.subheader("📝 Set Party Names")
    
    st.write("Enter the names of both parties in this case (defaults to Plaintiff and Defense):")
    
    col1, col2 = st.columns(2)
    
    with col1:
        name1_input = st.text_input(
            "First Party Name",
            value=st.session_state.name1,
            key="name1_input",
            placeholder="e.g., Plaintiff or Company A"
        )
    
    with col2:
        name2_input = st.text_input(
            "Second Party Name", 
            value=st.session_state.name2,
            key="name2_input",
            placeholder="e.g., Defense or Company B"
        )
    
    if st.button("✅ Confirm Party Names", type="primary"):
        st.session_state.name1 = name1_input
        st.session_state.name2 = name2_input
        st.session_state.getName_touched = True
        st.success(f"✅ Party names set: **{name1_input}** vs **{name2_input}**")
        st.rerun()
    
    # Show current status
    if st.session_state.getName_touched:
        st.info(f"📋 Current parties: **{st.session_state.name1}** vs **{st.session_state.name2}**")