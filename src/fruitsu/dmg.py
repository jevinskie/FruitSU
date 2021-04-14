#!/usr/bin/env python3

from ctypes import c_int, c_char, c_uint8, memset
import io
import mmap
import plistlib
from typing import IO, Final
import zlib

import attr
from construct import *
from rich import print as rprint
from rich import inspect as rinspect

SECTOR_SIZE: Final[int] = 512

UDIFChecksum = Struct(
    'chksum_type' / Int32ub,
    'chksum_sz' / Int32ub,
    'chksum' / Array(32, Int32ub),
)

UDIFResourceFile = Struct(
    'signature' / Const(b'koly'),
    'version' / Int32ub,
    'header_sz' / Const(512, Int32ub),
    'flags' / Int32ub,
    'running_data_fork_off' / Int64ub,
    'data_fork_off' / Int64ub,
    'data_fork_sz' / Int64ub,
    'rsrc_fork_off' / Int64ub,
    'rsc_fork_sz' / Int64ub,
    'seg_num' / Int32ub,
    'seg_count' / Int32ub,
    'seg_id' / Bytes(16),
    'data_chksum' / UDIFChecksum,
    'plist_off' / Int64ub,
    'plist_sz' / Int64ub,
    'external' / Bytes(64),
    'codesign_off' / Int64ub,
    'codesign_sz' / Int64ub,
    'reserved1' / Const(b'\0' * 40),
    'chksum' / UDIFChecksum,
    'image_variant' / Int32ub,
    'sector_count' / Int64ub,
    'reserved2' / Const(0, Int32ub),
    'reserved3' / Const(0, Int32ub),
    'reserved4' / Const(0, Int32ub),
)

BLKXChunkEntryType = Enum(
    Int32ub,
    zero=0x00000000,
    raw=0x00000001,
    ignore=0x00000002,
    comment=0x7ffffffe,
    adc=0x80000004,
    zlib=0x80000005,
    bzip2=0x80000006,
    lzfse=0x80000007,
    lzma=0x80000008,
    terminator=0xffffffff,
)

BLKXChunkEntry = Struct(
    'entry_type' / BLKXChunkEntryType,
    'comment' / Int32ub,
    'sector_num' / Int64ub,
    'sector_count' / Int64ub,
    'compressed_off' / Int64ub,
    'compressed_sz' / Int64ub,
)

BLKXTable = Struct(
    'signature' / Const(b'mish'),
    'version' / Int32ub,
    'sector_num' / Int64ub,
    'sector_count' / Int64ub,
    'data_off' / Int64ub,
    'buffers_needed' / Int32ub,
    'block_descriptors' / Int32ub,
    'reserved' / Const(b'\0' * 4 * 6),
    'chksum' / UDIFChecksum,
    'num_block_chunks' / Int32ub,
    'block_chunks' / Array(this.num_block_chunks, BLKXChunkEntry),
)

assert UDIFResourceFile.sizeof() == 512


@attr.s
class DMG:
    fh: IO[bytes] = attr.ib()
    buf: bytes = attr.ib(init=False)
    sz: Final[int] = attr.ib(init=False)

    def __attrs_post_init__(self):
        self.fh.seek(0, io.SEEK_END)
        self.sz = self.fh.tell()
        self.sz = 0
        self.fh.seek(0, io.SEEK_SET)
        self.buf = mmap.mmap(self.fh.fileno(), self.sz, mmap.MAP_PRIVATE, mmap.PROT_READ)

    def dump(self):
        print(f'dumping: {self}')
        self.fh.seek(-512, io.SEEK_END)
        buf = self.fh.read(512)
        print(f'UDIFResourceFile sz: {UDIFResourceFile.sizeof()}')
        print(f'buf: {buf.hex()}')
        hdr = UDIFResourceFile.parse(buf)
        print(f'hdr: {hdr}')
        self.fh.seek(hdr.plist_off, io.SEEK_SET)
        plist_buf = self.fh.read(hdr.plist_sz)
        plist_str = plist_buf.decode()
        # print(f'plist_str: {plist_str}')
        plist = plistlib.loads(plist_buf)
        # print(f'plist: {plist}')
        dmg_sz = hdr.sector_count * SECTOR_SIZE
        with mmap.mmap(-1, dmg_sz) as dmg_wbuf:
            dmg_mmty = c_uint8 * dmg_sz
            dmg_ptr = dmg_mmty.from_buffer(dmg_wbuf)
            memset(dmg_ptr, ord('Z'), dmg_sz)
            del dmg_ptr
            for blk_idx, blk_info in enumerate(plist['resource-fork']['blkx']):
                blk_data = blk_info['Data']
                assert len(blk_data) >= 4 and blk_data[:4] == b'mish'
                blkx_table = BLKXTable.parse(blk_data)
                print(f'blkx_table: {blkx_table}')
                part_sz = blkx_table.sector_count * SECTOR_SIZE
                with mmap.mmap(-1, part_sz) as mm:
                    mmty = c_uint8 * part_sz
                    ptr = mmty.from_buffer(mm)
                    memset(ptr, ord('U'), part_sz)
                    del ptr
                    for chunk in blkx_table.block_chunks:
                        print(f'chunk: {chunk}')
                        sn = chunk.sector_num
                        sc = chunk.sector_count
                        sz = sc * SECTOR_SIZE
                        off = sn * SECTOR_SIZE
                        coff = chunk.compressed_off
                        csz = chunk.compressed_sz
                        cty = chunk.entry_type
                        roff = blkx_table.sector_num * SECTOR_SIZE + off
                        scratch = b'X' * sz
                        mm[off:off + sz] = scratch
                        dmg_wbuf[off:off + sz] = scratch
                        if cty == BLKXChunkEntryType.ignore:
                            # mm[off:off + sz] = self.buf[roff:roff+sz]
                            # dmg_wbuf[roff:roff+sz] = mm[off:off + sz]
                            hashes = b'\x00' * sz
                            mm[off:off + sz] = hashes
                            dmg_wbuf[roff:roff + sz] = hashes
                        elif cty == BLKXChunkEntryType.zlib:
                            decomp = zlib.decompress(self.buf[coff:coff+csz])
                            mm[off:off + sz] = decomp
                            dmg_wbuf[roff:roff + sz] = decomp
                        elif cty == BLKXChunkEntryType.zero:
                            zeros = b'\x00' * sz
                            mm[off:off + sz] = zeros
                            dmg_wbuf[roff:roff + sz] = zeros
                        elif cty == BLKXChunkEntryType.terminator:
                            # no need to do anything
                            pass
                        else:
                            print(f'unhandled block run type: {cty}')
                    with open(f'dump-{blk_idx}.img', 'wb') as dumpf:
                        dumpf.write(mm)
            with open('dump-whole.img', 'wb') as dumpf:
                dumpf.write(dmg_wbuf)
