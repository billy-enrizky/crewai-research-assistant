# Handle SQLite for ChromaDB
try:
    __import__('pysqlite3')
    import sys
    sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
except (ImportError, KeyError):
    pass

import streamlit as st
import os
from source.components.sidebar import render_sidebar
from source.components.researcher import create_researcher, create_research_task, run_research
from source.utils.output_handler import capture_output

#--------------------------------#
#         Streamlit App          #
#--------------------------------#
# Configure the page
st.set_page_config(
    page_title="CrewAI Research Assistant",
    page_icon="🕵️‍♂️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Logo
st.logo(
    "https://cdn.prod.website-files.com/66cf2bfc3ed15b02da0ca770/66d07240057721394308addd_Logo%20(1).svg",
    link="https://www.crewai.com/",
    size="large"
)

# Main layout
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.title("🔍 :red[CrewAI] Research Assistant", anchor=False)
    
# Render sidebar and get selection (provider and model)
selection = render_sidebar()

# Check if API keys are set based on provider
if selection["provider"] == "OpenAI":
    if not os.environ.get("OPENAI_API_KEY"):
        st.warning("⚠️ Please enter your OpenAI API key in the sidebar to get started")
        st.stop()
elif selection["provider"] == "GROQ":
    if not os.environ.get("GROQ_API_KEY"):
        st.warning("⚠️ Please enter your GROQ API key in the sidebar to get started")
        st.stop()
