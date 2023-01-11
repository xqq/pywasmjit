from typing import Optional

from .wasm.components import WASMType

DEBUG = False


def debug_print(fmt: str, *args):
    if not DEBUG:
        return
    print('=' * 80)
    print(fmt, *args)


def pytype_to_wasmtype(pytype: Optional[str]) -> Optional[WASMType]:
    if pytype == 'int' or pytype == 'bool':
        return WASMType('i32')
    elif pytype == 'float':
        return WASMType('f64')
    elif pytype is None or pytype == 'None':
        return None
    else:
        raise RuntimeError(f'Unsupported type: {pytype}')


class FunctionSignature:
    __slots__ = ['params', 'return_type']

    def __init__(self, params: list[str | WASMType], return_type: str | WASMType):
        self.params: list[str | WASMType] = params
        self.return_type: str | WASMType = return_type
