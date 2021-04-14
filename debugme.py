#!/usr/bin/env python3

import fruitsu.dmg

with open('tests/fruitsu/hello.dmg', 'rb') as dmg_fh:
    dmg = fruitsu.dmg.DMG(dmg_fh)
    dmg.dump()
