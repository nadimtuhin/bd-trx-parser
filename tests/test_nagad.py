from decimal import Decimal

import pytest

from bd_trx_parser import WALLET, Bank, TxnType, parse_balance, parse_sms
from tests.fixtures import sms


@pytest.mark.parametrize(
    ("text", "txn_type", "amount", "description", "reference", "balance"),
    [
        (sms.NAGAD_MONEY_RECEIVED, TxnType.CREDIT, "1500.00", "Money Received from 01712****99", "73ABCD12", "2345.67"),
        (sms.NAGAD_CASH_IN, TxnType.CREDIT, "3000.00", "Cash In from 01812****88", "73EFGH34", "5345.67"),
        (sms.NAGAD_CASH_OUT, TxnType.DEBIT, "1000.00", "Cash Out to 01912****77", "73IJKL56", "4333.17"),
        (sms.NAGAD_SEND_MONEY, TxnType.DEBIT, "500.00", "Send Money to 01612****66", "73MNOP78", "3828.17"),
    ],
)
def test_nagad(text, txn_type, amount, description, reference, balance):
    txn = parse_sms(text, "NAGAD")
    assert txn.bank is Bank.NAGAD
    assert txn.account == WALLET
    assert txn.txn_type is txn_type
    assert txn.amount == Decimal(amount)
    assert txn.description == description
    assert txn.reference == reference

    assert parse_balance(text, "NAGAD").balance == Decimal(balance)


def test_otp_is_ignored():
    assert parse_sms(sms.NAGAD_OTP, "NAGAD") is None
    assert parse_balance(sms.NAGAD_OTP, "NAGAD") is None
