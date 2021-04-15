#!/usr/bin/env python3

import io
import mmap
from typing import IO, Final, Union
import zlib

import attr
from construct import *
from rich import print as rprint
from rich import inspect as rinspect

# struct HFSPlusVolumeHeader {
#   UInt16 signature;
#   UInt16 version;
#   UInt32 attributes;
#   UInt32 lastMountedVersion;
#   UInt32 journalInfoBlock;
#
#   UInt32 createDate;
#   UInt32 modifyDate;
#   UInt32 backupDate;
#   UInt32 checkedDate;
#
#   UInt32 fileCount;
#   UInt32 folderCount;
#
#   UInt32 blockSize;
#   UInt32 totalBlocks;
#   UInt32 freeBlocks;
#
#   UInt32 nextAllocation;
#   UInt32 rsrcClumpSize;
#   UInt32 dataClumpSize;
#   HFSCatalogNodeID nextCatalogID;
#
#   UInt32 writeCount;
#   UInt64 encodingsBitmap;
#
#   UInt32 finderInfo[8];
#
#   HFSPlusForkData allocationFile;
#   HFSPlusForkData extentsFile;
#   HFSPlusForkData catalogFile;
#   HFSPlusForkData attributesFile;
#   HFSPlusForkData startupFile;
# };

# struct HFSPlusExtentDescriptor {
#   UInt32 startBlock;
#   UInt32 blockCount;
# };

# typedef HFSPlusExtentDescriptor HFSPlusExtentRecord[8];
# struct HFSPlusForkData {
#   UInt64 logicalSize;
#   UInt32 clumpSize;
#   UInt32 totalBlocks;
#   HFSPlusExtentRecord extents;
# };

HFSCatalogNodeID = Int32ub

HFSPlusExtentDescriptor = Struct(
    'startBlock' / Int32ub,
    'blockCount' / Int32ub,
)

HFSPlusExtentRecord = HFSPlusExtentDescriptor[8]

HFSPlusForkData = Struct(
    'logicalSize' / Int64ub,
    'clumpSize' / Int32ub,
    'totalBlocks' / Int32ub,
    'extents' / HFSPlusExtentRecord,
)

HFSPlusVolumeHeader = Struct(
    'signature' / Const(b'H+'),
    'version' / Int16ub,
    'attributes' / Int32ub,
    'lastMountedVersion' / Int32ub,
    'jounalInfoBlock' / Int32ub,
    'createDate' / Int32ub,
    'modifyDate' / Int32ub,
    'backupDate' / Int32ub,
    'checkedDate' / Int32ub,
    'fileCount' / Int32ub,
    'folderCount' / Int32ub,
    'blockSize' / Int32ub,
    'totalBlocks' / Int32ub,
    'freeBlocks' / Int32ub,
    'nextAllocation' / Int32ub,
    'rsrcClumpSize' / Int32ub,
    'dataClumpSize' / Int32ub,
    'nextCatalogID' / HFSCatalogNodeID,
    'writeCount' / Int32ub,
    'encodingsBitmap' / Int64ub,
    'finderInfo' / Int32ub[8],
    'allocationFile' / HFSPlusForkData,
    'extentsFile' / HFSPlusForkData,
    'catalogFile' / HFSPlusForkData,
    'attributesFile' / HFSPlusForkData,
    'statupFile' / HFSPlusForkData,
)


@attr.s
class HFS:
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
        self.fh.seek(1024, io.SEEK_SET)
        buf = self.fh.read(HFSPlusVolumeHeader.sizeof())
        print(f'HFSPlusVolumeHeader sz: {HFSPlusVolumeHeader.sizeof()}')
        print(f'buf: {buf.hex()}')
        hdr = HFSPlusVolumeHeader.parse(buf)
        print(f'hdr: {hdr}')
