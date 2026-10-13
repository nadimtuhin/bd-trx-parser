"""Al-Arafah Islami Bank savings accounts."""

from __future__ import annotations

import re
from datetime import date

from ..models import AccountBalance, Bank, Transaction, TxnType
from ..utils import AMOUNT, group_or_none, parse_amount
from .base import BankParser

# "Your A/C 100200****300 has been Debited by BDT 2,750.00 on ..." / "A/C 100200****300 Credited BDT 10,000.00"
_ACCOUNT_TXN = re.compile(
    rf"A/C\s+([\d*]+)\s+(?:has\s+been\s+)?(Credited|Debited)\s+(?:by\s+)?BDT\s*{AMOUNT}", re.I
)
# "Tk. 5000 has been Transfered from A/C: 100200****300" (the bank's own spelling)
_TRANSFER = re.compile(
    rf"Tk\.?\s*{AMOUNT}\s+has\s+been\s+Transf?err?ed\s+(from|to)\s+A/C:?\s*([\d*]+)", re.I
)
_BALANCE = re.compile(rf"Balance:\s*(?:BDT|Tk\.?)?\s*{AMOUNT}", re.I)


class AIBLParser(BankParser):
    bank = Bank.AIBL
    sender_ids = ("AIBL", "AlArafah", "AIBLPLC")

    def parse_transaction(self, text: str, on: date | None = None) -> Transaction | None:
        if m := _ACCOUNT_TXN.search(text):
            account, direction, amount = m.groups()
            ref = group_or_none(r"Ref:\s*(\S+?)\.?(?:\s|$)", text)
            return Transaction(
                bank=self.bank,
                txn_type=TxnType.CREDIT if direction.lower() == "credited" else TxnType.DEBIT,
                amount=parse_amount(amount),
                description=f"Ref: {ref}" if ref else "Transfer",
                account=account,
                date=on,
                reference=ref,
            )

        if m := _TRANSFER.search(text):
            amount, direction, account = m.groups()
            return Transaction(
                bank=self.bank,
                txn_type=TxnType.CREDIT if direction.lower() == "to" else TxnType.DEBIT,
                amount=parse_amount(amount),
                description="Transfer",
                account=account,
                date=on,
            )

        return None

    def parse_balance(self, text: str, on: date | None = None) -> AccountBalance | None:
        m = _BALANCE.search(text)
        if not m:
            return None
        account = group_or_none(r"A/C:?\s*([\d*]+)", text)
        return AccountBalance(self.bank, account, parse_amount(m.group(1)), date=on)
