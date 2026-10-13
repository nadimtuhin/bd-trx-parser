from decimal import Decimal

import pytest

from bd_trx_parser import Bank, TxnType, parse_balance, parse_sms
from tests.fixtures import sms


@pytest.mark.parametrize(
    ("text", "txn_type", "amount", "description", "closing_balance"),
    [
        (sms.DBBL_ATM_WITHDRAWAL, TxnType.DEBIT, "5000.00", "ATM Cash Withdrawal", "12345.67"),
        (sms.DBBL_POS_REMOTE_ON_US, TxnType.DEBIT, "850.00", "POS Purchase Remote On Us", "11495.67"),
        (sms.DBBL_POS, TxnType.DEBIT, "1200.50", "POS Purchase", "10295.17"),
        (sms.DBBL_CREDIT, TxnType.CREDIT, "100000.00", "Fund Transfer", "110295.17"),
        (sms.DBBL_CREDIT_NO_DESCRIPTION, TxnType.CREDIT, "1000.00", "Transfer", "2000.00"),
    ],
)
def test_dbbl(text, txn_type, amount, description, closing_balance):
    txn = parse_sms(text, "DBBL")
    assert txn.bank is Bank.DBBL
    assert txn.txn_type is txn_type
    assert txn.amount == Decimal(amount)
    assert txn.account == "***1234"
    assert txn.description == description

    balance = parse_balance(text, "DBBL")
    assert balance.account == "***1234"
    assert balance.balance == Decimal(closing_balance)
    assert balance.is_liability is False


def test_short_code_sender_is_recognised():
    assert parse_sms(sms.DBBL_POS, "16216").bank is Bank.DBBL
