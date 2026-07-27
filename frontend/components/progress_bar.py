"""
Progress Bar Component - Visual quiz progress indicator
"""

import streamlit as st


def render_progress_bar(current: int, total: int, show_percentage: bool = True):
    """
    Render a custom styled progress bar.

    Args:
        current: Current question index (0-based)
        total: Total number of questions
        show_percentage: Whether to show percentage text
    """
    progress = (current / total) * 100 if total > 0 else 0

    # Color based on progress
    if progress < 33:
        color = "#ef4444"  # Red
    elif progress < 66:
        color = "#f59e0b"  # Orange
    else:
        color = "#10b981"  # Green

    st.markdown(f"""
    <div style="margin-bottom: 1.5rem;">
        <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
            <span style="font-weight: 600; color: #374151;">Question {current + 1} of {total}</span>
            <span style="font-weight: 600; color: {color};">{int(progress)}%</span>
        </div>
        <div class="progress-container">
            <div class="progress-fill" style="width: {progress}%; background: linear-gradient(90deg, {color}, {color}aa);"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_step_indicator(steps: list, current_step: int):
    """
    Render a multi-step progress indicator.

    Args:
        steps: List of step names
        current_step: Current active step index (0-based)
    """
    total_steps = len(steps)

    html = '<div style="display: flex; align-items: center; margin-bottom: 2rem;">'

    for i, step in enumerate(steps):
        # Determine state
        if i < current_step:
            bg_color = "#10b981"
            text_color = "white"
            icon = "✓"
        elif i == current_step:
            bg_color = "#667eea"
            text_color = "white"
            icon = str(i + 1)
        else:
            bg_color = "#e5e7eb"
            text_color = "#9ca3af"
            icon = str(i + 1)

        # Determine label color
        label_color = text_color if i == current_step else "#9ca3af"

        # Circle
        html += f'<div style="display: flex; flex-direction: column; align-items: center;">'
        html += f'<div style="width: 36px; height: 36px; border-radius: 50%; background: {bg_color}; color: {text_color}; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 0.9rem; transition: all 0.3s ease;">{icon}</div>'
        html += f'<span style="font-size: 0.75rem; margin-top: 0.25rem; color: {label_color};">{step}</span>'
        html += '</div>'

        # Connector line (except for last item)
        if i < total_steps - 1:
            line_color = "#10b981" if i < current_step else "#e5e7eb"
            html += f'<div style="flex: 1; height: 2px; background: {line_color}; margin: 0 0.5rem; margin-bottom: 1.5rem;"></div>'

    html += '</div>'

    st.markdown(html, unsafe_allow_html=True)


def render_circular_progress(score: int, total: int, size: int = 150):
    """
    Render a circular progress indicator for final score.

    Args:
        score: Correct answers count
        total: Total questions
        size: Diameter in pixels
    """
    percentage = (score / total) * 100 if total > 0 else 0

    # Color based on score
    if percentage >= 80:
        color = "#10b981"  # Green
        message = "Excellent! 🎉"
    elif percentage >= 60:
        color = "#f59e0b"  # Orange
        message = "Good job! 👍"
    elif percentage >= 40:
        color = "#f97316"  # Dark orange
        message = "Keep practicing! 💪"
    else:
        color = "#ef4444"  # Red
        message = "Don't give up! 📚"

    # Calculate SVG circle properties
    radius = (size - 10) / 2
    circumference = 2 * 3.14159 * radius
    stroke_dashoffset = circumference - (percentage / 100) * circumference

    st.markdown(f"""
    <div style="text-align: center; margin: 2rem 0;">
        <svg width="{size}" height="{size}" style="transform: rotate(-90deg);">
            <circle cx="{size/2}" cy="{size/2}" r="{radius}" fill="none" stroke="#e5e7eb" stroke-width="10"/>
            <circle cx="{size/2}" cy="{size/2}" r="{radius}" fill="none" stroke="{color}" stroke-width="10" stroke-dasharray="{circumference}" stroke-dashoffset="{stroke_dashoffset}" stroke-linecap="round" style="transition: stroke-dashoffset 1s ease;"/>
        </svg>
        <div style="position: relative; margin-top: -{size/2 + 20}px; font-size: 2rem; font-weight: 800; color: {color};">{score}/{total}</div>
        <div style="margin-top: {size/2 - 20}px; font-size: 1.2rem; font-weight: 600; color: #374151;">{message}</div>
        <div style="font-size: 0.9rem; color: #6b7280; margin-top: 0.5rem;">{int(percentage)}% Accuracy</div>
    </div>
    """, unsafe_allow_html=True)