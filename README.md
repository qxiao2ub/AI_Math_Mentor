# AI Math Mentor App

**Author:** Anchit Nayak  
**Advisor:** Dr. Qingyang Xiao

AI Math Mentor is a Streamlit-ready educational prototype derived from the accompanying Google Colab/Jupyter notebook. It checks mathematical solution steps, diagnoses likely mistakes, tracks learning history, and recommends what to practice next.

## Main capabilities

- Student profile and level-based problem selection
- Starter problem bank covering arithmetic, algebra, calculus, probability, and differential equations
- Step-by-step symbolic checking with SymPy
- Rule-assisted error diagnosis plus supervised ML and a compact DNN prototype
- SQLite attempt history, weakness analytics, and mastery estimates
- Adaptive next-problem recommendation
- Reinforcement-learning feedback-style selection with an epsilon-greedy contextual bandit
- Downloadable Markdown and JSON mentor reports from the Streamlit UI

## Repository structure

```text
.
├── app.py
├── math_mentor.py
├── Anchit_Nayak_AI_Math_Mentor_App_Colab_Prototype.ipynb
├── requirements.txt
├── README.md
├── LICENSE
└── .gitignore
```

## Run locally

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## Deploy on Streamlit Community Cloud

1. Create a new GitHub repository and upload the contents of this ZIP (not the outer ZIP folder itself if GitHub creates an extra nesting level).
2. On Streamlit Community Cloud, choose **Create app** / **Deploy an app**.
3. Select the GitHub repository and branch.
4. Set the main file path to `app.py`.
5. Deploy. No API key or secrets are required for this prototype.

## Important prototype notes

- The starter corpus is intentionally small and self-contained.
- The ML/DNN models are trained on synthetic educator-style examples at app startup.
- SQLite persistence on Streamlit Community Cloud is ephemeral and can reset when the app restarts/redeploys. Use a managed database for production persistence.
- The symbolic checker is the primary mathematical validator; ML/DNN components are used to diagnose likely error categories and personalize feedback.
- This prototype is an educational aid, not a replacement for a teacher. A production system should use a curated/licensed problem corpus, stronger proof checking, accessibility testing, child-safety review, privacy controls, and educator oversight.

## Credits

- **Author:** Anchit Nayak
- **Advisor:** Dr. Qingyang Xiao
