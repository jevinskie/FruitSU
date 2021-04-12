#!/usr/bin/env python3

import importlib.resources
import sys

import pytest

from rich import inspect as rinspect
from rich import print

import fruitsu
import fruitsu.dmg


def inc(x):
    return x + 1


def test_answer():
    test_dir = importlib.resources.files(__package__)
    hello_dmg_path = test_dir / 'hello.dmg'
    with open(hello_dmg_path, 'rb') as dmg_fh:
        dmg = fruitsu.dmg.DMG(dmg_fh)
        print(f'dmg: {dmg}')
        dmg.dump()
    fruitsu.dmg.dmg_func('foo.dmg')
    print('test_answer() WOOHOO!!!!')
    assert inc(3) == 4


if __name__ == '__main__':
    args = sys.argv
    print(f'pytest.main args: {args}')
    sys.exit(pytest.main(args))
