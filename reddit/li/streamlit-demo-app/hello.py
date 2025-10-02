import streamlit as st

st.write("## Welcome")
st.write("### This is a welcome page")

x = st.text_input("Your name")
if st.button("Click Me"):
    st.write(f"Your name is `{x}`")