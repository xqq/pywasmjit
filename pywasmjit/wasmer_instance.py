from collections import defaultdict

from wasmer import engine, Store, Module, Instance, Function, Type, FunctionType
from wasmer_compiler_cranelift import Compiler

from .exec_instance import ExecInstance


def print_int(x: int) -> None:
    print(x)


def print_float(x: float) -> None:
    print(x)


def print_bool(x: int) -> None:
    b = bool(x)
    print(b)


class WasmerInstance(ExecInstance):
    __slots__ = ['_store', '_module', '_instance']

    def __init__(self, buf: bytes):
        super().__init__(buf)
        self._store = Store(engine.Universal(Compiler))
        self._module = Module(self._store, buf)

        import_object = defaultdict(dict)
        import_object['js']['print_int'] = Function(self._store, print_int, FunctionType([Type.I32], []))
        import_object['js']['print_float'] = Function(self._store, print_float, FunctionType([Type.F64], []))
        import_object['js']['print_bool'] = Function(self._store, print_bool, FunctionType([Type.I32], []))

        self._instance = Instance(self._module, import_object)

    def exec_function(self, func_name, *args):
        wasm_func = getattr(self._instance.exports, func_name)
        if wasm_func is None:
            raise RuntimeError(f'Function \'{func_name}\' not found in runtime')
        result = wasm_func(*args)
        return result
