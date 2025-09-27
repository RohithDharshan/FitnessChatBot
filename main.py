import streamlit as st
import requests

# --- Page Configuration ---
st.set_page_config(
    page_title="REVLINE Fitness Chatbot",
    page_icon="💪",
    layout="centered",
    initial_sidebar_state="expanded",
)

# --- Custom CSS for Styling (optional, but nice) ---
st.markdown("""
<style>
    [data-testid="stAppViewContainer"] > .main {
        background-color: #1E1E1E;
    }
    [data-testid="stSidebar"] {
        background-color: #2C2C2C;
    }
</style>
""", unsafe_allow_html=True)

# --- Backend API URL ---
backend_url = "http://127.0.0.1:8000"

# --- Session State Initialization ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "chat_mode" not in st.session_state:
    st.session_state.chat_mode = "Fitness Q&A"
if "pdf_processed" not in st.session_state:
    st.session_state.pdf_processed = False

# --- Sidebar ---
with st.sidebar:
    st.header("Actions & Settings")

    st.radio(
        "Select Chat Mode:",
        ("Fitness Q&A", "Chat with your Plan (PDF)"),
        key="chat_mode",
        on_change=lambda: st.session_state.messages.clear(),
    )

    if st.button("Clear Chat History"):
        st.session_state.messages = []
        st.session_state.pdf_processed = False
        st.rerun()
    
    st.markdown("---")

    with st.expander("Upload & Analyze a Fitness Plan", expanded=True):
        uploaded_file = st.file_uploader("Upload a workout or nutrition PDF", type="pdf")
        if st.button("Process PDF"):
            if uploaded_file is not None:
                with st.spinner("Analyzing your plan..."):
                    try:
                        files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                        response = requests.post(f"{backend_url}/upload-pdf", files=files, timeout=300)
                        
                        if response.status_code == 200:
                            st.success("Plan processed! You can now ask questions in 'Chat with your Plan' mode.")
                            st.session_state.pdf_processed = True
                        else:
                            st.error(f"Error: {response.json().get('detail', 'Unknown error')}")
                    except requests.exceptions.RequestException as e:
                        st.error(f"Connection Error: Is the backend server running?")
            else:
                st.warning("Please upload a PDF file first.")

# --- Main Chat Interface ---
st.title("💪 REVLINE Fitness Chatbot")
st.markdown("Your AI-powered partner for fitness, nutrition, and wellness.")

# Initial message based on chat mode
if not st.session_state.messages:
    if st.session_state.chat_mode == "Fitness Q&A":
        st.session_state.messages.append({"role": "assistant", "content": "Hello! I'm REVLINE. Ask me anything about workouts, nutrition, or wellness!"})
    elif st.session_state.chat_mode == "Chat with your Plan (PDF)":
        if st.session_state.pdf_processed:
            st.session_state.messages.append({"role": "assistant", "content": "Your plan is ready. What would you like to know about it?"})
        else:
             st.session_state.messages.append({"role": "assistant", "content": "Please upload your fitness or nutrition plan to get started."})

# Display existing chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Input field for new user messages
if prompt := st.chat_input("Ask REVLINE for fitness advice..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Determine which endpoint to call
    is_rag_mode = st.session_state.chat_mode == "Chat with your Plan (PDF)"
    endpoint = "/chat-rag" if is_rag_mode else "/chat"
    
    # Check if a PDF is required but not processed
    if is_rag_mode and not st.session_state.pdf_processed:
        st.warning("Please upload and process a PDF plan before asking questions in this mode.")
        st.stop()

    with st.spinner("Thinking..."):
        try:
            payload = {"question": prompt} if is_rag_mode else {"messages": st.session_state.messages}
            response = requests.post(f"{backend_url}{endpoint}", json=payload)

            if response.status_code == 200:
                ai_response = response.json().get("response", {})
                st.session_state.messages.append(ai_response)
                st.rerun()
            else:
                error_detail = response.json().get('detail', f"{response.status_code} {response.reason}")
                st.error(f"Error: {error_detail}")
        except requests.exceptions.RequestException:
            st.error("Connection Error: Could not connect to the backend API. Please ensure the server is running.")