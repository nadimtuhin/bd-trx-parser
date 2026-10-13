from decimal import Decimal

import pytest

from bd_trx_parser import Bank, TxnType, parse_balance, parse_sms
from tests.fixtures import sms


def test_debit_with_reference():
    txn = parse_sms(sms.AIBL_DEBIT, "AIBL")
    assert txn.bank is Bank.AIBL
    assert txn.txn_type is TxnType.DEBIT
    assert txn.amount == Decimal("2750.00")
    assert txn.account == "100200****300"
    assert txn.reference == "FT26285ABCD"
    assert txn.description == "Ref: FT26285ABCD"


def test_short_credit_without_reference():
    txn = parse_sms(sms.AIBL_CREDIT_SHORT, "AIBL")
    assert txn.txn_type is TxnType.CREDIT
    assert txn.amount == Decimal("10000.00")
    assert txn.description == "Transfer"
    assert txn.reference is None


@pytest.mark.parametrize(
    ("text", "txn_type", "amount"),
    [
        (sms.AIBL_TRANSFER_FROM, TxnType.DEBIT, "5000"),
        (sms.AIBL_TRANSFER_TO, TxnType.CREDIT, "1500.00"),
    ],
)
def test_transfers_in_both_spellings(text, txn_type, amount):
    txn = parse_sms(text, "AIBL")
    assert txn.txn_type is txn_type
    assert txn.amount == Decimal(amount)
    assert txn.account == "100200****300"


@pytest.mark.parametrize(
    ("text", "balance"),
    [(sms.AIBL_DEBIT, "45678.90"), (sms.AIBL_CREDIT_SHORT, "55678.90")],
)
def test_balance_with_and_without_currency(text, balance):
    result = parse_balance(text, "AIBL")
    assert result.account == "100200****300"
    assert result.balance == Decimal(balance)
