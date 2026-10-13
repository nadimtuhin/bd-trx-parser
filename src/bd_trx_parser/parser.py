"""Entry points: hand in an SMS, get back a Transaction or AccountBalance."""

from __future__ import annotations

import re
from datetime import date, datetime

from .banks import PARSERS, BankParser
from .models import AccountBalance, Bank, Transaction
from .utils import clean_text

DateLike = date | datetime | str | None


def _normalise_sender(sender: str) -> str:
    return re.sub(r"[^a-z0-9]", "", sender.lower())


_PARSER_BY_SENDER: dict[str, BankParser] = {
    _normalise_sender(sender_id): parser for parser in PARSERS for sender_id in parser.sender_ids
}
_PARSER_BY_BANK: dict[Bank, BankParser] = {parser.bank: parser for parser in PARSERS}


def detect_bank(sender: str) -> Bank | None:
    """Map an SMS sender mask ('EBL', '16216', 'bKash', ...) to its institution."""
    parser = _PARSER_BY_SENDER.get(_normalise_sender(sender))
    return parser.bank if parser else None


def parse_sms(
    text: str, sender: str | None = None, *, date: DateLike = None, bank: Bank | None = None
) -> Transaction | None:
    """Parse a transaction alert. Returns None for anything that is not one.

    `bank` (or a recognised `sender`) restricts parsing to that institution.
    Without either, every parser is tried in a fixed order.
    `date` is the SMS receive time; it is copied onto the result and feeds the hash.
    """
    cleaned = clean_text(text)
    on = _to_date(date)
    for parser in _candidates(sender, bank):
        transaction = parser.parse_transaction(cleaned, on)
        if transaction:
            return transaction
    return None


def parse_balance(
    text: str, sender: str | None = None, *, date: DateLike = None, bank: Bank | None = None
) -> AccountBalance | None:
    """Pull the post-transaction balance (or card outstanding) out of an SMS."""
    cleaned = clean_text(text)
    on = _to_date(date)
    candidates = _candidates(sender, bank)
    if len(candidates) > 1:
        candidates = _owner_first(cleaned, candidates)
    for parser in candidates:
        balance = parser.parse_balance(cleaned, on)
        if balance:
            return balance
    return None


def _candidates(sender: str | None, bank: Bank | None) -> list[BankParser]:
    if bank is not None:
        return [_PARSER_BY_BANK[Bank(bank)]]
    if sender:
        parser = _PARSER_BY_SENDER.get(_normalise_sender(sender))
        if parser:
            return [parser]
    return list(PARSERS)


def _owner_first(text: str, parsers: list[BankParser]) -> list[BankParser]:
    """Balance phrases overlap between banks ('Balance BDT ...'), so when the sender
    is unknown, ask the parser that recognises the transaction first."""
    for parser in parsers:
        if parser.parse_transaction(text):
            return [parser, *(p for p in parsers if p is not parser)]
    return parsers


def _to_date(value: DateLike) -> date | None:
    if value is None or type(value) is date:
        return value
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, str):
        return date.fromisoformat(value[:10])
    raise TypeError(f"date must be a date, datetime or ISO string, not {type(value).__name__}")
