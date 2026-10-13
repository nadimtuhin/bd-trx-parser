"""Nagad wallet. Nagad alerts are one field per line:

    Money Received.
    Amount: Tk 1,500.00
    Sender: 01712****99
    TxnID: 73ABCD12
    Balance: Tk 2,345.67
"""

from __future__ import annotations

import re
from datetime import date

from ..models import WALLET, AccountBalance, Bank, Transaction, TxnType
from ..utils import AMOUNT, group_or_none, parse_amount
from .base import BankParser

_TK = rf"Tk\.?\s*{AMOUNT}"
_HEADER = re.compile(r"^(Money\s+Received|Cash\s+In|Cash\s+Out|Send\s+Money)\b", re.I | re.M)
_AMOUNT_LINE = re.compile(rf"^Amount:\s*{_TK}", re.I | re.M)
_COUNTERPARTY = re.compile(r"^(?:Sender|Receiver|Uddokta|Agent):\s*(\S+)", re.I | re.M)
_BALANCE = re.compile(rf"^Balance:\s*{_TK}", re.I | re.M)

# header (lower-cased, single-spaced) -> (direction, label, preposition before the counterparty)
_ACTIONS: dict[str, tuple[TxnType, str, str]] = {
    "money received": (TxnType.CREDIT, "Money Received", "from"),
    "cash in": (TxnType.CREDIT, "Cash In", "from"),
    "cash out": (TxnType.DEBIT, "Cash Out", "to"),
    "send money": (TxnType.DEBIT, "Send Money", "to"),
}


class NagadParser(BankParser):
    bank = Bank.NAGAD
    sender_ids = ("NAGAD", "16167")

    def parse_transaction(self, text: str, on: date | None = None) -> Transaction | None:
        header = _HEADER.search(text)
        amount = _AMOUNT_LINE.search(text)
        if not (header and amount):
            return None
        txn_type, label, preposition = _ACTIONS[" ".join(header.group(1).lower().split())]
        counterparty_match = _COUNTERPARTY.search(text)
        counterparty = counterparty_match.group(1) if counterparty_match else None
        return Transaction(
            bank=self.bank,
            txn_type=txn_type,
            amount=parse_amount(amount.group(1)),
            description=f"{label} {preposition} {counterparty}" if counterparty else label,
            account=WALLET,
            date=on,
            reference=group_or_none(r"TxnID:?\s*(\w+)", text),
        )

    def parse_balance(self, text: str, on: date | None = None) -> AccountBalance | None:
        m = _BALANCE.search(text)
        if not m:
            return None
        return AccountBalance(self.bank, WALLET, parse_amount(m.group(1)), date=on)
