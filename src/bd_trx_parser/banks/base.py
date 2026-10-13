from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import date
from typing import ClassVar

from ..models import AccountBalance, Bank, Transaction


class BankParser(ABC):
    """One institution's SMS layouts.

    Parsers receive text that has already been through `clean_text`, and
    return None for any message they do not recognise (OTPs, promos, ...).
    """

    bank: ClassVar[Bank]
    sender_ids: ClassVar[tuple[str, ...]] = ()
    """Sender masks this institution uses, compared case- and punctuation-insensitively."""

    @abstractmethod
    def parse_transaction(self, text: str, on: date | None = None) -> Transaction | None: ...

    def parse_balance(self, text: str, on: date | None = None) -> AccountBalance | None:
        return None
