import abc
from collections import abc as collect_abc


_ref_map: collect_abc.MutableMapping[str, 'Immediate'] = dict()


def __gen_sys():
    def __inner_gen_sys():
        counter = -1
        cname = ''
        while True:
            name = yield cname
            counter += 1
            cname = f'{name}_{counter}'
    tmp = __inner_gen_sys()
    next(tmp)
    return tmp


gen_sys = __gen_sys().send


class Immediate(abc.ABC):
    @property
    @abc.abstractmethod
    def fullname(self) -> str:
        ...

    @property
    @abc.abstractmethod
    def name(self) -> str:
        ...


class Alias(Immediate):
    def __init__(self, idx: str):
        self.idx = idx

    @property
    def fullname(self) -> str:
        return get_ref_id(self.idx).fullname

    @property
    def name(self) -> str:
        return get_ref_id(self.idx).name


class Ref(Immediate):
    def __init__(self, name: str):
        self._name = name

    @property
    def fullname(self) -> str:
        return self._name

    @property
    def name(self) -> str:
        return self._name


class Slot(Immediate):
    def __init__(self, imm: Immediate, name: str):
        self.imm = imm
        self._name = name

    @property
    def fullname(self) -> str:
        return self._name if self.imm.fullname == 'self' else f'{self.imm.fullname}.{self._name}'

    @property
    def name(self) -> str:
        return self._name


class Index(Immediate):
    def __init__(self, imm: Immediate, value: int):
        self.imm = imm
        self.value = value

    @property
    def name(self) -> str:
        return f'.{self.value}'

    @property
    def fullname(self) -> str:
        return f'{self.imm.fullname}.{self.value}'


def set_ref_id(idx: str, name: str, overwrite: bool) -> None:
    if overwrite or idx not in _ref_map:
        _ref_map[idx] = Ref(name)


def set_field_id(parent_id: str, idx: str, name: str) -> None:
    _ref_map[idx] = Slot(Alias(parent_id), name)


def set_index_id(parent_id: str, idx: str, index: int) -> None:
    _ref_map[idx] = Index(Alias(parent_id), index)


def get_ref_id(idx: str) -> Immediate:
    if idx in _ref_map:
        return _ref_map[idx]
    else:
        ref = Ref(gen_sys('T'))
        _ref_map[idx] = ref
        return ref
