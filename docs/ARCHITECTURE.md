# Architecture

Deep reference for the intelligence stack. `CLAUDE.md` is the lean always-loaded
summary; read this when working on any specific layer.

## The one line that organizes everything

**Shared world-model vs per-user assembly.** A company's annual report is the same
for everyone. Reliance's Q2 guidance is one number for everyone. A five-year revenue
CAGR is identical for everyone. All of that is a *shared world-model* — computed
once, stored keyed by entity, read by every user. Only the thin top slice (those
shared facts selected, ranked, and framed against one user's thesis, holdings, and
risk) is per-user, and it is cheap assembly.

> **The unit of computation is the entity-fact, never the user-view.**

Place that line correctly and "don't recompute per user" is solved by construction.
L1 and nearly all of L2 sit *below* the line — they are world, not user.

## Layer diagram (data reads UPWARD, one-way)

```
┌──────────────────────────────────────────────────────────────┐
│ L4 · BEHAVIORAL / ACCOUNTABILITY   (the payload)               │ ← user lives here
│   thesis journal · drift alerts · plan-vs-reality · nudges     │
├──────────────────────────────────────────────────────────────┤
│ L3 · DECISION / ASSEMBLY                          mode: suggest⇄enforce
│   sizing · entry/exit/average · diversification · hedging      │
├──────────────────────────────────────────────────────────────┤
│ L2 · INTELLIGENCE / SYNTHESIS   (two engines, run in parallel) │
│   [ company intel ]            [ macro / industry intel ]      │
├──────────────────────────────────────────────────────────────┤
│ L1 · EVIDENCE & RETRIEVAL   (the launchpad + fuel)             │
│   shared world: filings · calls · prices · macro (all cited)   │
│   per-user:     broker P&L / holdings parsing  ← THIS REPO     │
└──────────────────────────────────────────────────────────────┘
   ║ THESIS = vertical spine through all four layers
   ║ EVENT BUS = updates propagate async, recompute incrementally
```

Each layer is shaped by what the layer above needs to bolt onto it — design every
component knowing its consumer.

## L1 · Evidence & Retrieval

A pipeline, not a database: **ingest → normalize → resolve entities → store → serve.**
The design rule that makes "no fabrication" structural rather than a hope: **nothing
enters the stack as a bare string.** Every fact is an object — value + source + as-of
date + confidence + trust-tier. Store citations at ingestion, not retrofitted later.

### Shared world-model sources (by trust tier + cadence)
- **Primary structural** (tier 1, semi-structured): NSE/BSE filings, SEBI
  disclosures, MCA21 XBRL financials, annual reports, corporate actions, shareholding
  patterns, DRHP/RHP. The bedrock; everything else is verified against these.
- **Management communication** (high value, unstructured): earnings-call transcripts,
  investor presentations, guidance, MD&A. Where "guidance meets/misses" lives.
- **Market & pricing** (structured, high-frequency): corporate-action-adjusted OHLCV,
  index membership. Derivatives parked for the hedging module.
- **Macro & industry** (structured time-series + reports): RBI (rates/policy), MOSPI
  (GDP/IIP/CPI), global rates/commodities/FX, sector volumes.
- **Reference master data**: security master, sector classification, ISIN↔entity map.
- **Ownership & flows** (periodic): FII/DII flows, MF holdings, bulk/block deals,
  insider/SAST. Conviction signals for long holders.
- **News & sentiment** (noisy, low trust): treat every item as a *lead to verify
  against a filing*, never as a fact. Non-negotiable, or the stack launders rumor.

Two attributes ride on every source: a **trust tier** (filings outrank news) and a
**refresh cadence** (filings event-driven, prices intraday/EOD, macro monthly). The
cadence drives the event bus.

### Per-user L1 (this repo's starting point)
Parse a broker P&L / holdings file → a verified, broker-agnostic `PortfolioState`.
Same discipline as the shared side: typed objects, provenance, as-of dates, and a
reconciliation gate. ISIN resolves the user's holdings to the same `entity_key` the
shared world-model uses — that is the bolt joining personal data to shared facts.
Contract + parser detail: `docs/CANONICAL_CONTRACT.md`.

## L2 · Intelligence & Synthesis

Company and macro synthesis run in parallel, each on its own clock. Outputs are
**diffable structured state objects keyed by (entity, period)** — not prose — so L4
can detect when a user's thesis has drifted from the facts.
- **Company engine**: fundamentals time series, guidance tracking, competitive
  position, quality/risk scores, narrative synthesis.
- **Macro/industry engine**: regime indicators, sector-cycle position, cross-asset
  context.
Recomputed on events (a new filing recomputes that entity, not the universe), never
by polling or per-request.

## L3 · Decision / Assembly

Where shared facts meet individual holdings and the thesis spine. This is the only
per-user compute, and it is cheap: select, rank, and frame already-computed shared
facts against one user's portfolio. Carries the **mode flag**: the bottom of the
stack is pure tool (objective, cited facts); only here do we choose between "suggest
a level" (advisor posture) and "enforce the level the user set" (tool posture). Same
plumbing, one switch — which is also the regulatory off-ramp.

## L4 · Behavioral & Accountability

The product surface. Thesis journal (the reasoning at entry), drift alerts (the
reason you bought is no longer true), plan-vs-reality tracking, behavioral nudges.
Feedback scores **process quality** (did the user follow their plan, was the thesis
sound given what was knowable) — NEVER realized outcome, because in investing the
noise dwarfs the signal and outcome-learning overfits to luck.

## Not recomputing for multiple users — the mechanisms
1. Key everything by **entity, not user**.
2. **Hash documents** at ingestion; never parse the same doc twice. Cache extraction
   by (doc-version + model + prompt) so the same LLM call never re-runs.
3. Recompute **incrementally + event-driven**: one filing → one entity; one macro
   print → the regime once, shared.
4. Layer caches by **volatility** (prices short-TTL, fundamentals on-new-filing,
   macro monthly), with as-of date first-class so stale never masquerades as fresh.
5. Keep the user request path to **assembly only** — no heavy compute on it.

Corollary: upgrade the extraction model → backfill the shared store once → every user
inherits the improvement.

## The two interface contracts that matter most
Pin these down; the insides of each box can change freely behind them.
- **Evidence object** (L1 → L2): the typed shared-world fact with provenance.
- **Assessment / company-state object** (L2 → L3): the diffable structured assessment.
On the per-user side, the equivalent contract is **`PortfolioState`** (parser → L3/L4),
defined in `core/canonical.py`.
