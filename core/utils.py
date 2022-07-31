from typing import Iterable

from core.builder import *


def Cat(*r: '_Bits') -> '_Bits':
    if not r:
        raise ValueError('Empty Cat!')

    def doCat(*t: '_Bits') -> '_Bits':
        if len(t) == 1:
            return t[0]
        else:
            sl = len(t) / 2
            low = doCat(*t[0:sl])
            high = doCat(*t[sl:len(t)])
            is_const = low.isLitValue and high.isLitValue
            w = low.getWidth() + high.getWidth() if is_const else -1
            d = low.cloneType_with(w)
            if is_const:
                d.setLitValue((low.litValue << low.getWidth()) | high.litValue)
            pushCommand(DefPrim(d.idx, d.toType(), PrimOp.ConcatOp, [low.ref, high.ref], []))
            return d

    return doCat(*r)


def chiselCast(fr, to):
    pushCommand(DefWire(to.defined().idx, to.toType()))
    b = fr.toBits()
    pushCommand(Connect(to.ref, b.ref))
    return to


def PopCount(ins) -> '_UInt':
    from core.Bits import _Bits
    from core.UInt import UInt
    if isinstance(ins, _Bits):
        return PopCount([ins(idx) for idx in range(ins.getWidth())])
    size = len(ins)
    if size == 0:
        return UInt(0)
    elif size == 1:
        return ins[0]
    else:
        return PopCount(ins[0:size / 2]) + Cat(UInt(0), PopCount(ins[size / 2:size]))
