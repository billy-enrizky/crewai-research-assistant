import streamlit as st
import sys
from contextlib import contextmanager
from io import StringIO
import re

#--------------------------------#
#         Output Handler         #
#--------------------------------#

class StreamlitProcessOutput:
    
    def __init__(self, container):
        self.container = container
        self.output_text = ""
        self.seen_lines = set()
    
    def clean_text(self, text):
        # Remove ANSI escape codes
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        text = ansi_escape.sub('', text)