import streamlit as st
from helpers import read_markdown

def show_page():

    for i in range(8):
        st.sidebar.write("")

    intro_markdown = read_markdown("docs/markdown/introduction.md")
    st.markdown(intro_markdown)

    return