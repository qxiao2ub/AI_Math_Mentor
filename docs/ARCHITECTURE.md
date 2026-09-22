# Architecture

```text
Streamlit UI layer
(Home / Analyze / Mastery / About / Settings)
        |
        +---- ui_theme.py: ported visual system
        +---- ui_copy.py: UZ/RU/EN page copy
        |
        v
Uzbekistan learner profile
(country fixed, region, stage, grade/course, level)
        |
        v
Stage/grade/topic filter ----> Local multilingual problem bank
        |                                  |
        v                                  v
Student writes one mathematical step per line
        |
        v
SymPy parser and equivalence checker (primary correctness layer)
        |
        +---- correct --> score and mastery update
        |
        +---- incorrect --> rule signals + TF-IDF/LogReg + 2-layer MLP
                                  |
                                  v
                           Error classification
                                  |
                                  v
        Epsilon-greedy feedback-style bandit
          (Socratic / concise / worked example)
                                  |
                                  v
           Session analytics, export, and recommendation
```

## Why hybrid checking?

A generative model can produce a fluent explanation while still making a mathematical mistake. This prototype therefore uses deterministic symbolic mathematics for the primary correctness judgment. Machine-learning models are used only for the softer task of estimating the likely error category after a step is determined to be non-equivalent.

## UI architecture

The original React/Tailwind design was translated into native Streamlit rather than embedded as a second application. `ui_theme.py` carries the design tokens and CSS, while `app.py` owns all widget state and AI-engine calls. This avoids a Node build step and keeps GitHub-to-Streamlit deployment direct.

## Uzbekistan-only controls

- Country is read-only and fixed to Uzbekistan.
- Regions are limited to Uzbekistan's Republic of Karakalpakstan, regions, and Tashkent city.
- Education paths are limited to school, academic lyceum, and university.
- The bundled local problem bank is the sole content source in the demonstration.
- No general web search is performed by the application.

## State and storage

The prototype uses Streamlit session state for:

- Learner profile
- Current navigation destination
- Attempts
- Last analysis result
- Reinforcement-learning feedback values
- Prototype feedback messages
- Appearance mode

No persistent external database is used. Closing or expiring the browser session removes these records.

## Production extension points

- Curriculum-standard identifiers for each problem
- Teacher-reviewed Uzbek and Russian mathematical terminology
- Secure student and teacher authentication
- PostgreSQL or another encrypted managed database
- Institution tenancy and role-based access
- Consent and guardian workflows for minors
- Moderation and abuse prevention
- Versioned model registry and evaluation suite
- Teacher dashboards and assignment management
- Formal curriculum mapping and content governance
- Optional LLM explanation layer guarded by symbolic verification
