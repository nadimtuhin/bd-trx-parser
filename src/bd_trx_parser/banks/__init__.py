from .aibl import AIBLParser
from .base import BankParser
from .bkash import BkashParser
from .city_amex import CityAmexParser
from .city_bank import CityBankParser
from .dbbl import DBBLParser
from .ebl import EBLParser
from .midland import MidlandParser
from .nagad import NagadParser
from .pathao_pay import PathaoPayParser

PARSERS: tuple[BankParser, ...] = (
    # Order matters when the sender is unknown: layouts that are more
    # specific come first so a looser pattern further down cannot steal them.
    NagadParser(),
    BkashParser(),
    CityAmexParser(),
    MidlandParser(),
    EBLParser(),
    DBBLParser(),
    AIBLParser(),
    CityBankParser(),
    PathaoPayParser(),
)

__all__ = [
    "PARSERS",
    "AIBLParser",
    "BankParser",
    "BkashParser",
    "CityAmexParser",
    "CityBankParser",
    "DBBLParser",
    "EBLParser",
    "MidlandParser",
    "NagadParser",
    "PathaoPayParser",
]
