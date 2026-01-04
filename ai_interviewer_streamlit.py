import streamlit as st
import os
import pathlib
import pdfplumber
import docx
import google.generativeai as genai
from google.api_core.exceptions import ClientError, RetryError
from dotenv import load_dotenv  # Imports the library to read .env files

# --- LOAD ENVIRONMENT VARIABLES ---
load_dotenv()

# --- CONFIGURATION ---
API_KEY = os.getenv("GEMINI_API_KEY")

# System instruction to define the AI's role
SYSTEM_INSTRUCTION = """
You are a professional, rigorous, and helpful AI Technical Interviewer. Your goal is to assess a candidate's knowledge based on their resume.
Your persona is that of a senior engineer or hiring manager at a top tech company. You are thorough, fair, and insightful.

Your process is as follows:
1.  You will be given the candidate's resume text first.
2.  You will start the interview by asking a single, relevant opening question.
3.  You will then ask **only one question at a time.** Do not ask multiple questions in one turn.
4.  Wait for the user's answer before asking your next question.
5.  Your follow-up questions should dig deeper into their previous answer or explore a new area from their resume.
6.  The user will signal to end the interview.
7.  After the interview ends, you MUST provide a comprehensive, constructive performance review.
8.  The feedback should include:
    - An overall assessment of their knowledge.
    - Strengths (areas where they answered well).
    - Weaknesses (areas for improvement, or where answers were vague).
    - Specific, actionable advice for how they can improve.
"""

# --- STYLING (NEW!) ---
# We'll inject custom CSS with st.markdown
page_style = """
<style>
/* --- Main App Styling --- */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

body {
    font-family: 'Inter', sans-serif;
}

/* Set dark background */
[data-testid="stAppViewContainer"] {
    background-color: #0F172A; /* Dark Slate Blue */
    color: #E2E8F0; /* Light Slate */
}

/* Style headers */
h1, h2, h3, h4, h5, h6 {
    color: #FFFFFF; /* White text for titles */
    font-weight: 600;
}

/* --- Chat Styling --- */
[data-testid="stChatInput"] {
    background-color: #1E293B; /* Darker Slate */
    border-top: 1px solid #334155;
}

[data-testid="stChatMessage"] {
    padding: 1rem;
    border-radius: 0.5rem;
    margin-bottom: 1rem;
}

/* AI chat bubble */
[data-testid="stChatMessage"]:has(span[data-testid="chat-avatar-ai"]) {
    background-color: #1E293B; /* Darker Slate */
    color: #E2E8F0;
}

/* User chat bubble */
[data-testid="stChatMessage"]:has(span[data-testid="chat-avatar-user"]) {
    background-color: #334155; /* Mid Slate */
    color: #FFFFFF;
}

/* --- Button Styling --- */
[data-testid="stButton"] button {
    background-color: #3B82F6; /* Bright Blue */
    color: #FFFFFF;
    border: none;
    border-radius: 0.5rem;
    padding: 0.75rem 1.25rem;
    font-weight: 600;
    transition: background-color 0.2s ease, transform 0.2s ease;
}

[data-testid="stButton"] button:hover {
    background-color: #2563EB; /* Darker Blue */
    transform: scale(1.02);
}

[data-testid="stButton"] button:active {
    background-color: #1D4ED8; /* Even Darker Blue */
    transform: scale(0.98);
}

/* Make the "End Interview" button stand out */
[data-testid="stButton"] button:contains("End Interview") {
    background-color: #EF4444; /* Red */
}

[data-testid="stButton"] button:contains("End Interview"):hover {
    background-color: #DC2626; /* Darker Red */
}

/* --- File Uploader Styling --- */
[data-testid="stFileUploader"] {
    background-color: #1E293B;
    border: 1px dashed #334155;
    border-radius: 0.5rem;
    padding: 1rem;
}

[data-testid="stFileUploader"] label {
    color: #E2E8F0;
}

[data-testid="stFileUploader"] [data-testid="stButton"] button {
    background-color: #334155;
    color: #E2E8F0;
}

[data-testid="stFileUploader"] [data-testid="stButton"] button:hover {
    background-color: #475569;
}

/* --- Expander Styling --- */
[data-testid="stExpander"] {
    background-color: #1E293B;
    border-radius: 0.5rem;
}

[data-testid="stExpander"] summary {
    color: #E2E8F0;
    font-weight: 600;
}
</style>
"""

# --- FILE EXTRACTION ---

def extract_text_from_file(uploaded_file) -> str | None:
    """Extracts text from an uploaded PDF or DOCX file."""
    text = ""
    try:
        # Get file extension from the uploaded file's name
        file_name = uploaded_file.name
        file_extension = pathlib.Path(file_name).suffix

        if file_extension == ".pdf":
            # Use pdfplumber to open the file-like object
            with pdfplumber.open(uploaded_file) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            
        elif file_extension == ".docx":
            # Use docx to open the file-like object
            doc = docx.Document(uploaded_file)
            for para in doc.paragraphs:
                text += para.text + "\n"
        
        else:
            st.error(f"Unsupported file type: {file_extension}. Please upload .pdf or .docx.")
            return None
            
        if not text.strip():
            st.warning("Extracted text is empty. The file might be image-based or corrupt.")
            return None
            
        return text.strip()

    except Exception as e:
        st.error(f"Error reading file: {e}")
        return None

# --- AI MODEL SETUP ---

@st.cache_resource
def setup_ai_model():
    """Configures and returns the Gemini model."""
    # Check if the API key was loaded successfully
    if not API_KEY:
        st.error("GEMINI_API_KEY not found. Make sure it's in your .env file.")
        st.stop()
        
    try:
        # Configure the Generative AI library
        genai.configure(api_key=API_KEY)
        model = genai.GenerativeModel(
            # --- UPDATED MODEL NAME ---
            model_name="gemini-2.5-flash-preview-09-2025", 
            system_instruction=SYSTEM_INSTRUCTION
        )
        return model
    except Exception as e:
        st.error(f"Failed to configure AI model: {e}")
        st.stop()


# --- MAIN APP LOGIC ---

def main():
    # Set the page title and icon
    st.set_page_config(page_title="AI Interviewer", page_icon="🎙️", layout="centered")
    
    # --- INJECT THE CUSTOM CSS (NEW!) ---
    st.markdown(page_style, unsafe_allow_html=True)

    # Load the AI model
    model = setup_ai_model()

    # --- Initialize Session State ---
    if "chat_session" not in st.session_state:
        st.session_state.chat_session = None
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "interview_state" not in st.session_state:
        st.session_state.interview_state = "START" 

    # --- 1. UPLOAD PAGE (State: START) ---
    if st.session_state.interview_state == "START":
        st.title("📝 AI Interviewer")
        st.write("Welcome! Upload your resume (.pdf or .docx) to begin your technical interview.")
        
        uploaded_file = st.file_uploader("Choose your resume", type=["pdf", "docx"])
        
        if uploaded_file is not None:
            with st.spinner("Analyzing your resume..."):
                resume_text = extract_text_from_file(uploaded_file)
                
                if resume_text:
                    try:
                        st.session_state.chat_session = model.start_chat()
                        initial_prompt = f"""
                        Here is the candidate's resume. Please analyze it and start the interview by asking your first question.
                        --- RESUME TEXT ---
                        {resume_text}
                        --- END RESUME TEXT ---
                        """
                        response = st.session_state.chat_session.send_message(initial_prompt)
                        st.session_state.messages.append({"role": "ai", "content": response.text})
                        st.session_state.interview_state = "INTERVIEW"
                        st.rerun() 
                        
                    except (ClientError, RetryError) as e:
                        st.error(f"An API error occurred: {e}")
                    except Exception as e:
                        st.error(f"An unexpected error occurred: {e}")

    # --- 2. INTERVIEW CHAT PAGE (State: INTERVIEW) ---
    elif st.session_state.interview_state == "INTERVIEW":
        st.title("Interview in Progress...")

        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
        
        if user_answer := st.chat_input("Your answer..."):
            st.session_state.messages.append({"role": "user", "content": user_answer})
            with st.chat_message("user"):
                st.markdown(user_answer)
                
            with st.spinner("AI is thinking..."):
                try:
                    response = st.session_state.chat_session.send_message(user_answer)
                    st.session_state.messages.append({"role": "ai", "content": response.text})
                    with st.chat_message("ai"):
                        st.markdown(response.text)
                except (ClientError, RetryError) as e:
                    st.error(f"An API error occurred: {e}")
                except Exception as e:
                    st.error(f"An unexpected error occurred: {e}")

        st.write("") # Add a little space
        # This button will now be styled red because of the CSS
        if st.button("End Interview & Get Feedback", type="primary"):
            st.session_state.interview_state = "FEEDBACK"
            st.rerun() 

    # --- 3. FEEDBACK PAGE (State: FEEDBACK) ---
    elif st.session_state.interview_state == "FEEDBACK":
        st.title("Interview Feedback")
        
        st.write("---") # Simple separator
        with st.expander("Show Full Interview Transcript"):
            for msg in st.session_state.messages:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])
        st.write("---")

        with st.spinner("Generating your feedback..."):
            try:
                feedback_prompt = """
                The interview is now complete. Please provide comprehensive feedback on my performance.
                Analyze all my answers (the conversation history) and my resume. 
                Tell me my strengths, weaknesses, and how well my knowledge appears based on our interaction.
                Use Markdown for formatting (e.g., bolding, bullet points).
                """
                feedback_response = st.session_state.chat_session.send_message(feedback_prompt)
                
                st.subheader("Your Performance Review")
                st.markdown(feedback_response.text)
                
            except (ClientError, RetryError) as e:
                st.error(f"An API error occurred while generating feedback: {e}")
            except Exception as e:
                st.error(f"An unexpected error occurred: {e}")

        st.write("") 
        if st.button("Start New Interview"):
            st.session_state.clear()
            st.rerun()

if __name__ == "__main__":
    main()