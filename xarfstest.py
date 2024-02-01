#!/usr/bin/env python3

import fs
from fruitsu.xar import XARFSOpener

assert XARFSOpener is not None

xarfs = fs.open_fs("xar://tests/fruitsu/hello-bz2.xar")

xarfs.tree()
