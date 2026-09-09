import streamlit as st
from lawchatbot import ask_lawbot, listen, speak
import base64

# Function to set background image
def set_bg(image_file):
    with open(image_file, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()
    page_bg = f"""
    <style>
    [data-testid="stAppViewContainer"] {{
        background-image: url("data:image/png;base64,{encoded}");
        background-size: cover;
    }}
    [data-testid="stHeader"] {{
        background: rgba(0,0,0,0);
    }}
    </style>
    """
    st.markdown(page_bg, unsafe_allow_html=True)
    
# Use your local image here
set_bg(r"C:\Users\NEVILLE R\Downloads\1813abbf-0852-4ef9-b7e7-ea65b5c7d6b2.png")

st.title("Interactive Legal Assistant")

# Store chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Input box
user_input = st.text_input("ASK QUESTIONS / DOUBTS:")

# When user sends text
if st.button("Send"):
    if user_input.strip():
        st.session_state.messages.append(("You", user_input))
        response = ask_lawbot(user_input)
        st.session_state.messages.append(("Bot", response))
        speak(response)   

# When user uses voice
if st.button("Speak"):
    spoken_text = listen()
    if spoken_text:
        st.session_state.messages.append(("You (voice)", spoken_text))
        response = ask_lawbot(spoken_text)
        st.session_state.messages.append(("Bot", response))
        speak(response) 
    else:
        st.session_state.messages.append(("System", "Could not capture voice input."))

# Display chat history
for sender, msg in st.session_state.messages:
    st.write(f"**{sender}:** {msg}")
