from decimal import Decimal

import pytest

from bd_trx_parser import WALLET, Bank, TxnType, parse_balance, parse_sms
from tests.fixtures import sms


@pytest.mark.parametrize(
    ("text", "txn_type", "amount", "description", "reference"),
    [
        (sms.BKASH_PAYMENT, TxnType.DEBIT, "300.00", "Payment to SHOPNO", "AB12CD34EF"),
        (sms.BKASH_PAYMENT_OF_IS, TxnType.DEBIT, "50.00", "Payment to Grameenphone Ltd-MyGP", "GH56IJ78KL"),
        (sms.BKASH_SEND_MONEY, TxnType.DEBIT, "500.00", "Send Money to 01912****77", "MN90OP12QR"),
        (sms.BKASH_CASH_OUT, TxnType.DEBIT, "1000.00", "Cash Out to 01712****99", "ST34UV56WX"),
        (sms.BKASH_CASH_IN, TxnType.CREDIT, "2000.00", "Cash In from 01812****88", "YZ78AB90CD"),
        (sms.BKASH_RECEIVED, TxnType.CREDIT, "10000.00", "Received from 01800****02", "EF12GH34IJ"),
        (sms.BKASH_REMITTANCE, TxnType.CREDIT, "36597.11", "Remittance received", "KL56MN78OP"),
        (sms.BKASH_GOVT_INCENTIVE, TxnType.CREDIT, "914.93", "Govt. incentive for remittance", "QR90ST12UV"),
        (sms.BKASH_RECHARGE, TxnType.DEBIT, "400.00", "Mobile Recharge (01700****01)", "WX34YZ56AB"),
        (sms.BKASH_BILL, TxnType.DEBIT, "2910.00", "Bill: DESCO (POSTPAID)", "CD78EF90GH"),
        (sms.BKASH_RECHARGE_FAILED, TxnType.CREDIT, "108.00", "Refund (failed recharge)", None),
        (sms.BKASH_CASHBACK, TxnType.CREDIT, "67.30", "Cashback", None),
        (sms.BKASH_BANK_DEPOSIT, TxnType.CREDIT, "2500.00", "Deposit from Pubali Bank", "IJ12KL34MN"),
    ],
)
def test_bkash(text, txn_type, amount, description, reference):
    txn = parse_sms(text, "bKash")
    assert txn.bank is Bank.BKASH
    assert txn.account == WALLET
    assert txn.txn_type is txn_type
    assert txn.amount == Decimal(amount)
    assert txn.description == description
    assert txn.reference == reference


def test_promo_is_ignored():
    assert parse_sms(sms.BKASH_PROMO, "bKash") is None


@pytest.mark.parametrize(
    ("text", "balance"),
    [
        (sms.BKASH_PAYMENT, "1234.56"),
        (sms.BKASH_RECEIVED, "15234.56"),
        (sms.BKASH_BILL, "3090.00"),
    ],
)
def test_bkash_balance(text, balance):
    result = parse_balance(text, "bKash")
    assert result.account == WALLET
    assert result.balance == Decimal(balance)


def test_remittance_without_balance_line():
    assert parse_balance(sms.BKASH_REMITTANCE, "bKash") is None


def test_amount_is_not_confused_with_fee():
    """The Fee field also says 'Tk'; the amount must come from the action phrase."""
    assert parse_sms(sms.BKASH_CASH_OUT, "bKash").amount == Decimal("1000.00")
