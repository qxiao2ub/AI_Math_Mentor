# MathMentor AI React UI Source

This directory preserves the attached React and TypeScript UI that guided the Streamlit migration.

**Author:** Anchit Nayak  
**Advisor:** Dr. Qingyang Xiao

## Technology

- Vite
- React
- TypeScript
- Tailwind CSS
- shadcn/ui
- Framer Motion
- React Router
- Recharts

## Purpose in this repository

Streamlit Community Cloud runs the production prototype through the root-level `app.py`. The files in this directory are retained as the original design source for future front-end work, comparison, and possible deployment as a separate React client.

## Run the React reference locally

```bash
npm install
npm run dev
```

The React reference uses front-end prototype data. The deployable Streamlit app connects the migrated visual design to the Python symbolic-checking, ML/DNN diagnosis, SQLite history, mastery analytics, feedback-bandit, and recommendation pipeline.
