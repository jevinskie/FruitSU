
import bz2
import enum
import gzip
import lzma
from typing import Final
import zlib

from attrs import define, field
from construct import *
import untangle

from .io import FancyRawIOBase, OffsetRawIOBase

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

    def dump(self):
        print(self)
