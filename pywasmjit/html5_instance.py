import pyodide.ffi
import js
from js import Uint8Array
from js import WebAssembly

from .callback_pool import CallbackPool
from .exec_instance import ExecInstance


def print_int(x: int) -> None:
    print(x)

def print_float(x: float) -> None:
    print(x)

def print_bool(x: int) -> None:
    b = bool(x)
    print(b)


class HTML5Instance(ExecInstance):
    def __init__(self, callback_pool: CallbackPool, buf: bytes):
        super().__init__(callback_pool, buf)

        import_funcs = {
            'js': {
                'print_int': pyodide.ffi.create_proxy(print_int),
                'print_float': pyodide.ffi.create_proxy(print_float),
                'print_bool': pyodide.ffi.create_proxy(print_bool)
            }
        }

        if len(callback_pool.callbacks) > 0:
            import_funcs['callback'] = {}

        for func_name, value in callback_pool.callbacks.items():
            func = value[0]
            import_funcs['callback'][func_name] = pyodide.ffi.create_proxy(func)

        self._import_object = pyodide.ffi.to_js(import_funcs, dict_converter=js.Object.fromEntries)

        jsbuf = Uint8Array.new(len(buf))
        jsbuf.assign(buf)

        self._module = WebAssembly.Module.new(jsbuf)
        self._instance = WebAssembly.Instance.new(self._module, self._import_object)

    def exec_function(self, func_name: str, *args):
        wasm_func = getattr(self._instance.exports, func_name)
        if wasm_func is None:
            raise RuntimeError(f'Function \'{func_name}\' not found in runtime')
        result = wasm_func(*args)
        return result
