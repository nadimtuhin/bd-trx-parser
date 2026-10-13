"""Text cleaning, amount parsing and the dedup hash shared by all parsers."""

from __future__ import annotations

import hashlib
import re
from datetime import date
from decimal import Decimal, InvalidOperation

AMOUNT = r"(\d[\d,]*(?:\.\d+)?)"
"""Regex group for an amount: '5000', '1,000.00' and the Indian-style '1,00,000.50' all match."""

_INVISIBLE = {"\ufeff", "\ufffd", "\uffff", "\u200b"}


def clean_text(text: str) -> str:
    """Strip BOMs, replacement chars and control characters, keeping line breaks.

    Carrier gateways often inject '\\ufffd' or NULs, and some banks send CRLF.
    Line breaks are kept because several layouts (City Bank, Nagad, bKash bills)
    are one field per line.
    """
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    kept = (c for c in text if c == "\n" or (ord(c) >= 32 and c not in _INVISIBLE))
    lines = "".join(kept).split("\n")
    return "\n".join(line.strip() for line in lines).strip()


def parse_amount(raw: str) -> Decimal:
    """'1,00,000.00' -> Decimal('100000.00'). Raises ValueError on anything that is not a number."""
    cleaned = raw.replace(",", "").strip().rstrip(".")
    try:
        return Decimal(cleaned)
    except InvalidOperation:
        raise ValueError(f"not an amount: {raw!r}") from None


def transaction_hash(on: date | None, bank: str, amount: Decimal, txn_type: str) -> str:
    """Stable 16-hex-char id for deduplicating the same transaction seen twice.

    Deliberately ignores description and account so an SMS and an email alert
    for the same purchase collapse into one row.
    """
    day = on.isoformat() if on else ""
    key = f"{day}|{bank.upper()}|{abs(amount):.2f}|{txn_type}"
    return hashlib.sha256(key.encode()).hexdigest()[:16]


def group_or_none(pattern: str, text: str, flags: int = re.IGNORECASE) -> str | None:
    match = re.search(pattern, text, flags)
    return match.group(1) if match else None
