# /book-view — Render the whole book as a dashboard Artifact

`/report-view` renders ONE report. This renders the **book**: every active call in
`data/Watchlist.md`, each as a stop→target level ladder with its verdict, live trigger,
kill-criteria status and latest report version — plus the report ledger and the open items.
It is the "where does everything stand right now?" view.

Like `/report-view`, the output is a *view*: disposable, never the source of truth, never
committed, never written into `data/`. The `.md` files stay canonical.

**Usage:**
- `/book-view` — render the current book (default: artifact)
- `/book-view pdf` — render as PDF instead, via the LibreOffice route in `/report-view`

**Standing artifact URL:** `https://claude.ai/code/artifact/dec534ce-848e-4657-9b3f-4134920adaff`
Pass it as `url` to the Artifact tool so the dashboard redeploys in place instead of minting a
new link each cycle. Keep the favicon stable at 📓.

## Steps

1. **Read the sources** — cheap, targeted reads; do not read report bodies in full.
   - `data/Watchlist.md` — **the source of truth for levels and status.** One row per call:
     entry, target, stop, thesis, catalyst, horizon, status, call.
   - `data/Reports/_meta/Level-Watch.md` — last price per ticker and the sweep timestamp.
     **Never run the sweep to refresh it** (manual-only, cron disabled 2026-07-19); read what
     is there and label the page with its timestamp.
   - The newest `.md` per `data/Reports/{Crypto|Equities}/{TICKER}/` — take the version header
     (line 1) and grep only the fields the card needs: `**Verdict:**`, `| Confidence |`,
     `| Review date |`, `| Add levels |`, `| Stop |`, `**Kill criteria:**`.
   - `data/Reports/_meta/calibration.md` — scoreboard state and active biases.
   - `git log --oneline -- data/Watchlist.md` — when a row last moved, and why.

2. **Reconcile, and never silently pick a winner.** For each ticker, compare the Watchlist
   levels against the levels in its newest report. They drift apart whenever a report proposes
   a fix marked *owner decision, not applied*, or whenever the Watchlist is synced afterwards.
   - Draw the ladder from the **Watchlist**, per its source-of-truth role.
   - Every divergence becomes an **Open Item** naming both numbers and which one is drawn.
   - A `Level-Watch.md` row that disagrees with `Watchlist.md` means the sweep predates the
     last sync — say so rather than quietly using the newer number.

3. **Recompute every percentage here**, from Watchlist levels against the Level-Watch price.
   Do not copy percentages out of report bodies: reports are written against a later intraday
   print, so their figures will not tie out against the sweep. State that in the colophon.
   Ladder position is `(level − stop) / (target − stop)`; reward:risk is
   `(target − price) / (price − stop)`.

4. **Build from the template** — `.claude/assets/book-view.template.html`. Keep the CSS shell
   and the ladder/table rendering verbatim so the design stays stable across redeploys; the
   `REGENERATE` markers show what changes each cycle: the dateline, the gate strip, the summary
   tiles, the `assets` array, the `ledger` array, and the open items. Load the
   `artifact-design` skill only if you are changing the design, not to refill the data.

5. **Check the claims before publishing.** The summary tiles are the easiest place to state
   something the reports contradict — a "no triggers fired" tile is wrong if any rung fired and
   reversed. Every tile and every gate figure must trace to a line in a report or the Watchlist.

6. **Publish** with the Artifact tool at the standing URL. Private by default — do not share.
   Hand the owner the link plus the open items in the reply; the divergences are the part he
   actually needs to see, and they belong in the summary rather than only on the page.

7. **Never** write the rendered HTML into `data/`, and never commit it. The scratchpad copy and
   the artifact are the whole output.
