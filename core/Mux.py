import functools
import operator

from core.Bits import _Bits, Bits
from core.Bool import _Bool, Bool
from core.Data import Data
from core.utils import *


def Mux(cond: _Bool, con: Data, alt: Data) -> Data:
    r = con.cloneTypeWidth(-1)
    args = [cond.ref, con.ref, alt.ref]
    if isinstance(con, _Bits):
        pushCommand(DefPrimPad(r.defined().idx, r.toType(), PrimOp.MultiplexOp, args, NoLits))
    else:
        pushCommand(DefPrim(r.defined().idx, r.toType(), PrimOp.MultiplexOp, args, NoLits))
    return r


def PriorityMux(din, sel=None) -> Data:
    din = list(din)
    if sel is None:
        head_b, head_d = tuple(din[0])
        if len(din) == 1:
            return head_d
        else:
            return Mux(head_b, head_d, PriorityMux(din[1:]))
    elif isinstance(sel, _Bits):
        return PriorityMux([sel(x) for x in range(len(din))], din)
    else:
        return PriorityMux(zip(sel, din))


def Mux1H(din, sel=None) -> Data:
    if sel is None:
        din: list[tuple[_Bool, Data]] = list(din)
        sel: list[_Bool] = [d[0] for d in din]
        data: list[Data] = [d[1] for d in din]
        return Mux1H(data, sel)
    elif isinstance(sel, _Bits) and isinstance(din, _Bits):
        return (sel & din).orR()
    else:
        sel: list[_Bool] = list(sel)
        din: list[Data] = list(din)
        if len(din) == 1:
            return din[0]
        else:
            mask = [Mux(s, x.toBits(), Bits(0)) for s, x in zip(sel, din)]
            return din[0].fromBits(functools.reduce(operator.or_, mask))
