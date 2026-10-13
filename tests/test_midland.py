from decimal import Decimal

import pytest

from bd_trx_parser import Bank, TxnType, parse_balance, parse_sms
from tests.fixtures import sms


@pytest.mark.parametrize(
    ("text", "txn_type", "amount", "description"),
    [
        (sms.MIDLAND_CARD_USE, TxnType.DEBIT, "1050.00", "APON FAMILY MART"),
        (sms.MIDLAND_PURCHASE_TXN, TxnType.DEBIT, "2300.00", "DARAZ BD"),
        (sms.MIDLAND_PAYMENT, TxnType.CREDIT, "3000.00", "Card payment"),
    ],
)
def test_midland(text, txn_type, amount, description):
    txn = parse_sms(text, "MDB")
    assert txn.bank is Bank.MIDLAND
    assert txn.txn_type is txn_type
    assert txn.amount == Decimal(amount)
    assert txn.account == "455555*5555"
    assert txn.description == description


def test_bill_statement_is_a_balance_not_a_transaction():
    assert parse_sms(sms.MIDLAND_BILL, "MDB") is None
    result = parse_balance(sms.MIDLAND_BILL, "MDB")
    assert result.balance == Decimal("12345.00")
    assert result.account == "455555*5555"
    assert result.is_liability is True


def test_card_use_balance():
    result = parse_balance(sms.MIDLAND_CARD_USE, "MDB")
    assert result.balance == Decimal("23456.00")
    assert result.is_liability is True
