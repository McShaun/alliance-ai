import streamlit as st
import google.generativeai as genai
from pathlib import Path
from google.generativeai.types import HarmCategory, HarmBlockThreshold

# 1. Page Configuration (Make it look like a tactical terminal)
st.set_page_config(page_title="ALLIANCE Adjudicator", page_icon="🌍", layout="centered")
st.title("ALLIANCE: Global Adjudication Terminal")

with st.sidebar:
    offline_debug_mode = st.checkbox('Offline Debug Mode')

# 2. Secure the API Key
# This pulls the key you saved in the Streamlit Secrets menu
api_key = st.secrets["GOOGLE_API_KEY"]
genai.configure(api_key=api_key)

# 3. Load the Brain (Prompt + Rules)
# Make sure jane_mechanics.md is in the exact same folder as this script
rules_text = Path("jane_mechanics.md").read_text(encoding="utf-8")
nation_data_text = Path("ALLIANCE_nation_data_formatted.json").read_text(encoding="utf-8")

with open("oracle_skills.md", "r", encoding="utf-8") as f:
    master_prompt = f.read().format(
        nation_data_text=nation_data_text,
        rules_text=rules_text
    )

def consult_full_rulebook(query: str = "") -> str:
    """Search the full 01_alliance-rulebook.md for detailed rules and lore when the core mechanics are insufficient to answer the user's query."""
    return Path("01_alliance-rulebook.md").read_text()

# 4. Initialize the Model
# We use gemini-1.5-flash because it is fast and handles massive text (like your rulebook) easily
model = genai.GenerativeModel(
    model_name="gemini-2.5-flash",
    system_instruction=master_prompt,
    tools=[consult_full_rulebook],
    safety_settings={
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
    }
)

# 5. Set up Chat Memory
# This keeps the bot from getting amnesia after every single message
if "chat_session" not in st.session_state:
    st.session_state.chat_session = model.start_chat(history=[])

# Display the chat history on the screen
for message in st.session_state.chat_session.history:
    role = "assistant" if message.role == "model" else "user"
    with st.chat_message(role):
        st.markdown(message.parts[0].text)

# 6. The Input Box (Where students type their Action Reports)
user_input = st.chat_input("Submit Action Report or Query...")

if user_input:
    # Show what the user typed
    with st.chat_message("user"):
        st.markdown(user_input)
    
    # Send it to Jane and get the response
    with st.chat_message("assistant"):
        if offline_debug_mode:
            st.markdown(f"DEBUG MODE: Jane is offline. You submitted: {user_input}")
        else:
            # The user sees: "What are the rules on movement?"
            # The AI receives: "Adjudicate the following tabletop game query: What are the rules on movement?"
            
            fictional_context = "Adjudicate the following tabletop game query: "
            response = st.session_state.chat_session.send_message(fictional_context + user_input)
            # Check if the response actually has parts/text before displaying
            try:
                if response.parts:
                    st.markdown(response.text)
                else:
                    st.error("The Oracle has declined to adjudicate this strategy due to safety filters.")
            except ValueError:
                st.error("The Oracle is silent. The proposed action may be too extreme or violates safety guidelines.")
