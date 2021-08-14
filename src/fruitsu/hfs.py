#!/usr/bin/env python3

import datetime
import io
import math
import mmap
from typing import IO, Final

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

# struct HFSUniStr255 {
#   UInt16 length;
#   UniChar unicode[255];
# };

HFSUniStr255 = PaddedString(255, 'utf16')

# HFS epoch: January 1, 1904, GMT
# 24,107 days before 1970-01-01T00:00:00
# 2,082,844,800 seconds before 1970-01-01T00:00:00

HFSEpochUnixEpochSecondsDelta: Final[int] = 2_082_844_800

HFSEpoch = datetime.datetime(1904, 1, 1, 0, 0, 0)
UnixEpoch = datetime.datetime(1970, 1, 1, 0, 0, 0)
HFSEpochUnixEpochDelta = UnixEpoch - HFSEpoch
print(f'HFSEpochUnixEpochDelta: {HFSEpochUnixEpochDelta}')


class HFSDateAdapter(Adapter):
    def _decode(self, obj, context, path) -> datetime.datetime:
        return HFSEpoch + datetime.timedelta(seconds=obj)

    def _encode(self, obj: datetime.datetime, context, path):
        td = obj - HFSEpoch
        return int(math.ceil(td.total_seconds()))


HFSDate = HFSDateAdapter(Int32ub)

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
    'createDate' / HFSDate,
    'modifyDate' / HFSDate,
    'backupDate' / HFSDate,
    'checkedDate' / HFSDate,
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
    'startupFile' / HFSPlusForkData,
)

HFSPlusCatalogKey = Struct(
    'keyLength' / Int16ub,
    'parentID' / HFSCatalogNodeID,
    'nodeName' / HFSUniStr255,
)

kMaxKeyLength: Final = 520

BTNodeID = Int32ub

BTNodeKind = Enum(Int8sb,
    kBTLeafNode = -1,
    kBTIndexNode = 0,
    kBTHeaderNode = 1,
    kBTMapNode = 2,
)

BTNodeDescriptor = Struct(
    'fLink' / BTNodeID,
    'bLink' / BTNodeID,
    'kind' / BTNodeKind,
    'height' / Int8ub,
    'numRecords' / Int16ub,
    'reserved' / Int16ub,
)

# struct BTHeaderRec {
# 	u_int16_t	treeDepth;		/* maximum height (usually leaf nodes) */
# 	u_int32_t 	rootNode;		/* node number of root node */
# 	u_int32_t 	leafRecords;		/* number of leaf records in all leaf nodes */
# 	u_int32_t 	firstLeafNode;		/* node number of first leaf node */
# 	u_int32_t 	lastLeafNode;		/* node number of last leaf node */
# 	u_int16_t 	nodeSize;		/* size of a node, in bytes */
# 	u_int16_t 	maxKeyLength;		/* reserved */
# 	u_int32_t 	totalNodes;		/* total number of nodes in tree */
# 	u_int32_t 	freeNodes;		/* number of unused (free) nodes in tree */
# 	u_int16_t 	reserved1;		/* unused */
# 	u_int32_t 	clumpSize;		/* reserved */
# 	u_int8_t 	btreeType;		/* reserved */
# 	u_int8_t 	keyCompareType;		/* Key string Comparison Type */
# 	u_int32_t 	attributes;		/* persistent attributes about the tree */
# 	u_int32_t 	reserved3[16];		/* reserved */

BTHeaderRec = Struct(
    'treeDepth' / Int16ub,
    'rootNode' / Int32ub,
    'leafRecords' / Int32ub,
    'firstLeafNode' / Int32ub,
    'lastLeafNone' / Int32ub,
    'nodeSize' / Int16ub,
    'maxKeyLength' / Int16ub,
    'totalNodes' / Int32ub,
    'freeNodes' / Int32ub,
    'reserved1' / Int16ub,
    'clumpSize' / Int32ub,
    'btreeType' / Int8ub,
    'keyCompareType' / Int8ub,
    'attributes' / Int32ub,
    'reserved3' / Int32ub[16],
)

BTreeKey = Union('rawData',
    'length8' / Int8ub,
    'length16' / Int16ub,
    'rawData' / Byte[kMaxKeyLength+2],
)


@attr.s
class HFS:
    fh: IO[bytes] = attr.ib()
    buf: bytes = attr.ib(init=False)
    sz: Final[int] = attr.ib(init=False)
    hdr_buf: Final[bytes] = attr.ib(init=False, repr=False)
    hdr: HFSPlusVolumeHeader = attr.ib(init=False, repr=False)

    def __attrs_post_init__(self):
        old_tell = self.fh.tell()
        self.fh.seek(0, io.SEEK_END)
        self.sz = self.fh.tell()
        self.fh.seek(1024, io.SEEK_SET)
        self.hdr_buf = self.fh.read(HFSPlusVolumeHeader.sizeof())
        self.fh.seek(old_tell, io.SEEK_SET)
        self.buf = mmap.mmap(self.fh.fileno(), self.sz, mmap.MAP_PRIVATE, mmap.PROT_READ)
        self.hdr = HFSPlusVolumeHeader.parse(self.hdr_buf)

    def dump(self):
        print(f'dumping: {self}')
        print(f'HFSPlusVolumeHeader sz: {HFSPlusVolumeHeader.sizeof()}')
        print(f'buf: {self.hdr_buf.hex()}')
        print(f'hdr: {self.hdr}')
        blk_off = self.hdr.catalogFile.extents[0].startBlock * self.hdr.blockSize
        blk_cnt = self.hdr.catalogFile.extents[0].blockCount
        blk_byte_sz = blk_cnt * self.hdr.blockSize
        assert blk_cnt > 0
        assert self.hdr.catalogFile.extents[1].blockCount == 0
        cat_buf = self.buf[blk_off:blk_off+self.hdr.catalogFile.logicalSize]
        print(f'len(cat_buf) = {len(cat_buf)}')
        with open('cat_buf.bin', 'wb') as f:
            f.write(cat_buf)

        root_node = BTNodeDescriptor.parse(cat_buf)
        print(f'root_node: {root_node}')

        first_bthdrrec = BTHeaderRec.parse(cat_buf[14:])
        print(f'first_bthdrrec: {first_bthdrrec}')

        # root_cat_key = BTreeKey.parse(cat_buf)
        # print(f'root_cat_key: {root_cat_key}')
