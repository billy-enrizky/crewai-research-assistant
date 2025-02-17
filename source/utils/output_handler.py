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
    
        # Remove LiteLLM debug messages
        if text.strip().startswith('LiteLLM.Info:') or text.strip().startswith('Provider List:'):
            return None
        
        # Clean up the formatting
        text = text.replace('[1m', '').replace('[95m', '').replace('[92m', '').replace('[00m', '')
        return text
    
    def write(self, text):
        cleaned_text = self.clean_text(text)
        if cleaned_text is None:
            return
        
        # Split into lines and process each line
        lines = cleaned_text.split('\n')
        new_lines = []
        
        for line in lines:
            line = line.strip()
            if line and line not in self.seen_lines:
                self.seen_lines.add(line)
                new_lines.append(line)
        
        if new_lines:
            # Add the new lines to the output
            new_content = '\n'.join(new_lines)
            self.output_text = f"{self.output_text}\n{new_content}" if self.output_text else new_content
            
            # Update the display
            self.container.text(self.output_text)