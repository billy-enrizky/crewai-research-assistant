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

