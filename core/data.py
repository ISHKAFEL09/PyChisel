from abc import ABC
from functools import cached_property
from typing import Callable

from core import driver
from core.builder import module_stack, push_command
from core.inner_struct import gen_sys
from basic_types import *
from core.params import Parameters


class Id(ABC):
    def __init__(self):
        self.idx = gen_sys('id')
        self._is_defined = False

    def defined(self):
        self._is_defined = True
        return self

    @property
    def is_defined(self):
        return self._is_defined


class Data(Id, ABC):
    def __init__(self, direction: Direction):
        super(Data, self).__init__()
        self.mod = module_stack[-1]
        self._is_flip_var = direction is INPUT
        self._is_reg = False

    @abc.abstractmethod
    def to_type(self) -> Kind: ...

    @abc.abstractmethod
    def clone_type(self) -> 'Data': ...

    @abc.abstractmethod
    def clone_type_with(self, width: int) -> 'Data': ...

    @abc.abstractmethod
    def set_lit_value(self, x: int) -> None: ...

    @abc.abstractmethod
    def get_width(self) -> int: ...

    @abc.abstractmethod
    def flatten(self) -> list['Bits']: ...

    @abc.abstractmethod
    def collect_elements(self) -> None: ...

    @property
    def is_flip(self) -> bool:
        return self._is_flip_var

    @property
    def direction(self) -> Direction:
        return INPUT if self.is_flip else OUTPUT

    def set_direction(self, direction: Direction) -> None:
        self._is_flip_var = direction is INPUT

    def as_input(self) -> 'Data':
        self.set_direction(INPUT)
        return self

    def as_output(self) -> 'Data':
        self.set_direction(OUTPUT)
        return self

    def flip(self) -> 'Data':
        self._is_flip_var = not self._is_flip_var
        return self

    @cached_property
    def ref(self) -> Alias:
        return Alias(self.idx)

    def __ilshift__(self, other: 'Data') -> 'Data':
        push_command(Connect(self.ref, other.ref))
        return self

    @property
    def name(self) -> str:
        return get_ref_id(self.idx).name

    @property
    def debug_name(self) -> str:
        return f'{self.mod.debug_name}.{self.name}'

    @property
    def lit_value(self) -> int:
        return -1

    @property
    def is_lit_value(self) -> bool:
        return False

    def from_bits(self, n: 'Bits') -> 'Data':
        res = self.clone_type()
        _i = 0
        wire = Wire.apply(res)
        for x in reversed(wire.flatten()):
            x <<= n[_i + x.get_width():_i]
            _i += x.get_width()
        return res

    def to_bits(self) -> 'Bits':
        elements = self.flatten()
        return Cat(*elements)

    def make_lit(self, value: int, width: int) -> 'Data':
        x = self.clone_type()
        x.from_bits(Bits.apply(value, width))
        return x

    def to_bool(self) -> 'Bool':
        return chisel_cast(self, Bool.apply)

    def to_port(self) -> 'Port':
        return Port(self.idx, self.direction, self.to_type())

    @property
    def is_reg(self):
        return self._is_reg

    @property
    def params(self):
        return Parameters.empty if not driver.par_stack else driver.par_stack[-1]


class Wire:
    @classmethod
    def apply(cls, t: Data = None, init: Data = None) -> Data:
        mtype = init if not t else t
        if not mtype:
            raise TypeError('Cannot infer type of init.')
        x = mtype.clone_type()
        x.collect_elements()
        push_command(DefWire(x.defined().idx, x.to_type()))
        if init:
            push_command(Connect(x.ref, init.ref))
        return x


class Bits(Data, ABC):
    @staticmethod
    def apply(*args):
        match args:
            case int(value), int(width):
                print(value, width)

    def __getitem__(self, slice_item):
        match slice_item:
            case slice(start=start, stop=stop, step=None):
                ...


class Bool(Bits, ABC):
    @classmethod
    def apply(cls) -> 'Bool':
        ...


def Cat(*r: Bits) -> Bits:
    if not r:
        raise ValueError('Empty Cat!')

    def do_cat(*t: Bits) -> Bits:
        if len(t) == 1:
            return t[0]
        else:
            sl = len(t) / 2
            low = do_cat(*t[0:sl])
            high = do_cat(*t[sl:len(t)])
            is_const = low.is_lit_value and high.is_lit_value
            w = low.get_width() + high.get_width() if is_const else -1
            d = low.clone_type_with(w)
            if is_const:
                d.set_lit_value((low.lit_value << low.get_width()) | high.lit_value)
            push_command(DefPrim(d.idx, d.to_type(), PrimOp.ConcatOp, [low.ref, high.ref], []))
            return d
        
    return do_cat(*r)


def chisel_cast(fr, to):
    x = to()
    push_command(DefWire(x.defined().idx, x.to_type()))
    b = fr.to_bits()
    push_command(Connect(x.ref, b.ref))
    return x


if __name__ == '__main__':
    # idx = Data(INPUT)
    idx = Id()
    idx.defined()
    print(idx.is_defined)

    # from core.module import Module
    # push_module(Module())
    # push_commands()
    # data = Data(INPUT)
    # t = type(data)
    # b = t(OUTPUT)
    # data <<= b
    # print(data.idx)

    bits = Bits(INPUT)
    a = bits[3:0]
