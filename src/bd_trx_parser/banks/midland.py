"""Midland Bank (MDB) Visa credit cards: purchases, card payments, bill statements."""

from __future__ import annotations

import re
from datetime import date

from ..models import AccountBalance, Bank, Transaction, TxnType
from ..utils import AMOUNT, group_or_none, parse_amount
from .base import BankParser

_CARD = r"Card#?\s*([\d*]+)"
# "Thanks for using MDB Visa Card# 455555*5555 for BDT 1,050.00 at APON FAMILY MART on ..."
_CARD_USE = re.compile(rf"MDB\s+Visa\s+{_CARD}\s+for\s+BDT\s*{AMOUNT}\s+at\s+(.+?)\s+on\b", re.I)
# "MDB: Purchase txn BDT 2,300.00 from DARAZ BD. Card 455555*5555 ..."
_PURCHASE = re.compile(rf"Purchase\s+txn\s+BDT\s*{AMOUNT}\s+from\s+(.+?)\.\s*{_CARD}", re.I | re.S)
_PAYMENT = re.compile(rf"BDT\s*{AMOUNT}\s+has\s+been\s+credited\s+to\s+your\s+{_CARD}", re.I)
# "... MDB Card# 455555*5555 bill on 15-Oct-2026 is BDT 12,345.00 Dr ..."
_BILL = re.compile(rf"bill\s+on\b.*?BDT\s*{AMOUNT}\s*Dr\b", re.I | re.S)
_BALANCE = re.compile(rf"Balance\s+is\s+BDT\s*{AMOUNT}", re.I)
_BRAND = re.compile(r"\bMDB\b|Midland", re.I)


class MidlandParser(BankParser):
    bank = Bank.MIDLAND
    sender_ids = ("MDB", "Midland", "MidlandBank")

    def parse_transaction(self, text: str, on: date | None = None) -> Transaction | None:
        if m := _CARD_USE.search(text):
            card, amount, merchant = m.groups()
            return self._txn(TxnType.DEBIT, amount, merchant.strip(), card, on)

        # "Purchase txn" is shared with EBL, so only claim it when the SMS names Midland.
        if _BRAND.search(text) and (m := _PURCHASE.search(text)):
            amount, merchant, card = m.groups()
            return self._txn(TxnType.DEBIT, amount, merchant.strip(), card, on)

        if m := _PAYMENT.search(text):
            amount, card = m.groups()
            return self._txn(TxnType.CREDIT, amount, "Card payment", card, on)

        return None

    def parse_balance(self, text: str, on: date | None = None) -> AccountBalance | None:
        m = _BILL.search(text) or _BALANCE.search(text)
        if not m or not (_BRAND.search(text) or "Card#" in text):
            return None
        card = group_or_none(_CARD, text)
        return AccountBalance(self.bank, card, parse_amount(m.group(1)), date=on, is_liability=True)

    def _txn(self, txn_type: TxnType, amount: str, description: str, card: str, on: date | None) -> Transaction:
        return Transaction(
            bank=self.bank,
            txn_type=txn_type,
            amount=parse_amount(amount),
            description=description,
            account=card,
            date=on,
        )
