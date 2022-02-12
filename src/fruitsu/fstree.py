import enum
from pathlib import Path
from typing import Final
from typing_extensions import Self

import anytree
from attrs import define, field

from rich import (
    print as rprint,
    inspect as rinspect,
)

class InoVendor:
    _ino: int = 0

    @classmethod
    def next(cls) -> int:
        your_ino, cls._ino = cls._ino, cls._ino + 1
        return your_ino


class DirEntType(enum.Enum):
    DIR = 0
    REG = 1
    LINK = 2

@define
class INode:
    name: str
    size: int
    type: Final[DirEntType]
    children: [Self] = []
    _ino: Final[int] = field(default=InoVendor.next)

    @classmethod
    def root_node(cls):
        return cls("/", 0, DirEntType.DIR)
