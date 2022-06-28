import collections.abc
from collections import deque
from core.basic_types import *
from core.inner_struct import gen_sys
from typing import Callable


components: list[Component] = list()

scope_stack: deque[set[str]] = deque()

switch_keys_stack: deque[deque['Bits']] = deque()

modules: collections.abc.MutableMapping[str, 'Module'] = dict()

module_stack: deque['Module'] = deque()

component_names: set[str] = set()

command_stack: deque[list[Command]] = deque()


def scope() -> set[str]:
    return scope_stack[-1]


def switch_keys() -> deque['Bits']:
    return switch_keys_stack[-1]


def push_scope() -> None:
    scope_stack.append(set())
    switch_keys_stack.append(deque())


def pop_scope() -> None:
    scope_stack.pop()
    switch_keys_stack.pop()


def add_module(mod: 'Module') -> None:
    modules[mod.id] = mod


def push_module(mod: 'Module') -> None:
    module_stack.append(mod)


def get_component() -> 'Module':
    return module_stack[0]


def pop_module() -> None:
    module_stack.pop()


def unique_component(name: str, ports: list[Port], body: Command) -> Component:
    ret = Component(gen_sys(name) if name in component_names else name, ports, body)
    component_names.add(name)
    return ret


def commands() -> list[Command]:
    return command_stack[-1]


def push_command(cmd: Command) -> None:
    commands().append(cmd)


def to_command(cmds: list[Command]) -> Command:
    match (len(cmds)):
        case 0:
            return EmptyCommand()
        case 1:
            return cmds[0]
        case _:
            return Begin(cmds)


def push_commands() -> None:
    command_stack.append(list())


def pop_commands() -> Command:
    return to_command(command_stack.pop())


def collect_commands(f: Callable[[], 'Module']) -> tuple[Command, 'Module']:
    push_commands()
    ret = f()
    return pop_commands(), ret


def build(f: Callable[[], 'Module']) -> tuple[Circuit, 'Module']:
    _, mod = collect_commands(f)
    return Circuit(components, components[-1].name), mod


if __name__ == '__main__':
    print(gen_sys('id'))
    print(gen_sys('T'))
    scope_stack.extend([set('a'), set('b'), set('c')])
    print(scope())
    print(scope_stack.pop())
    print(scope_stack.pop())
