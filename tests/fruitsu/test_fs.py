#!/usr/bin/env python3

import importlib.resources
import sys

import pytest
from rich import print


def test_fs():
    test_dir = importlib.resources.files(__package__)
    hello_dmg_path = test_dir / "hello.dmg"
    print(hello_dmg_path)


if __name__ == "__main__":
    args = sys.argv
    print(f"pytest.main args: {args}")
    sys.exit(pytest.main(args))
