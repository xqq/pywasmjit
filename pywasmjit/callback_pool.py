import types
import inspect
from typing import Optional, Callable
from collections import OrderedDict

from .utils import pytype_to_wasmtype
from .utils import FunctionSignature


CALLBACK_NAME_BLACKLIST = ('print', 'print_int', 'print_float', 'print_bool')


class CallbackPool:
    __slots__ = ['callbacks']

    def __init__(self) -> None:
        # name => (func, py_sig, wasm_sig)
        self.callbacks: OrderedDict[str, tuple[Callable, FunctionSignature, FunctionSignature]] = OrderedDict()

    def add_callback(self, func):
        if not isinstance(func, types.FunctionType):
            raise RuntimeError('Callback must be a function')

        name = func.__name__
        if name in CALLBACK_NAME_BLACKLIST:
            raise RuntimeError(f'Reserved callback function name: {name}')

        sig = inspect.signature(func)

        if not hasattr(sig, 'return_annotation'):
            raise RuntimeError('Callback function must have return type annotation')

        py_params = []
        py_return_type = 'None'
        if sig.return_annotation is not None and sig.return_annotation.__name__ != '_empty':
            py_return_type = sig.return_annotation.__name__

        for param in sig.parameters.values():
            if param.annotation is None or param.annotation.__name__ == '_empty':
                raise RuntimeError(f'Callback function parameters require type annotations')
            if param.annotation not in (int, float, bool):
                raise RuntimeError(f'Unsupported callback function parameter type: {param.annotation}')
            py_params.append(param.annotation.__name__)

        py_sig = FunctionSignature(py_params, py_return_type)

        wasm_params = [pytype_to_wasmtype(param) for param in py_params]
        wasm_return_type = pytype_to_wasmtype(py_return_type)

        wasm_sig = FunctionSignature(wasm_params, wasm_return_type)

        self.callbacks[name] = (func, py_sig, wasm_sig)

    def query_function(self, func_name: str) -> Optional[Callable]:
        if func_name not in self.callbacks:
            return None
        return self.callbacks[func_name][0]

    def query_py_signature(self, func_name: str) -> Optional[FunctionSignature]:
        if func_name not in self.callbacks:
            return None
        return self.callbacks[func_name][1]

    def query_wasm_signature(self, func_name: str) -> Optional[FunctionSignature]:
        if func_name not in self.callbacks:
            return None
        return self.callbacks[func_name][2]
