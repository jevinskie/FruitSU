import enum
from pathlib import Path
from typing import Final, Optional, List
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

class INode(NodeMixin):
    name: str
    type: Final[DirEntType]
    size: int
    size_comp: Optional[int]
    _ino: Final[int]

    def __init__(self, name: str, type: Final[DirEntType], size: int = 0, size_comp: Optional[int] = None,
                 parent: Self = None, children: Optional[List[Self]] = None):
        super().__init__()
        self.name = name
        self.type = type
        self.size = size
        self.size_comp = size_comp
        self.parent = parent
        if type == DirEntType.DIR:
            self.children = children if children else []
        self._ino = InoVendor.next()

    @classmethod
    def root_node(cls):
        return cls(parent=None, name="rootfs", type=DirEntType.DIR)

    def dump(self):
        for pre, fill, node in RenderTree(self):
            print('{}{}'.format(pre, node.name))
