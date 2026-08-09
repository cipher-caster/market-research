# CLAUDE.md

## What This Repo Is

A market-research system for stocks and crypto — it issues scoreable buy/hold/avoid calls with invalidation levels; it tracks calls, never positions. One repo holds everything:
the system contract (`docs/SPEC.md`), the research skills (`.claude/commands/`),
the deterministic compute layer (`engine/`), and the data layer (`data/`).

**Read `docs/SPEC.md` first for any research task.** It defines
the tiered agent workflows, the Prediction Record format, risk rules, and the
calibration loop. This file only covers repo mechanics.

**Public repo — `data/` is published.** The owner's theses, watchlist levels, and
reports are all tracked and visible at `github.com/cipher-caster/market-research`
(public since 2026-07-25; this is the owner's deliberate choice, confirmed
2026-08-09). Write for that audience: anything committed under `data/` is
published the moment it is pushed. Never commit anything that must stay private —
API keys, `.env`, account or position sizes, personally identifying detail. If a
task would put genuinely private material into the repo, stop and ask.

## Commands

```sh
cd engine
[ -d .venv ] || (python3 -m venv .venv && .venv/bin/pip install -e ".[dev]")
.venv/bin/python test_smoke.py          # health check (live network test)
.venv/bin/python technicals.py NVDA     # stock snapshot
.venv/bin/python technicals.py BTC --crypto
.venv/bin/python regime.py              # crypto regime; regime.py SPY for stocks
.venv/bin/python check_levels.py        # watchlist level sweep
```

Prefer the `investments` MCP tools (`mcp__investments__*`) over the CLI when
available — same math, in-conversation.

## Structure

- `README.md` — short front door (tour + quick start)
- `docs/SPEC.md` — the system spec (the contract; read it, follow it)
- `.claude/commands/` — `/research`, `/refresh`, `/postmortem`, `/research-watchlist`, `/report-view` (render a report .md as a private artifact or PDF on request; .md stays canonical), `/book-view` (render the whole book as a dashboard artifact at one standing URL). Thin dispatchers: they wire inputs and spawn agents, they do not restate the briefs.
- `.claude/assets/` — resources commands render from, not commands themselves: `book-view.template.html` (the dashboard shell; refill the `REGENERATE` blocks, leave the design alone).
- `.claude/agents/` — the agent roster, one brief per role: `asset-analyst`, `report-verifier`, `fundamental-worker`, `quant-worker`, `bear-worker`, `synthesizer`. **Source of truth for how each role works** — edit the brief, not the command.
- `.claude/hooks/guard-owner-files.py` — PreToolUse guard making `data/Research/` append-only and `data/Watchlist.md` overwrite-proof, for main and agents alike. A block is a correct answer; never work around it.
- `engine/` — Python compute layer; setup in `engine/README.md`
- `data/Watchlist.md` — the calls table (source of truth for levels/status)
- `data/Research/{TICKER}.md` — the owner's own thesis, append-only. Agent writes ONLY dated one-line report pointers to the Updates Log (owner policy 2026-07-25); thesis content is owner-only. Validated reports auto-commit, house-style message.
- `data/Reports/{Crypto|Equities}/{TICKER}/` — agent-generated reports
- `data/Reports/_meta/calibration.md` — active biases; inject verbatim into EVERY agent brief
- `docs/` — design references

## Conventions

- No emojis. Direct tone, executive-summary-first.
- **Research is delegated, never written inline.** Spawn from the roster; orchestrate;
  summarize from the agents' return blocks rather than reading report bodies back. Bootstrap
  the venv once before spawning, put independent spawns in one message, and let only the main
  session run `git` or touch `data/Research/`, `data/Watchlist.md`, `calibration.md`. The
  inline exceptions are listed in `docs/SPEC.md` under "When NOT to delegate" — a single price
  lookup or a conversational question does not need an agent.
- **Every scoreable report gets a `report-verifier` pass before it commits.** The author is
  never the auditor.
- Answer market questions boldly when grounded in data/calculation/probability:
  run the computations (engine or quick scripts), give a confluence table with a
  basis per band, name a central estimate, caveats at the END. Never open with a
  hedge; "it's uncertain" is not an answer — a quantified band with reasoning is.
- Dates `YYYY-MM-DD`; prices in native currency.
- `data/Research/` is the owner's audit trail — append-only; agents add only the
  dated one-line report pointers (owner policy 2026-07-25), everything else ask-first.
- **Level-watch sweep is MANUAL-ONLY** (cron disabled 2026-07-19 at the owner's
  request — his machine is off at fixed times and he wants no automatic runs).
  Never run the sweep or re-enable the cron on your own. In a new session, when
  market data first becomes relevant, ask the owner ONCE: "run the level-watch
  sweep?" — run it only on his yes (engine/cron_sweep.sh refreshes
  data/Reports/_meta/Level-Watch.md).
