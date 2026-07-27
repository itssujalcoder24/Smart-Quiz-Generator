"""
Quiz Page - Interactive quiz taking interface
"""

import streamlit as st
import time
from components.progress_bar import render_progress_bar, render_step_indicator
from components.feedback_card import render_inline_feedback


def render_quiz_page():
    """Render the interactive quiz page."""

    # ── Header ──
    st.markdown('<h1 class="main-title">📝 Take Your Quiz</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Test your knowledge with AI-generated questions!</p>', unsafe_allow_html=True)

    # ── Step Indicator ──
    render_step_indicator(["Upload", "Quiz", "Results"], 1)

    # ── Check if quiz data exists ──
    if st.session_state.quiz_data is None:
        st.warning("⚠️ No quiz generated yet. Please upload your notes first.")
        if st.button("Go to Upload", type="primary"):
            st.session_state.navigate_to("upload")
        return

    quiz_data = st.session_state.quiz_data
    questions = quiz_data.get("questions", [])
    total = len(questions)
    current_idx = st.session_state.current_question_idx

    if total == 0:
        st.error("❌ No questions found in the quiz.")
        return

    # ── Progress Bar ──
    render_progress_bar(current_idx, total)

    # ── Current Question ──
    current_question = questions[current_idx]

    # Question card
    st.markdown(f"""
    <div style="
        background: white;
        border-radius: 20px;
        padding: 2rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
    ">
        <div style="display: flex; align-items: center; margin-bottom: 1rem;">
            <span style="
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 0.5rem 1rem;
                border-radius: 12px;
                font-weight: 700;
                font-size: 0.9rem;
                margin-right: 1rem;
            ">Q{current_idx + 1}</span>
            <span style="font-size: 0.85rem; color: #9ca3af; font-weight: 500;">
                Difficulty: {st.session_state.quiz_config['difficulty'].title()}
            </span>
        </div>
        <h3 style="color: #1f2937; font-size: 1.3rem; line-height: 1.6; margin: 0;">
            {current_question['question']}
        </h3>
    </div>
    """, unsafe_allow_html=True)

    # ── Options ──
    options = current_question.get("options", [])
    selected_option = st.session_state.user_answers.get(current_idx, None)

    # Track if user has answered this question
    has_answered = selected_option is not None

    # Show options as buttons
    for i, option in enumerate(options):
        # Determine button style based on state
        if has_answered:
            correct_idx = current_question.get("correct_index", 0)
            if i == correct_idx:
                # Correct answer - always show green
                btn_type = "primary"
                emoji = "✅ "
                disabled = True
            elif i == selected_option and i != correct_idx:
                # Wrong selection - show red
                btn_type = "secondary"
                emoji = "❌ "
                disabled = True
            else:
                # Other options - disabled neutral
                btn_type = "secondary"
                emoji = ""
                disabled = True
        else:
            # Not answered yet - all enabled
            btn_type = "primary" if selected_option == i else "secondary"
            emoji = ""
            disabled = False

        cols = st.columns([10, 1])
        with cols[0]:
            if st.button(
                f"{emoji}{chr(65 + i)}. {option}",
                key=f"option_{current_idx}_{i}",
                type=btn_type,
                use_container_width=True,
                disabled=disabled
            ):
                st.session_state.user_answers[current_idx] = i
                st.rerun()

    # ── Feedback (if answered) ──
    if has_answered:
        correct_idx = current_question.get("correct_index", 0)
        is_correct = selected_option == correct_idx
        explanation = current_question.get("explanation", "No explanation available.")

        render_inline_feedback(is_correct, explanation)

    # ── Navigation ──
    st.markdown("<div style='margin-top: 2rem;'></div>", unsafe_allow_html=True)

    nav_cols = st.columns([2, 3, 2])

    with nav_cols[0]:
        # Previous button
        if current_idx > 0:
            if st.button("⬅️ Previous", use_container_width=True, type="secondary"):
                st.session_state.current_question_idx = current_idx - 1
                st.rerun()

    with nav_cols[1]:
        # Question navigator dots
        dots_html = '<div style="display: flex; justify-content: center; gap: 0.5rem; align-items: center;">'
        for i in range(total):
            if i == current_idx:
                color = "#667eea"
                size = "14px"
            elif i in st.session_state.user_answers:
                # Answered
                color = "#10b981"
                size = "10px"
            else:
                # Not answered
                color = "#e5e7eb"
                size = "10px"

            dots_html += f'<div style="width: {size}; height: {size}; border-radius: 50%; background: {color}; transition: all 0.3s;"></div>'
        dots_html += '</div>'
        st.markdown(dots_html, unsafe_allow_html=True)

    with nav_cols[2]:
        # Next / Finish button
        if current_idx < total - 1:
            if st.button("Next ➡️", use_container_width=True, type="primary"):
                st.session_state.current_question_idx = current_idx + 1
                st.rerun()
        else:
            # Last question - show Finish button
            all_answered = len(st.session_state.user_answers) == total

            if st.button(
                "🏁 Finish Quiz",
                use_container_width=True,
                type="primary",
                disabled=not all_answered
            ):
                _calculate_score()
                st.session_state.quiz_completed = True
                st.session_state.navigate_to("results")


def _calculate_score():
    """Calculate the final score."""
    questions = st.session_state.quiz_data.get("questions", [])
    score = 0

    for idx, question in enumerate(questions):
        user_answer = st.session_state.user_answers.get(idx)
        correct_answer = question.get("correct_index", 0)

        if user_answer == correct_answer:
            score += 1

    st.session_state.score = score

    # Store in history
    quiz_result = {
        "quiz_id": st.session_state.quiz_data.get("quiz_id", "unknown"),
        "score": score,
        "total": len(questions),
        "difficulty": st.session_state.quiz_config["difficulty"],
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    st.session_state.quiz_history.append(quiz_result)