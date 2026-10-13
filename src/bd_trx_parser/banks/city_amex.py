"""City Bank American Express credit cards."""

from __future__ import annotations

import re
from datetime import date

from ..models import AccountBalance, Bank, Transaction, TxnType
from ..utils import AMOUNT, group_or_none, parse_amount
from .base import BankParser

_MONEY = rf"(?:Tk\.?|BDT)\s*{AMOUNT}"
_CARD_NO = r"CARD\s+NO:?\s*([\d*]+)"
# "Tk. 3,634.00 purchased at RANG BANGLADESH LTD JAMUNA FUT\nCARD NO: 371***999"
_PURCHASE = re.compile(rf"{_MONEY}\s+purchased\s+at\s+(.+?)\s*(?:\n|\bCARD\b|$)", re.I)
# "Tk. 28,260.00 payment received" / "Payment of BDT 28,260.00 received for AMEX CARD NO: ..."
_PAYMENT = re.compile(rf"{_MONEY}\s+payment\s+received|Payment\s+of\s+{_MONEY}\s+received", re.I)
_BALANCE = re.compile(rf"\bBal\s+{_MONEY}", re.I)


class CityAmexParser(BankParser):
    bank = Bank.CITY_AMEX
    sender_ids = ("CityAMEX", "AMEX", "City AMEX")

    def parse_transaction(self, text: str, on: date | None = None) -> Transaction | None:
        card = group_or_none(_CARD_NO, text)

        if m := _PURCHASE.search(text):
            amount, merchant = m.groups()
            return self._txn(TxnType.DEBIT, amount, merchant.strip(), card, on)

        if m := _PAYMENT.search(text):
            amount = m.group(1) or m.group(2)
            return self._txn(TxnType.CREDIT, amount, "Card payment", card, on)

        return None

    def parse_balance(self, text: str, on: date | None = None) -> AccountBalance | None:
        m = _BALANCE.search(text)
        if not m:
            return None
        card = group_or_none(_CARD_NO, text)
        return AccountBalance(self.bank, card, parse_amount(m.group(1)), date=on, is_liability=True)

    def _txn(
        self, txn_type: TxnType, amount: str, description: str, card: str | None, on: date | None
    ) -> Transaction:
        return Transaction(
            bank=self.bank,
            txn_type=txn_type,
            amount=parse_amount(amount),
            description=description,
            account=card,
            date=on,
        )
