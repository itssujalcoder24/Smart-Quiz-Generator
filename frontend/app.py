"""
Smart Quiz Generator - Streamlit Frontend
Main entry point with page routing and session state management.
"""

import streamlit as st
from pages.upload_page import render_upload_page
from pages.quiz_page import render_quiz_page
from pages.results_page import render_results_page
from components.sidebar import render_sidebar

# ────────────────────────────────────────────
# Page Configuration
# ────────────────────────────────────────────
st.set_page_config(
    page_title="Smart Quiz Generator",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ────────────────────────────────────────────
# Custom CSS for Modern UI
# ────────────────────────────────────────────
CUSTOM_CSS = """
<style>
    /* Global Styling */
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        min-height: 100vh;
    }

    /* Title Styling */
    .main-title {
        font-size: 3rem;
        font-weight: 800;
        background: linear-gradient(90deg, #f093fb 0%, #f5576c 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0.5rem;
    }

    .subtitle {
        text-align: center;
        color: #6b7280;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }

    /* Card Styling */
    .stCard {
        border-radius: 16px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        background: white;
        padding: 1.5rem;
        margin-bottom: 1rem;
    }

    /* Button Styling */
    .stButton > button {
        border-radius: 12px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
    }

    /* Progress Bar */
    .progress-container {
        background: #e5e7eb;
        border-radius: 10px;
        height: 10px;
        overflow: hidden;
    }

    .progress-fill {
        height: 100%;
        border-radius: 10px;
        transition: width 0.5s ease;
    }

    /* Feedback Cards */
    .correct-answer {
        border-left: 4px solid #10b981;
        background: #ecfdf5;
        padding: 1rem;
        border-radius: 0 12px 12px 0;
    }

    .wrong-answer {
        border-left: 4px solid #ef4444;
        background: #fef2f2;
        padding: 1rem;
        border-radius: 0 12px 12px 0;
    }

    /* Animation */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }

    .animate-fade-in {
        animation: fadeIn 0.6s ease-out;
    }

    /* Quiz Option Buttons */
    .quiz-option {
        width: 100%;
        padding: 1rem;
        margin: 0.5rem 0;
        border: 2px solid #e5e7eb;
        border-radius: 12px;
        background: white;
        cursor: pointer;
        transition: all 0.2s ease;
        text-align: left;
        font-size: 1rem;
    }

    .quiz-option:hover {
        border-color: #667eea;
        background: #f5f3ff;
    }

    .quiz-option.selected {
        border-color: #667eea;
        background: #ede9fe;
    }

    /* Score Circle */
    .score-circle {
        width: 150px;
        height: 150px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 2.5rem;
        font-weight: 800;
        margin: 0 auto;
    }
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ────────────────────────────────────────────
# Session State Initialization
# ────────────────────────────────────────────
def init_session_state():
    """Initialize all session state variables."""
    defaults = {
        "current_page": "upload",      # upload | quiz | results
        "uploaded_file": None,
        "extracted_text": "",
        "quiz_data": None,             # Generated quiz from backend
        "current_question_idx": 0,
        "user_answers": {},            # {question_idx: selected_option_idx}
        "quiz_completed": False,
        "score": 0,
        "total_questions": 0,
        "quiz_config": {
            "num_questions": 5,
            "difficulty": "medium",
            "question_type": "mcq"
        },
        "backend_url": "http://localhost:8000",
        "quiz_history": [],            # Past quiz results
        "show_explanation": False,     # Toggle for showing explanations
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

init_session_state()

# ────────────────────────────────────────────
# Navigation Handler
# ────────────────────────────────────────────
def navigate_to(page: str):
    """Navigate to a specific page."""
    st.session_state.current_page = page
    st.rerun()

# Make navigate_to available globally
st.session_state.navigate_to = navigate_to

# ────────────────────────────────────────────
# Main App Layout
# ────────────────────────────────────────────
def main():
    """Main application router."""

    # Render sidebar navigation
    render_sidebar()

    # Route to appropriate page
    current_page = st.session_state.current_page

    if current_page == "upload":
        render_upload_page()
    elif current_page == "quiz":
        render_quiz_page()
    elif current_page == "results":
        render_results_page()
    else:
        st.error(f"Unknown page: {current_page}")
        st.session_state.current_page = "upload"
        st.rerun()

if __name__ == "__main__":
    main()