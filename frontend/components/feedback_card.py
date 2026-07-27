"""
Feedback Card Component - Answer feedback display
"""

import streamlit as st


def render_feedback_card(
    question_text: str,
    selected_option: str,
    correct_option: str,
    explanation: str,
    is_correct: bool,
    question_number: int
):
    """
    Render a feedback card showing whether the answer was correct or not.

    Args:
        question_text: The question text
        selected_option: User's selected answer
        correct_option: The correct answer
        explanation: Explanation of the correct answer
        is_correct: Whether the user got it right
        question_number: Question number for display
    """
    # Determine styling
    if is_correct:
        border_color = "#10b981"
        bg_color = "#ecfdf5"
        icon = "✅"
        status_text = "Correct!"
        status_color = "#10b981"
    else:
        border_color = "#ef4444"
        bg_color = "#fef2f2"
        icon = "❌"
        status_text = "Incorrect"
        status_color = "#ef4444"

    st.markdown(f"""
    <div style="
        border-left: 5px solid {border_color};
        background: {bg_color};
        border-radius: 0 16px 16px 0;
        padding: 1.25rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    ">
        <div style="display: flex; align-items: center; margin-bottom: 0.75rem;">
            <span style="font-size: 1.5rem; margin-right: 0.5rem;">{icon}</span>
            <span style="font-weight: 700; font-size: 1.1rem; color: {status_color};">
                Question {question_number}: {status_text}
            </span>
        </div>

        <div style="margin-bottom: 0.75rem;">
            <span style="font-weight: 600; color: #374151;">Q: </span>
            <span style="color: #4b5563;">{question_text}</span>
        </div>

        <div style="display: flex; gap: 1rem; margin-bottom: 0.75rem;">
            <div style="flex: 1; padding: 0.5rem; background: white; border-radius: 8px;">
                <span style="font-size: 0.75rem; color: #9ca3af; text-transform: uppercase; font-weight: 600;">Your Answer</span><br>
                <span style="color: {status_color}; font-weight: 600;">{selected_option}</span>
            </div>
            <div style="flex: 1; padding: 0.5rem; background: white; border-radius: 8px;">
                <span style="font-size: 0.75rem; color: #9ca3af; text-transform: uppercase; font-weight: 600;">Correct Answer</span><br>
                <span style="color: #10b981; font-weight: 600;">{correct_option}</span>
            </div>
        </div>

        <div style="background: white; padding: 0.75rem; border-radius: 8px; margin-top: 0.5rem;">
            <span style="font-size: 0.75rem; color: #9ca3af; text-transform: uppercase; font-weight: 600;">💡 Explanation</span><br>
            <span style="color: #4b5563; font-size: 0.95rem;">{explanation}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_inline_feedback(is_correct: bool, explanation: str = None):
    """
    Render a compact inline feedback message.

    Args:
        is_correct: Whether the answer was correct
        explanation: Optional explanation text
    """
    if is_correct:
        st.success("✅ Correct! Great job!")
    else:
        st.error("❌ Incorrect. Don't worry, keep learning!")

    if explanation:
        with st.expander("💡 See Explanation"):
            st.markdown(f"<div style='color: #4b5563; padding: 0.5rem;'>{explanation}</div>", unsafe_allow_html=True)


def render_score_summary(
    score: int,
    total: int,
    correct_count: int,
    wrong_count: int,
    time_taken: str = None
):
    """
    Render a comprehensive score summary card.

    Args:
        score: Points scored
        total: Total possible points
        correct_count: Number of correct answers
        wrong_count: Number of wrong answers
        time_taken: Optional time string (e.g., "5m 30s")
    """
    percentage = (score / total) * 100 if total > 0 else 0

    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 20px;
        padding: 2rem;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 10px 40px rgba(102, 126, 234, 0.3);
    ">
        <h2 style="text-align: center; margin-bottom: 1.5rem; font-size: 1.5rem;">🎯 Quiz Complete!</h2>

        <div style="display: flex; justify-content: center; gap: 2rem; flex-wrap: wrap;">
            <div style="text-align: center;">
                <div style="font-size: 2.5rem; font-weight: 800;">{score}/{total}</div>
                <div style="font-size: 0.9rem; opacity: 0.9;">Score</div>
            </div>
            <div style="text-align: center;">
                <div style="font-size: 2.5rem; font-weight: 800;">{int(percentage)}%</div>
                <div style="font-size: 0.9rem; opacity: 0.9;">Accuracy</div>
            </div>
            <div style="text-align: center;">
                <div style="font-size: 2.5rem; font-weight: 800;">{correct_count}</div>
                <div style="font-size: 0.9rem; opacity: 0.9;">Correct</div>
            </div>
            <div style="text-align: center;">
                <div style="font-size: 2.5rem; font-weight: 800;">{wrong_count}</div>
                <div style="font-size: 0.9rem; opacity: 0.9;">Wrong</div>
            </div>
        </div>

        {time_html}
    </div>
    """.format(
        score=score,
        total=total,
        percentage=percentage,
        correct_count=correct_count,
        wrong_count=wrong_count,
        time_html=f'<div style="text-align: center; margin-top: 1rem; font-size: 1rem; opacity: 0.9;">⏱️ Time Taken: {time_taken}</div>' if time_taken else ''
    ), unsafe_allow_html=True)