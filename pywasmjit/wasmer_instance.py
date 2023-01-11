from collections import defaultdict

from wasmer import engine, Store, Module, Instance, Function, Type, FunctionType
from wasmer_compiler_cranelift import Compiler

from .wasm.components import WASMType
from .callback_pool import CallbackPool
from .exec_instance import ExecInstance


def print_int(x: int) -> None:
    print(x)


def print_float(x: float) -> None:
    print(x)


def print_bool(x: int) -> None:
    b = bool(x)
    print(b)


def wasmtype_to_wasmer_type(ty: WASMType):
    if ty == 'i32':
        return Type.I32
    elif ty == 'i64':
        return Type.I64
    elif ty == 'f32':
        return Type.F32
    elif ty == 'f64':
        return Type.F64
    elif ty is None or ty == 'None':
        raise RuntimeError(f'Invalid WASMType for convert into Wasmer type: {ty}')


class WasmerInstance(ExecInstance):
    __slots__ = ['_store', '_module', '_instance']

    def __init__(self, callback_pool: CallbackPool, buf: bytes):
        super().__init__(callback_pool, buf)
        self._store = Store(engine.Universal(Compiler))
        self._module = Module(self._store, buf)

        import_object = defaultdict(dict)
        import_object['js']['print_int'] = Function(self._store, print_int, FunctionType([Type.I32], []))
        import_object['js']['print_float'] = Function(self._store, print_float, FunctionType([Type.F64], []))
        import_object['js']['print_bool'] = Function(self._store, print_bool, FunctionType([Type.I32], []))

        for func_name, value in callback_pool.callbacks.items():
            func = value[0]
            wasm_sig = value[2]

            fntype_params = []
            for param in wasm_sig.params:
                fntype_params.append(wasmtype_to_wasmer_type(param))

            fntype_ret = []
            if wasm_sig.return_type is not None:
                fntype_ret.append(wasmtype_to_wasmer_type(wasm_sig.return_type))

            import_object['callback'][func_name] = Function(self._store, func, FunctionType(fntype_params, fntype_ret))

        self._instance = Instance(self._module, import_object)

    def exec_function(self, func_name: str, *args):
        wasm_func = getattr(self._instance.exports, func_name)
        if wasm_func is None:
            raise RuntimeError(f'Function \'{func_name}\' not found in runtime')
        result = wasm_func(*args)
        return result
