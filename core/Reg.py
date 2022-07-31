from core.utils import *


def Reg(out: 'Data' = None, nxt: 'Data' = None, init: 'Data' = None) -> 'Data':
    mtype = out
    if mtype is None:
        mtype = nxt
    if mtype is None:
        mtype = init
    if mtype is None:
        raise TypeError('Cannot infer type of Reg.')
    x = mtype.cloneType()
    x._isReg = True
    pushCommand(DefRegister(x.defined().idx, x.toType()))
    if init is not None:
        pushCommand(ConnectInit(x.ref, init.ref))
    if nxt is not None:
        pushCommand(ConnectPad(x.ref, nxt.ref))
    return x
