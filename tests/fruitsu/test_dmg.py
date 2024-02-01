#!/usr/bin/env python3

import importlib.resources
import sys

import fruitsu.dmg
import pytest
from rich import print


def inc(x):
    return x + 1


def test_dmg():
    test_dir = importlib.resources.files(__package__)
    hello_dmg_path = test_dir / "hello.dmg"
    # hello_dmg_path = test_dir / 'InstallESD.dmg'
    with open(hello_dmg_path, "rb") as dmg_fh:
        dmg = fruitsu.dmg.DMG(dmg_fh)
        print(f"dmg: {dmg}")
        dmg.dump()


if __name__ == "__main__":
    args = sys.argv
    print(f"pytest.main args: {args}")
    sys.exit(pytest.main(args))
