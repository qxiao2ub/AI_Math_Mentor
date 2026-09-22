# 🇺🇿 Uzbekistan AI Math Mentor

A GitHub- and Streamlit-ready AI mathematics mentor for learners in Uzbekistan. The app checks a student's solution **one mathematical step at a time**, diagnoses likely error patterns, adapts its explanation style from learner feedback, tracks mastery, and recommends the next practice problem.

The supplied React/Tailwind UI has been integrated into the Streamlit product as a native Streamlit design system. The repository now reproduces its core visual language—large display typography, top navigation, square high-contrast cards, cobalt accent color, dark/light display modes, Analyze workspace, Mastery view, About page, Settings page, and oversized footer—without requiring Node.js or a separate front-end deployment.

> **Independent prototype:** this is not an official product or approved assessment system of any Uzbekistan government authority.

## Uzbekistan-only scope

- Country is fixed to **Uzbekistan**.
- Student profiles use Uzbekistan's regions.
- Supported pathways are School Grades 1–11, Academic Lyceum, and University.
- The interface and problem statements support Uzbek, Russian, and English.
- The local starter bank includes Uzbekistan and UZS contexts.
- The app does not perform general web search.
- No OpenAI key or paid API is required.

## Main pages

### Home

A UI-driven landing page with the original design's oversized hero, three-step product explanation, and direct paths to Analyze, Mastery, About, and Settings.

### Analyze

- Filters problems by the saved Uzbekistan learner profile.
- Lets the learner choose a topic and problem.
- Accepts one mathematical step per line.
- Uses SymPy as the primary correctness layer.
- Classifies likely errors with rules, logistic regression, and a two-hidden-layer MLP.
- Shows a visual feedback card for every submitted step.
- Records accuracy, score, error labels, and feedback style.
- Recommends a next problem.
- Includes a browsable local problem bank.

### Mastery

- Attempt count
- Step accuracy
- Average score
- Topics practiced
- Topic-level progress bars
- Recurring-error chart
- Learned feedback-style preferences
- Attempt history and CSV export

### About

Explains the hybrid symbolic/ML architecture, Uzbekistan-only scope, responsible-AI limits, and a session-only prototype feedback form.

### Settings

- Dark/light display mode
- Fixed country: Uzbekistan
- Region
- Education stage
- Grade/course
- Current mathematics level
- Learner-profile JSON export
- Session-data reset

## AI pipeline

```text
Uzbekistan learner profile
        |
        v
Stage/grade/topic filter ----> Local multilingual problem bank
        |                                  |
        v                                  v
Student writes one mathematical step per line
        |
        v
SymPy parser and equivalence checker
        |
        +---- correct --> score/mastery update
        |
        +---- incorrect --> rule signals + TF-IDF/LogReg + 2-layer MLP
                                  |
                                  v
                           Error diagnosis
                                  |
                                  v
        Epsilon-greedy feedback-style bandit
          (Socratic / concise / worked example)
                                  |
                                  v
               Session analytics and recommendation
```

## Repository structure

```text
uzbekistan-ai-math-mentor/
├── app.py                         # Streamlit application and page workflows
├── ai_engine.py                   # Symbolic, ML, MLP, scoring, and bandit logic
├── localization.py                # Core Uzbek/Russian/English labels
├── ui_copy.py                     # New UI page copy in three languages
├── ui_theme.py                    # Ported React/Tailwind visual system for Streamlit
├── problem_bank.py                # Local bank loading and filtering
├── requirements.txt
├── requirements-dev.txt
├── README.md
├── LICENSE
├── .streamlit/
│   └── config.toml
├── assets/
│   ├── favicon.ico
│   └── placeholder.svg
├── data/
│   ├── problem_bank.json
│   └── error_examples.csv
├── docs/
│   ├── ARCHITECTURE.md
│   └── UI_INTEGRATION.md
├── notebooks/
│   └── AI_Math_Mentor_Uzbekistan_Colab.ipynb
└── tests/
    ├── test_engine.py
    └── test_app_smoke.py
```

## Run locally

Python 3.11–3.13 is recommended.

### Windows PowerShell

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
streamlit run app.py
```

### macOS or Linux

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
streamlit run app.py
```

Open the URL shown by Streamlit, normally `http://localhost:8501`.

## Deploy through GitHub to Streamlit Community Cloud

1. Extract the downloadable ZIP.
2. Open the extracted `uzbekistan-ai-math-mentor` folder.
3. Create a new GitHub repository.
4. Upload **the contents inside that folder** to the root of the GitHub repository.
5. Confirm that `app.py`, `requirements.txt`, `.streamlit`, `data`, and the other folders are visible at the repository root.
6. In Streamlit Community Cloud, select **Create app**.
7. Choose the GitHub repository and branch.
8. Set the main file path to:

```text
app.py
```

9. Deploy. No secrets are required.

The uploaded React source does **not** need to be built or deployed separately. Its UI has already been ported into the Python/Streamlit repository.

## Solution input syntax

Enter one mathematical step per line:

```text
3*x+5=20
3*x=15
x=5
```

Other supported examples include:

```text
3/4+1/8=7/8
sqrt(100)=10
sin(pi/6)=1/2
x^2-5*x+6=0
```

Use `*` for multiplication and `^` for powers. The app normalizes `^` internally for SymPy.

## Add more Uzbekistan problems

Edit `data/problem_bank.json`. Each record needs:

- `id`
- `stage`: `school`, `lyceum`, or `university`
- `grade_min` and `grade_max`
- `topic`
- `difficulty`
- localized `title`, `prompt`, and `hint`
- `expected_steps`
- `answer`

Use original or properly licensed content. A mathematics teacher should validate each expected solution and translation before classroom use.

## Testing

Install development dependencies:

```bash
pip install -r requirements-dev.txt
```

Run all tests:

```bash
python -m pytest -q
```

The test suite covers symbolic equivalence, scoring, Uzbekistan-only problem-bank scope, and smoke tests for all five Streamlit navigation pages.

## Important prototype limits

- The bundled supervised-learning examples are intentionally small and demonstrate architecture rather than production model quality.
- Attempts are stored only in the current Streamlit session and disappear when the session ends.
- The prototype does not include authentication or a persistent student database.
- Symbolic equivalence cannot interpret every informal or natural-language reasoning step.
- Error labels are learning aids, not permanent judgments of ability.
- Teachers should review translations, expected steps, and high-stakes conclusions.
- A production deployment should add consent workflows, role-based access, encrypted storage, moderation, audit logs, model evaluation, and formal curriculum mapping.

## License

MIT. Newly added problem content may require separate rights or licensing review.
