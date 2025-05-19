import os
import json
import torch
import tempfile
import streamlit as st
import pandas as pd
from langchain_ollama import ChatOllama

# ----- Custom Modules -----
from src.FUNCTION.run_function import FunctionExecutor #execute_function_call
from src.BRAIN.text_to_info import send_to_ai
from src.BRAIN.local_func_call import LocalFunctionCall #create_function_call
from src.CONVERSATION.text_to_speech import speak
from src.FUNCTION.Tools.random_respon import RandomChoice
from src.FUNCTION.Tools.greet_time import TimeOfDay #time_of_day
from DATA.msg import WELCOME_RESPONSES
from src.BRAIN.gem_func_call import GeminiFunctionCaller #gem_generate_fuction_calls
from src.BRAIN.RAG import RAGPipeline #setup_qa_session, ask_question
from src.BRAIN.chat_with_ai import PersonalChatAI #store_important_chat, message_management
from src.CONVERSATION.text_speech import text_to_speech_local
from src.CONVERSATION.voice_text import voice_to_text
from src.BRAIN.code_gen import CodeRefactorAssistant # data analysis 


# ----- Fix for Torch Compatibility -----
if hasattr(torch.classes, '__path__'):
    torch.classes.__path__ = []

#----- Initialize all reusable components once -------
gem_caller = GeminiFunctionCaller()
local_caller = LocalFunctionCall()
func_executor = FunctionExecutor()
time_greeter = TimeOfDay()
code_assistant = CodeRefactorAssistant()
chat_ai = PersonalChatAI()
rag = RAGPipeline()

# ----- Streamlit Watcher Optimization -----
os.environ["STREAMLIT_WATCHER_TYPE"] = "none"

# ---------------- Configuration Flags --------------------------
AI_MODEL = "granite3.1-dense:2b"
RAG_ENABLED = True
PERSONAL_CHAT_ENABLED = True
UPLOAD_DIR = "."
os.makedirs(UPLOAD_DIR, exist_ok=True)

# ---------------- Session Initialization -----------------------
def initialize_session():
    default_states = {
        "chat_mode": "normal",
        "chat_histories": {
            "normal": [],
            "chat_with_ai": [],
            "chat_with_rag": [],
            "data_analysis": []
        },
        "rag_subject": "",
        "voice_output": False,
        "uploaded_file_path": None,
        "audio_input_key_counter": 0
    }
    for key, value in default_states.items():
        if key not in st.session_state:
            st.session_state[key] = value

def set_greeting():
    if "greeted_once" not in st.session_state:
        st.session_state.greeted_once = False

    if not st.session_state.greeted_once:
        greeting_message = f"{time_greeter.time_of_day()}. {RandomChoice.random_choice(WELCOME_RESPONSES)}"
        st.session_state.greeting_message = greeting_message
        st.session_state.greeted_once = True

#---------------- Main Streamlit Flow -------------------
# Ensure the session is initialized
initialize_session()
# Ensure the greeting message is set
set_greeting()

# Check if greeting message exists, and only speak if it's there
if "greeting_message" in st.session_state:
    speak(st.session_state.greeting_message)
    del st.session_state["greeting_message"]

@st.cache_resource(show_spinner=False)
def load_rag_chain(subject):
    try:
        return rag.setup_chain(subject.lower().strip().replace(" ", "_"))
    except Exception as e:
        print(f"Error loading RAG chain: {e}")
        return None

@st.cache_data(show_spinner=False)
def personal_chat_ai(query, max_token=2000):
    try:
        messages = chat_ai.message_management(query)
        llm = ChatOllama(model=AI_MODEL, temperature=0.3, max_token=max_token)
        response_content = "".join(chunk.content for chunk in llm.stream(messages))
        chat_ai.store_important_chat(query, response_content)
        return response_content
    except Exception as e:
        return f"An error occurred: {e}"


def data_analysis(user_prompt: str , file_path:str):
    try:
        # Try to generate code via API
        response = code_assistant.gem_text_to_code(user_prompt , file_path)
        
    except Exception as e:
        # If API fails, log the error and fall back to local code generation
        response = code_assistant.local_text_to_code(user_prompt , file_path)
    return response


def chat_with_rag_session(subject, query):
    subject_key = subject.lower().strip().replace(" ", "_")
    if f"qa_chain_{subject_key}" not in st.session_state:
        st.session_state[f"qa_chain_{subject_key}"] = load_rag_chain(subject_key)
    qa_chain = st.session_state.get(f"qa_chain_{subject_key}")
    return rag.ask(qa_chain, query) if qa_chain else f"Error: Unable to load RAG chain for '{subject}'."


def process_command(command):
    try:
        response_list_dic = gem_caller.generate_function_calls(command)
        if not response_list_dic:
            raise ValueError("Empty or invalid Gemini output.")
    except:
        response_list_dic = local_caller.create_function_call(command)
        if not response_list_dic:
            raise ValueError("Empty or invalid Local model output.")
    results = []
    for response_dic in response_list_dic:
        func_name = response_dic.get("name")
        args = response_dic.get("arguments", {})
        speak(f"Executing function: {func_name}")
        try:
            response = func_executor.execute(response_dic)
            results.append(response)
        except Exception as e:
            speak("An unexpected error occurred.")
            results.append({
                "status": "failed",
                "function_name": func_name,
                "args": args,
                "output": str(e)
            })
    send_to_ai(f"Respond to the user's command '{command}' concisely.")
    return results

def add_message(role, content):
    history = st.session_state.chat_histories[st.session_state.chat_mode]
    if not any(msg["content"] == content and msg["role"] == role for msg in history):
        history.append({"role": role, "content": content})


# ---------------- Sidebar & Mode Selector ---------------------
st.sidebar.markdown("### 🔁 Select Chat Mode")

mode_display_map = {
    "💬 Normal": "normal",
    "🧍 Personal Chat": "chat_with_ai",
    "📚 RAG Chat": "chat_with_rag",
    "📊 Data Analysis": "data_analysis"
}
selected_display = st.sidebar.selectbox("🧠 Select Chat Mode", list(mode_display_map.keys()))
selected_mode = mode_display_map[selected_display]
if selected_mode != st.session_state.chat_mode:
    st.session_state.chat_mode = selected_mode

# Voice Output Toggle
on = st.sidebar.toggle("🎙️ Voice Reply", value=st.session_state.voice_output)
st.session_state.voice_output = on

if st.session_state.chat_mode == "chat_with_rag":
    st.session_state.rag_subject = st.sidebar.selectbox("📘 Select RAG Topic", [
        "Disaster", "Finance", "Healthcare", "Artificial Intelligence", "Climate Change",
        "Cybersecurity", "Education", "Space Technology", "Politics", "History", "Biology"
    ])

# ---------------- Data Analysis Upload ------------------------
if st.session_state.chat_mode == "data_analysis":
    st.sidebar.markdown("### 📤 Upload CSV File")
    uploaded_file = st.sidebar.file_uploader("Choose a CSV file", type=["csv"])

    if uploaded_file:
        file_path = os.path.join(UPLOAD_DIR, uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.session_state.uploaded_file_path = file_path
        st.sidebar.success(f"✅ File saved to: `{file_path}`")
    elif st.session_state.uploaded_file_path:
        st.sidebar.success(f"File already uploaded: `{st.session_state.uploaded_file_path}`")

# ---------------- Current Mode Display ------------------------
st.markdown(f"<div style='text-align: center; font-size: 30px;'>🧠 <b>Current Mode:</b> {st.session_state.chat_mode.upper()}</div>", unsafe_allow_html=True)

# ---------------- Chat History -----------------------
for message in st.session_state.chat_histories[st.session_state.chat_mode]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"], unsafe_allow_html=True)

# ---------------- Chat Input -----------------------
if user_input := st.chat_input("Ask me anything... "):
    st.chat_message("user").markdown(user_input)
    add_message("user", user_input)

    if st.session_state.chat_mode == "chat_with_ai":
        response = personal_chat_ai(user_input)
    elif st.session_state.chat_mode == "chat_with_rag":
        subject = st.session_state.rag_subject
        response = chat_with_rag_session(subject, user_input) if subject else "🚨 Please enter a subject."
    elif st.session_state.chat_mode == "data_analysis":
        try:
            if not st.session_state.uploaded_file_path:
                response = "🚨 Please upload a CSV file first."
            else:
                file_path = st.session_state.uploaded_file_path
                response = data_analysis(user_input,file_path)
        except Exception as e:
            response = f"Error reading CSV: {e}"
    else:
        response = process_command(user_input)

    if isinstance(response, list) and isinstance(response[0], dict):
        for entry in response:
            with st.chat_message("assistant"):
                st.markdown(f"""
                **🔧 Function Executed:** `{entry.get('function_name', 'N/A')}`  
                **📌 Status:** ✅ `{entry.get('status', 'unknown')}`  
                **📂 Arguments:** `{entry.get('args', {})}`  
                **📜 Output:** *{entry.get('output', 'No output.')}*
                """)
        add_message("assistant", json.dumps(response, indent=2))
    else:
        st.chat_message("assistant").markdown(response)
        add_message("assistant", response)

    if st.session_state.voice_output:
        audio_io = text_to_speech_local(str(response).replace("*", ""))
        st.markdown(f"""
            <audio autoplay="true">
                <source src="data:audio/mp3;base64,{audio_io}" type="audio/mp3">
            </audio>
        """, unsafe_allow_html=True)


#------------------- Voice Input & Audio Handling -------------------
audio_key = f"audio_input_key_{st.session_state.audio_input_key_counter}"
audio_value = st.sidebar.audio_input("🎤 Speak", key=audio_key)

if audio_value:
    with tempfile.TemporaryFile(suffix=".wav") as temp_audio:
        temp_audio.write(audio_value.getvalue())
        temp_audio.seek(0)
        transcribed_text = voice_to_text(temp_audio)

    if transcribed_text:
        st.chat_message("user").markdown(transcribed_text)
        add_message("user", transcribed_text)

        if st.session_state.chat_mode == "chat_with_ai":
            response = personal_chat_ai(transcribed_text)
        elif st.session_state.chat_mode == "chat_with_rag":
            subject = st.session_state.rag_subject
            response = chat_with_rag_session(subject, transcribed_text) if subject else "🚨 Please enter a subject."
        elif st.session_state.chat_mode == "data_analysis":
            try:
                if not st.session_state.uploaded_file_path:
                    response = "🚨 Please upload a CSV file first."
                else:
                    file_path = st.session_state.uploaded_file_path
                    response = data_analysis(transcribed_text,file_path)
            except Exception as e:
                response = f"Error reading CSV: {e}"
        else:
            response = process_command(transcribed_text)
        
        if isinstance(response, list) and isinstance(response[0], dict):
            for entry in response:
                with st.chat_message("assistant"):
                    st.markdown(f"""
                    **🔧 Function Executed:** `{entry.get('function_name', 'N/A')}`  
                    **📌 Status:** ✅ `{entry.get('status', 'unknown')}`  
                    **📂 Arguments:** `{entry.get('args', {})}`  
                    **📜 Output:** *{entry.get('output', 'No output.')}*
                    """)
            add_message("assistant", json.dumps(response, indent=2))
        else:
            st.chat_message("assistant").markdown(response)
            add_message("assistant", response)

        # st.chat_message("assistant").markdown(str(response))
        # add_message("assistant", str(response))

        if st.session_state.voice_output:
            full_response = "\n".join([sub_response.get("output", "") for sub_response in response]) if isinstance(response, list) else str(response)
            audio_io = text_to_speech_local(full_response.replace("*", ""))
            st.markdown(f"""
                <audio autoplay="true">
                    <source src="data:audio/mp3;base64,{audio_io}" type="audio/mp3">
                </audio>
            """, unsafe_allow_html=True)

        del st.session_state[audio_key]
        st.session_state.audio_input_key_counter += 1

# ---------------- Download History -------------------
st.sidebar.download_button(
    label="📅 Download Chat History",
    data=json.dumps(st.session_state.chat_histories[st.session_state.chat_mode], indent=2),
    file_name="chat_history.json",
    mime="application/json"
)