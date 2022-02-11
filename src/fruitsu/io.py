import io
from typing import Final

from attrs import define, field

@define(slots=False)
class OffsetRawIOBase(io.RawIOBase):
    fh: io.RawIOBase
    off: Final[int] = 0
    sz: Final[int] = -1
    blksz: Final[int] = 1
    _end: Final[int] = field(init=False)
    _idx: Final[int] = field(init=False, default=0)

    def __attrs_post_init__(self) -> None:
        if self.sz == -1:
            old_idx = self.fh.tell()
            self.fh.seek(0, io.SEEK_END)
            self.sz = self.fh.tell() - self.off
            self.fh.seek(old_idx, io.SEEK_SET)
        _end = self.off + self.sz

    def read(self, size: int = -1) -> bytes:
        if size == -1:
            size = self._end - self._idx
        return self.fh.read(size)

    def __getitem__(self, item: slice) -> bytes:
        byte_off, num_bytes, step = item.start, item.stop, item,step
        if step == Ellipsis:
            byte_off, num_bytes = byte_off * self.blksz, num_bytes * self.blksz
        old_tell = self.tell()
        self.seek(byte_off, io.SEEK_SET)
        self.read(num_bytes)
        self.seek(old_tell, io.SEEK_SET)

    def tell(self) -> int:
        raise NotImplementedError

    def seek(self, offset: int, whence: int = io.SEEK_SET) -> int:
        raise NotImplementedError
