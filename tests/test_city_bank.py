from decimal import Decimal

import pytest

from bd_trx_parser import Bank, TxnType, parse_balance, parse_sms
from tests.fixtures import sms


@pytest.mark.parametrize(
    ("text", "txn_type", "amount", "description"),
    [
        (sms.CITY_WITHDRAWAL_LINES, TxnType.DEBIT, "5000.00", "Citytouch Fund Transfer"),
        (sms.CITY_DEPOSIT_LINES, TxnType.CREDIT, "80000.00", "Salary ACME LTD"),
        (sms.CITY_PURCHASE_LINES_WITH_RATE, TxnType.DEBIT, "1225.00", "AMAZON WEB SERVICES"),
        (sms.CITY_CREDITED_SENTENCE, TxnType.CREDIT, "2500.00", "Citytouch transfer from 1781***2210"),
        (sms.CITY_DEBITED_SENTENCE, TxnType.DEBIT, "1000.00", "bKash transfer"),
    ],
)
def test_city_bank(text, txn_type, amount, description):
    txn = parse_sms(text, "CityBank")
    assert txn.bank is Bank.CITY_BANK
    assert txn.txn_type is txn_type
    assert txn.amount == Decimal(amount)
    assert txn.account == "9900***0042"
    assert txn.description == description


@pytest.mark.parametrize(
    ("text", "balance"),
    [
        (sms.CITY_WITHDRAWAL_LINES, "20345.50"),
        (sms.CITY_DEPOSIT_LINES, "100345.50"),
    ],
)
def test_city_bank_balance(text, balance):
    result = parse_balance(text, "CityBank")
    assert result.account == "9900***0042"
    assert result.balance == Decimal(balance)
