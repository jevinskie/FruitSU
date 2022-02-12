import enum
from pathlib import Path
from typing import Final, Optional
from typing_extensions import Self

from anytree import Node, NodeMixin, RenderTree
from attrs import define, field, Factory

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
    LNK = 2

@define
class INode(NodeMixin):
    name: str
    type: Final[DirEntType]
    size: int = 0
    size_comp: Optional[int] = None
    children: [Self] = []
    _ino: Final[int] = field(init=False, default=Factory(InoVendor.next))

    @classmethod
    def root_node(cls):
        return cls(name="/", type=DirEntType.DIR)

    def dump(self):
        RenderTree(self)
