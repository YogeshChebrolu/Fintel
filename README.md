# Fintel (codename)

An investment intelligence layer for Indian retail investors — sits on top of
existing brokers and turns holdings + trade history into behavioral and market
intelligence. Not a broker; not (yet) a registered advisor.

- **Start here:** `CLAUDE.md` (project constitution) and `docs/ARCHITECTURE.md`.
- **The contract:** `src/fintel/core/canonical.py` + `docs/CANONICAL_CONTRACT.md`.
- **Build order / status:** `docs/ROADMAP.md`.

## Layout
```
src/fintel/
  core/        broker-agnostic contract (canonical.py) — the spine
  parsers/     the ONLY broker-aware code (groww/ done; others stubbed)
  enrichment/  join lots to shared-world facts        (next)
  primitives/  deterministic per-lot/position/portfolio (next)
  patterns/    declarative rules over primitives        (next)
  storage/     PortfolioState versioning, file-hash dedup
tests/         reconciliation tests + real fixtures
docs/          architecture, contract, roadmap
```

## Dev setup
```bash
python -m venv .venv
.venv\Scripts\activate            # Windows
pip install -e ".[dev]"
pytest
```
