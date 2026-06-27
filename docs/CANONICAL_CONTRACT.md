# Canonical Contract

`src/fintel/core/canonical.py` is the broker-agnostic interface every parser and every
layer above binds to. This doc explains the *why* behind it. **Change the schema
deliberately** — adapters and downstream layers depend on it.

## The objects
- **`SourceRef`** — provenance stamped on every fact: broker, file_hash, sheet, row,
  as_of date. Lets the UI answer "why this number" with a link, and makes
  reconciliation auditable.
- **`Instrument`** — `isin` (primary identity), `broker_symbol` (raw name),
  `asset_class` (from ISIN prefix: `INE…`=EQUITY, `INF…`=FUND), and `entity_key`
  (== ISIN until resolved to the shared world-model key).
- **`Execution`** — the canonical atom: one buy or sell of one instrument. Brokers
  that give raw orders (Zerodha) and brokers that give pre-matched lots (Groww) both
  normalize to this.
- **`MatchedLot`** — a closed/realized position: a buy leg matched to a sell leg
  (broker FIFO), with realized P&L and holding days.
- **`OpenLot`** — an open/unrealized position lot, **acquisition date preserved**.
- **`Charges`** — the full cost block (STT, brokerage, DP, GST, stamp, SEBI,
  exchange, IPFT, total). Needed for net-of-cost returns.
- **`Reconciliation`** — the gate result (see below).
- **`PortfolioState`** — the top-level per-user object. The ONLY thing layers above
  the parser read. Immutable + versioned so L4 can diff across uploads.

## Invariants (enforce in code + tests)
1. **Money is `Decimal`.** Never `float`. Route external numbers through `D()` /
   `money()` so float binary-noise (e.g. `-277.2999999999`) never enters.
2. **Every derived fact carries a `SourceRef`.** No bare values.
3. **`entity_key` is set at parse time** from ISIN. Unresolved → review queue, never
   a guess.
4. **`PortfolioState` is never mutated in place.** A new upload yields a new version;
   L4 diffs versions to detect thesis drift.
5. **No broker-shaped data leaks above `parsers/`.** If a field only makes sense for
   one broker, it does not belong in the canonical schema — adapt it away.

## The reconciliation gate (the trust mechanism)
Every adapter sums what it extracted and compares to the broker's own stated Summary
totals. **Match → ingest. Mismatch beyond tolerance → flag, do not store.** This is
what lets the pipeline run unattended without eyeballing every file. For Groww the
anchors are the Summary block's Realised P&L and Unrealised P&L; the `Scrip Level`
sheet is a second independent cross-check (it is fully derivable from `Trade Level`,
so it is a *check*, not a source).

Validated example (the bundled fixture): realized 493.04 == 493.04, unrealized
1310.85 == 1310.85, charges total 1188.86 — 44 closed lots, 29 open lots, 30
instruments.

## Entity resolution
ISIN is globally unique and stable, so it collapses entity resolution to a direct key
lookup — no fuzzy ticker matching. `entity_key = ISIN` initially; a later mapping step
binds it to the canonical company entity in the shared world-model. Keep a fallback
(`NAME::<symbol>`) only for instruments missing an ISIN, and route those to review.

## What the parser extracts (and what it cannot)
**Faithful from a P&L:** per-lot quantity, price, buy/sell dates, gross value,
realized/unrealized P&L, intraday vs delivery (Groww `Remark` or same-day round
trip), charges, the reporting period, holding days for both closed AND open lots.

**NOT recoverable from a P&L — flag, never synthesize:**
- **Order counts** — a single order split across fills/sales shows as multiple rows,
  so "number of trades" is unreliable. Needs the tradebook.
- **Corporate actions** — prices are pre-adjusted; you cannot see a split happened.
- **Intra-position history** that was fully exited and rebought.

Groww's P&L is richer than a generic one: it includes open positions with per-lot buy
dates, so holding-period / averaging / long-hold analysis works without a separate
holdings statement.

## Adding a new broker adapter (Zerodha, Angel One, INDmoney)
1. Read `src/fintel/parsers/CLAUDE.md` (the adapter contract).
2. Implement the parse function in `parsers/<broker>/adapter.py`; emit ONLY canonical
   objects.
3. Normalize the broker's format to `Execution` atoms (+ `MatchedLot` / `OpenLot`).
4. Implement the reconciliation gate against that broker's own stated totals.
5. Add a real (anonymized) export to `tests/fixtures/<broker>/` and a reconciliation
   test in `tests/parsers/test_<broker>.py`.
