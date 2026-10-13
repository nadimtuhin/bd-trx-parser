from decimal import Decimal

import pytest

from bd_trx_parser import Bank, TxnType, parse_balance, parse_sms
from tests.fixtures import sms


def ebl(text):
    return parse_sms(text, "EBL")


@pytest.mark.parametrize(
    ("text", "txn_type", "amount", "account", "description"),
    [
        (sms.EBL_SAVINGS_CREDIT_BEFTN, TxnType.CREDIT, "25000.00", "101***111", "BEFTN Inward from ACME TRADING LTD"),
        (sms.EBL_SAVINGS_DEBIT_NPSB, TxnType.DEBIT, "2000.00", "101***111", "NPSB Fund Transfer to 1234****5678"),
        (sms.EBL_SAVINGS_DEBIT_NO_DESCRIPTION, TxnType.DEBIT, "500", "202***222", "Transfer"),
        (sms.EBL_DEBIT_CARD_PURCHASE, TxnType.DEBIT, "6000.00", "101***111", "GREEN LEAF CAFE DHAKA"),
        (sms.EBL_DEBIT_CARD_PURCHASE_DOTTED_MERCHANT, TxnType.DEBIT, "1499", "422222**2222", "DARAZ.COM.BD"),
        (sms.EBL_CREDIT_CARD_BDT_PURCHASE, TxnType.DEBIT, "1250.50", "411111**1111", "SHOPNO SUPERSTORE"),
        (sms.EBL_CREDIT_CARD_LEGACY_LAYOUT, TxnType.DEBIT, "500.00", "411111**1111", "POS txn"),
        (sms.EBL_ATM_WITHDRAWAL, TxnType.DEBIT, "5000", "101***111", "ATM Cash WD (EBL GULSHAN BRANCH ATM)"),
    ],
)
def test_bdt_transactions(text, txn_type, amount, account, description):
    txn = ebl(text)
    assert txn.bank is Bank.EBL
    assert txn.txn_type is txn_type
    assert txn.amount == Decimal(amount)
    assert txn.currency == "BDT"
    assert txn.account == account
    assert txn.description == description


@pytest.mark.parametrize(
    ("text", "txn_type", "amount", "description"),
    [
        (sms.EBL_CREDIT_CARD_USD_PURCHASE, TxnType.DEBIT, "15.99", "NETFLIX.COM"),
        (sms.EBL_CREDIT_CARD_USD_PAYMENT, TxnType.CREDIT, "120.00", "Card payment (USD)"),
        (sms.EBL_CREDIT_CARD_USD_REVERSAL, TxnType.CREDIT, "15.99", "Reversal"),
    ],
)
def test_usd_credit_card_transactions(text, txn_type, amount, description):
    txn = ebl(text)
    assert txn.currency == "USD"
    assert txn.txn_type is txn_type
    assert txn.amount == Decimal(amount)
    assert txn.account == "411111**1111"
    assert txn.description == description


def test_otp_is_not_a_transaction():
    assert ebl(sms.EBL_OTP) is None
    assert parse_balance(sms.EBL_OTP, "EBL") is None


@pytest.mark.parametrize(
    ("text", "account", "balance"),
    [
        (sms.EBL_SAVINGS_CREDIT_BEFTN, "101***111", "102345.67"),
        (sms.EBL_SAVINGS_DEBIT_NPSB, "101***111", "98765.43"),
        (sms.EBL_DEBIT_CARD_PURCHASE, "101***111", "45000.00"),
        (sms.EBL_ATM_WITHDRAWAL, "101***111", "40000.00"),
    ],
)
def test_savings_balance(text, account, balance):
    result = parse_balance(text, "EBL")
    assert result.bank is Bank.EBL
    assert result.account == account
    assert result.balance == Decimal(balance)
    assert result.is_liability is False


def test_credit_card_balance_is_a_liability():
    result = parse_balance(sms.EBL_CREDIT_CARD_BDT_PURCHASE, "EBL")
    assert result.account == "411111**1111"
    assert result.balance == Decimal("14750.50")
    assert result.is_liability is True


def test_purchase_without_balance_line_has_no_balance():
    assert parse_balance(sms.EBL_DEBIT_CARD_PURCHASE_DOTTED_MERCHANT, "EBL") is None
