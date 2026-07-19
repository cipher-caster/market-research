# engine/

The deterministic compute layer for the market-research system — Python venv,
MCP server, cron. It reads and writes the sibling `data/` folder in this repo.

The *system spec* — research tiers, Prediction Record format, calibration loop —
lives at the repo root `README.md`. That's the contract; this README is just how
to run the code.

## Setup

```sh
cd ~/Documents/projects/market-research/engine
python3 -m venv .venv
.venv/bin/pip install -e ".[dev]"
.venv/bin/python test_smoke.py
```

`config.py` resolves the data layer repo-relative (`../data`). Override with the
`DATA_DIR` env var only for testing; if the folder is missing the engine fails
fast with a clear message.

## Layout

```
config.py            data bridge — resolves ../data, exposes TRADE_LOG/REPORTS paths
investments_mcp.py   MCP server (FastMCP, stdio) — the primary interface, 5 tools
technicals.py        MA/RSI/MACD/ATR, S/R, SMC dealing range
regime.py            risk-on/neutral/off gate on the benchmark
funding.py           perp funding + open interest (Binance/Bybit)
defillama.py         on-chain TVL/fees/revenue
check_levels.py      watchlist level-watch sweep (the cron job)
fetch_ohlcv.py       Yahoo OHLCV (stocks)
exchange_ohlcv.py    crypto OHLCV from OKX -> Bybit -> Binance (matches TradingView)
test_smoke.py        live smoke test — "is it still working?"
cron_sweep.sh        cron entry: runs check_levels.py, writes ../data/Reports/_meta/Level-Watch.md
```

Flat layout on purpose: the modules import each other as siblings and the MCP
server puts its own dir on `sys.path`. No package indirection needed.

## Interfaces

**MCP server (primary).** Registered with Claude Code (user scope):

```sh
claude mcp add --scope user investments \
  ~/Documents/projects/market-research/engine/.venv/bin/python \
  ~/Documents/projects/market-research/engine/investments_mcp.py
```

Tools: `technicals_snapshot`, `market_regime`, `funding_oi`, `watchlist_levels`,
`defillama_protocol`. Registration is machine-local (not in git) — redo it on a
new machine.

> **If a tool errors with a stray import (e.g. `No module named 'numpy.rec'`) but
> the same call works from the CLI:** Claude Code launches the MCP server once at
> session start and holds that process. If the venv was moved, rebuilt, or deleted
> mid-session (or you re-ran `claude mcp add` against a new path), the live server
> is the stale one pointing at the old interpreter — its lazy imports break.
> **Fix: restart Claude Code** so it respawns the server from the current `.venv`.
> Verify the engine itself first with `.venv/bin/python -c "import investments_mcp
> as S; print(S.market_regime('crypto')[:80])"` — if that prints, the env is fine
> and it's purely the stale in-session server.

**CLI (fallback / debugging).**

```sh
.venv/bin/python technicals.py NVDA            # stock
.venv/bin/python technicals.py BTC --crypto    # crypto
.venv/bin/python regime.py                     # benchmark regime
.venv/bin/python funding.py HYPE               # funding + OI
.venv/bin/python check_levels.py               # level-watch sweep
.venv/bin/python defillama.py hyperliquid      # on-chain metrics
```

**Cron.** `cron_sweep.sh` runs the level sweep twice daily and writes
`../data/Reports/_meta/Level-Watch.md`:

```
17 8,20 * * * $HOME/Documents/projects/market-research/engine/cron_sweep.sh
```

## Data sources

Crypto OHLCV comes from the exchange (OKX -> Bybit -> Binance) so numbers match
the TradingView crypto charts the owner trades off. Stocks use Yahoo Finance. Validated
2026-06-11: exchange vs Yahoo agreed to <0.1% on BTC/ZEC/HYPE.

## History

Extracted from the owner's Obsidian vault as `investments-engine` on 2026-06-11 (code
only), then the whole system — spec, skills, and data — consolidated into this
repo on 2026-07-19. The vault no longer holds any investments files.
