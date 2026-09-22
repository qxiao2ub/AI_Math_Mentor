# UI Integration Notes

## Source design translated into Streamlit

The supplied UI was a Vite/React application using TypeScript, Tailwind CSS, shadcn/ui, Framer Motion, React Router, Archivo Black, and Inter. It defined five primary routes:

- Home
- Analyze
- Mastery
- About
- Settings

The final repository keeps those five information-architecture destinations but implements them natively in Streamlit so Streamlit Community Cloud can launch the project directly from `app.py`.

## Retained visual characteristics

- Oversized Archivo-style display headings
- Inter-style body typography with safe fallbacks
- Dark mode as the default
- Light-mode option
- Cobalt-blue primary accent
- Square, border-driven cards and controls
- Top horizontal navigation
- Large landing-page hero
- Three-step "how it works" presentation
- Analyze workspace with problem, solution, and feedback phases
- Step feedback cards with correct/error edge treatments
- Mastery progress cards
- Large typographic footer

## Uzbekistan adaptations

The visual design is combined with the existing Uzbekistan-only product constraints:

- Uzbekistan flag stripe and country branding
- Uzbekistan regions
- School, academic lyceum, and university pathways
- Uzbek, Russian, and English interface copy
- Local UZS/problem contexts
- Independent-prototype notice

## Why the React project is not embedded

Embedding a separate React application inside Streamlit would require a second build toolchain, static-asset hosting, component messaging, and duplicated application state. Instead, the design tokens and layouts were ported into `ui_theme.py` and the page copy into `ui_copy.py`. This keeps the deployment single-process, GitHub-friendly, and compatible with Streamlit Community Cloud.

## Main implementation files

- `ui_theme.py`: colors, typography, card treatment, navigation styling, button/input styling, metrics, progress bars, and footer.
- `ui_copy.py`: Uzbek, Russian, and English copy for the redesigned pages.
- `app.py`: page composition and integration with the existing AI engine.
