import streamlit as st; st.write('ALLIANCE Ai Engine Online')

from pathlib import Path
import streamlit as st

def read_rules(file_path):
    return Path(file_path).read_text()

# Load the rulebook into a variable
rules_content = read_rules("01_alliance-rulebook.md")

# Inject it into your System Prompt
system_prompt = f"You are the ALLIANCE Facilitator. Use these rules: {rules_content}"
