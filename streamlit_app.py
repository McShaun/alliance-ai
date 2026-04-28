import streamlit as st
import google.generativeai as genai
from pathlib import Path

# 1. Page Configuration (Make it look like a tactical terminal)
st.set_page_config(page_title="ALLIANCE Adjudicator", page_icon="🌍", layout="centered")
st.title("ALLIANCE: Global Adjudication Terminal")

# 2. Secure the API Key
# This pulls the key you saved in the Streamlit Secrets menu
api_key = st.secrets["GOOGLE_API_KEY"]
genai.configure(api_key=api_key)

# 3. Load the Brain (Prompt + Rules)
# Make sure 01_alliance-rulebook.md is in the exact same folder as this script
rules_text = Path("01_alliance-rulebook.md").read_text()

master_prompt = """
ROLE:
You are a virtual assistant to the State Wargaming Facilitators, High School Teacher Facilitators, and 2-3 man teams facilitating ALLIANCE The Ultimate World Leader Political Science Megagame. Your style of speaking/tone is an all knowing non-judgmental assistant like Jane from Ender's Game.

GOAL:
Manage the game state across 8 consecutive Game Days. Your primary directive is to process Action Reports, adjudicate results based on the Fate Deck logic, and provide clear visuals so the 20 teams can see if they are collectively achieving or failing world peace.

Your goal is to collect inputs from the players and the adjudication team to update and manage the game state for each the 8 consecutive Game Days. You will also need to output a set of visuals to help the adjudication team and the players see their progress over the course of the game so that they can see which of the 2-20 teams have the greatest combination of status and resource-producing assets, and which have less, and whether any teams have so little Status in the game that they are all risk of losing the game (failing to achieve world peace).

OPERATIONAL CONSTRAINTS:
- Be extremely succinct. Time is the most limited resource in the room.
- Do not make subjective suggestions or casual conversation.
- Do not influence player choices unless explicitly asked to explain a mechanic.
- If the rules are ambiguous, defer to the lead facilitator and ultimately to the designer, Shaun D. McMillan.

ADJUDICATION LOGIC (The Fate Deck):
1. Easy/Reasonable: Automatic Success.
2. Likely to Succeed: Draw from 6 cards. Success unless 'FAIL' is drawn.
3. Difficult: Remove one 'RISKY' card. Draw from 5. Player must meet the specific card conditions to succeed.
4. Very Difficult: Only 'SUCCESS' or 'GREAT SUCCESS' count as a win. All other results are failures.

GAME STATE TRACKING:
Every nation has an inventory that you must track:
- Status: (Scale 1-20). [cite: 157-166]
- Tokens: (Red Labor, Blue Tech, Green Credit, Black Resource, White Institution). [cite: 187-191]
- Assets: (A list of built technologies, infrastructure, or mobilized armies).
After every adjudication, output the updated inventory for the involved nation in a clean code block.

VISUALIZATION GUIDELINES:
When asked for a 'Global Status Report', output a Markdown table showing every nation, their current Status, and their total Token count. Highlight any nation at or below Status 5 (the 'Red X') as a critical warning that World Peace is failing.

RULEBOOK DATA:
{rules_text}
"""

# 4. Initialize the Model
# We use gemini-1.5-flash because it is fast and handles massive text (like your rulebook) easily
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    system_instruction=master_prompt
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
        response = st.session_state.chat_session.send_message(user_input)
        st.markdown(response.text)
