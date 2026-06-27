# Parsers — Adapter Contract

This package is the **only** place in the system that knows broker file formats.
Rules for anything under `parsers/`:

## Hard rules
1. **Emit ONLY canonical objects** (`from fintel.core.canonical import ...`). No
   broker-shaped dict, tuple, or string crosses the boundary upward.
2. **Normalize to `Execution` atoms.** Brokers differ: Groww gives pre-matched lots,
   Zerodha gives raw orders. Both must produce the same `Execution` / `MatchedLot` /
   `OpenLot` shapes so downstream logic is broker-blind.
3. **Reconciliation is a gate, not a log line.** Sum extracted P&L and compare to the
   broker's own stated Summary totals. Mismatch beyond tolerance → set the
   `Reconciliation` failure + notes; do NOT pretend success.
4. **`entity_key` from ISIN at parse time.** Missing ISIN → `NAME::<symbol>` fallback
   + route to review; never guess a mapping.
5. **Money through `D()` / `money()`** — never raw `float`.
6. **Dates** parse explicitly (Groww is `DD-MM-YYYY` strings, not Excel dates).
7. **PII**: capture account identifiers only as a hash (`account_ref`); never log or
   commit investor names / client codes.

## The pattern (sectioned reports)
Broker P&L exports are usually **sectioned reports, not flat tables** — parse them as
a **section state machine**, not `read_excel`. Track which section you're in
(Summary → Charges → Realised → Unrealised → Disclaimer); each section has its own
header row and column layout. See `groww/adapter.py` as the reference implementation.

## Intraday vs delivery
Prefer the broker's explicit flag (Groww `Remark == "Intraday trade"`); fall back to
same-day buy==sell. This split matters: intraday = trading behavior, delivery =
investing behavior, and they feed different pattern rules.

## Every adapter ships with a test
A reconciliation test in `tests/parsers/test_<broker>.py` against a real, anonymized
export in `tests/fixtures/<broker>/`. An adapter without a passing reconciliation
test on a real file is not done.

## Known per-broker notes
- **Groww**: two sheets — `Trade Level` (source of truth, lot-level) and `Scrip
  Level` (derived aggregate → cross-check only). Open lots carry buy dates. ISIN on
  every row. `INF…` ISINs are funds/ETFs.
- **Zerodha / Angel One / INDmoney**: not yet built. Expect raw tradebooks (do FIFO
  matching ourselves) rather than pre-matched lots.
