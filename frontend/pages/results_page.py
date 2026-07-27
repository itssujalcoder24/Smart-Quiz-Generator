"""
Results Page - Quiz results, analytics, and review
"""

import streamlit as st
import requests
from components.progress_bar import render_step_indicator, render_circular_progress
from components.feedback_card import render_feedback_card, render_score_summary


def render_results_page():
    """Render the quiz results page."""

    # ── Header ──
    st.markdown('<h1 class="main-title">📊 Quiz Results</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Review your performance and learn from your mistakes!</p>', unsafe_allow_html=True)

    # ── Step Indicator ──
    render_step_indicator(["Upload", "Quiz", "Results"], 2)

    # ── Check if quiz was completed ──
    if not st.session_state.quiz_completed or st.session_state.quiz_data is None:
        st.warning("⚠️ No completed quiz found. Please take a quiz first.")
        if st.button("Go to Upload", type="primary"):
            st.session_state.navigate_to("upload")
        return

    quiz_data = st.session_state.quiz_data
    questions = quiz_data.get("questions", [])
    total = len(questions)
    score = st.session_state.score
    correct_count = score
    wrong_count = total - score

    # ── Score Summary Card ──
    render_score_summary(
        score=score,
        total=total,
        correct_count=correct_count,
        wrong_count=wrong_count
    )

    # ── Circular Progress & Stats ──
    col1, col2 = st.columns([1, 2])

    with col1:
        render_circular_progress(score, total)

    with col2:
        st.markdown("### 📈 Performance Breakdown")

        # Performance message
        percentage = (score / total) * 100 if total > 0 else 0
        if percentage >= 80:
            message = "🌟 Outstanding! You have mastered this topic!"
            color = "#10b981"
        elif percentage >= 60:
            message = "👍 Good work! You're on the right track."
            color = "#f59e0b"
        elif percentage >= 40:
            message = "💪 Keep practicing! Review the explanations below."
            color = "#f97316"
        else:
            message = "📚 Don't worry! Learning is a journey. Study the explanations!"
            color = "#ef4444"

        st.markdown(f"""
        <div style="
            background: white;
            border-radius: 16px;
            padding: 1.5rem;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
            border-left: 4px solid {color};
        ">
            <p style="font-size: 1.1rem; color: #374151; margin: 0;">{message}</p>
        </div>
        """, unsafe_allow_html=True)

        # Stats grid
        stats_col1, stats_col2, stats_col3 = st.columns(3)

        with stats_col1:
            st.metric("✅ Correct", correct_count)
        with stats_col2:
            st.metric("❌ Wrong", wrong_count)
        with stats_col3:
            accuracy = f"{int(percentage)}%"
            st.metric("🎯 Accuracy", accuracy)

    # ── Action Buttons ──
    st.markdown("<div style='margin: 1.5rem 0;'></div>", unsafe_allow_html=True)

    action_col1, action_col2, action_col3 = st.columns(3)

    with action_col1:
        if st.button("🔄 Retake Quiz", use_container_width=True, type="primary"):
            # Reset quiz state but keep quiz data
            st.session_state.current_question_idx = 0
            st.session_state.user_answers = {}
            st.session_state.quiz_completed = False
            st.session_state.score = 0
            st.session_state.navigate_to("quiz")

    with action_col2:
        if st.button("📤 New Quiz", use_container_width=True, type="secondary"):
            # Full reset
            st.session_state.quiz_data = None
            st.session_state.current_question_idx = 0
            st.session_state.user_answers = {}
            st.session_state.quiz_completed = False
            st.session_state.score = 0
            st.session_state.total_questions = 0
            st.session_state.uploaded_file = None
            st.session_state.extracted_text = ""
            st.session_state.navigate_to("upload")

    with action_col3:
        if st.button("💾 Save Results", use_container_width=True, type="secondary"):
            _save_results_to_backend()

    # ── Detailed Review ──
    st.markdown("<div style='margin: 2rem 0;'></div>", unsafe_allow_html=True)
    st.markdown("### 🔍 Detailed Review")

    # Toggle for showing all explanations
    show_all = st.toggle("Show all explanations", value=st.session_state.get("show_explanation", False))
    st.session_state.show_explanation = show_all

    # Review each question
    for idx, question in enumerate(questions):
        user_answer = st.session_state.user_answers.get(idx)
        correct_answer = question.get("correct_index", 0)
        is_correct = user_answer == correct_answer

        with st.expander(
            f"{'✅' if is_correct else '❌'} Question {idx + 1}: {question['question'][:60]}...",
            expanded=show_all or not is_correct  # Auto-expand wrong answers
        ):
            render_feedback_card(
                question_text=question['question'],
                selected_option=question['options'][user_answer] if user_answer is not None else "Not answered",
                correct_option=question['options'][correct_answer],
                explanation=question.get('explanation', 'No explanation available.'),
                is_correct=is_correct,
                question_number=idx + 1
            )

    # ── Quiz History ──
    if st.session_state.quiz_history and len(st.session_state.quiz_history) > 1:
        st.markdown("<div style='margin: 2rem 0;'></div>", unsafe_allow_html=True)
        st.markdown("### 📚 Quiz History")

        history_data = []
        for i, result in enumerate(st.session_state.quiz_history[-5:]):  # Last 5
            history_data.append({
                "Quiz #": i + 1,
                "Score": f"{result['score']}/{result['total']}",
                "Accuracy": f"{int((result['score']/result['total'])*100)}%",
                "Difficulty": result['difficulty'].title(),
                "Date": result['timestamp']
            })

        st.dataframe(
            history_data,
            use_container_width=True,
            hide_index=True
        )

    # ── Topic Analysis (if available) ──
    st.markdown("<div style='margin: 2rem 0;'></div>", unsafe_allow_html=True)
    st.markdown("### 🎯 Topic Analysis")

    # Simple topic analysis based on wrong answers
    wrong_questions = []
    for idx, question in enumerate(questions):
        user_answer = st.session_state.user_answers.get(idx)
        correct_answer = question.get("correct_index", 0)
        if user_answer != correct_answer:
            wrong_questions.append(question)

    if wrong_questions:
        st.markdown("""
        <div style="
            background: #fffbeb;
            border: 1px solid #fcd34d;
            border-radius: 12px;
            padding: 1rem;
            margin-bottom: 1rem;
        ">
            <p style="margin: 0; color: #92400e; font-weight: 600;">
                📌 You got {count} question(s) wrong. Focus on these areas:
            </p>
        </div>
        """.format(count=len(wrong_questions)), unsafe_allow_html=True)

        for q in wrong_questions:
            st.markdown(f"""
            <div style="
                background: white;
                border-radius: 8px;
                padding: 0.75rem 1rem;
                margin-bottom: 0.5rem;
                border-left: 3px solid #f59e0b;
            ">
                <span style="color: #4b5563; font-size: 0.95rem;">• {q['question']}</span>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.success("🎉 Perfect score! You nailed every question. Amazing work!")

    # ── Share Results ──
    st.markdown("<div style='margin: 2rem 0;'></div>", unsafe_allow_html=True)
    st.markdown("### 📤 Share Your Results")

    share_text = f"I scored {score}/{total} ({int(percentage)}%) on my Smart Quiz! 🧠✨"

    share_col1, share_col2 = st.columns(2)
    with share_col1:
        st.code(share_text, language="text")
    with share_col2:
        st.button("📋 Copy to Clipboard", use_container_width=True)


def _save_results_to_backend():
    """Save quiz results to the backend."""
    try:
        backend_url = st.session_state.backend_url
        payload = {
            "quiz_id": st.session_state.quiz_data.get("quiz_id", "unknown"),
            "score": st.session_state.score,
            "total_questions": st.session_state.total_questions,
            "user_answers": st.session_state.user_answers,
            "difficulty": st.session_state.quiz_config["difficulty"]
        }

        response = requests.post(
            f"{backend_url}/api/save-results",
            json=payload,
            timeout=10
        )

        if response.status_code == 200:
            st.success("✅ Results saved successfully!")
        else:
            st.warning("⚠️ Could not save to backend. Results are stored locally.")

    except requests.exceptions.ConnectionError:
        st.info("💾 Results saved locally. (Backend not connected)")
    except Exception as e:
        st.error(f"❌ Error saving results: {str(e)}")