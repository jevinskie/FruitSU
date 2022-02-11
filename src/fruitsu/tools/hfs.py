import argparse
import sys

from rich import inspect as rinspect
from rich import print

import fruitsu.hfs

def real_main(args):
    with open(args.path, 'rb') as hfs_fh:
        hfs = fruitsu.hfs.HFS(hfs_fh)
        print(f'hfs: {hfs}')
        hfs.dump()

def main():
    parser = argparse.ArgumentParser(
        description="FruitSU"
    )
    parser.add_argument('path', type=str, help='Input HFS image', metavar='HFS_IMG')
    real_main(parser.parse_args())
    return 0
