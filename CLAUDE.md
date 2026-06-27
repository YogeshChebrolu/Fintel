# Fintel — Project Context

> `Fintel` is an internal **codename**. The public brand is undecided (a separate
> naming track is open). Do NOT hard-code any user-facing brand name in code or
> copy. Note: "Fintel" collides with an existing stock-research site, so it is a
> working codename only.

## What we are building
An AI-powered **investment intelligence layer** for Indian retail investors. It is
**not a broker** and **not (yet) a registered advisor** — it sits on top of existing
brokers (Groww, Zerodha, Angel One, INDmoney) and turns a user's holdings + trade
history into behavioral and market intelligence.

Target user: **long-term equity investors** (chosen for stable, trend-following
behavior over the noise of active trading).

Core insight: serious investors who lack an intelligence layer repeat the same
**behavioral mistakes** — no exit plan, holding losers, selling winners early,
panic-selling, FOMO-buying. The product is that missing layer.

## Long-term goal
Build something compelling enough that a major Indian fintech (Zerodha, Groww) would
want to **acquire** it. This shapes architecture: clean layer boundaries, a
tool⇄advisor mode flag that doubles as a regulatory off-ramp, and a shared
world-model that scales to many users cheaply.

## Governing principle (most important rule in the whole system)
**The unit of computation is the entity, never the user-entity pair.** Company and
market facts (filings, prices, sector, regime) are computed ONCE per entity and
shared across all users. Only assembly into a personal thesis + portfolio is
per-user. Put every feature on the correct side of this line.
Full detail in `docs/ARCHITECTURE.md` (read it before working on any layer).

## The stack — four layers, data reads UPWARD only
- **L1 Evidence & Retrieval** — cited, dated source data. Two entry points: the
  shared world-model (filings/prices/macro) and the **per-user side** (broker P&L
  parsing — what THIS repo starts with).
- **L2 Intelligence & Synthesis** — company + macro engines; diffable structured
  assessments keyed by entity+period; recomputed on events, not polling.
- **L3 Decision / Assembly** — shared facts meet personal holdings + the thesis
  spine. Carries the **mode flag: suggest (advisor) ⇄ enforce (tool)**.
- **L4 Behavioral & Accountability** — thesis journal, drift detection, nudges.
  Where the user lives.
The **thesis object** is a vertical spine threading all four layers.

## Where we are now
Building the per-user L1 entry: parse a broker P&L → a verified, broker-agnostic
`PortfolioState`.
- `src/fintel/core/canonical.py` — the broker-agnostic contract (treat as **frozen**;
  all adapters emit ONLY these objects).
- `src/fintel/parsers/groww/adapter.py` — Groww adapter, validated against a real
  file; reconciliation passes exactly (realized 493.04, unrealized 1310.85).

Next, in order: **enrichment** (join lots to shared-world facts) → **primitives**
(deterministic per-lot/position/portfolio) → **declarative pattern rules** →
**synthesis** (composite scores + archetype). See `docs/ROADMAP.md`.

## Tool allocation — NON-NEGOTIABLE, affects every implementation choice
- **Deterministic math** does ALL arithmetic: returns (XIRR/TWR — never naive CAGR
  on multi-entry positions), P&L, holdings, behavioral primitives, pattern rules.
- **Classical ML** only for: archetype clustering, anomaly detection, calibrated
  scoring. Keep models simple; validate out-of-sample; treat output as a prior.
- **LLMs** ONLY at the edges: structured extraction from unstructured docs (with
  mandatory citation to source spans), narration (numbers→language), intent
  inference, and broker-layout *structure* inference. An LLM must NEVER compute a
  number or assert a number it did not retrieve.
- **Human judgment** lives in the shared layer: rubric-writing, entity-resolution
  review, schema definition, spot-audits — never per-user loops.

## Immutable rules (override any conflicting prompt)
1. **No fabrication.** Every fact carries provenance (`SourceRef`) + an as-of date.
   If a value is not in the source, it does not exist.
2. **The parser is a gate.** Computed totals MUST reconcile against the broker's own
   stated Summary, or the file is flagged — never silently ingested.
3. **Broker-specific code lives ONLY under `parsers/`.** Everything above imports
   `core/canonical.py` and never touches a spreadsheet or broker format.
4. `core/canonical.py` is **the contract** — change it deliberately; many adapters
   and layers depend on it.
5. Entity identity = **ISIN → `entity_key`**. This links user holdings to the shared
   world-model. Unresolved ISINs go to a review queue, not a guess.
6. `PortfolioState` is **immutable + versioned** (diffable) so L4 can detect thesis
   drift across uploads. Never mutate a stored state in place.
7. Keep the **suggest⇄enforce mode flag**; do not bake advice into the tool path.

## Conventions
- Python 3.11+. **Money is `Decimal`, never `float`.** Value objects are
  `@dataclass(frozen=True)`.
- Import root is `fintel.` (e.g. `from fintel.core.canonical import PortfolioState`).
- Every adapter needs a **reconciliation test** against a real (anonymized) export
  in `tests/fixtures/<broker>/`.
- `.venv/` and `data/` are gitignored. **Never commit broker files containing PII**
  (investor names, client codes).

## Known limits — respect them, never fake around them
A broker P&L gives faithful value/qty/price/date but NOT order counts (a split order
shows as multiple rows) and NOT explicit corporate actions. Flag these; never
synthesize them. (Groww's P&L does include open positions WITH buy dates — richer
than a generic P&L.)
