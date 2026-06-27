"""Reconciliation tests for the Groww adapter, run against a real (anonymized) export.
An adapter is not 'done' until its computed totals tie to the broker's own Summary."""
from decimal import Decimal
from pathlib import Path

import pytest

from fintel.parsers.groww.adapter import parse
from fintel.core.canonical import AssetClass, Segment

FIXTURE = Path(__file__).parent.parent / "fixtures" / "groww" / "sample_pnl.xlsx"


@pytest.fixture(scope="module")
def state():
    return parse(str(FIXTURE))


def test_reconciliation_passes(state):
    assert state.reconciliation.passed, state.reconciliation.notes


def test_realized_ties_to_summary(state):
    r = state.reconciliation
    assert r.realized_stated == r.realized_computed == Decimal("493.04")


def test_unrealized_ties_to_summary(state):
    r = state.reconciliation
    assert r.unrealized_stated == r.unrealized_computed == Decimal("1310.85")


def test_lot_and_instrument_counts(state):
    assert len(state.matched_lots) == 44
    assert len(state.open_lots) == 29
    assert len(state.instruments()) == 30


def test_charges_total(state):
    assert state.charges.total == Decimal("1188.86")


def test_every_fact_has_provenance(state):
    for lot in state.matched_lots:
        assert lot.source.broker == "GROWW"
        assert lot.source.file_hash and lot.source.row > 0
    for lot in state.open_lots:
        assert lot.source.file_hash


def test_entity_key_is_isin(state):
    for inst in state.instruments().values():
        if inst.isin:
            assert inst.entity_key == inst.isin


def test_segment_and_asset_class(state):
    intraday = sum(1 for l in state.matched_lots if l.segment == Segment.INTRADAY)
    assert intraday == 18
    funds = sum(1 for i in state.instruments().values()
                if i.asset_class == AssetClass.FUND)
    assert funds == 2
