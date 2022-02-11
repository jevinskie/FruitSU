import importlib.resources

import pytest

from rich import print

from fruitsu.xar import XARFile


def test_xar_etc():
    test_dir = importlib.resources.files(__package__)
    etc_xar_path = test_dir / 'etc.xar'
    with open(etc_xar_path, 'rb') as xar_fh:
        xar = XARFile(xar_fh.raw)
        print(f'xar: {xar}')
        xar.dump()
