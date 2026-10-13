"""Dutch-Bangla Bank: savings credits/debits, ATM and POS alerts."""

from __future__ import annotations

import re
from datetime import date

from ..models import AccountBalance, Bank, Transaction, TxnType
from ..utils import AMOUNT, group_or_none, parse_amount
from .base import BankParser

# "your A/C ***1234 debited (ATM Cash Withdrawal) by Tk5,000.00 on ..."
# "your A/C ***1234 credited by Tk1,000.00 on ..."
_TXN = re.compile(
    rf"A/C\s+([\d*]+)\s+(credited|debited)\s*(?:\(([^)]*)\))?\s*by\s+Tk\.?\s*{AMOUNT}", re.I
)
_CLOSING_BALANCE = re.compile(rf"C/B\s+Tk\.?\s*{AMOUNT}", re.I)


class DBBLParser(BankParser):
    bank = Bank.DBBL
    sender_ids = ("DBBL", "16216", "DutchBangla")

    def parse_transaction(self, text: str, on: date | None = None) -> Transaction | None:
        m = _TXN.search(text)
        if not m:
            return None
        account, direction, description, amount = m.groups()
        return Transaction(
            bank=self.bank,
            txn_type=TxnType.CREDIT if direction.lower() == "credited" else TxnType.DEBIT,
            amount=parse_amount(amount),
            description=(description or "").strip() or "Transfer",
            account=account,
            date=on,
        )

    def parse_balance(self, text: str, on: date | None = None) -> AccountBalance | None:
        m = _CLOSING_BALANCE.search(text)
        if not m:
            return None
        account = group_or_none(r"A/C\s+([\d*]+)", text)
        return AccountBalance(self.bank, account, parse_amount(m.group(1)), date=on)
