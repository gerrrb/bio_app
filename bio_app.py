import pandas as pd
import streamlit as st

from helpers import read_markdown

import page_pengantar as pe
import page_fauna as fa
import page_flora as fl


# Page settings

#emojis: https://www.webfx.com/tools/emoji-cheat-sheet/
st.set_page_config(page_title='Kalkulator Indeks Keragaman dan Indeks Nilai Penting',
                   page_icon=":bar_chart:",
                   layout="wide")

st.sidebar.write(" ")

pages = {
        "Pengantar": pe,
        "Fauna": fa,
        "Flora": fl,
    }

st.sidebar.title("Menu")

# Radio buttons to select desired option
page = st.sidebar.radio(" ", tuple(pages.keys()))

pages[page].show_page()
        
# About
about = read_markdown("about.md")
st.sidebar.markdown(about)
