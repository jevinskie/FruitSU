#!/usr/bin/env python3

import sys

import pytest

def inc(x):
    return x + 1


def test_answer():
    print('test_answer() WOOHOO!!!!')
    assert inc(3) == 4

if __name__ == '__main__':
	args = sys.argv
	print(f'pytest.main args: {args}')
	sys.exit(pytest.main(args))
