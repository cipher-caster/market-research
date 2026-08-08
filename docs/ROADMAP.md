# Roadmap

Goal: a portfolio-grade AI-agentic market-research system (scoreable calls, no position tracking) — professional,
efficient, every addition justified. Commit locally as work lands; push/publish
only when the repo earns it. Real data never enters git history.

## Phase 0 — Foundations (in progress)

- [x] Consolidate system into one repo (spec, skills, engine, data) — 2026-07-19
- [x] Scrub personal identity/machine paths from code and docs — 2026-07-19
- [x] Clean-slate data layer (empty watchlist, fresh calibration) — 2026-07-19
- [x] Delete accidentally-pushed remote repo — 2026-07-19
- [x] Data policy: `data/` IS tracked — progress visible in history (owner's call); repo stays private — 2026-07-19
- [x] Initial commit (local only) — 2026-07-19
- [ ] Delete parked pre-consolidation git history folder (owner)

## Phase 1 — Engineering hygiene

- [x] `pyproject.toml` packaging, pinned deps; ruff + mypy clean — 2026-07-19
- [x] Fixture unit tests (goldens + invariants + parsing, 18 tests, no network) — 2026-07-19
- [x] CI workflow: ruff + mypy + pytest (runs when the repo gets a remote) — 2026-07-19
- [x] Prediction Record pydantic schema + validator CLI, wired into the skills — 2026-07-19

## Phase 2 — System improvements (from the 2026-07-19 opus review)

- [x] Calibration scoreboard + confidence probabilities + bias lifecycle — 2026-07-19
- [x] Correlation flag in the sweep digest (beta clusters) — 2026-07-19
- [x] Premortem line in Self-Critique Pass (red-team the call) — 2026-07-19
- [x] Tier 3 model flip: opus synthesizer, sonnet workers — 2026-07-19
- [x] Hard gate: crypto unlock table enforced by prediction_record.py — 2026-07-19
- [x] Event-window row in the Prediction Record — 2026-07-19
- [x] Delete the dead trade-log schema; reframe to pure research calls (no positions) — 2026-07-19

## Phase 3 — Turn it back on

- [x] Watchlist seeded — BTC first call live (more tickers as the owner names them) — 2026-07-19
- [x] First Tier 2 run (BTC deep dive v1, HOLD) — provenance + schema validation + sweep all exercised — 2026-07-19

## Phase 3.5 — Agent architecture (owner-approved 2026-08-08)

The tiered subagent design existed on paper but ran only on Tier 2 deep dives — one report
per asset, ever. Refreshes (the highest-volume path, and the one carrying every live call
after v1) ran inline, unverified, and serially.

- [x] Agent roster in `.claude/agents/` — `asset-analyst`, `report-verifier`,
      `fundamental-worker`, `quant-worker`, `bear-worker`, `synthesizer`. Briefs moved out
      of the command files (which had drifted apart) into one file per role, each carrying
      its own tool grants and model — 2026-08-08
- [x] `report-verifier` stage on every scoreable report — the author is never the auditor.
      Re-derives numbers rather than re-reading them; writes an independent premortem — 2026-08-08
- [x] Refresh & Scan promoted to a first-class tier (analyst + verifier); a refresh that
      changes the call also spawns the bear worker — 2026-08-08
- [x] Orchestration rules: return-block contract (main never reads a report body), venv
      bootstrapped once, agents never run git, single writer for the shared files — 2026-08-08
- [x] `.claude/hooks/guard-owner-files.py` — append-only enforcement for `data/Research/`
      and overwrite-proofing for `data/Watchlist.md`, structural rather than prose, binding
      main and agents alike (18-case test suite) — 2026-08-08
- [x] Score the architecture: after ~5 verified reports, check whether verifier blockers
      are catching real defects or generating noise — 2026-08-08. **Verdict: keep, and
      tighten.** Five reports audited (ETH v3, SOL v2 pre-commit; BTC v4, ZEC v6, HYPE v2
      retrospectively). Ten blockers, zero noise — every finding reproduced from primary
      data, and several inverted a claim rather than nitpicking it: a reclaim trigger that
      had already fired and reversed while the report called it pending; a bear leg
      measured at roughly half its stated severity; a base rate softened by the exact
      overlapping-window artifact the report claimed to have excluded; a silent target cut
      that would have reached the owner invisibly. The two reports that ran the full
      pipeline are the two that came out clean.
      Adversarial value runs both ways: correction authors caught errors in the *verifiers*
      (a premortem resting on a six-up-close streak that was actually 4 up / 2 down; a
      decay figure computed against a window containing its own comparison period), and
      one found a gate-semantics error — risk_off is an OR-gate — that no prior pass saw.
- [x] Gate the three recurring defect classes in `prediction_record.py` — Self-Critique
      heading completeness, ATR multiple on the Stop, premortem classification label.
      WARN by default so the immutable back catalogue still validates; `--strict` fails,
      and all new work validates with `--strict`. Empirical confirmation of the diagnosis:
      of the eight non-clean reports, every one is missing *Internal consistency*
      specifically, never the other two — 2026-08-08
- [ ] Re-score after the next ~5 reports written UNDER the architecture (the first five
      were mostly written before it). The question shifts from "does the verifier catch
      defects" to "does it still find enough to justify its cost once authors improve"

## Phase 4 — Portfolio polish

- [ ] Showcase README: architecture diagram, calibration-loop story (short
      README + docs/SPEC.md contract split done 2026-07-25)
- [ ] Decision log (e.g. "vector DB/RAG: considered, rejected until corpus scale
      demands it — revisit when reports span years")
- [ ] Synthetic demo data + demo calibration run so the public repo demos itself
- [ ] Public portfolio version: separate clean extract (framework + synthetic data) — this repo stays private since history contains real research
- [ ] Optional: /report-view dashboard artifact as the visual demo

## Principles

- .md is canonical for reports; rendered views (artifact/PDF) are disposable
- Reports immutable + versioned (provenance header); thesis append-only
- Deterministic compute layer; agents interpret, never recompute
- New tech (vector DB, RAG, more agents) only when a measured bottleneck
  justifies it — record the decision either way
