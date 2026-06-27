"""
angelone/adapter.py — NOT YET IMPLEMENTED.

Angel One exports vary by report type (P&L statement vs contract notes).
Confirm the exact export format before implementing.

Expected input: Angel One → Reports → P&L Statement
"""
from lib.types import PortfolioState


def parse(path: str) -> PortfolioState:
    raise NotImplementedError("Angel One adapter is not yet implemented.")
