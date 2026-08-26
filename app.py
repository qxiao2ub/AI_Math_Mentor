import hashlib
import json

import pandas as pd
import streamlit as st

from math_mentor import (
    ADVISOR,
    AUTHOR,
    FEEDBACK_STYLES,
    LEVEL_TO_DIFFICULTY,
    PROBLEM_BANK,
    PROBLEMS_BY_ID,
    StudentProfile,
    load_student_history,
    record_feedback_reward,
    report_to_markdown,
    run_mentor_attempt,
    weakness_summary,
)

st.set_page_config(
    page_title="AI Math Mentor | Anchit Nayak",
    page_icon="🧠",
    layout="wide",
)


def safe_student_id(display_name: str) -> str:
    base = (display_name or "student").strip().lower().encode("utf-8")
    return "streamlit_" + hashlib.sha256(base).hexdigest()[:12]


st.title("🧠 AI Math Mentor")
st.caption(f"Author: **{AUTHOR}** · Advisor: **{ADVISOR}**")
st.write(
    "A prototype math-learning assistant that checks submitted steps symbolically, "
    "diagnoses mistakes with hybrid rules + ML/DNN models, tracks weaknesses, and recommends what to practice next."
)

with st.sidebar:
    st.header("Student profile")
    display_name = st.text_input("Display name", value="Demo Student")
    grade_band = st.selectbox(
        "Grade band",
        ["Grades 5-7", "Grades 7-10", "Grades 9-12", "College / AP", "College"],
        index=2,
    )
    preferred_feedback = st.radio(
        "Preferred feedback style",
        FEEDBACK_STYLES,
        format_func=lambda x: x.replace("_", " ").title(),
    )
    st.subheader("Current level by topic")
    levels = list(LEVEL_TO_DIFFICULTY)
    algebra_level = st.selectbox("Algebra", levels, index=2)
    calculus_level = st.selectbox("Calculus", levels, index=0)
    probability_level = st.selectbox("Probability", levels, index=2)
    de_level = st.selectbox("Differential Equations", levels, index=0)
    st.divider()
    st.markdown(f"**Author:** {AUTHOR}")
    st.markdown(f"**Advisor:** {ADVISOR}")

profile = StudentProfile(
    student_id=safe_student_id(display_name),
    display_name=display_name or "Student",
    grade_band=grade_band,
    current_levels={
        "Algebra": algebra_level,
        "Calculus": calculus_level,
        "Probability": probability_level,
        "Differential Equations": de_level,
    },
    preferred_feedback=preferred_feedback,
)

mentor_tab, progress_tab, about_tab = st.tabs(["Math Mentor", "Learning Progress", "About"])

with mentor_tab:
    left, right = st.columns([1.3, 1])
    with left:
        problem_labels = {
            f"{p.problem_id} · {p.topic} · difficulty {p.difficulty}": p.problem_id
            for p in PROBLEM_BANK
        }
        selected_label = st.selectbox("Choose a problem", list(problem_labels.keys()), index=1)
        problem_id = problem_labels[selected_label]
        problem = PROBLEMS_BY_ID[problem_id]
        st.subheader("Problem")
        st.info(problem.prompt)
        st.caption("Skills: " + " · ".join(problem.skills))
        with st.expander("Hints"):
            for idx, hint in enumerate(problem.hints, start=1):
                st.markdown(f"**Hint {idx}:** {hint}")

        defaults = {
            "ARITH-001": "3/4 + 2/3\n9/12 + 8/12\n17/12",
            "ALG-LIN-001": "2*x + 3 = 11\n2*x = 8\nx = 4",
            "ALG-QUAD-001": "x**2 - 5*x + 6 = 0\n(x - 2)*(x - 3) = 0\nx = 2\nx = 3",
            "CALC-DERIV-001": "Derivative(x**3 - 4*x + 7, x)\n3*x**2 - 4 + 0\n3*x**2 - 4",
            "PROB-001": "P_none = (1/2)**2\nP_at_least_one = 1 - P_none\nP_at_least_one = 3/4",
            "DE-EXP-001": "1/y\nlog(y) = 3*t + C\ny = C*exp(3*t)\ny = 2*exp(3*t)",
        }
        steps_text = st.text_area(
            "Solution steps — one mathematical step per line",
            value=defaults[problem_id],
            height=190,
            help="You can use forms such as 2x + 3 = 11, 2*x = 8, x^2, or x**2.",
        )
        analyze = st.button("Analyze solution", type="primary", use_container_width=True)

    with right:
        st.subheader("How the prototype evaluates work")
        st.markdown(
            "1. **Parse** each submitted line with SymPy.\n"
            "2. **Compare symbolically** with the expected solution trajectory.\n"
            "3. **Classify mistakes** with transparent rules plus ML/DNN classifiers.\n"
            "4. **Store attempt history** in SQLite for weakness analysis.\n"
            "5. **Select feedback style** using an epsilon-greedy contextual bandit.\n"
            "6. **Recommend the next problem** from current level + observed weaknesses."
        )
        st.warning(
            "Educational prototype only. It is not a replacement for a teacher, and the starter problem bank is intentionally small."
        )

    if analyze:
        steps = [line.strip() for line in steps_text.splitlines() if line.strip()]
        if not steps:
            st.error("Enter at least one solution step.")
        else:
            with st.spinner("Analyzing the submitted solution..."):
                report = run_mentor_attempt(profile, problem_id, steps, save=True)
            st.session_state["last_report"] = report
            st.session_state["feedback_recorded"] = False

    report = st.session_state.get("last_report")
    if report:
        st.divider()
        st.subheader("Mentor analysis")
        scores = report["scores"]
        c1, c2, c3 = st.columns(3)
        c1.metric("Overall score", f"{scores['overall_score']:.1f}/100")
        c2.metric("Step accuracy", f"{100*scores['step_accuracy']:.1f}%")
        c3.metric("Expected-path coverage", f"{100*scores['coverage']:.1f}%")

        evaluation_df = pd.DataFrame(report["evaluations"])
        if not evaluation_df.empty:
            visible_cols = ["student_step_index", "student_step", "is_correct", "error_type", "confidence", "concept", "expected_step"]
            st.dataframe(evaluation_df[visible_cols], use_container_width=True, hide_index=True)

        feedback_by_step = {item["step"]: item for item in report["feedback"]}
        for evaluation in report["evaluations"]:
            status = "✅ Correct" if evaluation["is_correct"] else "🔎 Needs revision"
            with st.expander(f"Step {evaluation['student_step_index']} · {status}", expanded=not evaluation["is_correct"]):
                st.code(evaluation["student_step"], language=None)
                st.write(f"**Expected target:** `{evaluation['expected_step']}`")
                st.write(f"**Diagnosis:** {evaluation['explanation']}")
                item = feedback_by_step[evaluation["student_step_index"]]
                st.success(f"Mentor response — {item['style'].replace('_', ' ')}: {item['feedback']}")

        rec = report["recommended_problem"]
        st.subheader("Recommended next problem")
        st.info(f"**{rec['problem_id']} · {rec['topic']} · difficulty {rec['difficulty']}**\n\n{rec['prompt']}")

        incorrect = [e for e in report["evaluations"] if not e["is_correct"]]
        if incorrect and not st.session_state.get("feedback_recorded", False):
            st.caption("Help the reinforcement-learning prototype learn which feedback style works for this type of error.")
            b1, b2 = st.columns(2)
            first = incorrect[0]
            first_feedback = feedback_by_step[first["student_step_index"]]
            if b1.button("👍 Feedback was helpful", use_container_width=True):
                record_feedback_reward(profile.student_id, first["error_type"], first_feedback["style"], 1.0)
                st.session_state["feedback_recorded"] = True
                st.success("Feedback preference recorded for this session.")
            if b2.button("👎 Feedback was not helpful", use_container_width=True):
                record_feedback_reward(profile.student_id, first["error_type"], first_feedback["style"], -1.0)
                st.session_state["feedback_recorded"] = True
                st.info("Feedback preference recorded for this session.")

        report_md = report_to_markdown(report)
        st.download_button(
            "Download Markdown report",
            data=report_md,
            file_name=f"math_mentor_attempt_{report.get('attempt_id') or 'latest'}.md",
            mime="text/markdown",
        )
        st.download_button(
            "Download JSON report",
            data=json.dumps(report, indent=2, ensure_ascii=False),
            file_name=f"math_mentor_attempt_{report.get('attempt_id') or 'latest'}.json",
            mime="application/json",
        )

with progress_tab:
    st.subheader(f"Learning progress for {profile.display_name}")
    history = load_student_history(profile.student_id)
    summary = weakness_summary(profile.student_id)
    if history.empty:
        st.info("No saved attempts yet. Analyze a solution in the Math Mentor tab first.")
    else:
        attempt_summary = (
            history[["attempt_id", "problem_id", "topic", "difficulty", "overall_score", "submitted_at"]]
            .drop_duplicates("attempt_id")
            .sort_values("attempt_id", ascending=False)
        )
        c1, c2, c3 = st.columns(3)
        c1.metric("Attempts", int(attempt_summary.shape[0]))
        c2.metric("Average score", f"{attempt_summary['overall_score'].mean():.1f}")
        c3.metric("Topics practiced", int(attempt_summary["topic"].nunique()))
        st.markdown("#### Attempt history")
        st.dataframe(attempt_summary, use_container_width=True, hide_index=True)
        st.markdown("#### Weakness & mastery profile")
        if not summary.empty:
            chart_df = summary[["topic", "concept", "mastery"]].copy()
            chart_df["skill"] = chart_df["topic"] + ": " + chart_df["concept"].str.replace("_", " ")
            st.bar_chart(chart_df.set_index("skill")["mastery"])
            st.dataframe(summary, use_container_width=True, hide_index=True)

with about_tab:
    st.subheader("Project architecture")
    st.code(
        """Student profile
    ↓
Personalization + problem selector
    ↓
Problem bank → submitted solution steps
    ↓
Symbolic step checker (SymPy)
    ↓
Rules + ML/DNN error diagnosis
    ↓
SQLite attempt history
    ↓
Weakness/mastery model + RL feedback bandit
    ↓
Personalized report + next-problem recommendation""",
        language="text",
    )
    st.markdown(
        f"**Author:** {AUTHOR}  \n"
        f"**Advisor:** {ADVISOR}  \n\n"
        "The deterministic symbolic checker is the primary mathematical validator. "
        "Machine-learning components help classify why a step is wrong and personalize feedback; they are not the sole source of mathematical truth."
    )
