#!/usr/bin/env python3

import sys

def dmg_func():
    print('dmg_func()')

def dmg_main(dmg_path):
    print(f'dmg_main(\'{dmg_path}\')')
    return 0

if __name__ == '__main__':
    sys.exit(dmg_main(sys.argv[1]))
