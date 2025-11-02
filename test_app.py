import streamlit as st

# Set page config
st.set_page_config(
    page_title="WorkBridge Test",
    page_icon="W",
    layout="wide"
)

# Basic styling
st.markdown("""
<style>
.stApp {
    background: #1a1a2e !important;
}
.stApp * {
    color: white !important;
}
</style>
""", unsafe_allow_html=True)

# Test content
st.title("🚀 WorkBridge - Test Version")
st.write("If you can see this, the basic app is working!")

# Simple navigation
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("Dashboard"):
        st.write("Dashboard clicked!")

with col2:
    if st.button("Resume Analyzer"):
        st.write("Resume Analyzer clicked!")

with col3:
    if st.button("Settings"):
        st.write("Settings clicked!")

st.markdown("---")
st.write("This is a test to see if Streamlit is working properly.")