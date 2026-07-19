# /report-view — Render a report as an Artifact or PDF (on demand)

Reports are stored as `.md` in `data/Reports/` — that stays canonical (parseable,
diffable, agent-readable). This command renders a *view* of one when the owner
wants to read it properly. The rendered output is disposable, never the source
of truth; never edit a report through its rendered form.

**Usage:**
- `/report-view HYPE` — render the most recent report for a ticker (default: artifact)
- `/report-view HYPE pdf` — render as PDF instead
- `/report-view digest` — render the latest `data/Reports/_meta/Watchlist-Scan/` digest

## Steps

1. **Locate the source** — the most recent `.md` in
   `data/Reports/{Crypto|Equities}/{TICKER}/` (or the named file if the owner
   points at one). Read it fully.

2. **Artifact (default):** load the `artifact-design` skill first, then build a
   single self-contained HTML page and publish with the Artifact tool
   (private by default — do not share).
   - Prediction Record rendered as proper tables at the top; Verdict visually
     prominent.
   - Inline CSS only (CSP blocks external assets); light + dark theme support.
   - Keep the favicon stable per ticker across redeploys.
   - No emojis, no decorative fluff — same tone as the report.

3. **PDF:** convert via LibreOffice (installed) from an intermediate HTML:
   ```sh
   # write report.html (same clean HTML as the artifact path), then:
   libreoffice --headless --convert-to pdf report.html --outdir /tmp/claude-reports/
   ```
   Build the intermediate HTML yourself from the .md (tables as <table>, no
   external assets). Hand the owner the output path. Do not commit PDFs or
   intermediate HTML to the repo.

4. **Never** write rendered output into `data/` — it holds canonical `.md` only.
