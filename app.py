from __future__ import annotations

import json
import random
from datetime import datetime, timezone
from html import escape
from typing import Any, Dict, Iterable, List

import pandas as pd
import streamlit as st

from ai_engine import (
    LABEL_TEXT,
    choose_feedback_style,
    evaluate_steps,
    recommend_problem,
    score_results,
    train_error_models,
    update_feedback_bandit,
)
from localization import LANGUAGES, LEVELS, REGIONS, STAGES, tr
from problem_bank import filter_problems, load_problem_bank
from ui_copy import ui
from ui_theme import inject_ui_css, page_header, render_footer, section_heading


st.set_page_config(
    page_title="Uzbekistan AI Math Mentor",
    page_icon="🇺🇿",
    layout="wide",
    initial_sidebar_state="collapsed",
)

NAV_PAGES = ["Home", "Analyze", "Mastery", "About", "Settings"]
NAV_KEYS = {
    "Home": "nav_home",
    "Analyze": "nav_analyze",
    "Mastery": "nav_mastery",
    "About": "nav_about",
    "Settings": "nav_settings",
}
STAGE_KEYS = ["school", "lyceum", "university"]
LEVEL_KEYS = ["entry", "intermediate", "advanced"]


def init_state() -> None:
    defaults: Dict[str, Any] = {
        "lang": "uz",
        "dark_mode": True,
        "nav_page": "Home",
        "profile": {
            "name": "O‘quvchi",
            "country": "O‘zbekiston",
            "region": "Toshkent shahri",
            "stage": "school",
            "grade": 7,
            "level": "intermediate",
        },
        "attempts": [],
        "feedback_entries": [],
        "feedback_q": {"socratic": 0.0, "concise": 0.0, "worked": 0.0},
        "feedback_n": {"socratic": 0, "concise": 0, "worked": 0},
        "last_style": "concise",
        "last_analysis": None,
        "analysis_notice": "",
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


@st.cache_resource(show_spinner=False)
def warm_models() -> bool:
    train_error_models()
    return True


def localized(problem: Dict[str, Any], field: str, lang: str) -> str:
    value = problem.get(field, "")
    if isinstance(value, dict):
        return str(value.get(lang, value.get("en", next(iter(value.values()), ""))))
    return str(value)


def stage_label(lang: str, stage: str) -> str:
    idx = STAGE_KEYS.index(stage) if stage in STAGE_KEYS else 0
    return STAGES.get(lang, STAGES["en"])[idx]


def level_label(lang: str, level: str) -> str:
    idx = LEVEL_KEYS.index(level) if level in LEVEL_KEYS else 1
    return LEVELS.get(lang, LEVELS["en"])[idx]


def grade_options(stage: str) -> List[int]:
    if stage == "school":
        return list(range(1, 12))
    if stage == "lyceum":
        return [1, 2]
    return [1, 2, 3, 4]


def go_to(page: str) -> None:
    st.session_state.nav_page = page


def clear_learning_session() -> None:
    st.session_state.attempts = []
    st.session_state.feedback_entries = []
    st.session_state.feedback_q = {"socratic": 0.0, "concise": 0.0, "worked": 0.0}
    st.session_state.feedback_n = {"socratic": 0, "concise": 0, "worked": 0}
    st.session_state.last_analysis = None
    st.session_state.analysis_notice = "cleared"
    for key in list(st.session_state.keys()):
        if key.startswith("solution_"):
            del st.session_state[key]


def open_problem(problem: Dict[str, Any]) -> None:
    st.session_state.nav_page = "Analyze"
    st.session_state.analyze_topic = problem["topic"]
    st.session_state.analyze_problem_id = problem["id"]
    st.session_state.last_analysis = None


def pick_random_problem(problem_ids: List[str]) -> None:
    if not problem_ids:
        return
    current = st.session_state.get("analyze_problem_id")
    alternatives = [pid for pid in problem_ids if pid != current]
    st.session_state.analyze_problem_id = random.choice(alternatives or problem_ids)
    st.session_state.last_analysis = None


def divider(spacing: str = "4.5rem") -> None:
    st.markdown(
        f'<div style="border-top:1px solid var(--mm-border);margin:{spacing} 0 3.5rem;"></div>',
        unsafe_allow_html=True,
    )


def profile_summary_html(lang: str, profile: Dict[str, Any]) -> str:
    return f"""
    <div class="mm-card mm-card-accent">
        <span class="mm-card-label">{escape(ui(lang, 'profile_summary'))}</span>
        <div class="mm-meta-row" style="margin-top:0">
            <span class="mm-chip mm-chip-primary">🇺🇿 {escape(profile['country'])}</span>
            <span class="mm-chip">{escape(profile['region'])}</span>
            <span class="mm-chip">{escape(stage_label(lang, profile['stage']))}</span>
            <span class="mm-chip">{escape(str(profile['grade']))}</span>
            <span class="mm-chip">{escape(level_label(lang, profile['level']))}</span>
        </div>
    </div>
    """


def problem_bank_dataframe(problems: Iterable[Dict[str, Any]], lang: str) -> pd.DataFrame:
    rows = []
    for problem in problems:
        rows.append(
            {
                "ID": problem["id"],
                tr(lang, "stage"): stage_label(lang, problem["stage"]),
                tr(lang, "grade"): f"{problem['grade_min']}–{problem['grade_max']}",
                tr(lang, "choose_topic"): problem["topic"],
                tr(lang, "difficulty"): int(problem["difficulty"]),
                "Title": localized(problem, "title", lang),
            }
        )
    return pd.DataFrame(rows)


init_state()

# Read the language widget state before the widget is rendered so a language
# change updates all labels in the same rerun.
current_language_label = next(
    (label for label, code in LANGUAGES.items() if code == st.session_state.lang),
    "O‘zbekcha",
)
selected_language_label = st.session_state.get("language_selector", current_language_label)
lang = LANGUAGES.get(selected_language_label, st.session_state.lang)
st.session_state.lang = lang

inject_ui_css(bool(st.session_state.dark_mode))
warm_models()
problems = load_problem_bank()

st.markdown('<div class="mm-flag-line"></div>', unsafe_allow_html=True)
nav_brand, nav_menu, nav_language = st.columns([2.15, 6.3, 1.55])
with nav_brand:
    st.markdown(
        f"""
        <div class="mm-brand">MATHMENTOR <span>AI</span>
            <small>🇺🇿 {escape(ui(lang, 'brand_country'))}</small>
        </div>
        """,
        unsafe_allow_html=True,
    )
with nav_menu:
    st.radio(
        "Navigation",
        NAV_PAGES,
        key="nav_page",
        horizontal=True,
        label_visibility="collapsed",
        format_func=lambda value: ui(lang, NAV_KEYS[value]),
    )
with nav_language:
    language_label = st.selectbox(
        "Til / Язык / Language",
        list(LANGUAGES.keys()),
        index=list(LANGUAGES.keys()).index(selected_language_label)
        if selected_language_label in LANGUAGES
        else 0,
        key="language_selector",
        label_visibility="collapsed",
    )
    st.session_state.lang = LANGUAGES[language_label]
    lang = st.session_state.lang
st.markdown('<div class="mm-nav-shell"></div>', unsafe_allow_html=True)

profile = st.session_state.profile


def render_home() -> None:
    st.markdown(
        f"""
        <section class="mm-hero">
            <span class="mm-scope-badge">{escape(ui(lang, 'scope_badge'))}</span>
            <h1 class="mm-hero-title">{escape(ui(lang, 'hero_first'))}<br>
                <span>{escape(ui(lang, 'hero_second'))}</span>
            </h1>
            <p class="mm-hero-copy">{escape(ui(lang, 'hero_body'))}</p>
        </section>
        """,
        unsafe_allow_html=True,
    )
    cta_primary, cta_secondary, cta_space = st.columns([2.25, 2.25, 5.5])
    with cta_primary:
        st.button(
            f"{ui(lang, 'start_analyzing')}  →",
            type="primary",
            use_container_width=True,
            on_click=go_to,
            args=("Analyze",),
        )
    with cta_secondary:
        st.button(
            f"{ui(lang, 'see_how')}  →",
            use_container_width=True,
            on_click=go_to,
            args=("About",),
        )

    divider("6rem")
    section_heading(ui(lang, "how_kicker"), ui(lang, "how_title"), "mastery" if lang == "en" else None)

    # Step 1
    text_col, visual_col = st.columns([5, 7], gap="large")
    with text_col:
        st.markdown(
            f"""
            <span class="mm-step-number">01</span>
            <h3 class="mm-card-title">{escape(ui(lang, 'step1_title'))}</h3>
            <p class="mm-card-copy" style="font-size:1.08rem">{escape(ui(lang, 'step1_body'))}</p>
            """,
            unsafe_allow_html=True,
        )
    with visual_col:
        st.markdown(
            f"""
            <div class="mm-card">
                <span class="mm-card-label">{escape(ui(lang, 'your_problem'))}</span>
                <p class="mm-problem-text">3x + 5 = 20</p>
                <div class="mm-meta-row">
                    <span class="mm-chip mm-chip-primary">Algebra</span>
                    <span class="mm-chip">7</span>
                    <span class="mm-chip">Toshkent shahri</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.write("")
    st.write("")
    visual_col, text_col = st.columns([7, 5], gap="large")
    with visual_col:
        st.markdown(
            f"""
            <div class="mm-card">
                <span class="mm-card-label">{escape(ui(lang, 'your_solution'))}</span>
                <div class="mm-math-line">1. 3*x + 5 = 20</div>
                <div class="mm-math-line">2. 3*x = 15</div>
                <div class="mm-math-line">3. x = 5</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with text_col:
        st.markdown(
            f"""
            <span class="mm-step-number">02</span>
            <h3 class="mm-card-title">{escape(ui(lang, 'step2_title'))}</h3>
            <p class="mm-card-copy" style="font-size:1.08rem">{escape(ui(lang, 'step2_body'))}</p>
            """,
            unsafe_allow_html=True,
        )

    st.write("")
    st.write("")
    text_col, visual_col = st.columns([5, 7], gap="large")
    with text_col:
        st.markdown(
            f"""
            <span class="mm-step-number">03</span>
            <h3 class="mm-card-title">{escape(ui(lang, 'step3_title'))}</h3>
            <p class="mm-card-copy" style="font-size:1.08rem">{escape(ui(lang, 'step3_body'))}</p>
            """,
            unsafe_allow_html=True,
        )
    with visual_col:
        st.markdown(
            f"""
            <div class="mm-card mm-card-success">
                <span class="mm-card-label">{escape(ui(lang, 'feedback_preview'))}</span>
                <p class="mm-card-copy"><span class="mm-chip mm-chip-success">✓</span>
                    <strong> Step 1–2:</strong> {escape(tr(lang, 'correct'))}</p>
                <div style="height:.85rem"></div>
                <p class="mm-card-copy"><span class="mm-chip mm-chip-error">!</span>
                    <strong> Step 3:</strong> {escape(LABEL_TEXT[lang]['incomplete_step'])}</p>
                <div class="mm-note" style="margin-top:1.25rem">x = 5</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    divider("6rem")
    section_heading(ui(lang, "how_kicker"), ui(lang, "pick_path"))
    paths = [
        ("Analyze", "path_analyze", "path_analyze_desc"),
        ("Mastery", "path_mastery", "path_mastery_desc"),
        ("About", "path_about", "path_about_desc"),
        ("Settings", "path_settings", "path_settings_desc"),
    ]
    cols = st.columns(4, gap="medium")
    for col, (page, title_key, desc_key) in zip(cols, paths):
        with col:
            st.markdown(
                f"""
                <div class="mm-card" style="min-height:250px">
                    <h3 class="mm-card-title">{escape(ui(lang, title_key))}</h3>
                    <p class="mm-card-copy">{escape(ui(lang, desc_key))}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.button(
                f"{ui(lang, 'go')}  →",
                key=f"home_{page}",
                use_container_width=True,
                on_click=go_to,
                args=(page,),
            )


def render_analyze() -> None:
    page_header(ui(lang, "analyze_title"), ui(lang, "analyze_subtitle"))
    profile_col, profile_action = st.columns([8, 2])
    with profile_col:
        st.markdown(profile_summary_html(lang, profile), unsafe_allow_html=True)
    with profile_action:
        st.button(
            ui(lang, "change_profile"),
            use_container_width=True,
            on_click=go_to,
            args=("Settings",),
        )

    available = filter_problems(problems, profile["stage"], int(profile["grade"]))
    if not available:
        st.warning("No bundled starter problem matches this profile yet.")
        st.button(ui(lang, "change_profile"), on_click=go_to, args=("Settings",))
        return

    st.write("")
    topics = sorted({problem["topic"] for problem in available})
    if st.session_state.get("analyze_topic") not in topics:
        st.session_state.analyze_topic = topics[0]

    selector_topic, selector_problem, selector_random = st.columns([2.2, 5.8, 2])
    with selector_topic:
        topic = st.selectbox(tr(lang, "choose_topic"), topics, key="analyze_topic")
    topic_problems = [problem for problem in available if problem["topic"] == topic]
    problem_ids = [problem["id"] for problem in topic_problems]
    if st.session_state.get("analyze_problem_id") not in problem_ids:
        st.session_state.analyze_problem_id = problem_ids[0]
    problem_lookup = {problem["id"]: problem for problem in topic_problems}
    with selector_problem:
        problem_id = st.selectbox(
            tr(lang, "choose_problem"),
            problem_ids,
            key="analyze_problem_id",
            format_func=lambda pid: f"{pid} — {localized(problem_lookup[pid], 'title', lang)}",
        )
    with selector_random:
        st.button(
            f"↻ {ui(lang, 'new_problem')}",
            use_container_width=True,
            on_click=pick_random_problem,
            args=(problem_ids,),
        )

    problem = problem_lookup[problem_id]
    st.markdown(
        f"""
        <div class="mm-card" style="margin-top:1.4rem">
            <span class="mm-card-label">{escape(ui(lang, 'your_problem'))}</span>
            <h3 class="mm-card-title">{escape(localized(problem, 'title', lang))}</h3>
            <p class="mm-problem-text">{escape(localized(problem, 'prompt', lang))}</p>
            <div class="mm-meta-row">
                <span class="mm-chip mm-chip-primary">{escape(problem['topic'])}</span>
                <span class="mm-chip">{escape(tr(lang, 'difficulty'))}: {'●' * int(problem['difficulty'])}</span>
                <span class="mm-chip">{escape(problem['id'])}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f'<span class="mm-card-label" style="margin-top:1.8rem">{escape(ui(lang, "one_step"))}</span>',
        unsafe_allow_html=True,
    )
    solution_key = f"solution_{problem_id}"
    steps_text = st.text_area(
        ui(lang, "one_step"),
        key=solution_key,
        height=220,
        placeholder="3*x+5=20\n3*x=15\nx=5",
        label_visibility="collapsed",
    )
    st.caption(ui(lang, "syntax_help"))
    analyze_button_col, spacer = st.columns([3, 7])
    with analyze_button_col:
        analyze_clicked = st.button(
            f"{ui(lang, 'analyze_cta')}  →",
            type="primary",
            use_container_width=True,
        )

    if analyze_clicked:
        student_steps = [line.strip() for line in steps_text.splitlines() if line.strip()]
        if not student_steps:
            st.warning(tr(lang, "need_steps"))
        else:
            style = choose_feedback_style(st.session_state)
            results = evaluate_steps(
                student_steps,
                problem["expected_steps"],
                lang=lang,
                style=style,
                hint=localized(problem, "hint", lang),
            )
            score = score_results(results, len(problem["expected_steps"]))
            errors = [result.diagnosis for result in results if not result.is_correct]
            attempt = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "student": profile["name"],
                "region": profile["region"],
                "stage": profile["stage"],
                "grade": int(profile["grade"]),
                "problem_id": problem["id"],
                "topic": problem["topic"],
                "score": score,
                "correct_steps": sum(result.is_correct for result in results),
                "total_steps": len(results),
                "errors": errors,
                "feedback_style": style,
            }
            st.session_state.attempts.append(attempt)
            st.session_state.last_style = style
            st.session_state.last_analysis = {
                "problem_id": problem["id"],
                "score": score,
                "results": results,
                "attempt_index": len(st.session_state.attempts) - 1,
            }

    analysis = st.session_state.get("last_analysis")
    if analysis and analysis.get("problem_id") == problem_id:
        divider("4rem")
        section_heading(ui(lang, "feedback_kicker"), ui(lang, "review_title"))
        results = analysis["results"]
        score = float(analysis["score"])
        score_col, stats_col = st.columns([3, 7], gap="large")
        with score_col:
            st.markdown(
                f"""
                <div class="mm-card mm-card-accent">
                    <div class="mm-score">{score:.1f}%</div>
                    <div class="mm-score-label">{escape(ui(lang, 'overall_score'))}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with stats_col:
            m1, m2, m3 = st.columns(3)
            m1.metric(tr(lang, "correct"), sum(result.is_correct for result in results))
            m2.metric(tr(lang, "incorrect"), sum(not result.is_correct for result in results))
            m3.metric("Style", st.session_state.last_style.title())

        for result in results:
            diagnosis = LABEL_TEXT.get(lang, LABEL_TEXT["en"]).get(result.diagnosis, result.diagnosis)
            card_class = "mm-card-success" if result.is_correct else "mm-card-error"
            chip_class = "mm-chip-success" if result.is_correct else "mm-chip-error"
            status_icon = "✓" if result.is_correct else "×"
            st.markdown(
                f"""
                <div class="mm-card {card_class}" style="margin-top:1rem">
                    <div style="display:flex;justify-content:space-between;gap:1rem;flex-wrap:wrap">
                        <div>
                            <span class="mm-card-label">{escape(tr(lang, 'step'))} {result.index}</span>
                            <p class="mm-math-line" style="font-size:1.12rem">{escape(result.student_step)}</p>
                        </div>
                        <div style="text-align:right">
                            <span class="mm-chip {chip_class}">{status_icon} {escape(diagnosis)}</span>
                            <div class="mm-card-copy" style="font-size:.78rem;margin-top:.65rem">
                                {escape(ui(lang, 'confidence'))}: {result.confidence * 100:.0f}%
                            </div>
                        </div>
                    </div>
                    <div class="mm-note" style="margin-top:1rem">{escape(result.feedback)}</div>
                    <div class="mm-meta-row">
                        <span>{escape(ui(lang, 'expected'))}</span>
                        <span class="mm-chip">{escape(result.expected_step or '—')}</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown(
            f'<p class="mm-card-copy" style="margin-top:1.5rem">{escape(ui(lang, "helpful_question"))}</p>',
            unsafe_allow_html=True,
        )
        helpful, not_helpful, feedback_space = st.columns([2, 2, 6])
        with helpful:
            if st.button(f"👍 {tr(lang, 'liked')}", use_container_width=True):
                update_feedback_bandit(st.session_state, st.session_state.last_style, 1.0)
                st.toast("Rahmat / Спасибо / Thank you")
        with not_helpful:
            if st.button(f"👎 {tr(lang, 'disliked')}", use_container_width=True):
                update_feedback_bandit(st.session_state, st.session_state.last_style, -1.0)
                st.toast("Feedback recorded")

        recommended = recommend_problem(available, problem_id, st.session_state.attempts)
        if recommended:
            st.markdown(
                f"""
                <div class="mm-card mm-card-accent" style="margin-top:2rem">
                    <span class="mm-card-label">{escape(tr(lang, 'recommended'))}</span>
                    <h3 class="mm-card-title">{escape(localized(recommended, 'title', lang))}</h3>
                    <p class="mm-card-copy">{escape(localized(recommended, 'prompt', lang))}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
            rec_col, rec_space = st.columns([3, 7])
            with rec_col:
                st.button(
                    f"{ui(lang, 'open_recommended')}  →",
                    use_container_width=True,
                    on_click=open_problem,
                    args=(recommended,),
                )

    divider("4rem")
    with st.expander(f"{ui(lang, 'problem_bank')} — {ui(lang, 'problem_bank_desc')}"):
        bank_df = problem_bank_dataframe(problems, lang)
        topic_filter = st.selectbox(
            tr(lang, "choose_topic"),
            [tr(lang, "all_topics")] + sorted(bank_df[tr(lang, "choose_topic")].unique().tolist()),
            key="bank_topic_filter",
        )
        if topic_filter != tr(lang, "all_topics"):
            bank_df = bank_df[bank_df[tr(lang, "choose_topic")] == topic_filter]
        st.dataframe(bank_df, use_container_width=True, hide_index=True)


def render_mastery() -> None:
    page_header(ui(lang, "mastery_title"), ui(lang, "mastery_subtitle"))
    attempts = st.session_state.attempts
    if attempts:
        df = pd.DataFrame(attempts)
        total_steps = int(df["total_steps"].sum())
        correct_steps = int(df["correct_steps"].sum())
        accuracy = 100.0 * correct_steps / max(1, total_steps)
        average_score = float(df["score"].mean())
        topics_practiced = int(df["topic"].nunique())
    else:
        df = pd.DataFrame()
        accuracy = 0.0
        average_score = 0.0
        topics_practiced = 0

    m1, m2, m3, m4 = st.columns(4)
    m1.metric(tr(lang, "attempts"), len(attempts))
    m2.metric(tr(lang, "accuracy"), f"{accuracy:.1f}%")
    m3.metric(ui(lang, "average_score"), f"{average_score:.1f}%")
    m4.metric(ui(lang, "topics_practiced"), topics_practiced)

    divider("4rem")
    section_heading(ui(lang, "mastery_title"), ui(lang, "topic_progress"))
    relevant = filter_problems(problems, profile["stage"], int(profile["grade"]))
    topics = sorted({problem["topic"] for problem in relevant} | {a["topic"] for a in attempts})
    if not topics:
        st.info(ui(lang, "no_topic_data"))
    else:
        for topic in topics:
            topic_attempts = [attempt for attempt in attempts if attempt["topic"] == topic]
            if topic_attempts:
                attempted_steps = sum(int(attempt["total_steps"]) for attempt in topic_attempts)
                correct_steps = sum(int(attempt["correct_steps"]) for attempt in topic_attempts)
                mastery = 100.0 * correct_steps / max(1, attempted_steps)
                average = sum(float(attempt["score"]) for attempt in topic_attempts) / len(topic_attempts)
            else:
                mastery = 0.0
                average = 0.0
            st.markdown(
                f"""
                <div class="mm-card" style="margin-bottom:.85rem">
                    <div style="display:flex;justify-content:space-between;gap:1rem;align-items:end">
                        <div>
                            <span class="mm-card-label">{len(topic_attempts)} {escape(tr(lang, 'attempts').lower())}</span>
                            <h3 class="mm-card-title">{escape(topic)}</h3>
                        </div>
                        <div style="text-align:right">
                            <div style="font-family:'Archivo Black',Impact,sans-serif;font-size:2rem;color:var(--mm-primary)">{mastery:.0f}%</div>
                            <div class="mm-card-copy" style="font-size:.75rem">{escape(ui(lang, 'average_score'))}: {average:.1f}%</div>
                        </div>
                    </div>
                    <div class="mm-progress-track" style="margin-top:1rem"><div class="mm-progress-fill" style="width:{max(0.0, min(100.0, mastery)):.1f}%"></div></div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    divider("4rem")
    left, right = st.columns([6, 4], gap="large")
    with left:
        section_heading(ui(lang, "mastery_title"), tr(lang, "weaknesses"))
        if not attempts:
            st.info(tr(lang, "no_attempts"))
        else:
            error_labels = [label for attempt in attempts for label in attempt.get("errors", [])]
            if not error_labels:
                st.success(tr(lang, "correct"))
            else:
                counts = pd.Series(error_labels, dtype="object").value_counts().rename_axis("error").reset_index(name="count")
                counts["error"] = counts["error"].map(
                    lambda label: LABEL_TEXT.get(lang, LABEL_TEXT["en"]).get(label, label)
                )
                st.bar_chart(counts.set_index("error"))
    with right:
        section_heading(ui(lang, "mastery_title"), ui(lang, "feedback_preferences"))
        q_values = st.session_state.feedback_q
        n_values = st.session_state.feedback_n
        preference_df = pd.DataFrame(
            [
                {"Style": style.title(), "Learned value": round(float(q_values.get(style, 0.0)), 3), "Ratings": int(n_values.get(style, 0))}
                for style in ["socratic", "concise", "worked"]
            ]
        )
        st.dataframe(preference_df, use_container_width=True, hide_index=True)

    divider("4rem")
    section_heading(ui(lang, "mastery_title"), ui(lang, "recent_attempts"))
    if attempts:
        display_df = pd.DataFrame(attempts).copy()
        display_df["errors"] = display_df["errors"].apply(
            lambda labels: ", ".join(LABEL_TEXT.get(lang, LABEL_TEXT["en"]).get(label, label) for label in labels) or "—"
        )
        st.dataframe(display_df, use_container_width=True, hide_index=True)
        csv_bytes = display_df.to_csv(index=False).encode("utf-8-sig")
        st.download_button(
            tr(lang, "download"),
            csv_bytes,
            "uzbekistan_math_mentor_attempts.csv",
            "text/csv",
        )
    else:
        st.info(tr(lang, "no_attempts"))
        cta_col, cta_space = st.columns([3, 7])
        with cta_col:
            st.button(
                f"{ui(lang, 'start_analyzing')}  →",
                type="primary",
                use_container_width=True,
                on_click=go_to,
                args=("Analyze",),
            )


def render_about() -> None:
    page_header(
        ui(lang, "about_title"),
        f"{ui(lang, 'about_pitch_first')} {ui(lang, 'about_pitch_second')}",
    )
    st.markdown(
        f"""
        <div style="max-width:850px">
            <p class="mm-hero-copy" style="margin-top:0">{escape(ui(lang, 'about_p1'))}</p>
            <p class="mm-hero-copy">{escape(ui(lang, 'about_p2'))}</p>
            <p class="mm-hero-copy">{escape(ui(lang, 'about_p3'))}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    divider("5rem")
    section_heading(ui(lang, "pipeline_kicker"), ui(lang, "pipeline_title"))
    pipeline = [
        ("01", "pipeline_profile"),
        ("02", "pipeline_symbolic"),
        ("03", "pipeline_ml"),
        ("04", "pipeline_dnn"),
        ("05", "pipeline_rl"),
        ("06", "pipeline_analytics"),
    ]
    for start in range(0, len(pipeline), 3):
        cols = st.columns(3, gap="medium")
        for col, (number, text_key) in zip(cols, pipeline[start : start + 3]):
            with col:
                st.markdown(
                    f"""
                    <div class="mm-card" style="min-height:205px">
                        <span class="mm-step-number" style="font-size:3.4rem">{number}</span>
                        <h3 class="mm-card-title" style="font-size:1.45rem">{escape(ui(lang, text_key))}</h3>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        st.write("")

    divider("5rem")
    section_heading(ui(lang, "about_title"), ui(lang, "responsible_title"))
    responsible_bullets = {
        "en": [
            "Use a nickname; do not enter addresses, phone numbers, health records, or other sensitive student data.",
            "Treat error labels as learning aids, not permanent judgments about ability.",
            "Teachers should review translations, expected steps, and high-stakes conclusions.",
            "Only original or properly licensed problems should be added to the bank.",
            "A production version needs authentication, consent, encrypted storage, moderation, audit logs, and curriculum review.",
        ],
        "uz": [
            "Taxallusdan foydalaning; manzil, telefon, sog‘liq ma’lumoti yoki boshqa maxfiy o‘quvchi ma’lumotlarini kiritmang.",
            "Xato yorliqlarini qobiliyat haqidagi doimiy hukm emas, o‘quv yordami sifatida qabul qiling.",
            "O‘qituvchilar tarjimalar, kutilgan qadamlar va muhim xulosalarni tekshirishi kerak.",
            "Bankka faqat original yoki tegishli litsenziyali masalalarni qo‘shing.",
            "Ishlab chiqarish versiyasi autentifikatsiya, rozilik, shifrlangan saqlash, moderatsiya, audit va o‘quv dasturi tekshiruvini talab qiladi.",
        ],
        "ru": [
            "Используйте псевдоним; не вводите адреса, телефоны, медицинские или другие чувствительные данные ученика.",
            "Воспринимайте метки ошибок как учебную помощь, а не как постоянное суждение о способностях.",
            "Учителя должны проверять переводы, ожидаемые шаги и выводы с серьёзными последствиями.",
            "Добавляйте в банк только оригинальные или надлежащим образом лицензированные задачи.",
            "Промышленная версия требует аутентификации, согласия, шифрования, модерации, аудита и проверки по учебной программе.",
        ],
    }
    bullet_html = "".join(f"<li>{escape(item)}</li>" for item in responsible_bullets[lang])
    st.markdown(
        f"""
        <div class="mm-card mm-card-accent">
            <ul class="mm-card-copy" style="margin:0;padding-left:1.2rem;line-height:1.9">{bullet_html}</ul>
        </div>
        <div class="mm-notice" style="margin-top:1rem">{escape(ui(lang, 'independent_notice'))}</div>
        """,
        unsafe_allow_html=True,
    )

    divider("5rem")
    left, right = st.columns([6, 4], gap="large")
    with left:
        section_heading(ui(lang, "about_title"), ui(lang, "feedback_title"))
        st.markdown(f'<p class="mm-card-copy">{escape(ui(lang, "feedback_desc"))}</p>', unsafe_allow_html=True)
        with st.form("prototype_feedback", clear_on_submit=True):
            feedback_name = st.text_input(ui(lang, "feedback_name"))
            feedback_message = st.text_area(ui(lang, "feedback_message"), height=150)
            submitted = st.form_submit_button(ui(lang, "feedback_submit"), type="primary")
            if submitted:
                if feedback_message.strip():
                    st.session_state.feedback_entries.append(
                        {
                            "timestamp": datetime.now(timezone.utc).isoformat(),
                            "name": feedback_name.strip() or "Anonymous",
                            "message": feedback_message.strip(),
                        }
                    )
                    st.success("Rahmat / Спасибо / Thank you")
                else:
                    st.warning(ui(lang, "feedback_message"))
    with right:
        st.markdown(
            f"""
            <div class="mm-card" style="margin-top:3.1rem">
                <span class="mm-card-label">Prototype scope</span>
                <h3 class="mm-card-title">🇺🇿 Uzbekistan only</h3>
                <p class="mm-card-copy">22 bundled starter problems<br>Grades 1–11<br>Academic lyceum<br>University<br>UZ / RU / EN</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.session_state.feedback_entries:
            st.caption(f"Session feedback entries: {len(st.session_state.feedback_entries)}")


def render_settings() -> None:
    page_header(ui(lang, "settings_title"), ui(lang, "settings_subtitle"))

    section_heading(ui(lang, "settings_title"), ui(lang, "display"))
    display_text = ui(lang, "dark_mode") if st.session_state.dark_mode else ui(lang, "light_mode")
    display_desc = ui(lang, "appearance_dark_desc") if st.session_state.dark_mode else ui(lang, "appearance_light_desc")
    display_info, display_toggle = st.columns([8, 2])
    with display_info:
        st.markdown(
            f"""
            <div class="mm-card mm-card-accent">
                <span class="mm-card-label">{escape(ui(lang, 'display_desc'))}</span>
                <h3 class="mm-card-title">{'☾' if st.session_state.dark_mode else '☀'} {escape(display_text)}</h3>
                <p class="mm-card-copy">{escape(display_desc)}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with display_toggle:
        st.toggle(ui(lang, "dark_mode"), key="dark_mode")

    divider("4rem")
    section_heading(ui(lang, "settings_title"), ui(lang, "learner_profile"))
    st.markdown(f'<p class="mm-card-copy">{escape(ui(lang, "learner_profile_desc"))}</p>', unsafe_allow_html=True)

    # Initialize editable widget state from the saved profile once.
    widget_defaults = {
        "settings_name": profile["name"],
        "settings_region": profile["region"],
        "settings_stage": profile["stage"],
        "settings_grade": int(profile["grade"]),
        "settings_level": profile["level"],
    }
    for key, value in widget_defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

    c1, c2 = st.columns(2, gap="large")
    with c1:
        st.text_input(tr(lang, "country"), value=tr(lang, "country_value"), disabled=True)
        st.text_input(tr(lang, "name"), key="settings_name")
        st.selectbox(tr(lang, "region"), REGIONS, key="settings_region")
    with c2:
        selected_stage = st.selectbox(
            tr(lang, "stage"),
            STAGE_KEYS,
            key="settings_stage",
            format_func=lambda value: stage_label(lang, value),
        )
        valid_grades = grade_options(selected_stage)
        if st.session_state.get("settings_grade") not in valid_grades:
            st.session_state.settings_grade = valid_grades[0]
        st.selectbox(tr(lang, "grade"), valid_grades, key="settings_grade")
        st.selectbox(
            tr(lang, "level"),
            LEVEL_KEYS,
            key="settings_level",
            format_func=lambda value: level_label(lang, value),
        )

    save_col, save_space = st.columns([3, 7])
    with save_col:
        if st.button(ui(lang, "save_settings"), type="primary", use_container_width=True):
            st.session_state.profile = {
                "name": st.session_state.settings_name.strip() or "O‘quvchi",
                "country": "O‘zbekiston",
                "region": st.session_state.settings_region,
                "stage": st.session_state.settings_stage,
                "grade": int(st.session_state.settings_grade),
                "level": st.session_state.settings_level,
            }
            st.session_state.last_analysis = None
            st.success(tr(lang, "profile_saved"))

    divider("4rem")
    section_heading(ui(lang, "settings_title"), ui(lang, "data_controls"))
    st.markdown(f'<p class="mm-card-copy">{escape(ui(lang, "data_controls_desc"))}</p>', unsafe_allow_html=True)
    data_left, data_right = st.columns([5, 5], gap="large")
    with data_left:
        profile_json = json.dumps(st.session_state.profile, ensure_ascii=False, indent=2).encode("utf-8")
        st.download_button(
            "Download learner profile JSON",
            profile_json,
            "uzbekistan_math_mentor_profile.json",
            "application/json",
            use_container_width=True,
        )
    with data_right:
        st.button(
            ui(lang, "clear_attempts"),
            use_container_width=True,
            on_click=clear_learning_session,
        )
    if st.session_state.analysis_notice == "cleared":
        st.success(ui(lang, "cleared"))
        st.session_state.analysis_notice = ""

    st.markdown(
        f'<div class="mm-notice" style="margin-top:2rem">{escape(ui(lang, "independent_notice"))}</div>',
        unsafe_allow_html=True,
    )


page = st.session_state.nav_page
if page == "Home":
    render_home()
elif page == "Analyze":
    render_analyze()
elif page == "Mastery":
    render_mastery()
elif page == "About":
    render_about()
else:
    render_settings()

render_footer(ui(lang, "footer_line"), ui(lang, "no_paid_api"))
