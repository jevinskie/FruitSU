#!/usr/bin/env python3

import io
from typing import IO

import attr
from construct import *
from rich import print as rprint
from rich import inspect as rinspect

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
    'data_chksum_type' / Int32ub,
    'data_chksum_sz' / Int32ub,
    'data_chksum' / Array(32, Int32ub),
    'xml_off' / Int64ub,
    'xml_sz' / Int64ub,
    'reserved1' / Const(b'\0' * 120),
    'chksum_type' / Int32ub,
    'chksum_sz' / Int32ub,
    'chksum' / Array(32, Int32ub),
    'image_variant' / Int32ub,
    'sector_count' / Int64ub,
    'reserved2' / Const(0, Int32ub),
    'reserved3' / Const(0, Int32ub),
    'reserved4' / Const(0, Int32ub),
)

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

def dmg_func(dmg_path):
    print(f'dmg_func() __package__: {__package__}')
    dmg = DMG(dmg_path)
    print(f'dmg: {dmg}')


def dmg_main(dmg_path):
    print(f'dmg_main(\'{dmg_path}\')')
    return 0


if __name__ == '__main__':
    sys.exit(dmg_main(sys.argv[1]))
