import sys
import ast
import inspect
from textwrap import dedent
from typing import Optional

from .ast_transformer import ASTTransformer
from .codegen import WASMCodeGen
from .exec_instance import ExecInstance
from .type_checker import TypeChecker
from .utils import DEBUG, debug_print

if 'pyodide' in sys.modules or sys.platform == 'emscripten':
    from .html5_instance import HTML5Instance
else:
    from .wasmer_instance import WasmerInstance


type_checker = TypeChecker()
codegen = WASMCodeGen()

wasm_composed = False
wasm_exec_instance: Optional[ExecInstance] = None


def wasmjit(func):
    transformer = ASTTransformer()
    transformed_ast = transformer.transform(func)

    type_checker.visit(transformed_ast)

    if DEBUG:
        dump = ast.dump(transformed_ast, indent=4)
        debug_print(dump)

    codegen.visit(transformed_ast)

    global wasm_composed, wasm_exec_instance
    wasm_composed = False
    wasm_exec_instance = None

    return create_func_wrapper(transformed_ast)


def create_func_wrapper(ast):
    func_name = ast.func_name

    def wrapper(*func_args):
        warmup()
        ret = wasm_exec_instance.exec_function(func_name, *func_args)
        return ret

    return wrapper


def compose_wasm():
    codegen.build()
    buf = codegen.get_bytes()

    if DEBUG:
        print(buf)
        with open("debug.wasm", "wb") as binary_file:
            binary_file.write(buf)

    global wasm_composed
    wasm_composed = True


def init_instance():
    buf = codegen.get_bytes()

    global wasm_exec_instance
    if 'pyodide' in sys.modules or sys.platform == 'emscripten':
        wasm_exec_instance = HTML5Instance(buf)
    else:
        wasm_exec_instance = WasmerInstance(buf)


def warmup():
    if not wasm_composed:
        compose_wasm()
    if wasm_exec_instance is None:
        init_instance()


def cleanup():
    global type_checker, codegen, wasm_composed, wasm_exec_instance
    type_checker = TypeChecker()
    codegen = WASMCodeGen()
    wasm_composed = False
    wasm_exec_instance = None
