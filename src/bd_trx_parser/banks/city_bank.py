"""City Bank savings accounts (including Citytouch transfers).

City Bank sends a one-field-per-line layout:

    12-Oct-2026
    Citytouch Fund Transfer
    Tk. 5,000.00 Withdrawal
    Tk. 20,345.50 Balance
    A/C: 9900***0042
"""

from __future__ import annotations

import re
from datetime import date

from ..models import AccountBalance, Bank, Transaction, TxnType
from ..utils import AMOUNT, group_or_none, parse_amount
from .base import BankParser

_ACCOUNT = r"A/C[:\s]*([\d*]+)"
_LINE_LAYOUT = re.compile(rf"Tk\.?\s*{AMOUNT}\s+(Deposit|Withdrawal|Purchased)\b", re.I)
# "Tk. 2,500.00 credited to A/C 9900***0042 by Citytouch transfer from ..."
_SENTENCE_LAYOUT = re.compile(
    rf"Tk\.?\s*{AMOUNT}\s+(?:has\s+been\s+)?(credited\s+to|debited\s+from)\s+(?:your\s+)?{_ACCOUNT}"
    r"\s*(?:(?:by|for|via)\s+)?([^.\n]*)",
    re.I,
)
_BALANCE = re.compile(rf"Tk\.?\s*{AMOUNT}\s+Balance", re.I)
_DATE_LINE = re.compile(r"^\d{1,2}[-/ ][A-Za-z]{3}[-/ ]\d{2,4}\b|^\d{1,2}[-/]\d{1,2}[-/]\d{2,4}\b")


def _description_line(text: str) -> str:
    """The free-text line: not the date, not an amount, account, balance or rate line."""
    for line in filter(None, text.split("\n")):
        if _DATE_LINE.match(line):
            continue
        if any(marker in line for marker in ("Tk.", "A/C", "Balance")) or "rate" in line.lower():
            continue
        return line
    return "Transfer"


class CityBankParser(BankParser):
    bank = Bank.CITY_BANK
    sender_ids = ("CityBank", "City Bank", "Citytouch", "CityBankPLC")

    def parse_transaction(self, text: str, on: date | None = None) -> Transaction | None:
        if m := _SENTENCE_LAYOUT.search(text):
            amount, direction, account, rest = m.groups()
            txn_type = TxnType.CREDIT if direction.lower().startswith("credited") else TxnType.DEBIT
            return self._txn(txn_type, amount, rest.strip() or "Transfer", account, on)

        if m := _LINE_LAYOUT.search(text):
            amount, action = m.groups()
            txn_type = TxnType.CREDIT if action.lower() == "deposit" else TxnType.DEBIT
            return self._txn(txn_type, amount, _description_line(text), group_or_none(_ACCOUNT, text), on)

        return None

    def parse_balance(self, text: str, on: date | None = None) -> AccountBalance | None:
        m = _BALANCE.search(text)
        if not m:
            return None
        return AccountBalance(self.bank, group_or_none(_ACCOUNT, text), parse_amount(m.group(1)), date=on)

    def _txn(
        self, txn_type: TxnType, amount: str, description: str, account: str | None, on: date | None
    ) -> Transaction:
        return Transaction(
            bank=self.bank,
            txn_type=txn_type,
            amount=parse_amount(amount),
            description=description,
            account=account,
            date=on,
        )
