from decimal import Decimal

import pytest

from bd_trx_parser import WALLET, Bank, TxnType, parse_balance, parse_sms
from tests.fixtures import sms


@pytest.mark.parametrize(
    ("text", "amount", "description", "reference", "balance"),
    [
        (sms.PATHAO_PAID, "938.00", "Paid to Pathao Food", "PP12345678", "1062.00"),
        (sms.PATHAO_PAID_ONE_LINE, "120.00", "Paid to Pathao Parcel", None, "942.00"),
    ],
)
def test_pathao_pay(text, amount, description, reference, balance):
    txn = parse_sms(text, "PathaoPay")
    assert txn.bank is Bank.PATHAO_PAY
    assert txn.txn_type is TxnType.DEBIT
    assert txn.account == WALLET
    assert txn.amount == Decimal(amount)
    assert txn.description == description
    assert txn.reference == reference

    assert parse_balance(text, "PathaoPay").balance == Decimal(balance)
