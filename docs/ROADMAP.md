# Roadmap

Build order for the per-user pipeline (the user-side L1 → up the stack). Each step
binds to the canonical contract and adds nothing broker-aware above `parsers/`.

## Status
- [x] **Canonical contract** — `core/canonical.py`. Frozen-ish; change deliberately.
- [x] **Groww adapter** — `parsers/groww/adapter.py`. Reconciles exactly against a
      real file. Needs a proper test suite (see below) before it's production-trusted.
- [ ] **Test suite** — reconciliation tests per adapter against real anonymized
      fixtures; edge cases (multi-page export, non-equity ISIN, missing ISIN).
- [ ] **Enrichment** — join lots to shared-world facts by `entity_key`: sector,
      market-cap, market regime @ trade date, post-trade price path. Pure join; no
      recompute of market context per user. Depends on the shared world-model having
      price/sector data available.
- [ ] **Primitives** — deterministic functions computing per-lot / per-position /
      portfolio measurements once (holding days, price-vs-avg-cost, realized/
      unrealized split, concentration, turnover, regime-at-trade, etc.). Pure math.
- [ ] **Pattern rules** — declarative expressions over primitives, each emitting
      `{pattern, frequency, severity, confidence}`. Add a pattern = add a rule, not
      new code. (Disposition effect, averaging-down, panic-sell, FOMO-buy,
      long-hold, sunk-cost, house-money, etc.)
- [ ] **Synthesis** — collapse correlated flags into a few composite scores (risk
      posture, discipline, timing, bias load) + archetype clustering (classical ML).
- [ ] **Narration** — LLM turns the fact-set into language (consumes numbers,
      invents none). Last, once the numbers underneath are trustworthy.
- [ ] **Thesis seed** — each `OpenLot` becomes a thesis anchor in L4.

## Remaining broker adapters
- [ ] Zerodha (likely raw tradebook → must do FIFO matching ourselves)
- [ ] Angel One
- [ ] INDmoney

## Sequencing principle
Build the deterministic engine first and ship with templated insights. Add the LLM as
narration once the math is trustworthy. Reach for ML clustering only with enough users
to find archetypes worth naming. Inverting this order means debugging hallucinated
returns instead of building the product.
