from decimal import Decimal

import pytest

from bd_trx_parser import Bank, TxnType, parse_balance, parse_sms
from tests.fixtures import sms


@pytest.mark.parametrize(
    ("text", "txn_type", "amount", "description"),
    [
        (sms.AMEX_PURCHASE, TxnType.DEBIT, "3634.00", "RANG BANGLADESH LTD JAMUNA FUT"),
        (sms.AMEX_PURCHASE_BDT_ONE_LINE, TxnType.DEBIT, "2000.00", "UNIMART GULSHAN"),
        (sms.AMEX_PAYMENT_RECEIVED, TxnType.CREDIT, "28260.00", "Card payment"),
        (sms.AMEX_PAYMENT_OF, TxnType.CREDIT, "28260.00", "Card payment"),
    ],
)
def test_city_amex(text, txn_type, amount, description):
    txn = parse_sms(text, "AMEX")
    assert txn.bank is Bank.CITY_AMEX
    assert txn.txn_type is txn_type
    assert txn.amount == Decimal(amount)
    assert txn.account == "371***999"
    assert txn.description == description


@pytest.mark.parametrize(
    ("text", "balance"),
    [(sms.AMEX_PURCHASE, "120000.00"), (sms.AMEX_PURCHASE_BDT_ONE_LINE, "98000.00")],
)
def test_amex_balance_is_a_liability(text, balance):
    result = parse_balance(text, "AMEX")
    assert result.account == "371***999"
    assert result.balance == Decimal(balance)
    assert result.is_liability is True


def test_payment_alert_has_no_balance():
    assert parse_balance(sms.AMEX_PAYMENT_RECEIVED, "AMEX") is None
