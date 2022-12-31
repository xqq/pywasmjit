import ast
import inspect
from textwrap import dedent

from .ast_transformer import ASTTransformer
from .codegen import WASMCodeGen
from .type_checker import TypeChecker
from .utils import DEBUG, debug_print


type_checker = TypeChecker()
codegen = WASMCodeGen()


def wasmjit(func):
    if DEBUG:
        func_str = dedent(inspect.getsource(func))
        dump = ast.dump(ast.parse(func_str), indent=4)
        debug_print(dump)
    
    transformer = ASTTransformer()
    transformed_ast = transformer.transform(func)

    if DEBUG:
        dump = ast.dump(transformed_ast, indent=4)
        debug_print(dump)

    type_checker.visit(transformed_ast)

    if DEBUG:
        dump = ast.dump(transformed_ast, indent=4)
        debug_print(dump)

    codegen.visit(transformed_ast)

    codegen.dump()
