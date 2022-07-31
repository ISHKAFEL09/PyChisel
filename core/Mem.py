from core.Bits import _Bits
from core.Data import Data
from core.utils import *


class _Mem:
    def __init__(self, mt: Data, n: int):
        self.mt = mt
        self.size = n

    def __call__(self, ids: '_Bits') -> Data:
        x = self.mt.cloneType()
        pushCommand(DefAccessor(x.defined().idx, Alias(self.mt.idx), NO_DIR, ids.ref))
        return x

    @property
    def name(self):
        return getRefID(self.mt.idx).name

    @property
    def debugName(self):
        return f'{self.mt.mod.debugName!r}.{self.name!r}'


def Mem(t: Data, size: int) -> _Mem:
    mt = t.cloneType()
    mem = _Mem(mt, size)
    pushCommand(DefMemory(mt.defined().idx, mt.toType(), size))
    return mem
