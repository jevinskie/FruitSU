#!/usr/bin/env python3

import fs
from fruitsu.xar import *

xarfs = fs.open_fs("xar://tests/fruitsu/hello-bz2.xar")

xarfs.tree()
