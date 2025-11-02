import streamlit as st

# Absolutely minimal Streamlit app
st.title("🚀 WorkBridge Test")
st.write("Hello World!")
st.success("If you can see this, Streamlit is working!")

# Simple button test
if st.button("Click me!"):
    st.balloons()
    st.write("Button works!")

# Simple metrics
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Users", "1,234", "12%")
with col2:
    st.metric("Jobs", "567", "8%")
with col3:
    st.metric("Matches", "89", "15%")