#!/usr/bin/env python3

import importlib.resources
import sys

import fruitsu.hfs
import pytest
from rich import print


def test_dmg():
    test_dir = importlib.resources.files(__package__)
    hello_hfs_part_path = test_dir / "hello-hfs-part.img"
    # hello_hfs_part_path = test_dir / 'InstallESD.dmg'
    with open(hello_hfs_part_path, "rb") as hfs_fh:
        hfs = fruitsu.hfs.HFS(hfs_fh)
        print(f"hfs: {hfs}")
        hfs.dump()


if __name__ == "__main__":
    args = sys.argv
    print(f"pytest.main args: {args}")
    sys.exit(pytest.main(args))
