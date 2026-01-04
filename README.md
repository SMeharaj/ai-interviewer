🎙️ AI-Powered Mock Interviewer

An intelligent, resume-driven technical interview simulator built with Python, Streamlit, and the Google Gemini API.

📖 Overview

The AI-Powered Mock Interviewer is a web-based application designed to help job seekers practice technical interviews in a personalized environment. Unlike generic interview prep tools, this application analyzes your specific resume to ask tailored questions, simulates a real conversational flow, and provides detailed performance feedback.

✨ Features

Resume Analysis: Supports PDF and DOCX file uploads.

Dynamic Questioning: Generates interview questions based on the candidate's unique skills and projects.

Conversational AI: Uses a state-of-the-art LLM to handle follow-up questions and probe deeper into answers.

Instant Feedback: Provides a comprehensive review highlighting strengths, weaknesses, and actionable advice.

Modern UI: Responsive dark-themed interface built with Streamlit and custom CSS.

🛠️ Tech Stack

Frontend/Backend: Streamlit

AI Model: Google Gemini API (gemini-2.5-flash-preview-09-2025)

Document Parsing: pdfplumber (PDF) and python-docx (DOCX)

Environment Management: python-dotenv

🚀 Setup & Installation

1. Prerequisites

Python 3.10 or higher

A Google Gemini API Key (obtainable from Google AI Studio)

2. Clone the Repository

git clone [https://github.com/YOUR_USERNAME/ai-interviewer.git](https://github.com/YOUR_USERNAME/ai-interviewer.git)
cd ai-interviewer


3. Install Dependencies

python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

pip install -r requirements.txt


4. Configuration

Create a .env file in the root directory and add your API key:

GEMINI_API_KEY="your_api_key_here"


5. Run the Application

streamlit run ai_interviewer_streamlit.py


📝 License

This project is for educational purposes as a part of a Mini Project.
