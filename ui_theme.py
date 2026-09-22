from __future__ import annotations

from html import escape

import streamlit as st


def inject_ui_css(dark: bool) -> None:
    if dark:
        background = "#080808"
        foreground = "#F8F8F8"
        surface = "#121212"
        surface_2 = "#181818"
        muted = "#A4A4A4"
        border = "#2B2B2B"
        input_bg = "#0D0D0D"
        shadow = "rgba(24, 84, 255, .20)"
    else:
        background = "#FAFAFB"
        foreground = "#111318"
        surface = "#FFFFFF"
        surface_2 = "#EEF1F6"
        muted = "#596273"
        border = "#D8DCE5"
        input_bg = "#FFFFFF"
        shadow = "rgba(24, 84, 255, .14)"

    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Archivo+Black&family=Inter:wght@400;500;600;700&display=swap');

        :root {{
            --mm-bg: {background};
            --mm-fg: {foreground};
            --mm-surface: {surface};
            --mm-surface-2: {surface_2};
            --mm-muted: {muted};
            --mm-border: {border};
            --mm-input: {input_bg};
            --mm-primary: #1854FF;
            --mm-primary-soft: rgba(24, 84, 255, .14);
            --mm-green: #1EB53A;
            --mm-red: #E04455;
            --mm-uz-blue: #0099B5;
            --mm-shadow: {shadow};
        }}

        html, body, [class*="css"] {{
            font-family: 'Inter', 'Segoe UI', sans-serif;
        }}

        .stApp {{
            background: var(--mm-bg);
            color: var(--mm-fg);
        }}

        [data-testid="stHeader"] {{
            background: transparent;
            height: 0;
        }}

        [data-testid="stToolbar"], #MainMenu, footer, [data-testid="stDecoration"] {{
            display: none !important;
        }}

        [data-testid="stSidebar"] {{
            display: none !important;
        }}

        .block-container {{
            max-width: 1280px;
            padding-top: 1.15rem;
            padding-bottom: 2.5rem;
        }}

        h1, h2, h3, h4, h5, h6,
        .mm-display, .mm-brand, .mm-step-number {{
            font-family: 'Archivo Black', Impact, sans-serif !important;
            letter-spacing: -0.045em;
        }}

        p, li, label, span {{
            color: inherit;
        }}

        a {{ color: var(--mm-primary); }}
        ::selection {{ background: var(--mm-primary); color: #FFFFFF; }}

        .mm-flag-line {{
            height: 4px;
            margin: -1.15rem calc(50% - 50vw) 1.05rem calc(50% - 50vw);
            background: linear-gradient(90deg,
                var(--mm-uz-blue) 0 31%, #FFFFFF 31% 33%,
                #CE1126 33% 34%, #FFFFFF 34% 66%,
                #CE1126 66% 67%, var(--mm-green) 67% 100%);
        }}

        .mm-brand {{
            font-size: clamp(1.05rem, 1.7vw, 1.45rem);
            line-height: .95;
            white-space: nowrap;
            color: var(--mm-fg);
        }}
        .mm-brand span {{ color: var(--mm-primary); }}
        .mm-brand small {{
            display: block;
            margin-top: .35rem;
            font-family: 'Inter', sans-serif;
            font-size: .58rem;
            letter-spacing: .18em;
            color: var(--mm-muted);
        }}

        .mm-nav-shell {{
            border-bottom: 1px solid var(--mm-border);
            margin-bottom: 2.25rem;
            padding-bottom: .85rem;
        }}

        div[data-testid="stRadio"] > div[role="radiogroup"] {{
            gap: .4rem;
            flex-wrap: wrap;
            justify-content: center;
        }}
        div[data-testid="stRadio"] > div[role="radiogroup"] label {{
            background: transparent;
            border: 1px solid transparent;
            padding: .52rem .65rem;
            min-height: auto;
            transition: 160ms ease;
        }}
        div[data-testid="stRadio"] > div[role="radiogroup"] label:hover {{
            border-color: var(--mm-border);
            background: var(--mm-surface);
        }}
        div[data-testid="stRadio"] > div[role="radiogroup"] label p {{
            color: var(--mm-muted);
            font-size: .75rem;
            font-weight: 700;
            letter-spacing: .10em;
            text-transform: uppercase;
        }}
        div[data-testid="stRadio"] > div[role="radiogroup"] label:has(input:checked) {{
            border-color: var(--mm-primary);
            background: var(--mm-primary-soft);
        }}
        div[data-testid="stRadio"] > div[role="radiogroup"] label:has(input:checked) p {{
            color: var(--mm-primary);
        }}
        div[data-testid="stRadio"] input {{ display: none; }}

        .mm-hero {{
            padding: clamp(3.6rem, 10vw, 8rem) 0 clamp(4.5rem, 11vw, 8.5rem);
        }}
        .mm-scope-badge {{
            display: inline-flex;
            align-items: center;
            gap: .55rem;
            padding: .52rem .7rem;
            margin-bottom: 1.7rem;
            border: 1px solid var(--mm-border);
            background: var(--mm-surface);
            color: var(--mm-muted);
            font-size: .68rem;
            font-weight: 700;
            letter-spacing: .14em;
            text-transform: uppercase;
        }}
        .mm-scope-badge::before {{
            content: '';
            width: .55rem;
            height: .55rem;
            background: var(--mm-green);
            border-radius: 50%;
            box-shadow: 0 0 0 4px rgba(30, 181, 58, .12);
        }}
        .mm-hero-title {{
            margin: 0;
            max-width: 1120px;
            color: var(--mm-fg);
            font-family: 'Archivo Black', Impact, sans-serif;
            font-size: clamp(3.7rem, 9.2vw, 8.7rem);
            line-height: .86;
            letter-spacing: -.067em;
        }}
        .mm-hero-title span {{ color: var(--mm-primary); }}
        .mm-hero-copy {{
            max-width: 760px;
            margin: 2.7rem 0 2rem;
            color: var(--mm-muted);
            font-size: clamp(1.05rem, 2vw, 1.48rem);
            line-height: 1.55;
        }}

        .mm-page-header {{
            padding: clamp(2.5rem, 6vw, 5rem) 0 clamp(2.5rem, 6vw, 4.5rem);
        }}
        .mm-page-title {{
            margin: 0 0 1.65rem;
            color: var(--mm-fg);
            font-family: 'Archivo Black', Impact, sans-serif;
            font-size: clamp(3.6rem, 10vw, 9rem);
            line-height: .82;
            letter-spacing: -.065em;
        }}
        .mm-page-subtitle {{
            max-width: 760px;
            color: var(--mm-muted);
            font-size: clamp(1.03rem, 2vw, 1.32rem);
            line-height: 1.6;
        }}

        .mm-section {{
            border-top: 1px solid var(--mm-border);
            padding: clamp(3.7rem, 8vw, 7rem) 0;
        }}
        .mm-kicker {{
            display: block;
            margin-bottom: .75rem;
            color: var(--mm-muted);
            font-size: .68rem;
            font-weight: 700;
            letter-spacing: .16em;
            text-transform: uppercase;
        }}
        .mm-section-title {{
            margin: 0 0 2.4rem;
            color: var(--mm-fg);
            font-family: 'Archivo Black', Impact, sans-serif;
            font-size: clamp(2.2rem, 5.3vw, 4.8rem);
            line-height: .92;
            letter-spacing: -.05em;
        }}
        .mm-section-title span {{ color: var(--mm-primary); }}

        .mm-card {{
            height: 100%;
            border: 1px solid var(--mm-border);
            background: var(--mm-surface);
            padding: clamp(1.25rem, 3vw, 2rem);
            box-shadow: none;
        }}
        .mm-card-accent {{
            border-left: 4px solid var(--mm-primary);
        }}
        .mm-card-error {{ border-left: 4px solid var(--mm-red); }}
        .mm-card-success {{ border-left: 4px solid var(--mm-green); }}
        .mm-card:hover {{
            border-color: var(--mm-primary);
            box-shadow: 0 0 30px var(--mm-shadow);
            transition: 180ms ease;
        }}
        .mm-card-label {{
            display: block;
            margin-bottom: .8rem;
            color: var(--mm-muted);
            font-size: .66rem;
            font-weight: 700;
            letter-spacing: .15em;
            text-transform: uppercase;
        }}
        .mm-card-title {{
            margin: 0 0 .75rem;
            color: var(--mm-fg);
            font-family: 'Archivo Black', Impact, sans-serif;
            font-size: clamp(1.35rem, 2.5vw, 2rem);
            line-height: 1;
            letter-spacing: -.035em;
        }}
        .mm-card-copy {{
            margin: 0;
            color: var(--mm-muted);
            font-size: .98rem;
            line-height: 1.62;
        }}
        .mm-card-copy strong {{ color: var(--mm-fg); }}

        .mm-step-number {{
            display: block;
            margin-bottom: 1rem;
            color: var(--mm-primary);
            font-size: clamp(3.6rem, 7vw, 6.5rem);
            line-height: .8;
        }}

        .mm-problem-text {{
            color: var(--mm-fg);
            font-size: clamp(1.25rem, 2.5vw, 2rem);
            line-height: 1.4;
        }}
        .mm-math-line {{
            padding: .6rem 0;
            color: var(--mm-fg);
            font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
            font-size: 1rem;
        }}
        .mm-meta-row {{
            display: flex;
            flex-wrap: wrap;
            gap: .65rem 1.1rem;
            margin-top: 1rem;
            color: var(--mm-muted);
            font-size: .76rem;
            letter-spacing: .07em;
            text-transform: uppercase;
        }}
        .mm-chip {{
            display: inline-block;
            border: 1px solid var(--mm-border);
            background: var(--mm-surface-2);
            padding: .35rem .52rem;
            color: var(--mm-muted);
            font-size: .68rem;
            letter-spacing: .08em;
            text-transform: uppercase;
        }}
        .mm-chip-primary {{
            border-color: var(--mm-primary);
            background: var(--mm-primary-soft);
            color: var(--mm-primary);
        }}
        .mm-chip-success {{
            border-color: rgba(30, 181, 58, .6);
            background: rgba(30, 181, 58, .12);
            color: var(--mm-green);
        }}
        .mm-chip-error {{
            border-color: rgba(224, 68, 85, .6);
            background: rgba(224, 68, 85, .12);
            color: var(--mm-red);
        }}

        .mm-score {{
            font-family: 'Archivo Black', Impact, sans-serif;
            color: var(--mm-primary);
            font-size: clamp(3.3rem, 8vw, 7rem);
            line-height: .85;
            letter-spacing: -.06em;
        }}
        .mm-score-label {{
            margin-top: .8rem;
            color: var(--mm-muted);
            font-size: .7rem;
            font-weight: 700;
            letter-spacing: .15em;
            text-transform: uppercase;
        }}

        .mm-progress-track {{
            width: 100%;
            height: .52rem;
            background: var(--mm-surface-2);
            border: 1px solid var(--mm-border);
            overflow: hidden;
        }}
        .mm-progress-fill {{
            height: 100%;
            background: var(--mm-primary);
        }}

        .mm-note {{
            border-left: 3px solid var(--mm-primary);
            padding: .9rem 1rem;
            background: var(--mm-primary-soft);
            color: var(--mm-muted);
            line-height: 1.55;
        }}
        .mm-notice {{
            border: 1px solid var(--mm-border);
            background: var(--mm-surface);
            padding: 1rem 1.15rem;
            color: var(--mm-muted);
            font-size: .88rem;
            line-height: 1.55;
        }}

        .mm-footer {{
            margin-top: 5rem;
            padding-top: 3.5rem;
            border-top: 1px solid var(--mm-border);
            overflow: hidden;
        }}
        .mm-footer-name {{
            margin: 0;
            text-align: center;
            white-space: nowrap;
            color: var(--mm-fg);
            font-family: 'Archivo Black', Impact, sans-serif;
            font-size: clamp(2.8rem, 10vw, 8.2rem);
            line-height: .82;
            letter-spacing: -.065em;
        }}
        .mm-footer-name span {{ color: var(--mm-primary); }}
        .mm-footer-bottom {{
            display: flex;
            justify-content: space-between;
            gap: 1rem;
            flex-wrap: wrap;
            margin-top: 3rem;
            padding: 1.4rem 0 .5rem;
            border-top: 1px solid var(--mm-border);
            color: var(--mm-muted);
            font-size: .8rem;
        }}

        div[data-testid="stButton"] > button,
        div[data-testid="stDownloadButton"] > button {{
            min-height: 3.15rem;
            border-radius: 0 !important;
            border: 1px solid var(--mm-border);
            background: var(--mm-surface);
            color: var(--mm-fg);
            font-size: .75rem;
            font-weight: 700;
            letter-spacing: .09em;
            text-transform: uppercase;
            transition: 160ms ease;
        }}
        div[data-testid="stButton"] > button:hover,
        div[data-testid="stDownloadButton"] > button:hover {{
            border-color: var(--mm-primary);
            color: var(--mm-primary);
            box-shadow: 0 0 24px var(--mm-shadow);
        }}
        div[data-testid="stButton"] > button[kind="primary"] {{
            border-color: var(--mm-primary);
            background: var(--mm-primary);
            color: #FFFFFF;
        }}
        div[data-testid="stButton"] > button[kind="primary"]:hover {{
            background: #0C46E6;
            color: #FFFFFF;
        }}

        div[data-baseweb="select"] > div,
        div[data-baseweb="input"] > div,
        div[data-baseweb="textarea"] > div,
        textarea, input {{
            border-radius: 0 !important;
        }}
        div[data-baseweb="select"] > div,
        div[data-baseweb="input"] > div,
        div[data-baseweb="textarea"] > div {{
            border-color: var(--mm-border) !important;
            background: var(--mm-input) !important;
            color: var(--mm-fg) !important;
        }}
        textarea, input {{
            background: var(--mm-input) !important;
            color: var(--mm-fg) !important;
            caret-color: var(--mm-primary) !important;
        }}
        textarea:focus, input:focus,
        div[data-baseweb="select"] > div:focus-within {{
            border-color: var(--mm-primary) !important;
            box-shadow: 0 0 0 1px var(--mm-primary) !important;
        }}
        [data-baseweb="popover"] ul {{
            background: var(--mm-surface) !important;
            color: var(--mm-fg) !important;
        }}

        div[data-testid="stMetric"] {{
            min-height: 8rem;
            border: 1px solid var(--mm-border);
            border-radius: 0;
            background: var(--mm-surface);
            padding: 1.15rem;
        }}
        div[data-testid="stMetric"] label {{
            color: var(--mm-muted) !important;
            font-size: .67rem !important;
            font-weight: 700 !important;
            letter-spacing: .10em !important;
            text-transform: uppercase;
        }}
        div[data-testid="stMetric"] [data-testid="stMetricValue"] {{
            color: var(--mm-fg);
            font-family: 'Archivo Black', Impact, sans-serif;
            font-size: 2rem;
        }}

        div[data-testid="stDataFrame"],
        div[data-testid="stTable"] {{
            border: 1px solid var(--mm-border);
            background: var(--mm-surface);
        }}

        div[data-testid="stAlert"] {{
            border-radius: 0;
            border: 1px solid var(--mm-border);
        }}
        div[data-testid="stExpander"] {{
            border-radius: 0 !important;
            border: 1px solid var(--mm-border) !important;
            background: var(--mm-surface) !important;
        }}
        button[data-baseweb="tab"] {{
            color: var(--mm-muted);
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: .08em;
        }}

        .stCaption, small {{ color: var(--mm-muted) !important; }}
        hr {{ border-color: var(--mm-border) !important; }}

        @media (max-width: 800px) {{
            .block-container {{ padding-left: 1rem; padding-right: 1rem; }}
            .mm-nav-shell {{ margin-bottom: 1rem; }}
            .mm-hero {{ padding-top: 3rem; }}
            .mm-footer-bottom {{ flex-direction: column; }}
            div[data-testid="stRadio"] > div[role="radiogroup"] {{ justify-content: flex-start; }}
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def page_header(title: str, subtitle: str) -> None:
    st.markdown(
        f"""
        <header class="mm-page-header">
            <h1 class="mm-page-title">{escape(title)}</h1>
            <p class="mm-page-subtitle">{escape(subtitle)}</p>
        </header>
        """,
        unsafe_allow_html=True,
    )


def section_heading(kicker: str, title: str, accent: str | None = None) -> None:
    rendered_title = escape(title)
    if accent and accent in title:
        before, after = title.split(accent, 1)
        rendered_title = f"{escape(before)}<span>{escape(accent)}</span>{escape(after)}"
    st.markdown(
        f"""
        <div>
            <span class="mm-kicker">{escape(kicker)}</span>
            <h2 class="mm-section-title">{rendered_title}</h2>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_footer(line: str, api_note: str) -> None:
    st.markdown(
        f"""
        <footer class="mm-footer">
            <h2 class="mm-footer-name">MATHMENTOR <span>AI</span></h2>
            <div class="mm-footer-bottom">
                <span>© 2026 Uzbekistan AI Math Mentor</span>
                <span>{escape(line)}</span>
                <span>{escape(api_note)}</span>
            </div>
        </footer>
        """,
        unsafe_allow_html=True,
    )
