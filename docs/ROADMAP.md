# Roadmap

Goal: a portfolio-grade AI-agentic trading research system — professional,
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

- [ ] `pyproject.toml` packaging, pinned deps
- [ ] Unit tests on indicator math against recorded OHLCV fixtures (no network);
      keep `test_smoke.py` as the separate live check
- [ ] CI: lint (ruff) + typecheck + fixture tests on every push
- [ ] Prediction Record as a validated schema (pydantic) — calibration scores
      parsed fields, not regex-over-markdown

## Phase 2 — System improvements (from the 2026-07-19 opus review)

- [ ] Calibration scoreboard: append-only results table; confidence→probability
      mapping (high=0.7 / med=0.55 / low=0.4); bias lifecycle (added/evidence/retired)
- [ ] Portfolio heat: sweep digest sums open R; crypto counted as one correlated
      cluster; aggregate heat ceiling in the spec
- [ ] Premortem line in Self-Critique Pass — red-team the synthesized call
      (regime/correlation/size), not just the thesis
- [ ] Tier 3 model flip: opus on the synthesizer (judgment), not only workers
- [ ] Hard gate: crypto reports fail review without a literal unlock table
- [ ] Macro event-window line in Prediction Record (FOMC/CPI/expiry inside horizon)
- [ ] Delete the dead Trade Log schema from the spec

## Phase 3 — Turn it back on

- [ ] Seed the watchlist with real Entry/Target/Stop per ticker (owner decides tickers)
- [ ] First /research run under the new spec — end-to-end test of provenance,
      schema validation, calibration hooks

## Phase 4 — Portfolio polish

- [ ] Showcase README: architecture diagram, calibration-loop story
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
