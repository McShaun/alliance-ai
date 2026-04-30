import streamlit as st
import streamlit.components.v1 as components
import google.generativeai as genai
from pathlib import Path
from google.generativeai.types import HarmCategory, HarmBlockThreshold
import shutil
import json

CURRENT_DIR = Path(__file__).parent

def initialize_new_game():
    """Copies alliance_master.json to alliance_active.json for a new session."""
    shutil.copy(CURRENT_DIR / "alliance_master.json", CURRENT_DIR / "alliance_active.json")
    if "chat_session" in st.session_state:
        del st.session_state.chat_session

if not (CURRENT_DIR / "alliance_active.json").exists():
    initialize_new_game()

# 1. Page Configuration (Make it look like a tactical terminal)
st.set_page_config(page_title="ALLIANCE Adjudicator", page_icon="🌍", layout="wide", initial_sidebar_state="collapsed")

# Hide Streamlit Chrome and remove padding
st.markdown("""
<style>
    .block-container {
        padding-top: 0rem;
        padding-bottom: 0rem;
        padding-left: 0rem;
        padding-right: 0rem;
        max-width: 100%;
    }
    header {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# Embed Dashboard HTML
dashboard_html = (CURRENT_DIR / "dashboard.html").read_text(encoding="utf-8")
components.html(dashboard_html, height=2000, scrolling=True)

st.title("ALLIANCE: Global Adjudication Terminal")

with st.sidebar:
    offline_debug_mode = st.checkbox('Offline Debug Mode')
    if st.button('Reset Game'):
        initialize_new_game()
        st.success("Game reset to initial state!")
        st.rerun()

# 2. Secure the API Key
# This pulls the key you saved in the Streamlit Secrets menu
api_key = st.secrets["GOOGLE_API_KEY"]
genai.configure(api_key=api_key)

# 3. Load the Brain (Prompt + Rules)
# Make sure jane_mechanics.md is in the exact same folder as this script
rules_text = (CURRENT_DIR / "jane_mechanics.md").read_text(encoding="utf-8")
nation_data_text = (CURRENT_DIR / "alliance_active.json").read_text(encoding="utf-8")

with open(CURRENT_DIR / "oracle_skills.md", "r", encoding="utf-8") as f:
    master_prompt = f.read().format(
        nation_data_text=nation_data_text,
        rules_text=rules_text
    )

master_prompt += "\n\nCRITICAL INSTRUCTION: You are the ALLIANCE Oracle. You MUST use the update_alliance_ledger tool for all transactions and token deductions."

def consult_full_rulebook(query: str = "") -> str:
    """Search the full 01_alliance-rulebook.md for detailed rules and lore when the core mechanics are insufficient to answer the user's query."""
    return (CURRENT_DIR / "01_alliance-rulebook.md").read_text()

def update_alliance_ledger(team_name: str, token_type: str, amount: int) -> str:
    """
    Updates the active ledger with token deductions. Must ONLY read/write alliance_active.json.
    Args:
        team_name: The title of the nation (e.g., 'Fast-Growing Nation').
        token_type: The type of token (e.g., 'green tokens', 'red tokens', 'white tokens', 'black tokens', 'blue tokens').
        amount: The integer amount to deduct.
    Returns:
        String indicating success or failure.
    """
    ledger_path = CURRENT_DIR / "alliance_active.json"
    if not ledger_path.exists():
        return "Failure: Active ledger not found."
    
    try:
        with open(ledger_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        team_found = False
        for nation in data:
            if nation.get("title", "").strip().lower() == team_name.lower():
                team_found = True
                token_updated = False
                for i in ["1st", "2nd", "3rd", "4th"]:
                    key_num = f"num-of-token_{i}"
                    key_name = f"@{i}_token"
                    if nation.get(key_name, "").strip().lower() == token_type.lower():
                        current_amount_str = nation.get(key_num, "0").strip()
                        current_amount = int(current_amount_str) if current_amount_str else 0
                        
                        if current_amount >= amount:
                            nation[key_num] = str(current_amount - amount)
                            token_updated = True
                            break
                        else:
                            return f"Failure: {team_name} does not have enough {token_type}. Required: {amount}, Available: {current_amount}."
                
                if token_updated:
                    break
                else:
                    return f"Failure: {team_name} does not have {token_type}."
                    
        if not team_found:
            return f"Failure: Team {team_name} not found."
            
        with open(ledger_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
            
        return f"Success: Deducted {amount} {token_type} from {team_name}."
    except Exception as e:
        return f"Failure: An error occurred - {str(e)}"

# 4. Initialize the Model
# We use gemini-1.5-flash because it is fast and handles massive text (like your rulebook) easily
model = genai.GenerativeModel(
    model_name="gemini-2.5-flash",
    system_instruction=master_prompt,
    tools=[consult_full_rulebook, update_alliance_ledger],
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
