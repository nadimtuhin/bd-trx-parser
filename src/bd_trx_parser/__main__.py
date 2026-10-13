"""CLI: python -m bd_trx_parser [--sender EBL] [--date 2026-10-12] [TEXT]

Reads the SMS from TEXT or stdin and prints JSON:
{"transaction": {...} | null, "balance": {...} | null}
Exits 1 when the SMS holds neither.
"""

from __future__ import annotations

import argparse
import json
import sys

from . import __version__, parse_balance, parse_sms
from .models import Bank


def main(argv: list[str] | None = None) -> int:
    args = _build_arg_parser().parse_args(argv)
    text = args.text if args.text is not None else sys.stdin.read()
    bank = Bank(args.bank) if args.bank else None

    transaction = parse_sms(text, args.sender, date=args.date, bank=bank)
    balance = parse_balance(text, args.sender, date=args.date, bank=bank)
    result = {
        "transaction": transaction.to_dict() if transaction else None,
        "balance": balance.to_dict() if balance else None,
    }
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if transaction or balance else 1


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="bd-trx-parser",
        description="Parse a Bangladeshi bank / MFS SMS into JSON.",
    )
    parser.add_argument("text", nargs="?", help="SMS body; read from stdin when omitted")
    parser.add_argument("--sender", help="SMS sender mask, e.g. EBL, bKash, 16216")
    parser.add_argument("--bank", choices=[b.value for b in Bank], help="force a specific institution")
    parser.add_argument("--date", help="receive date, YYYY-MM-DD")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    return parser


if __name__ == "__main__":
    sys.exit(main())
