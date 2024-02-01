import importlib.resources

from fruitsu.xar import XARFile
from rich import print


def test_xar_etc():
    test_dir = importlib.resources.files(__package__)
    etc_xar_path = test_dir / "hello-bz2.xar"
    with open(etc_xar_path, "rb") as xar_fh:
        xar = XARFile(xar_fh.raw)
        print(f"xar: {xar}")
        # xar.dump()
        xar.toc.rootfs.dump()
