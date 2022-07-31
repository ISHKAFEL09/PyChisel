from core.utils import *


def Wire(t: 'Data' = None, init: 'Data' = None) -> 'Data':
    mtype = init if t is None else t
    if mtype is None:
        raise TypeError('Cannot infer type of init.')
    x = mtype.cloneType()
    x.collectElms()
    pushCommand(DefWire(x.defined().idx, x.toType()))
    if init:
        pushCommand(Connect(x.ref, init.ref))
    return x
