"""
Sidebar Component - Navigation and Settings
"""

import streamlit as st


def render_sidebar():
    """Render the navigation sidebar with settings."""

    with st.sidebar:
        # ── Logo & Title ──
        st.markdown("""
        <div style="text-align: center; padding: 1rem 0;">
            <h1 style="font-size: 1.5rem; margin: 0;">🧠 Smart Quiz</h1>
            <p style="font-size: 0.8rem; color: #9ca3af; margin-top: 0.25rem;">
                AI-Powered Quiz Generator
            </p>
        </div>
        """, unsafe_allow_html=True)

        st.divider()

        # ── Navigation ──
        st.markdown("### 📍 Navigation")

        current = st.session_state.current_page

        # Upload Page Button
        upload_disabled = False
        if st.button(
            "📤 Upload Notes",
            type="primary" if current == "upload" else "secondary",
            use_container_width=True,
            disabled=upload_disabled
        ):
            st.session_state.navigate_to("upload")

        # Quiz Page Button
        quiz_disabled = st.session_state.quiz_data is None
        if st.button(
            "📝 Take Quiz",
            type="primary" if current == "quiz" else "secondary",
            use_container_width=True,
            disabled=quiz_disabled
        ):
            st.session_state.navigate_to("quiz")

        # Results Page Button
        results_disabled = not st.session_state.quiz_completed
        if st.button(
            "📊 Results",
            type="primary" if current == "results" else "secondary",
            use_container_width=True,
            disabled=results_disabled
        ):
            st.session_state.navigate_to("results")

        st.divider()

        # ── Quiz Settings ──
        st.markdown("### ⚙️ Quiz Settings")

        col1, col2 = st.columns(2)
        with col1:
            num_questions = st.number_input(
                "Questions",
                min_value=3,
                max_value=20,
                value=st.session_state.quiz_config["num_questions"],
                step=1,
                key="sidebar_num_questions"
            )
        with col2:
            difficulty = st.selectbox(
                "Difficulty",
                options=["easy", "medium", "hard"],
                index=["easy", "medium", "hard"].index(
                    st.session_state.quiz_config["difficulty"]
                ),
                key="sidebar_difficulty"
            )

        # Update config
        st.session_state.quiz_config["num_questions"] = num_questions
        st.session_state.quiz_config["difficulty"] = difficulty

        # Backend URL
        st.markdown("### 🔗 Backend")
        backend_url = st.text_input(
            "API URL",
            value=st.session_state.backend_url,
            key="sidebar_backend_url"
        )
        st.session_state.backend_url = backend_url

        st.divider()

        # ── Session Info ──
        st.markdown("### 📋 Session Info")

        info_items = []
        if st.session_state.uploaded_file:
            info_items.append(f"📄 File: {st.session_state.uploaded_file}")
        if st.session_state.quiz_data:
            info_items.append(f"❓ Questions: {len(st.session_state.quiz_data.get('questions', []))}")
        if st.session_state.quiz_completed:
            info_items.append(f"✅ Score: {st.session_state.score}/{st.session_state.total_questions}")

        if info_items:
            for item in info_items:
                st.markdown(f"<small>{item}</small>", unsafe_allow_html=True)
        else:
            st.markdown("<small style='color: #9ca3af;'>No active session</small>", unsafe_allow_html=True)

        st.divider()

        # ── Reset Button ──
        if st.button("🔄 Reset Session", use_container_width=True, type="secondary"):
            for key in list(st.session_state.keys()):
                if key not in ["navigate_to", "backend_url"]:
                    del st.session_state[key]
            st.session_state.current_page = "upload"
            st.session_state.uploaded_file = None
            st.session_state.extracted_text = ""
            st.session_state.quiz_data = None
            st.session_state.current_question_idx = 0
            st.session_state.user_answers = {}
            st.session_state.quiz_completed = False
            st.session_state.score = 0
            st.session_state.total_questions = 0
            st.session_state.quiz_config = {
                "num_questions": 5,
                "difficulty": "medium",
                "question_type": "mcq"
            }
            st.session_state.quiz_history = []
            st.session_state.show_explanation = False
            st.rerun()

        # ── Footer ──
        st.markdown("""
        <div style="position: fixed; bottom: 1rem; left: 1rem; right: 1rem;">
            <p style="text-align: center; font-size: 0.7rem; color: #9ca3af;">
                Made with 💜 by AI/ML Club<br>
                DPES College of Engineering
            </p>
        </div>
        """, unsafe_allow_html=True)