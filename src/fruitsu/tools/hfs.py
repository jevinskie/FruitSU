import argparse
import logging
import sys
from typing import Final

from packaging.version import Version
from path import Path
from rich import print
from rich.console import Console
from rich.logging import RichHandler

from .. import _version, hfs
from ..io import OffsetRawIOBase

LOG_FORMAT = "%(message)s"
logging.basicConfig(
    level=logging.WARNING,
    format=LOG_FORMAT,
    datefmt="[%X]",
    handlers=[RichHandler(console=Console(stderr=True), rich_tracebacks=True)],
)

program_name = "fruitsu-hfs"

log = logging.getLogger(program_name)


def get_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=program_name)
    parser.add_argument("path", type=Path, help="input HFS image", metavar="HFS_IMG")
    parser.add_argument("-v", "--verbose", action="store_true", help="be verbose")
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s version: {Version(_version.version)}",
    )
    return parser


def real_main(args: argparse.Namespace) -> int:
    verbose: Final[bool] = args.verbose
    if verbose:
        log.setLevel(logging.INFO)
        log.info(f"{program_name}: verbose mode enabled")
    if args.version:
        print(f"{program_name} version: {Version(_version.version)}")
        return 0
    with open(args.path, "rb") as hfs_fh:
        hfs_file = hfs.HFS(OffsetRawIOBase(hfs_fh))
        print(f"hfs: {hfs_file}")
        hfs_file.dump()
    return 0


def main() -> int:
    try:
        args = get_arg_parser().parse_args()
        return real_main(args)
    except Exception:
        log.exception(f"Received an unexpected exception when running {program_name}")
        return 1
    except KeyboardInterrupt:
        return 0


if __name__ == "__main__":
    sys.exit(main())
