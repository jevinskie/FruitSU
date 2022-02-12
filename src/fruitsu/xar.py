
import bz2
import enum
import lzma
from pathlib import Path
from typing import Final
import zlib

from anytree import RenderTree
from attrs import define, field
from construct import *
import untangle

from rich import (
    print as rprint,
    inspect as rinspect,
)

from .io import FancyRawIOBase, OffsetRawIOBase
from .fstree import INode, DirEntType


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
        for f in xml.xar.toc.file:
            name = f.name.cdata
            ty = {
                'directory': DirEntType.DIR,
                'file': DirEntType.REG,
                'link': DirEntType.LNK,
            }[f.type.cdata]
            sz = 0
            sz_comp = None
            if ty == DirEntType.REG:
                sz = int(f.data.size.cdata)
                if f.data.encoding["style"] != "application/octet-stream":
                    sz_comp = int(f.data.length.cdata)
            INode(parent=root, name=name, size=sz, size_comp=sz_comp, type=ty)
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
        print(f"xml_comp_fh: {xml_comp_fh[:4].hex()}")
        xml_comp_buf = xml_comp_fh[:]
        print(f"len(xml_comp_buf): {len(xml_comp_buf)}")
        xml = zlib.decompress(xml_comp_fh[:]).decode('utf-8')
        with open('toc.xml', 'w') as toc_fh:
            toc_fh.write(xml)
        self.toc = XARTOC.from_xml(xml)


__all__ = [
    "ChecksumAlgorithmEnum",
    "ChecksumAlgorithm",
    "XARTOC",
    "XARFile",
    "XARHeader",
]
