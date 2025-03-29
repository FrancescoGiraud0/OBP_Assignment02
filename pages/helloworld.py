"""
Script for testing streamlit library capabilities.
"""
import pip

try:
    import streamlit as st
except:
    import os
    pip.main(['install', streamlit])

st.write("Hello World!")
