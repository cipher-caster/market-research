# /research — Asset Research (stocks & crypto)

Run the research workflow for the asset in `$ARGUMENTS`. You orchestrate; the agents in
`.claude/agents/` do the work.

**Usage:**
- `/research MU` — deep dive (defaults to Tier 2)
- `/research BTC quick` — Tier 1 quick check
- `/research NVDA tier3` — high-stakes (opus synthesizer + opus bear)

## The contract lives in docs/SPEC.md

`docs/SPEC.md` is the source of truth for the tiers, the pipeline, the Prediction Record
format, the risk rules, the orchestration rules, and the calibration loop. The **agent briefs
in `.claude/agents/`** are the source of truth for how each role works. **Read the spec and
follow it.** This command only wires up the inputs.

## Steps

1. **Parse `$ARGUMENTS`** — ticker (uppercase) and any tier hint (`quick` / `tier2` / `tier3`).
   Triage per the spec: default Tier 2, but if the asset already has a report on file and the
   ask is "where are we", that is a Refresh — use `/refresh`.

2. **Resolve the inputs** (cheap reads, main session — agents re-read what they need):
   - `data/Watchlist.md` row(s). `Type` decides the `--crypto` flag and the `Crypto|Equities`
     path. No row is fine for a new asset; note it.
   - Any existing report in `data/Reports/{Crypto|Equities}/{TICKER}/` — the version to
     supersede, or "none — first report".
   - `data/Reports/_meta/calibration.md` — the latest **Active biases**, verbatim.

3. **Bootstrap the venv ONCE, before spawning anything:**
   ```bash
   cd engine && [ -d .venv ] || (python3 -m venv .venv && .venv/bin/pip install -e ".[dev]")
   .venv/bin/python test_smoke.py
   ```
   If the smoke test fails, stop and report — never spawn against a broken data layer.

4. **Dispatch by tier.** Every brief carries: ticker, Type, asset-class path, today's date, the
   version to supersede, the trigger, and the active calibration biases verbatim.

   | Tier | Spawn |
   |---|---|
   | Tier 1 | One `asset-analyst` in quick mode → `{date}-quick-{slug}.md`. No Prediction Record, no verifier |
   | Tier 2 | `fundamental-worker` + `quant-worker` + `bear-worker` **in one message** (parallel) → then `synthesizer` with all three return briefs → `{date}-deep-dive.md` |
   | Tier 3 | Same as Tier 2, but spawn `synthesizer` and `bear-worker` with `model: opus` |

   Do not pass the workers' numbers to the synthesizer as gospel — the synthesizer re-pulls
   anything decision-critical. That is deliberate; see "Whoever cites a number pulls it
   themselves" in the spec.

5. **Verify.** Spawn `report-verifier` on the finished report (Tier 2/3 only). `NEEDS FIX` →
   send the blockers back to the `synthesizer` via `SendMessage` so it keeps its context, then
   re-verify. Loop until PASS. Where the verifier's independent premortem names a different
   primary failure mode than the author's, both belong in the Self-Critique Pass.

6. **Commit — main session only, agents never run git.** Once `prediction_record.py` prints OK
   and the verifier PASSes: append the dated one-line pointer (version, verdict, report path)
   to `data/Research/{TICKER}.md` Updates Log via a pure-append Edit, and commit the report +
   pointer together. Pointers only, never analysis.

7. **Summarize from the return blocks — do not paste the report.** Give the owner the call, the
   levels, and the one decision he owns. If the asset has no Watchlist row, or the call changes
   an existing row, ask whether to add/update it. Thesis content in `data/Research/` stays
   owner-only; anything beyond the pointer line is ask-first.
