from __future__ import annotations

import enum
from typing import Final, List, Optional, Self

from anytree import NodeMixin, RenderTree
from anytree.resolver import ChildResolverError, Resolver, ResolverError
from fs.enums import ResourceType
from rich import (
    print as rprint,
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
    _size: int
    size_comp: Optional[int]
    _ino: Final[int]

    def __init__(
        self,
        name: str,
        type: DirEntType,
        size: int = 0,
        size_comp: Optional[int] = None,
        parent: Optional[Self] = None,
        children: Optional[List[Self]] = None,
    ):
        super().__init__()
        self.name = name
        self.type = type
        self._size = size
        self.size_comp = size_comp
        self.parent = parent
        if type == DirEntType.DIR:
            self.children = children if children else []
        self._ino = InoVendor.next()

    @property
    def size(self):
        return self._size

    @size.setter
    def size(self, value):
        self._size = value

    @property
    def is_dir(self) -> bool:
        return self.type == DirEntType.DIR

    @property
    def pyfs_type(self) -> ResourceType:
        return {
            DirEntType.DIR: ResourceType.directory,
            DirEntType.REG: ResourceType.file,
            DirEntType.LNK: ResourceType.symlink,
        }[self.type]

    @classmethod
    def root_node(cls):
        return cls(parent=None, name="rootfs", type=DirEntType.DIR)

    def dump(self):
        for pre, fill, node in RenderTree(self):
            rprint("[yellow]{}[/]{}".format(pre, node.name))

    @staticmethod
    def _norm_path(path: str):
        if path[0] == "/":
            return "/rootfs" + path
        return path

    def lookup(self, path: str) -> INode:
        r = Resolver("name")
        try:
            res = r.get(self, self._norm_path(path))
        except (ResolverError, ChildResolverError):
            res = None
        return res
