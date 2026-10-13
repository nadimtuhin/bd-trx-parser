"""Eastern Bank PLC: savings, debit card, credit card (BDT/USD), ATM, BEFTN/NPSB."""

from __future__ import annotations

import re
from datetime import date

from ..models import AccountBalance, Bank, Transaction, TxnType
from ..utils import AMOUNT, group_or_none, parse_amount
from .base import BankParser

_CARD = r"([\d*]+)"
_SAVINGS_ACCOUNT = r"\bA/?C\s+([\d*]+)"

# "Purchase txn BDT 6,000.00 from GREEN LEAF CAFE DHAKA.Card 422222**2222 ..."
# "EBL CARDS: Purchase txn USD 15.99 from NETFLIX.COM.Card 411111**1111 ..."
_PURCHASE = re.compile(
    rf"Purchase\s+txn\s+(BDT|USD)\s*{AMOUNT}\s+from\s+(.+?)\.\s*Card\s+{_CARD}", re.I | re.S
)
# "EBL CARDS: POS txn BDT 500.00 using Card 411111**1111 ..." (older card alert layout)
_CARD_OTHER = re.compile(
    rf"EBL CARDS:\s*(.+?)\s+(BDT|USD)\s*{AMOUNT}\s+(?:using|from)\s+.*?Card\s+{_CARD}", re.I | re.S
)
_CARD_PAYMENT = re.compile(rf"Payment\s+of\s+(BDT|USD)\s*{AMOUNT}\s+credited\s+to\s+Card\s+{_CARD}", re.I)
_CARD_REVERSAL = re.compile(
    rf"Purchase\s+transaction\s+(BDT|USD)\s*{AMOUNT}\s+has\s+been\s+reversed\s+to\s+card\s+{_CARD}", re.I
)
# "Cash WD BDT5000 from EBL GULSHAN BRANCH ATM. Card 422222**2222 ..."
_CASH_WITHDRAWAL = re.compile(rf"Cash\s+WD\s+BDT\s*{AMOUNT}\s+from\s+(.+?)\.\s*Card\s+{_CARD}", re.I | re.S)
# "AC 101***111 is credited with BDT 25,000.00 BEFTN Inward from ACME LTD. Balance is ..."
_SAVINGS = re.compile(
    rf"\bA/?C\s+([\d*]+)\s+is\s+(credited|debited)\s+with\s+BDT\s*{AMOUNT}\s*([^.\n]*)", re.I
)
_BALANCE = re.compile(rf"Balance\s*(?:is|:)?\s*BDT\s*{AMOUNT}", re.I)


def _is_credit_card(text: str) -> bool:
    return "EBL CARDS" in text.upper()


class EBLParser(BankParser):
    bank = Bank.EBL
    sender_ids = ("EBL", "EBLBANK", "EBL CARDS")

    def parse_transaction(self, text: str, on: date | None = None) -> Transaction | None:
        if m := _PURCHASE.search(text):
            currency, amount, merchant, card = m.groups()
            return self._txn(TxnType.DEBIT, amount, merchant.strip(), self._account(text, card), currency, on)

        if m := _CARD_OTHER.search(text):
            label, currency, amount, card = m.groups()
            return self._txn(TxnType.DEBIT, amount, label.strip(), card, currency, on)

        if m := _CARD_PAYMENT.search(text):
            currency, amount, card = m.groups()
            return self._txn(TxnType.CREDIT, amount, f"Card payment ({currency.upper()})", card, currency, on)

        if m := _CARD_REVERSAL.search(text):
            currency, amount, card = m.groups()
            return self._txn(TxnType.CREDIT, amount, "Reversal", card, currency, on)

        if m := _CASH_WITHDRAWAL.search(text):
            amount, location, card = m.groups()
            description = f"ATM Cash WD ({location.strip()})"
            return self._txn(TxnType.DEBIT, amount, description, self._account(text, card), "BDT", on)

        if m := _SAVINGS.search(text):
            account, direction, amount, rest = m.groups()
            txn_type = TxnType.CREDIT if direction.lower() == "credited" else TxnType.DEBIT
            return self._txn(txn_type, amount, rest.strip() or "Transfer", account, "BDT", on)

        return None

    def parse_balance(self, text: str, on: date | None = None) -> AccountBalance | None:
        m = _BALANCE.search(text)
        if not m:
            return None
        if _is_credit_card(text):
            account = group_or_none(rf"Card\s+{_CARD}", text)
            return AccountBalance(self.bank, account, parse_amount(m.group(1)), date=on, is_liability=True)
        account = group_or_none(_SAVINGS_ACCOUNT, text)
        if account is None:
            return None
        return AccountBalance(self.bank, account, parse_amount(m.group(1)), date=on)

    @staticmethod
    def _account(text: str, card: str) -> str:
        """Debit card alerts end with 'Your A/C 101***111 Balance ...'; prefer that account over the card."""
        if _is_credit_card(text):
            return card
        return group_or_none(r"A/C\s+([\d*]+)\s+Balance", text) or card

    def _txn(
        self, txn_type: TxnType, amount: str, description: str, account: str, currency: str, on: date | None
    ) -> Transaction:
        return Transaction(
            bank=self.bank,
            txn_type=txn_type,
            amount=parse_amount(amount),
            description=description,
            account=account,
            currency=currency.upper(),
            date=on,
        )
