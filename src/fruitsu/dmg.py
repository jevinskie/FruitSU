#!/usr/bin/env python3

import sys

import attr

@attr.s
class DMG:
    path: str = attr.ib()


def dmg_func(dmg_path):
    print(f'dmg_func() __package__: {__package__}')
    dmg = DMG(dmg_path)
    print(f'dmg: {dmg}')


def dmg_main(dmg_path):
    print(f'dmg_main(\'{dmg_path}\')')
    return 0


if __name__ == '__main__':
    sys.exit(dmg_main(sys.argv[1]))
