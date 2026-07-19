# Claude Markets Analysis System — Architecture, Skills, Prompts & Rules

> A working blueprint for using Claude as a disciplined, repeatable analyst over crypto
> and stock markets — consuming OHLCV from your **existing app's backend**, layering in
> news/macro via web search, and producing trade theses you act on.
>
> **Not investment advice.** Claude is an analyst that enforces your checklist and removes
> emotional bias. It is not an oracle and has no proven edge. You make every decision.

---

## 0. The one distinction that governs the whole design

There are two different things people mean by "let AI handle the markets," and conflating
them is the #1 way to lose money:

| Layer | What it does | Who does it here |
|-------|--------------|------------------|
| **Decide (analyst)** | Reads data + news, computes technicals, produces buy/sell/hold *theses* with risk framing | **Claude** — this is what it's genuinely good at |
| **Execute (trader)** | Places live orders on an exchange/broker, manages fills | **Not Claude.** Your code, human-gated, paper-traded first |

Keep these layers separate. An LLM firing live orders against your capital with no human
gate is how accounts get wrecked. The reference you're modelling on (the public "Claude
Portfolio" experiment) is exactly this split: the AI *thinks*, a separate product does the
*plumbing*.

**Reality check on that reference:** a few months of a public performance contest is
statistically meaningless and carries heavy selection/marketing bias. Use it as inspiration
for the *workflow*, not as evidence of edge.

---

## 1. Your revised architecture (you already have the data layer)

Because your existing app already produces OHLCV, the "new folder" is **not** a
data-collection project. It is a thin **analysis layer that consumes your backend's output.**
This is a much cleaner design than starting from scratch.

```
┌─────────────────────────────────────────────────────────┐
│  YOUR EXISTING APP (backend)                              │
│  → produces OHLCV (+ volume, maybe on-chain / fundamentals)│
└───────────────────────────┬─────────────────────────────┘
                            │ exposes data (CSV export, JSON endpoint, or DB read)
                            ▼
┌─────────────────────────────────────────────────────────┐
│  NEW: ANALYSIS LAYER ("the folder")                       │
│  • strategy-rules.md        (your mandate & risk limits)  │
│  • prompts/                 (reusable analysis prompts)   │
│  • data adapter             (pulls from your backend)     │
│  • optional: api runner     (Anthropic API + cron)        │
└───────────────────────────┬─────────────────────────────┘
                            │
              ┌─────────────┴─────────────┐
              ▼                           ▼
   ┌──────────────────┐        ┌────────────────────┐
   │  CLAUDE (decide) │        │  WEB SEARCH (news,  │
   │  reasons over    │◀──────▶│  macro, catalysts,  │
   │  numbers + rules │        │  narratives)        │
   └────────┬─────────┘        └────────────────────┘
            │ outputs: theses, watchlist, risk flags
            ▼
   ┌──────────────────┐
   │  YOU (execute)   │  ← human gate. Optionally a paper-trading
   │  pull the trigger│    endpoint before any real capital.
   └──────────────────┘
```

### How your backend plugs in
Pick the lowest-friction integration that your app already supports:

1. **CSV export (simplest, start here).** Your app dumps OHLCV to CSV; you upload it to
   Claude. Claude runs real pandas/Python on it (it can compute indicators itself, not just
   eyeball charts). This is the same CSV-analysis workflow you already used on the
   air-quality project — identical muscle, different columns.
2. **JSON endpoint.** If your backend exposes an API, the optional Layer-4 runner fetches it
   on a schedule and passes it to Claude via the Anthropic API.
3. **Direct DB read.** The runner queries your app's database directly. Most coupling; only
   worth it if you're automating heavily.

**Recommendation:** begin with CSV export. It requires zero new code and proves the analysis
value before you invest in plumbing.

---

## 2. Do you need TradingView? Is web search enough?

Neither is mandatory; they do *different jobs*. You likely want all three sources, each used
for what it's good at:

| Source | Good for | Bad for |
|--------|----------|---------|
| **Your backend / CSV** | Precise OHLCV, exact indicator computation, backtests | News, narrative, macro |
| **Web search** | Current news, earnings dates, macro/regulatory events, sector narrative | Precise prices, exact candle data, indicator values |
| **TradingView** | Live charting, multi-timeframe eyeballing, your own alerts | Feeding precise data *into* Claude (Claude can't see your screen or query TV here) |

**Verdict:** Since you already have a backend for OHLCV, TradingView becomes *optional* —
useful for live charts and alerts, but your own data + Claude's pandas computation can
replace it for the analysis itself. Keep web search in the loop for everything qualitative.

---

## 3. The build, in layers (stop at whatever matches your effort/risk budget)

### Layer 0 — Data inputs
Three channels: (a) your backend's OHLCV, (b) web search for news/macro/narrative,
(c) **your own context**: current holdings, cost basis, risk limits, open theses.
Garbage in, garbage out — analysis quality is capped by input quality and freshness.

### Layer 1 — Prompt library (highest leverage, lowest effort)
Reusable, standardized prompts so the *same rigorous checklist* runs every time. This is the
actual "skill set." See §5.

### Layer 2 — Persistent strategy-rules document
A markdown file holding your mandate, risk parameters, sizing logic, universe, and watchlist.
Attach it to every session (or load it into a Claude Project) so Claude reasons *within your
system*, not as a generic chatbot. See §6. **This is the difference between "an opinion" and
"an analyst who knows your mandate."**

### Layer 3 — Routine cadence
- **Pre-market / pre-session scan** — what's set up today
- **End-of-day review** — what happened, what changed
- **Weekly portfolio review** — rebalance, heat check, thesis audit
- **Trade post-mortem** — every closed trade, win or lose

Run on schedule. This is where it starts *feeling* automated even though you're running prompts.

### Layer 4 (optional, separate project) — Real automation
Anthropic API + your backend's data + a cron job. Claude generates analysis; **your code**
fetches and schedules. Execution stays human-gated, or behind a **paper-trading endpoint for
months** before any real capital. This is a software project, not a prompt — treat it as such.

---

## 4. Technicals Claude needs

You don't have to teach Claude RSI or MACD — it knows the toolkit. You need to **supply the
data** and **specify which framework** to apply and how to weight it.

**Both markets:** trend structure (HH/HL, 50/200 MA posture), momentum (RSI, MACD),
volatility (ATR, Bollinger), volume confirmation, support/resistance.

**Crypto-specific:** funding rates, on-chain flows, exchange reserves, BTC dominance, sector
rotation/narrative (e.g. rotation into AI tokens).

**Stock-specific:** earnings dates & surprises, valuation multiples, sector relative
strength, macro/rates backdrop.

**The skill is asking Claude to synthesize these into a thesis with explicit invalidation
levels** — conditional scenarios with probabilities, never a single magic price prediction.

---

## 5. Prompt library

### 5.1 Daily / pre-session scan
```
You are my markets analyst. Apply my attached strategy-rules.md.
Inputs: [attach OHLCV CSV from my backend] + [recent news via web search]
        + [my current positions below].

For each ticker:
1. Trend — structure + 50/200 MA posture
2. Momentum — RSI, MACD — and volume confirmation
3. Key support/resistance + current ATR
4. Catalyst/news in next 1–2 weeks (search if needed)
5. Thesis — bias (long/short/flat), conviction (1–5), entry zone,
   invalidation level, and what would change your mind.

Flag anything that violates my risk rules. No price predictions —
give conditional scenarios with rough probabilities.
End with: top 3 actionable setups ranked, and what to ignore.
```

### 5.2 Single-asset deep dive
```
Deep dive on [TICKER] under my strategy-rules.md.
Data attached: [OHLCV CSV, multiple timeframes if available].
Cover: multi-timeframe trend alignment, momentum/volume, volatility regime,
the bull case, the bear case, the key level that decides which plays out,
and the single most important catalyst on the horizon (search).
Finish with a concrete plan: entry, stop (= thesis-invalidation), targets,
and position size per my sizing rule. Tell me the conviction honestly,
including if the answer is "no trade."
```

### 5.3 Weekly portfolio review
```
Review my portfolio against strategy-rules.md.
Positions: [list: ticker, size, entry, current, stop, thesis].
Assess: total portfolio heat vs my limit, concentration vs my limits,
any thesis that's now invalidated or stale, correlation clustering,
and rebalancing actions. Rank actions by urgency. Be blunt about
losers I'm holding for emotional reasons.
```

### 5.4 Trade post-mortem
```
Post-mortem this closed trade: [entry, exit, size, original thesis, outcome].
Was the original thesis sound regardless of outcome? Did I follow my rules?
What was process vs luck? One concrete lesson for strategy-rules.md.
Don't be nice — be useful.
```

### Prompt-engineering notes
- Always attach `strategy-rules.md` so output is bounded by your mandate.
- Demand **invalidation levels** on every thesis — this is the discipline that protects you.
- Forbid single-point price predictions; require **conditional scenarios + probabilities**.
- Ask for "no trade" as a valid, encouraged answer. Most days have no good setup.

---

## 6. strategy-rules.md skeleton (your mandate)

```markdown
# Strategy Rules

## Risk
- Max risk per trade: 2% of account
- Max total portfolio heat: 6%
- Max allocation to any one asset: 20%
- No leverage on crypto. [Stocks: define if/what margin.]

## Universe
- Trade: [your tickers / coins]
- Never trade: [exclusions — illiquid, scam-prone, outside competence]

## Position sizing
- size = (account * 0.02) / (entry_price - stop_price)
- Round down. Never up.

## Style
- Swing trades, 3–15 day holds [adjust to you]
- Every trade has a pre-defined stop = the price that proves the thesis wrong

## Review cadence
- Daily scan (pre-session)
- Weekly portfolio + heat review
- Monthly strategy audit
- Post-mortem on every closed trade

## Hard "don't" list
- No averaging down on a losing thesis
- No trade without an invalidation level
- No revenge trading after a loss
- No position that breaches heat/concentration limits
```

Tune every number to your own risk tolerance and capital. The structure matters more than my
placeholder values.

---

## 7. Suggested folder layout for the new analysis layer

```
markets-analysis/
├── strategy-rules.md          # your mandate (§6)
├── prompts/
│   ├── daily-scan.md
│   ├── deep-dive.md
│   ├── weekly-review.md
│   └── post-mortem.md
├── data/
│   └── adapter.(py|ts)        # pulls OHLCV from your existing backend → CSV/JSON
├── runs/
│   └── YYYY-MM-DD-scan.md     # archived outputs, so you can audit Claude over time
└── (optional) runner.(py|ts)  # Layer 4: Anthropic API + cron, paper-trade first
```

Archiving every run in `runs/` matters: after a month you can review whether Claude's
*reasoning quality* actually improved your decisions — which is the only metric that counts.

---

## 8. Recommended path

1. **This week:** write your real `strategy-rules.md`; save the four prompts.
2. **Wire the data:** add a tiny adapter so your backend exports OHLCV to CSV on demand.
3. **Run daily for a month** against a **paper portfolio**. Archive every run.
4. **Judge on reasoning quality**, not P&L — a month of P&L is noise.
5. **Only then**, if you want unattended operation, build the Layer-4 API runner as a
   deliberate second project — execution still human-gated, paper-traded for months.

Don't build the app first. The prompts + rules + your existing backend get you ~80% of the
value with near-zero new code.

---

## 9. Honest caveats

- A few months of any AI portfolio proves nothing statistically.
- Claude's value is **consistency and bias-removal**, not predictive edge.
- Your backend's data quality and freshness cap everything downstream.
- I'm not a financial advisor; this is an architecture, not a recommendation to trade.
- The sound parts of this design (separation of decide/execute, human gate, paper-trading,
  invalidation discipline) hold regardless of whether any strategy makes money.
```
