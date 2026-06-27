"""
zerodha/adapter.py — NOT YET IMPLEMENTED.

Zerodha exports a raw tradebook (not pre-matched lots), so this adapter will need
to perform FIFO buy-sell matching before emitting MatchedLot objects.

Expected input: Zerodha Console → P&L → Tradebook CSV/XLSX
"""
from lib.types import PortfolioState


def parse(path: str) -> PortfolioState:
    raise NotImplementedError("Zerodha adapter is not yet implemented.")
