"""
Upload Page - File upload and text extraction interface
"""

import streamlit as st
import requests
import time
from components.progress_bar import render_step_indicator


def render_upload_page():
    """Render the file upload page."""

    # ── Header ──
    st.markdown('<h1 class="main-title">🧠 Smart Quiz Generator</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Upload your study notes and let AI generate a personalized quiz!</p>', unsafe_allow_html=True)

    # ── Step Indicator ──
    render_step_indicator(["Upload", "Quiz", "Results"], 0)

    # ── Main Content Area ──
    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("### 📤 Upload Your Study Material")

        # File upload area
        uploaded_file = st.file_uploader(
            "Drag and drop your file here",
            type=["pdf", "txt", "docx"],
            help="Supported formats: PDF, TXT, DOCX. Max file size: 10MB",
            label_visibility="collapsed"
        )

        # Or paste text directly
        st.markdown("<p style='text-align: center; color: #9ca3af; margin: 0.5rem 0;'>— OR —</p>", unsafe_allow_html=True)

        pasted_text = st.text_area(
            "Paste your notes here",
            placeholder="Paste your study notes, paragraphs, or any text content here...",
            height=150,
            label_visibility="collapsed"
        )

        # Quiz configuration
        st.markdown("### ⚙️ Quiz Configuration")

        config_col1, config_col2, config_col3 = st.columns(3)

        with config_col1:
            num_questions = st.number_input(
                "Number of Questions",
                min_value=3,
                max_value=20,
                value=st.session_state.quiz_config["num_questions"],
                step=1
            )

        with config_col2:
            difficulty = st.selectbox(
                "Difficulty Level",
                options=["easy", "medium", "hard"],
                index=["easy", "medium", "hard"].index(
                    st.session_state.quiz_config["difficulty"]
                )
            )

        with config_col3:
            question_type = st.selectbox(
                "Question Type",
                options=["Multiple Choice", "True/False"],
                index=0
            )

        # Update session config
        st.session_state.quiz_config["num_questions"] = num_questions
        st.session_state.quiz_config["difficulty"] = difficulty
        st.session_state.quiz_config["question_type"] = "mcq" if question_type == "Multiple Choice" else "true_false"

        # Generate button
        has_content = uploaded_file is not None or (pasted_text and pasted_text.strip())

        generate_disabled = not has_content

        if st.button(
            "🚀 Generate Quiz",
            type="primary",
            use_container_width=True,
            disabled=generate_disabled
        ):
            _handle_generate(uploaded_file, pasted_text)

    with col2:
        # Info card
        st.markdown("""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 16px; padding: 1.5rem; color: white;">
            <h3 style="margin-top: 0; font-size: 1.1rem;">💡 How It Works</h3>
            <ol style="padding-left: 1.2rem; line-height: 1.8;">
                <li>Upload your PDF, TXT, or paste text</li>
                <li>Choose quiz settings</li>
                <li>AI analyzes and generates questions</li>
                <li>Take the interactive quiz</li>
                <li>Get instant feedback & explanations</li>
            </ol>
        </div>
        """, unsafe_allow_html=True)

        # Features card
        st.markdown("""
        <div style="background: white; border-radius: 16px; padding: 1.5rem; margin-top: 1rem; box-shadow: 0 2px 10px rgba(0,0,0,0.05);">
            <h3 style="margin-top: 0; font-size: 1.1rem; color: #374151;">✨ Features</h3>
            <ul style="padding-left: 1.2rem; line-height: 1.8; color: #4b5563;">
                <li>🤖 AI-powered question generation</li>
                <li>📊 Smart difficulty adjustment</li>
                <li>💡 Detailed explanations</li>
                <li>📈 Performance analytics</li>
                <li>🎯 Topic-wise weakness detection</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

        # Supported formats
        st.markdown("""
        <div style="background: #f9fafb; border-radius: 16px; padding: 1.5rem; margin-top: 1rem;">
            <h3 style="margin-top: 0; font-size: 1.1rem; color: #374151;">📁 Supported Formats</h3>
            <div style="display: flex; gap: 0.5rem; flex-wrap: wrap;">
                <span style="background: #ede9fe; color: #7c3aed; padding: 0.25rem 0.75rem; border-radius: 20px; font-size: 0.8rem; font-weight: 600;">PDF</span>
                <span style="background: #dbeafe; color: #2563eb; padding: 0.25rem 0.75rem; border-radius: 20px; font-size: 0.8rem; font-weight: 600;">TXT</span>
                <span style="background: #d1fae5; color: #059669; padding: 0.25rem 0.75rem; border-radius: 20px; font-size: 0.8rem; font-weight: 600;">DOCX</span>
            </div>
        </div>
        """, unsafe_allow_html=True)


def _handle_generate(uploaded_file, pasted_text):
    """Handle quiz generation request."""

    progress_bar = st.progress(0)
    status_text = st.empty()

    try:
        backend_url = st.session_state.backend_url

        # Step 1: Prepare content
        status_text.info("📄 Reading your content...")
        progress_bar.progress(10)
        time.sleep(0.5)

        files = None
        data = {
            "num_questions": st.session_state.quiz_config["num_questions"],
            "difficulty": st.session_state.quiz_config["difficulty"],
            "question_type": st.session_state.quiz_config["question_type"]
        }

        if uploaded_file:
            files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
            st.session_state.uploaded_file = uploaded_file.name
        elif pasted_text:
            data["text_content"] = pasted_text
            st.session_state.extracted_text = pasted_text

        # Step 2: Send to backend
        status_text.info("🤖 AI is analyzing your content...")
        progress_bar.progress(30)

        try:
            if files:
                response = requests.post(
                    f"{backend_url}/api/upload",
                    files=files,
                    data=data,
                    timeout=120
                )
            else:
                response = requests.post(
                    f"{backend_url}/api/generate-from-text",
                    json=data,
                    timeout=120
                )

            progress_bar.progress(70)

            if response.status_code == 200:
                quiz_data = response.json()
                st.session_state.quiz_data = quiz_data
                st.session_state.total_questions = len(quiz_data.get("questions", []))
                st.session_state.current_question_idx = 0
                st.session_state.user_answers = {}
                st.session_state.quiz_completed = False
                st.session_state.score = 0

                progress_bar.progress(100)
                status_text.success("✅ Quiz generated successfully!")
                time.sleep(1)

                st.session_state.navigate_to("quiz")
            else:
                error_msg = response.json().get("detail", "Unknown error occurred")
                status_text.error(f"❌ Error: {error_msg}")
                progress_bar.empty()

        except requests.exceptions.ConnectionError:
            # Fallback: Generate mock quiz for demo/testing
            status_text.warning("⚠️ Backend not connected. Using demo mode...")
            progress_bar.progress(50)
            time.sleep(1)

            # Create mock quiz data
            mock_quiz = _generate_mock_quiz()
            st.session_state.quiz_data = mock_quiz
            st.session_state.total_questions = len(mock_quiz["questions"])
            st.session_state.current_question_idx = 0
            st.session_state.user_answers = {}
            st.session_state.quiz_completed = False
            st.session_state.score = 0

            progress_bar.progress(100)
            status_text.success("✅ Demo quiz generated! (Backend not connected)")
            time.sleep(1)

            st.session_state.navigate_to("quiz")

    except Exception as e:
        status_text.error(f"❌ Error: {str(e)}")
        progress_bar.empty()


def _generate_mock_quiz():
    """Generate mock quiz data for demo purposes."""
    return {
        "quiz_id": "demo-quiz-001",
        "title": "Demo Quiz",
        "total_questions": 5,
        "difficulty": st.session_state.quiz_config["difficulty"],
        "questions": [
            {
                "id": 1,
                "question": "What is the primary function of a neural network's hidden layers?",
                "options": [
                    "To store the final output",
                    "To extract features and patterns from input data",
                    "To display results to the user",
                    "To connect directly to the database"
                ],
                "correct_index": 1,
                "explanation": "Hidden layers in a neural network are responsible for extracting features and learning representations from the input data through weighted connections and activation functions."
            },
            {
                "id": 2,
                "question": "Which optimization algorithm is commonly used to minimize the loss function in deep learning?",
                "options": [
                    "Bubble Sort",
                    "Gradient Descent",
                    "Binary Search",
                    "Quick Sort"
                ],
                "correct_index": 1,
                "explanation": "Gradient Descent is the most commonly used optimization algorithm in deep learning. It iteratively adjusts weights to minimize the loss function by moving in the direction of the negative gradient."
            },
            {
                "id": 3,
                "question": "What does 'overfitting' mean in machine learning?",
                "options": [
                    "The model performs well on training data but poorly on new data",
                    "The model is too simple to capture patterns",
                    "The training process is too fast",
                    "The dataset is too large"
                ],
                "correct_index": 0,
                "explanation": "Overfitting occurs when a model learns the training data too well, including its noise and outliers, resulting in poor generalization to unseen data."
            },
            {
                "id": 4,
                "question": "Which of the following is a type of unsupervised learning?",
                "options": [
                    "Linear Regression",
                    "K-Means Clustering",
                    "Decision Trees",
                    "Logistic Regression"
                ],
                "correct_index": 1,
                "explanation": "K-Means Clustering is an unsupervised learning algorithm that groups data points into clusters without predefined labels, unlike supervised methods like regression and classification."
            },
            {
                "id": 5,
                "question": "What is the purpose of the ReLU activation function?",
                "options": [
                    "To normalize input data",
                    "To introduce non-linearity by outputting max(0, x)",
                    "To compress data into a smaller dimension",
                    "To shuffle the training data"
                ],
                "correct_index": 1,
                "explanation": "ReLU (Rectified Linear Unit) introduces non-linearity by outputting the input directly if positive, otherwise zero. This helps neural networks learn complex patterns efficiently."
            }
        ]
    }