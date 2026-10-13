import json
from datetime import date, datetime
from decimal import Decimal

import pytest

from bd_trx_parser import (
    Bank,
    TxnType,
    clean_text,
    detect_bank,
    parse_amount,
    parse_balance,
    parse_sms,
)
from bd_trx_parser.__main__ import main
from tests.fixtures import sms

# Every transaction fixture and the bank it belongs to; auto-detection must agree.
TRANSACTION_FIXTURES = [
    (Bank.EBL, sms.EBL_SAVINGS_CREDIT_BEFTN),
    (Bank.EBL, sms.EBL_SAVINGS_DEBIT_NPSB),
    (Bank.EBL, sms.EBL_DEBIT_CARD_PURCHASE),
    (Bank.EBL, sms.EBL_CREDIT_CARD_BDT_PURCHASE),
    (Bank.EBL, sms.EBL_CREDIT_CARD_USD_PURCHASE),
    (Bank.EBL, sms.EBL_CREDIT_CARD_USD_PAYMENT),
    (Bank.EBL, sms.EBL_CREDIT_CARD_USD_REVERSAL),
    (Bank.EBL, sms.EBL_ATM_WITHDRAWAL),
    (Bank.DBBL, sms.DBBL_ATM_WITHDRAWAL),
    (Bank.DBBL, sms.DBBL_CREDIT_NO_DESCRIPTION),
    (Bank.CITY_BANK, sms.CITY_WITHDRAWAL_LINES),
    (Bank.CITY_BANK, sms.CITY_PURCHASE_LINES_WITH_RATE),
    (Bank.CITY_BANK, sms.CITY_CREDITED_SENTENCE),
    (Bank.CITY_BANK, sms.CITY_DEBITED_SENTENCE),
    (Bank.CITY_AMEX, sms.AMEX_PURCHASE),
    (Bank.CITY_AMEX, sms.AMEX_PAYMENT_OF),
    (Bank.AIBL, sms.AIBL_DEBIT),
    (Bank.AIBL, sms.AIBL_TRANSFER_FROM),
    (Bank.BKASH, sms.BKASH_PAYMENT),
    (Bank.BKASH, sms.BKASH_CASH_IN),
    (Bank.BKASH, sms.BKASH_REMITTANCE),
    (Bank.BKASH, sms.BKASH_BILL),
    (Bank.MIDLAND, sms.MIDLAND_CARD_USE),
    (Bank.MIDLAND, sms.MIDLAND_PURCHASE_TXN),
    (Bank.MIDLAND, sms.MIDLAND_PAYMENT),
    (Bank.PATHAO_PAY, sms.PATHAO_PAID),
    (Bank.NAGAD, sms.NAGAD_MONEY_RECEIVED),
    (Bank.NAGAD, sms.NAGAD_CASH_IN),
    (Bank.NAGAD, sms.NAGAD_CASH_OUT),
]


@pytest.mark.parametrize(("bank", "text"), TRANSACTION_FIXTURES)
def test_auto_detects_bank_without_sender(bank, text):
    assert parse_sms(text).bank is bank


@pytest.mark.parametrize(
    ("bank", "text", "balance"),
    [
        (Bank.EBL, sms.EBL_DEBIT_CARD_PURCHASE, "45000.00"),
        (Bank.EBL, sms.EBL_CREDIT_CARD_BDT_PURCHASE, "14750.50"),
        (Bank.DBBL, sms.DBBL_POS, "10295.17"),
        (Bank.CITY_BANK, sms.CITY_WITHDRAWAL_LINES, "20345.50"),
        (Bank.CITY_AMEX, sms.AMEX_PURCHASE, "120000.00"),
        (Bank.AIBL, sms.AIBL_DEBIT, "45678.90"),
        (Bank.BKASH, sms.BKASH_PAYMENT, "1234.56"),
        (Bank.MIDLAND, sms.MIDLAND_CARD_USE, "23456.00"),
        (Bank.PATHAO_PAY, sms.PATHAO_PAID, "1062.00"),
        (Bank.NAGAD, sms.NAGAD_SEND_MONEY, "3828.17"),
    ],
)
def test_balance_auto_detects_bank_without_sender(bank, text, balance):
    result = parse_balance(text)
    assert result.bank is bank
    assert result.balance == Decimal(balance)


def test_unknown_sender_falls_back_to_auto_detection():
    assert parse_sms(sms.DBBL_POS, "SOMEBODY").bank is Bank.DBBL


def test_known_sender_restricts_to_that_bank():
    assert parse_sms(sms.BKASH_PAYMENT, "DBBL") is None


def test_bank_argument_overrides_sender():
    assert parse_sms(sms.NAGAD_CASH_OUT, "bKash", bank=Bank.NAGAD).bank is Bank.NAGAD


@pytest.mark.parametrize(
    ("sender", "bank"),
    [
        ("EBL", Bank.EBL),
        ("ebl-cards", Bank.EBL),
        ("16216", Bank.DBBL),
        ("City Bank", Bank.CITY_BANK),
        ("bKash", Bank.BKASH),
        ("NAGAD", Bank.NAGAD),
        ("Pathao Pay", Bank.PATHAO_PAY),
        ("random", None),
    ],
)
def test_detect_bank(sender, bank):
    assert detect_bank(sender) is bank


@pytest.mark.parametrize("text", ["", "Hello, how are you?", sms.EBL_OTP, sms.NAGAD_OTP, sms.BKASH_PROMO])
def test_non_transactions_return_none(text):
    assert parse_sms(text) is None


@pytest.mark.parametrize(
    "when", [date(2026, 10, 12), datetime(2026, 10, 12, 23, 59), "2026-10-12", "2026-10-12T23:59:00+06:00"]
)
def test_date_inputs_are_normalised(when):
    assert parse_sms(sms.EBL_SAVINGS_CREDIT_BEFTN, date=when).date == date(2026, 10, 12)


def test_bad_date_type_raises():
    with pytest.raises(TypeError):
        parse_sms(sms.EBL_SAVINGS_CREDIT_BEFTN, date=20261012)


def test_hash_matches_reference_formula():
    # sha256("2026-10-12|EBL|25000.00|CR")[:16], computed outside Python
    txn = parse_sms(sms.EBL_SAVINGS_CREDIT_BEFTN, date="2026-10-12")
    assert txn.hash == "6dc90d2595f01b11"


def test_hash_ignores_description_so_duplicates_collapse():
    a = parse_sms(sms.DBBL_POS, date="2026-10-13")
    b = parse_sms(sms.DBBL_POS.replace("POS Purchase", "Something else"), date="2026-10-13")
    assert a.description != b.description
    assert a.hash == b.hash


def test_garbled_carrier_bytes_are_cleaned():
    noisy = "﻿\x00" + sms.BKASH_PAYMENT.replace("Tk 300", "Tk� 300") + "\x00"
    txn = parse_sms(noisy)
    assert txn.amount == Decimal("300.00")


def test_clean_text_keeps_line_breaks():
    assert clean_text("a\r\n b \x07\nc�") == "a\nb\nc"


@pytest.mark.parametrize(
    ("raw", "expected"),
    [("5000", "5000"), ("1,000.00", "1000.00"), ("1,00,000.50", "100000.50"), ("12.", "12")],
)
def test_parse_amount(raw, expected):
    assert parse_amount(raw) == Decimal(expected)


def test_parse_amount_rejects_garbage():
    with pytest.raises(ValueError):
        parse_amount("abc")


def test_to_dict_is_json_serialisable():
    txn = parse_sms(sms.BKASH_PAYMENT, date="2026-10-12")
    data = json.loads(json.dumps(txn.to_dict()))
    assert data["bank"] == "bKash"
    assert data["txn_type"] == TxnType.DEBIT.value
    assert data["amount"] == "300.00"
    assert data["date"] == "2026-10-12"


def test_cli_prints_transaction_and_balance(capsys):
    exit_code = main([sms.DBBL_ATM_WITHDRAWAL, "--sender", "DBBL", "--date", "2026-10-12"])
    out = json.loads(capsys.readouterr().out)
    assert exit_code == 0
    assert out["transaction"]["amount"] == "5000.00"
    assert out["transaction"]["date"] == "2026-10-12"
    assert out["balance"]["balance"] == "12345.67"


def test_cli_reads_stdin(monkeypatch, capsys):
    monkeypatch.setattr("sys.stdin", __import__("io").StringIO(sms.NAGAD_CASH_IN))
    assert main([]) == 0
    assert json.loads(capsys.readouterr().out)["transaction"]["bank"] == "Nagad"


def test_cli_exits_1_on_unparseable_sms(capsys):
    assert main(["hello"]) == 1
    assert json.loads(capsys.readouterr().out) == {"transaction": None, "balance": None}
