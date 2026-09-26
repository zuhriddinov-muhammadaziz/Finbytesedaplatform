# FinBytes EDA site

A public-facing Streamlit report that explains the project data and analysis. It is an exploratory report, not a prediction or model-serving application.

## Run locally

From the project root, install the website dependencies and build its aggregate-only summary once:

```bash
python -m pip install -r eda_site/requirements.txt
python eda_site/build_summary.py
python -m streamlit run eda_site/app.py
```

Then open the local URL printed by Streamlit (normally `http://localhost:8501`). The builder reads the project CSV and Parquet inputs, applies the as-of-signal temporal rule to transaction summaries, and writes `eda_site/assets/eda_summary.json`. The app loads this small precomputed file, so requests do not repeatedly scan the source transaction data.

The aggregate JSON contains counts, distributions, and summary statistics only; it does not contain signal identifiers or individual transaction rows. Rebuild it whenever the source dataset changes.

## Deploy

Push this project to a Git repository, then create a Streamlit Community Cloud app using `eda_site/app.py` as the entry point. Streamlit installs the dependencies from `eda_site/requirements.txt`. Include the precomputed `eda_site/assets/eda_summary.json` in the repository. Do not include private/local data paths, organizer-only materials, or raw competition data in a public deployment. Confirm you have permission to publish the aggregate findings and charts before making the repository or app public.

For a static GitHub Pages deployment, the repository workflow publishes `docs/index.html` and copies only the aggregate `eda_summary.json` into the Pages artifact. Enable Pages once in the repository's **Settings → Pages** by selecting **GitHub Actions** as the build and deployment source, then rerun the **Deploy static EDA to GitHub Pages** workflow. After it succeeds, the site is available at `https://zuhriddinov-muhammadaziz.github.io/Finbytesedaplatform/`. GitHub Pages cannot run the Streamlit Python app itself.

The static workflow is configured in `.github/workflows/pages.yml`. Do not describe the site as deployed until the workflow succeeds and the public URL has been checked.

The GitHub Pages version is a standalone static dashboard at `docs/index.html`; Pages cannot execute this Streamlit app. It shares the app's restrained white-and-teal dashboard styling and includes aggregate outcome charts, analytics, monthly transaction summaries, forward-validation results, year filters, and search. It embeds the aggregate summary so its charts work without a separate JSON request or project-subpath asset URL. Keep its layout and published findings aligned with `app.py`, and refresh the embedded summary in `docs/index.html` after rebuilding `eda_site/assets/eda_summary.json`.

## Contents

- `app.py` — interactive report with all 14 requested sections.
- `build_summary.py` — builds aggregate-only chart data from the project's source data.
- `assets/eda_summary.json` — precomputed summary consumed by the app.
- `requirements.txt` — deployment dependencies.
