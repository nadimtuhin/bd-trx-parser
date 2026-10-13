"""bKash wallet: payments, send money, cash in/out, remittance, recharge, bill pay."""

from __future__ import annotations

import re
from collections.abc import Callable
from datetime import date

from ..models import WALLET, AccountBalance, Bank, Transaction, TxnType
from ..utils import group_or_none, parse_amount
from .base import BankParser

_TK = r"Tk\.?\s*(?P<amount>\d[\d,]*(?:\.\d+)?)"

DescribeMatch = Callable[[re.Match[str]], str]


def _strip_merchant_suffix(name: str) -> str:
    """'SHOPNO-RM12345 TrxID ...' -> 'SHOPNO'; bKash appends a merchant id after '-RM'."""
    name = re.sub(r"\s*TrxID.*$", "", name, flags=re.I)
    return re.sub(r"-RM\d+$", "", name).strip()


def _counterparty(m: re.Match[str]) -> str:
    return m.group("who").strip().rstrip(".")


# Checked in order; the first match wins.
_LAYOUTS: list[tuple[re.Pattern[str], TxnType, DescribeMatch]] = [
    (
        re.compile(rf"Payment\s+(?:of\s+)?{_TK}\s+to\s+(?P<who>.+?)\s+(?:is\s+)?successful", re.I),
        TxnType.DEBIT,
        lambda m: f"Payment to {_strip_merchant_suffix(m.group('who'))}",
    ),
    (
        re.compile(rf"Cash\s+Out\s+{_TK}(?:\s+to\s+(?P<who>\S+))?", re.I),
        TxnType.DEBIT,
        lambda m: f"Cash Out to {_counterparty(m)}" if m.group("who") else "Cash Out",
    ),
    (
        re.compile(rf"Cash\s+In\s+{_TK}(?:\s+from\s+(?P<who>\S+))?", re.I),
        TxnType.CREDIT,
        lambda m: f"Cash In from {_counterparty(m)}" if m.group("who") else "Cash In",
    ),
    (
        re.compile(rf"Send\s+Money\s+{_TK}(?:\s+to\s+(?P<who>\S+))?", re.I),
        TxnType.DEBIT,
        lambda m: f"Send Money to {_counterparty(m)}" if m.group("who") else "Send Money",
    ),
    (
        re.compile(rf"You\s+have\s+received\s+{_TK}\s+from\s+(?P<who>\S+)", re.I),
        TxnType.CREDIT,
        lambda m: f"Received from {_counterparty(m)}",
    ),
    (
        re.compile(rf"received\s+remittance.*?Amount:\s*{_TK}", re.I | re.S),
        TxnType.CREDIT,
        lambda m: "Remittance received",
    ),
    (
        re.compile(rf"govt\.?\s*incentive.*?Amount:\s*{_TK}", re.I | re.S),
        TxnType.CREDIT,
        lambda m: "Govt. incentive for remittance",
    ),
    (
        re.compile(rf"Recharge\s+request\s+of\s+{_TK}\s+for\s+(?P<who>\S+)", re.I),
        TxnType.DEBIT,
        lambda m: f"Mobile Recharge ({_counterparty(m)})",
    ),
    (
        re.compile(
            rf"Bill\s+successfully\s+paid.*?Biller:\s*(?P<who>[^\n]+?)\s*(?:\n|$).*?Amount:\s*{_TK}", re.I | re.S
        ),
        TxnType.DEBIT,
        lambda m: f"Bill: {m.group('who').strip()}",
    ),
    (
        re.compile(rf"{_TK}\s+returned", re.I),
        TxnType.CREDIT,
        lambda m: "Refund (failed recharge)",
    ),
    (
        re.compile(rf"received\s+Cashback\s+{_TK}", re.I),
        TxnType.CREDIT,
        lambda m: "Cashback",
    ),
    (
        re.compile(rf"received\s+deposit.*?{_TK}\s+from\s+(?P<who>.+?)\.?\s*Fee", re.I | re.S),
        TxnType.CREDIT,
        lambda m: f"Deposit from {m.group('who').strip()}",
    ),
]

_BALANCE = re.compile(rf"Balance:?\s+{_TK}", re.I)


class BkashParser(BankParser):
    bank = Bank.BKASH
    sender_ids = ("bKash", "16247")

    def parse_transaction(self, text: str, on: date | None = None) -> Transaction | None:
        for pattern, txn_type, describe in _LAYOUTS:
            m = pattern.search(text)
            if m:
                return Transaction(
                    bank=self.bank,
                    txn_type=txn_type,
                    amount=parse_amount(m.group("amount")),
                    description=describe(m),
                    account=WALLET,
                    date=on,
                    reference=group_or_none(r"TrxID:?\s*(\w+)", text),
                )
        return None

    def parse_balance(self, text: str, on: date | None = None) -> AccountBalance | None:
        m = _BALANCE.search(text)
        if not m:
            return None
        return AccountBalance(self.bank, WALLET, parse_amount(m.group("amount")), date=on)
