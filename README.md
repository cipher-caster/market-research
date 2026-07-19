# market-research — System Spec

This is the contract for a market-research system covering stocks and crypto. It produces decisive, time-bound, scoreable BUY / HOLD / AVOID calls with defined invalidation levels — it tracks research calls, never positions. No holdings, executions, sizing, or portfolio data exist anywhere in this system. Any Claude session in this repo reads this first. Research sessions run from this repo; the Obsidian vault is no longer involved (fully migrated 2026-07-19).

## Folder Layout

```
market-research/
  README.md              ← this file (the system contract)
  .claude/commands/      ← /research /refresh /postmortem /research-watchlist /report-view
  engine/                ← deterministic compute layer (scripts, MCP server, cron)
  docs/                  ← design references and clippings
  data/                  ← the data layer (source of truth)
    Watchlist.md         ← the calls table (levels + status)
    Research/            ← the owner's own thesis files, one per asset
    Reports/
      Crypto/{TICKER}/   ← Agent-generated reports for a crypto asset
        {YYYY-MM-DD}-{slug}.md
      Equities/{TICKER}/ ← Agent-generated reports for a stock
        {YYYY-MM-DD}-{slug}.md
      _meta/             ← System-level reports (calibration, level watch)
        calibration.md   ← Rolling calibration log, updated on events + monthly
```

**This repo is private and must stay private** — `data/` holds the owner's theses, watchlist levels, and reports.

Reports are split by asset class: **`data/Reports/Crypto/{TICKER}/`** and **`data/Reports/Equities/{TICKER}/`**. `_meta/` stays at the `data/Reports/` root (system-level, not per-asset). `data/Research/` and `data/Watchlist.md` are NOT split — they stay flat.

**Critical separation:** `data/Research/` is the owner's belief and audit trail. `data/Reports/` is agent output — inputs the owner can cite or disagree with. Never mix. Never overwrite a Research/ file with agent content.

## File Naming

- Research: `data/Research/{TICKER}.md` — one per asset, append-only Updates Log inside
- Reports: `data/Reports/{Crypto|Equities}/{TICKER}/{YYYY-MM-DD}-{slug}.md` — slug e.g. `initial-deep-dive`, `earnings-followup`, `bear-case`
- Tickers uppercase. Crypto uses common symbol (BTC, ETH, SOL).

## Watchlist.md Schema

### Calls table

Status is the call lifecycle: `Active` (call stands), `Resolved` (target hit or thesis played out), `Invalidated` (invalidation level printed or a kill criterion hit).

| Column | Format | Notes |
|---|---|---|
| Date | `YYYY-MM-DD` | When added to watchlist |
| Asset | `[[TICKER]]` | Wiki-link to Research/ file |
| Type | `Stock` / `Crypto` | |
| Thesis | one line, ≤15 words | Long-form goes in Research note |
| Catalyst | one line | What triggers the move |
| Entry | number or range | E.g. `20-22` |
| Target | number | |
| Stop | number | The invalidation level |
| Horizon | e.g. `12mo`, `3mo`, `swing` | |
| Status | `Active` / `Resolved` / `Invalidated` | |
| Call | `Buy` / `Hold` / `Avoid` | Latest verdict from the most recent report; update it (with the owner's confirmation) when a new report changes the call |

## Research Workflows — Tiered

The depth of agent research is determined by the decision being made. Don't over-spend on swings; don't under-spend on conviction calls.

### Tier 1 — Quick Check (1 sonnet agent)

**When:** ticker clarification, "what is X", swing trade context, fast-news interpretation. Anything that doesn't warrant a full scoreable call.

**Workflow:** Single sonnet subagent, web access, one-shot report. Output to `data/Reports/{Crypto|Equities}/{TICKER}/{date}-quick-{slug}.md`. Compact format: Summary, Key Facts, Levels, Sources.

### Tier 2 — Standard Deep Dive (orchestrator + 3 parallel workers + synthesis)

**Default for any asset the owner wants a real call on.**

**Architecture:**
1. **Fundamental worker** (sonnet) — narrative thesis, business model, catalysts, qualitative risks. NO price/numeric claims unless cited.
2. **Quant worker** (sonnet) — financials, valuation multiples, comp table, levels. **CITE-OR-FAIL: every number requires a source URL or gets `[UNVERIFIED]` tag.**
3. **Bear worker** (sonnet) — explicit adversarial case. Job is to argue this is a bad bet. Highest-conviction reasons it fails. Not "balanced" — actually bearish.
4. **Synthesizer** (sonnet, runs after all 3 complete) — produces the final report combining all three. Surfaces disagreements. Flags any `[UNVERIFIED]` numbers at the top.

**Output:** `data/Reports/{Crypto|Equities}/{TICKER}/{date}-deep-dive.md` — final synthesis only. Worker drafts are not saved (synthesis carries the conclusions).

**Cost:** ~4-5x a Tier 1 run. Justified by the asset deserving real conviction work.

### Tier 3 — High-Stakes (same architecture, opus workers)

**When:** the owner flags a call as high-stakes (unusual conviction, IPO coverage, a major at an inflection point).

**Architecture:** identical to Tier 2 but the three parallel workers run on **opus** instead of sonnet. Synthesizer stays sonnet. The owner must explicitly request Tier 3 OR the trigger conditions above must be met.

### Triage rule

When the owner says "research X", I default to **Tier 2** unless:
- The ask is clearly a quick check ("what is X", "what's the ticker for X")
- The owner specifies otherwise

If unsure between Tier 1 and Tier 2, ask once. Don't ask between Tier 2 and Tier 3 — apply the trigger rules.

## Mandatory Report Sections

Two required sections: **Prediction Record at the TOP** (decision-first — the owner reads the call before the analysis), and **Self-Critique Pass at the end** — plus a one-line **Provenance header** above everything.

### Provenance header — first line of every report

One line, above the Prediction Record:

`v{N} | Supersedes: {previous report filename, or "none — first report"} | Trigger: {what prompted this — scheduled sweep / owner request / stop-kill-target event / new data: <what>}`

`v{N}` counts per ticker across ALL report types (deep dives, refreshes, scans) — it is the version of the *call*, not the file. Reports are immutable: an update is always a NEW dated file with a bumped version, never an edit to an old one. The chain of versions plus each refresh's "What Changed" section is the revision history. The owner's own thesis history lives separately in `data/Research/{TICKER}.md` (append-only dated Updates Log — same rule: never rewrite past entries).

### `## Prediction Record` — goes at the top of the report

This is what makes the system score-able later, so the fields below are required. **Render it as markdown tables and plain text, never as a fenced ```yaml/code block** — tables stay readable and parse cleaner. Use this layout:

**Verdict:** one line — the action NOW + the trigger/level for the next action.

**Targets** (time-bound, each with a basis):

| Horizon | Target | Return* | Basis |
|---|---|---|---|
| Swing (~Qx) | `<price>` | `+x%` | technical measured move / level |
| EOY 2026 (base) | `<price>` | `+x%` | revenue × multiple ÷ supply |
| EOY 2026 (bull) | `<price>` | `+x%` | … |
| EOY 2027 | `<price>` | `+x%` | … (omit if catalyst horizon is shorter) |

\*returns from the current price; flag any `[UNVERIFIED]` inputs.

**Entries & risk:**

| Field | Value |
|---|---|
| Direction | buy / hold / avoid (primary, default). Optionally add a secondary **Downside flag** line when the exhaustion+premium setup is present — with its own reversal target and invalidation level |
| Regime | risk_on / neutral / risk_off (from `regime.py` on the class benchmark) — risk_off suspends the add levels below |
| Add levels | breakout trigger + add-ladder rungs (from technicals; never cost-anchored). Rungs fire on reclaim confirmation, not touch |
| Stop | `<price>` — MANDATORY; the invalidation level where the call is wrong, defined when the call is issued |
| Confidence | high / medium / low |
| Review date | `YYYY-MM-DD` — when to score this |

**Kill criteria:** one line — what invalidates the thesis.

The calibration loop parses these fields wherever they sit — tables are fine as long as the field names and values are present and unambiguous.

### `## Self-Critique Pass`

A short check appended by the synthesizer. Two questions only:
- **Citation coverage:** what % of numeric claims have a source URL? Any `[UNVERIFIED]` items?
- **Internal consistency:** does the Bear case actually contradict the bull, or are they talking past each other?

Don't expand this into a full critic agent. The point is forcing the synthesizer to look back, not generating more output.

## Calibration Loop (Auto-Improvement)

The whole point of the Prediction Record is making the system score-able.

### Mechanism

`data/Reports/_meta/calibration.md` is a rolling log updated **on resolution events and monthly**.

**Event-driven entries (the primary data feed):** the moment a stop is breached, a
target is hit, or a kill criterion triggers, write a dated calibration entry *that day*
— score the call, note what the system got right/wrong mechanically (was the stop
placement sound? did the rungs fire into weakness? was the regime missed?), and update
the Active biases if the miss reveals a pattern. Do not wait for the monthly sweep;
outcomes logged while fresh are the only honest ones.

**Monthly sweep (the aggregate):**

Process:
1. Scan all Reports/ for Prediction Records where `review_date` has passed
2. Pull current price for each asset
3. Score each: direction correct? Magnitude within ±50% of target? Kill criteria triggered as expected?
4. Compute rolling stats: hit rate by direction, by horizon, by sector
5. Identify systematic biases ("over-bullish on AI infra", "underweight regulatory risk on privacy", "stops too tight on swings")
6. Append a dated entry to `calibration.md` with stats + biases

### Feedback

Every Tier 2/3 orchestrator brief includes the **latest calibration entry as context**, with the instruction: "the system has shown the following biases in past calls — actively counter-weight."

This is the auto-improvement. Past misses get cited in future research.

## Crypto-Specific Additions

For any crypto Tier 2/3 report, the Quant worker MUST include:

- **Token unlock table** — upcoming unlocks by date and % of supply, as a literal table not prose. This is the single biggest catalyst class for crypto and gets buried in narrative every time.
- **Sentiment source:** Kaito (higher-signal than generic CT scraping)
- **On-chain sources:** Glassnode and/or Token Terminal — these are the citable primary sources

Crypto reports do not have SEC filings, so the Fundamental worker must lean harder on team, prior delivery history, and tokenomics design.

## Technicals — Programmatic Data Layer

The Quant worker does not eyeball charts, trust scraped price numbers, or hand-write
indicator math. It runs one deterministic computation and *interprets* the output, so the
numbers are identical and auditable on every run.

> **Code lives in `engine/`.** The compute layer (scripts, MCP server, cron) sits in this
> repo at `engine/` — see `engine/README.md` for setup. It reads and writes the sibling
> `data/` folder, resolved repo-relative in `engine/config.py` (override with `DATA_DIR`
> only for testing). The bare script names below (`technicals.py`, `regime.py`, …) all
> live in `engine/`.

### Primary interface: the `investments` MCP server (no manual scripts)

`investments_mcp.py` (in the engine repo) exposes the whole data layer as MCP tools, so the
assistant pulls live numbers **directly in-conversation** — no `python ...` runs by hand. It
reuses the exact same `compute()` functions as the CLI scripts (identical, auditable math), so
MCP output and CLI output agree. Registered at user scope (`claude mcp add`); the venv and the
registration are machine-local, so on a new machine rebuild the venv (`pip install -e ".[dev]"` in `engine/`) and re-run `claude mcp add` (see the engine README).

Tools (prefix `mcp__investments__`):

| Tool | Does | Source |
|---|---|---|
| `technicals_snapshot(ticker, asset_type, period, range_lookback)` | full technicals snapshot | crypto → exchange; stock → Yahoo |
| `market_regime(market)` | regime gate on BTC (`crypto`) or SPY (`stocks`) | crypto → exchange; stocks → Yahoo |
| `funding_oi(ticker)` | perp funding + OI crowding | Binance USD-M, Bybit fallback |
| `watchlist_levels()` | the Watchlist level-watch sweep | reuses the cron sweep |
| `defillama_protocol(slug)` | TVL / fees / revenue / DEX volume | DefiLlama API |

**Crypto data comes from the exchange, not Yahoo** (`exchange_ohlcv.py`): OKX primary
(the owner's main venue), Bybit fallback (HYPE etc.), Binance last, Yahoo only if all exchanges fail.
TradingView's crypto candles *are* exchange klines, so this matches the charts the owner actually
trades off — and it dodges yfinance's flakiness on newer tokens. All daily bars are
UTC-aligned. Validated 2026-06-11: exchange vs Yahoo agreed to <0.1% on BTC/ZEC/HYPE with
identical regime calls, so the switch carries no level-drift risk. Stocks stay on Yahoo
(exchanges don't list them). The crypto source stamp reads the real venue (e.g. "Source: own
computation on OKX OHLCV"), not Yahoo.

### Fallback: the CLI scripts (cron, manual, debugging)

The same logic still runs as standalone scripts — used by the cron sweep and available when
the MCP path isn't (e.g. a non-Claude shell):

```bash
cd ~/Documents/projects/market-research/engine
[ -d .venv ] || (python3 -m venv .venv && . .venv/bin/activate && pip install -e ".[dev]")
. .venv/bin/activate
python technicals.py MU            # stock
python technicals.py BTC --crypto  # crypto (or pass BTC-USD directly)
python exchange_ohlcv.py BTC       # raw exchange OHLCV (OKX/Bybit/Binance)
python technicals.py MU --json     # machine-readable
```

**Known minor inconsistency:** `technicals.py`/`regime.py`/`check_levels.py` (and thus the
cron sweep) still source crypto from Yahoo, while the MCP tools use the exchange. The two
agree to <0.1%, so no decision diverges — but the cron sweep's "Source" line still says
Yahoo. Migrate the CLI crypto path to `exchange_ohlcv.fetch_crypto` when convenient for full
consistency.

The snapshot reports: price, 20/50/200-MA posture (golden/death + % vs each), RSI(14),
MACD(12,26,9), ATR(14) with a 2·ATR long-stop suggestion, 10/20/50-bar support &
resistance, volume vs 20-day average, and — when the asset is in a golden-cross uptrend
— a **structural pullback add-ladder** (near/mid/deep rungs from the 10-bar swing low,
20-MA, and 50-MA, each with % below price). It also computes the **SMC dealing range**
(premium/discount — see below). The worker reads these and explains what they
mean — it does not recompute them.

**Add levels in an uptrend come from the add-ladder, never from cost basis.** When the
asset is trending up and the question is "where's the next buy / where do I add", the
answer must be a rung of the computed add-ladder (or a confirmed close above the prior
ATH/resistance for a breakout add) — a real level the chart defends. Do **not** anchor
an add to entry price, a round number, or "a bit below current"; if price is extended
far above the nearest rung, say so plainly (there may be no low-risk add near current
price) rather than inventing one. This is the deterministic guard against eyeballed levels.

**Rungs fire on reclaim, not on touch.** A rung (or planned entry level) is *armed* when
price touches it, but the buy signal requires **confirmation: a daily close back above
the rung with momentum turning (MACD histogram rising vs the prior bar)**. A touch that
keeps falling is distribution, not support — ZEC (2026-06) gapped through two rungs and
the stop in six days; touch-based rungs would have averaged into that. Breakout adds
already carry their own confirmation (daily close above the level on above-average
volume). No confirmation, no add — report "rung armed, awaiting reclaim" instead.

### Market regime gate — `regime.py`

Per-asset levels mean nothing in a market-wide deleveraging. Before any add/entry call,
run the regime gate on the relevant benchmark (computed, never eyeballed):

```bash
python regime.py              # crypto regime (BTC-USD)
python regime.py SPY          # equities regime
```

Deterministic rules: **risk_off** = benchmark below its 200-MA OR ≥20% drawdown from
the 90-bar high; **risk_on** = above 50-MA, golden cross, drawdown <10%; otherwise
**neutral**. The gate:

- **risk_off** — add rungs SUSPENDED across the asset class. Stops and exits still
  execute (discipline is regime-independent). New longs: starter size (1%) only, and
  only at the owner's explicit call. A rung touched during risk_off is noted as "armed" but
  never fired — the floor itself is moving.
- **neutral** — rungs fire only with the reclaim confirmation above (which is mandatory
  anyway); no leverage on new adds.
- **risk_on** — normal operation.

Every Tier 2/3 report and every `/refresh` states the current regime in the Prediction
Record. The level-watch sweep (below) prints it automatically.

### Level-watch sweep — `check_levels.py`

Monitoring is alert-driven, not calendar-driven. The sweep parses the Watchlist table,
pulls live prices, and reports only triggered levels (stop breached/near, entry or
re-entry zone reached, target hit/near), with the regime line on top:

```bash
python check_levels.py            # full output
python check_levels.py --quiet    # prints only when something triggered (cron mode)
```

Run it daily (scheduled) and whenever the owner asks "where are we". A trigger means **run
`/refresh` on that ticker** — it is never a mechanical trade signal. This exists because
levels get breached *between* scheduled reports (ZEC's stop was found 2% late).

**Standing schedule:** an OS cron job (`crontab -l` to inspect) runs the engine's
`cron_sweep.sh` at 08:17 and 20:17 local and overwrites
`data/Reports/_meta/Level-Watch.md` with the result — check that file for the
latest regime + triggers. If the machine was asleep at both run times, the note is
stale; the "Last run" line at the top tells you.

### On-chain / protocol data — `defillama.py`

For any crypto with a live protocol (DEXs, perps, RWA), the Quant worker pulls TVL,
fees, revenue, and DEX volume from DefiLlama's free API instead of flagging
`[UNVERIFIED]`:

```bash
python defillama.py hyperliquid   # slug from the defillama.com URL
```

Output counts as cited ("Source: DefiLlama API, as of {date}"). Derivatives volume /
perps market share is behind DefiLlama's paid tier — cite that limitation explicitly,
never guess the number.

### Positioning / crowding — `funding.py`

For any crypto with a listed perp, the Quant worker pulls funding rate + open interest
(Binance USD-M public API, Bybit fallback — free, no keys):

```bash
python funding.py ZEC             # maps to ZECUSDT perp
```

Reports funding now + 7d mean (per-interval and annualized), a deterministic crowding
tag (negative = shorts paying longs = squeeze fuel at support; elevated positive =
longs crowded = chase risk), and OI with 24h/7d change. Output counts as cited. Never a
standalone signal — combine with the technicals levels and the regime gate.

**Known free-tier gaps (checked 2026-06-10, do not re-litigate each report):** token
unlock schedules (DefiLlama emissions = paid) and spot-ETF flow tables (Farside blocks
scraping) have no free citable API. Unlocks and ETF flows stay web-research items with
per-claim source URLs.

### SMC execution sublayer — dealing range, premium/discount

The snapshot also computes a **dealing range** (highest high / lowest low over a
lookback, default 60 bars; tune with `--range-lookback`) and locates price within it:
the **equilibrium** (50% mid), the **% of range** price sits at, and the **zone**
(`premium` above the mid / `discount` below). This is the *WHERE/WHEN* layer on top of
the add-ladder's *WHAT* — it answers "is this even a good place to be adding?"

- **Premium (>50% of range):** a poor place to ADD — upper half of the range, where you
  trim or wait, not chase. If the owner asks "should I add here" and zone is premium, the default
  answer is **no, wait for a pullback into discount** (and name the add-ladder rung).
- **Discount (<50%):** where long adds belong. An add-ladder rung that also sits in
  discount is a higher-quality entry than one in premium. Long-side only.

A strong uptrend usually prints **premium** (it's near its highs by definition). That's
the point — it's the honest signal that *now* is not a low-risk add, the exact failure
mode (cost-anchored "add a bit below current") this layer exists to prevent. (Fib/OTE
bands are intentionally not computed: in any uptrend they fall below the invalidation
stop, so they're unreachable noise, not an entry.)

**Crypto symbols are explicit, never guessed.** Pass `--crypto` (or a `-USD` symbol)
for any asset tagged `Type: Crypto` in Watchlist. Bare majors like `BTC`/`ETH` are
*refused* — they are also stock tickers on Yahoo and would return the wrong asset.

**Citation rule:** the snapshot's computed values count as *cited* — source is
already stamped "own computation on Yahoo Finance OHLCV, as of {date}". No
`[UNVERIFIED]` tag needed. This is the deterministic counterpart to cite-or-fail on
web numbers.

**Resolution:** daily, ≥200 bars for the 200-MA (default `--period 1y`). yfinance is
unofficial; if the script errors or returns empty, say so and fall back to cited web
numbers rather than inventing levels. Health check: `python test_smoke.py`.

## Call Style

**Research calls, not positions.** The system issues BUY / HOLD / AVOID calls — long-primary, swing-horizon — and scores them later. It never tracks holdings, executions, sizing, or portfolio exposure; "risk" here means the call's invalidation level, not money at risk.

**Downside calls are allowed — as an explicit, secondary, opt-in flag, never the default.** When a high-conviction downside setup exists, the report surfaces it instead of staying silent. The primary call stays long-side (usually HOLD / WAIT / AVOID); the downside flag is offered alongside. A losing bull case still defaults to HOLD/AVOID — a downside call is only raised when the setup below is genuinely there, not every time the bear case wins.

**When to raise a downside flag (need most of these, not just one):**
- **Exhaustion:** RSI(14) ≳ 72–75 (overbought) AND momentum rolling over (MACD histogram turning negative / bearish cross).
- **Location:** price in deep **premium** (≳ 85–90% of the SMC dealing range) and at/through a major resistance or a vertical blow-off into the ATH.
- **No fresh bid:** no imminent bullish catalyst; for crypto, note any buyback/structural bid — never call downside into a strong mechanical bid or an intact, non-extended uptrend.

A downside call carries its own invalidation (above the swing high) and a defined reversal target at the obvious support / add-ladder rung. If the reversal target and a long re-entry rung point at the same level, they are one call seen from both sides.

**Be decisive — this is the house style.** Every report commits to a concrete call: the action at the current level, a defined trigger/level for the next action, and time-bound price targets. "Wait and see" is not a call. Bold, scoreable calls are the point — they get scored by the calibration loop, which is what makes boldness safe rather than reckless. Don't hedge into mush. Equally, don't fabricate precision: every price target carries a one-line valuation basis (revenue scenario × multiple ÷ supply, or a technical measured move), so a dated target is never a vibe with a timestamp.

**Horizon: swing-primary, catalyst-matched.** Most calls run weeks-to-months around a catalyst. Targets are time-bound: a near-term swing level **plus EOY-2026 and (where relevant) 2027 levels**, each with rationale. Use a `review_date` that fits the catalyst window.

Defaults (the owner can override):

- **Tier 3 trigger:** the owner flags a call as high-stakes
- **Invalidation level (Stop) MANDATORY on every call, defined when the call is issued. No exceptions.**
- **Regime gate:** check `regime.py` before any buy/add call. risk_off = no add calls (invalidation levels still resolve calls); fresh buy calls only at the owner's explicit request

## Conventions

- No emojis
- Direct tone, executive-summary-first
- Prices in native currency
- Dates always `YYYY-MM-DD`
- One-line summary columns are hard limits — long-form belongs in Research/ or Reports/
- All numeric claims in agent reports require source URLs or `[UNVERIFIED]` tag

## Workflows (Quick Reference)

### Log a watchlist entry
1. Append row to Watchlist table
2. If data/Research/{TICKER}.md doesn't exist, create it with Thesis / Levels / Updates Log sections

### A call resolves (target hit / invalidation printed / kill criterion)
1. Update the matching Watchlist row Status (`Resolved` / `Invalidated`) — the levels stay as the record of the call
2. Run /postmortem to score it into the calibration log
3. Append a dated entry to data/Research/{TICKER}.md Updates Log if the thesis changed (ask first; never auto-edit)

### Update existing thesis
- Always append to Updates Log with `### YYYY-MM-DD` header
- Never rewrite past entries — audit trail is the point

### Request agent research
1. Triage tier (default Tier 2)
2. For Tier 2/3: spawn orchestrator with calibration context, three workers run in parallel, synthesizer runs after
3. Report saved to `data/Reports/{Crypto|Equities}/{TICKER}/`
4. Summarize findings to the owner, ask whether to update data/Research/{TICKER}.md
5. Do NOT auto-update the owner's thesis — that's his audit trail

### Read patterns
When the owner references an asset by ticker, default to:
1. Watchlist.md row(s) — current status
2. data/Research/{TICKER}.md — the owner's thesis
3. Latest file in data/Reports/{Crypto|Equities}/{TICKER}/ — most recent agent input
4. `_meta/calibration.md` — current systematic biases
