#!/usr/bin/env python3

import importlib.resources
import sys

import pytest
from fruitsu.xar import XARFile
from rich import print


def test_xar_etc():
    test_dir = importlib.resources.files(__package__)
    etc_xar_path = test_dir / "hello-bz2.xar"
    with open(etc_xar_path, "rb") as xar_fh:
        xar = XARFile(xar_fh.raw)
        print(f"xar: {xar}")
        # xar.dump()
        xar.toc.rootfs.dump()


if __name__ == "__main__":
    args = sys.argv
    print(f"pytest.main args: {args}")
    sys.exit(pytest.main(args))
