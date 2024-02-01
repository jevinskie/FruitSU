import argparse

from rich import print

import fruitsu.hfs
from fruitsu.io import OffsetRawIOBase


def real_main(args):
    with open(args.path, "rb") as hfs_fh:
        hfs = fruitsu.hfs.HFS(OffsetRawIOBase(hfs_fh))
        print(f"hfs: {hfs}")
        hfs.dump()


def main():
    parser = argparse.ArgumentParser(description="FruitSU")
    parser.add_argument("path", type=str, help="Input HFS image", metavar="HFS_IMG")
    real_main(parser.parse_args())
    return 0
