#!/usr/bin/env python3

import importlib.resources
import sys

import pytest

from rich import inspect as rinspect
from rich import print

import tests
# import testsz
import fruitsu
import fruitsu.dmg


def inc(x):
    return x + 1


def test_answer():
    # rinspect(fruitsu)
    # rinspect(fruitsu.dmg)
    files = importlib.resources.files(fruitsu)
    print(f'self files: {files}')
    print(f'__package__: {__package__}')
    files2 = importlib.resources.files(__package__)
    print(f'self self files2: {files2}')
    print(f'sys.path: {sys.path} argv: {sys.argv}')
    fruitsu.dmg.dmg_func('foo.dmg')
    print('test_answer() WOOHOO!!!!')
    assert inc(3) == 4


if __name__ == '__main__':
    args = sys.argv
    print(f'pytest.main args: {args}')
    sys.exit(pytest.main(args))
