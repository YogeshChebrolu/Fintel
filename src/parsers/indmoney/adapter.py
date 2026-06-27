"""
indmoney/adapter.py — NOT YET IMPLEMENTED.

INDmoney aggregates across multiple brokers; the export format and field
availability (especially buy dates for open lots) needs verification.

Expected input: INDmoney → Portfolio → Export
"""
from lib.types import PortfolioState


def parse(path: str) -> PortfolioState:
    raise NotImplementedError("INDmoney adapter is not yet implemented.")
