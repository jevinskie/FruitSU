
import bz2
import enum
import lzma
from pathlib import Path
from typing import Final, Optional, Collection
import zlib

from anytree import RenderTree
from attrs import define, field
from construct import *
import fs.base
from fs.base import FS, SubFS, Permissions, RawInfo, Info, BinaryIO
from fs.opener.errors import *
from fs.opener.parse import ParseResult, ParseError
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
    toc: untangle.Element = field(init=False)

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
    resource: Final[str]

    def __attrs_post_init(self):
        print(f"XARFS resource: {self.resource}")

    def getinfo(self, path:str , namespaces: Optional[Collection[str]] = None) -> Info:
        pass

    def listdir(self, path: str) -> [str]:
        pass

    def makedir(self, path: str, permissions: Optional[Permissions] = None, recreate: bool = False) -> SubFS[FS]:
        pass

    def openbin(self, path: str, mode: str = "r", buffering: int = -1, **kwargs) -> BinaryIO:
        pass

    def remove(self, path: str) -> None:
        pass

    def removedir(self, path: str) -> None:
        pass

    def setinfo(self, path: str, info: RawInfo) -> None:
        pass


@fs.opener.registry.install
class XARFSOpener(fs.opener.Opener):
    protocols = ["xar"]

    def open_fs(self, fs_url: str, parse_result: ParseResult, writeable: bool, create: bool, cwd: str):
        if create or writeable:
            raise NotWriteable("XAR supports only reading")
        return XARFS(parse_result.resource)
