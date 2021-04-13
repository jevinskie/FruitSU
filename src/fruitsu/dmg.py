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
    'reserved1' / Const(b'\0' * 120),
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
    sparse=0x00000002,
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
        sz = hdr.sector_count * SECTOR_SIZE
        with mmap.mmap(-1, sz) as mm:
            mmty = c_uint8 * len(mm)
            ptr = mmty.from_buffer(mm)
            # mv = memoryview(mm)
            print(f'ptr {ptr}')
            memset(ptr, ord('U'), sz)
            del ptr
            print(f'mm: {mm}')
            for blk_info in plist['resource-fork']['blkx']:
                data = blk_info['Data']
                if len(data) >= 4 and data[:4] == b'mish':
                    print('got mish block')
                    blkx_table = BLKXTable.parse(data)
                    print(f'blkx_table: {blkx_table}')
            with open('dump.img', 'wb') as dumpf:
                dumpf.write(mm)


def dmg_func(dmg_path):
    print(f'dmg_func() __package__: {__package__}')
    dmg = DMG(dmg_path)
    print(f'dmg: {dmg}')


def dmg_main(dmg_path):
    print(f'dmg_main(\'{dmg_path}\')')
    return 0


if __name__ == '__main__':
    sys.exit(dmg_main(sys.argv[1]))
