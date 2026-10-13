"""Typed results returned by every parser."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from enum import Enum
from typing import Any

from .utils import transaction_hash


class Bank(str, Enum):
    EBL = "EBL"
    DBBL = "DBBL"
    CITY_BANK = "City Bank"
    CITY_AMEX = "City AMEX"
    AIBL = "AIBL"
    BKASH = "bKash"
    MIDLAND = "Midland Bank"
    PATHAO_PAY = "PathaoPay"
    NAGAD = "Nagad"


class TxnType(str, Enum):
    DEBIT = "DR"
    CREDIT = "CR"


WALLET = "wallet"
"""Account label for MFS wallets (bKash, Nagad, PathaoPay), which have no account number in the SMS."""


@dataclass(frozen=True)
class Transaction:
    bank: Bank
    txn_type: TxnType
    amount: Decimal
    description: str
    account: str | None = None
    currency: str = "BDT"
    date: date | None = None
    reference: str | None = None

    @property
    def hash(self) -> str:
        return transaction_hash(self.date, self.bank.value, self.amount, self.txn_type.value)

    def to_dict(self) -> dict[str, Any]:
        return {
            "bank": self.bank.value,
            "txn_type": self.txn_type.value,
            "amount": str(self.amount),
            "currency": self.currency,
            "account": self.account,
            "description": self.description,
            "date": self.date.isoformat() if self.date else None,
            "reference": self.reference,
            "hash": self.hash,
        }


@dataclass(frozen=True)
class AccountBalance:
    bank: Bank
    account: str | None
    balance: Decimal
    currency: str = "BDT"
    date: date | None = None
    is_liability: bool = False
    """True for credit cards, where the balance is money owed rather than money held."""

    def to_dict(self) -> dict[str, Any]:
        return {
            "bank": self.bank.value,
            "account": self.account,
            "balance": str(self.balance),
            "currency": self.currency,
            "date": self.date.isoformat() if self.date else None,
            "is_liability": self.is_liability,
        }
