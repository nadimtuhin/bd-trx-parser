"""PathaoPay wallet."""

from __future__ import annotations

import re
from datetime import date

from ..models import WALLET, AccountBalance, Bank, Transaction, TxnType
from ..utils import AMOUNT, group_or_none, parse_amount
from .base import BankParser

# "Paid to Pathao Food.\nAmount BDT 938.00 Fee BDT 0.00"
_PAID = re.compile(rf"Paid\s+to\s+(.+?)[.\n].*?Amount:?\s+BDT\s*{AMOUNT}", re.I | re.S)
_BALANCE = re.compile(rf"Balance:?\s+BDT\s*{AMOUNT}", re.I)


class PathaoPayParser(BankParser):
    bank = Bank.PATHAO_PAY
    sender_ids = ("PathaoPay", "Pathao Pay", "Pathao")

    def parse_transaction(self, text: str, on: date | None = None) -> Transaction | None:
        m = _PAID.search(text)
        if not m:
            return None
        recipient, amount = m.groups()
        return Transaction(
            bank=self.bank,
            txn_type=TxnType.DEBIT,
            amount=parse_amount(amount),
            description=f"Paid to {recipient.strip()}",
            account=WALLET,
            date=on,
            reference=group_or_none(r"(?:Txn|Trx)\s*ID:?\s*(\w+)", text),
        )

    def parse_balance(self, text: str, on: date | None = None) -> AccountBalance | None:
        m = _BALANCE.search(text)
        if not m:
            return None
        return AccountBalance(self.bank, WALLET, parse_amount(m.group(1)), date=on)
