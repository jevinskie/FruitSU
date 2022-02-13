
import bz2
import enum
import io
import lzma
from pathlib import Path
from typing import Final, Optional, Collection, BinaryIO, Mapping
import zlib

from anytree import RenderTree
from attrs import define, field
from construct import *
from construct import (
    Optional as ConstructOptional,
    Mapping as ConstructMapping,
)
from typing import Optional, Mapping
from fs.base import FS
from fs.enums import ResourceType
from fs.errors import *
from fs.info import Info
from fs.permissions import Permissions
from fs.subfs import SubFS
from fs.opener.errors import *
from fs.opener.parse import ParseResult
import fs.opener.registry
import untangle

from rich import (
    print as rprint,
    inspect as rinspect,
)

from .io import FancyRawIOBase, OffsetRawIOBase
from .fs import INode, DirEntType


__all__ = [
    "ChecksumAlgorithmEnum",
    "ChecksumAlgorithm",
    "XARTOC",
    "XARFile",
    "XARFS",
    "XARHeader",
]


class ChecksumAlgorithmEnum(enum.IntEnum):
    none = 0
    sha1 = 1
    md5 = 2
    sha256 = 3
    sha512 = 4

ChecksumAlgorithm = Enum(Int32ub, ChecksumAlgorithmEnum)

XARHeader = Struct(
    'magic' / Int32ub,
    'size' / Int16ub,
    'version' / Int16ub,
    'toc_length_compressed' / Int64ub,
    'toc_length_uncompressed' / Int64ub,
    'cksum_alg' / ChecksumAlgorithm,
    '_padding_begin' / Tell,
    'padding' / Padding(this.size - this._padding_begin),
)


@define
class XARTOC:
    rootfs: Final[INode]

    @classmethod
    def from_xml(cls, xml):
        xml = untangle.parse(xml)
        root = INode.root_node()
        print("TREE:")
        root.dump()
        print("/TREE")

        def add_files_children(node, file):
            if hasattr(file, 'file'):
                for f in file.file:
                    name = f.name.cdata
                    ty = {
                        'directory': DirEntType.DIR,
                        'file': DirEntType.REG,
                        'symlink': DirEntType.LNK,
                    }[f.type.cdata]
                    sz = 0
                    sz_comp = None
                    if ty == DirEntType.REG:
                        sz = int(f.data.size.cdata)
                        if f.data.encoding["style"] != "application/octet-stream":
                            sz_comp = int(f.data.length.cdata)
                    child_node = INode(parent=node, name=name, size=sz, size_comp=sz_comp, type=ty)
                    add_files_children(child_node, f)

        add_files_children(root, xml.xar.toc)

        return cls(rootfs=root)

    def dump(self):
        print(self)


@define
class XARFile:
    fh: Final[FancyRawIOBase] = field(converter=FancyRawIOBase)
    hdr: XARHeader = field(init=False)
    toc: Final[XARTOC] = field(init=False)

    def __attrs_post_init__(self):
        with self.fh.seek_ctx(0):
            hdr_buf = self.fh.read()
        self.hdr = XARHeader.parse(hdr_buf)
        print(f"hdr: {self.hdr}")
        print(f"self.fh: {self.fh} self.fh.seek_ctx: {self.fh.seek_ctx}")
        xml_comp_fh = OffsetRawIOBase(self.fh, self.hdr.size, self.hdr.toc_length_compressed)
        # print(f"xml_comp_fh: {xml_comp_fh[:4].hex()}")
        xml_comp_buf = xml_comp_fh.read()
        print(f"len(xml_comp_buf): {len(xml_comp_buf)} {len(xml_comp_fh[:])}")
        xml = zlib.decompress(xml_comp_fh[:]).decode('utf-8')
        with open('toc.xml', 'w') as toc_fh:
            toc_fh.write(xml)
        self.toc = XARTOC.from_xml(xml)


@define
class XARFS(fs.base.FS):
    file: Final[FancyRawIOBase]
    xar: Final[XARFile] = field(init=False)

    def __attrs_post_init__(self):
        if not isinstance(self.file, BinaryIO):
            self.file = FancyRawIOBase(io.FileIO(self.file, 'r'))
        self.xar = XARFile(self.file)

    def getinfo(self, path: str, namespaces: Optional[Collection[str]] = None) -> Info:
        ino = self.xar.toc.rootfs.lookup(path)
        if ino is None:
            raise ResourceNotFound(path)
        return Info({"basic": {"name": ino.name, "is_dir": ino.is_dir},
                     "details": {"type": ino.pyfs_type, "size": ino.size}})

    def listdir(self, path: str) -> [str]:
        ino = self.xar.toc.rootfs.lookup(path)
        if ino is None:
            raise ResourceNotFound(path)
        return [ino.name for ino in ino.children]

    def makedir(self, path: str, permissions: Optional[Permissions] = None, recreate: bool = False) -> SubFS[FS]:
        raise NotWriteable("XAR supports only reading")

    def openbin(self, path: str, mode: str = "r", buffering: int = -1, **kwargs) -> BinaryIO:
        raise NotImplementedError

    def remove(self, path: str) -> None:
        raise NotWriteable("XAR supports only reading")

    def removedir(self, path: str) -> None:
        raise NotWriteable("XAR supports only reading")

    def setinfo(self, path: str, info: Mapping[str, Mapping[str, object]]) -> None:
        raise NotWriteable("XAR supports only reading")


# @fs.opener.registry.install
class XARFSOpener(fs.opener.Opener):
    protocols = ["xar"]

    def open_fs(self, fs_url: str, parse_result: ParseResult, writeable: bool, create: bool, cwd: str):
        if create or writeable:
            raise NotWriteable("XAR supports only reading")
        return XARFS(parse_result.resource)
