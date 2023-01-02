from typing import Optional

from .ast import *
from .wasm.builder import Builder, FunctionContext
from .wasm.components import WASMType


def pytype_to_wasmtype(pytype: str):
    if pytype == 'int' or pytype == 'bool':
        return WASMType('i32')
    elif pytype == 'float':
        return WASMType('f64')
    elif pytype is None or pytype == 'None':
        return None
    else:
        raise RuntimeError(f'Unsupported type: {pytype}')


class WASMCodeGen:
    _fields = ['_builder', '_ctx']

    def __init__(self):
        self._builder = Builder()
        self._ctx: Optional[FunctionContext] = None

    def dump(self):
        self._ctx.dump_locals()
        self._ctx.dump_instructions()

    def visit(self, node: ast.AST):
        fn = f'visit_{type(node).__name__}'
        if hasattr(self, fn):
            return getattr(self, fn)(node)
        else:
            raise NotImplementedError(ast.dump(node))

    def infer(self, node: ast.AST):
        fn = f'infer_{type(node).__name__}'
        if hasattr(self, fn):
            return getattr(self, fn)(node)
        else:
            raise NotImplementedError(ast.dump(node))

    def visit_FuncDef(self, node: FuncDef):
        if self._ctx is not None:
            raise RuntimeError('Function definition inside function is not allowed')

        params: list[tuple[str, WASMType]] = []
        for var in node.params:
            params.append((var.id, pytype_to_wasmtype(var.type)))

        self._ctx = FunctionContext(func_name=node.func_name,
                                    is_export=True,
                                    return_type=pytype_to_wasmtype(node.return_type),
                                    params=params)

        for stmt in node.stmts:
            self.visit(stmt)

        # TODO: Append function into builder

    def infer_FuncCall(self, node: FuncCall):
        if node.func_name in ('int', 'float', 'bool'):
            return node.func_name
        elif node.func_name == 'print':
            return None
        else:
            # TODO: Support for custom functions
            return None

    def visit_FuncCall(self, node: FuncCall):
        if node.func_name == 'int':
            # int()
            input_ty = self.infer(node.args[0])
            self.visit(node.args[0])
            if input_ty == 'int' or input_ty == 'bool':
                # Convert int/bool to int
                pass
            elif input_ty == 'float':
                # Convert float to int
                self._ctx.add_instruction(('i32.trunc_f64_s',))
        elif node.func_name == 'float':
            # float()
            input_ty = self.infer(node.args[0])
            self.visit(node.args[0])
            if input_ty == 'float':
                # Convert float to float, no-op
                pass
            elif input_ty == 'int' or input_ty == 'bool':
                # Convert int to float
                self._ctx.add_instruction(('f64.convert_i32_s',))
        elif node.func_name == 'bool':
            # bool()
            input_ty = self.infer(node.args[0])
            self.visit(node.args[0])
            if input_ty == 'int' or input_ty == 'bool':
                pass
            elif input_ty == 'float':
                # Convert float to bool
                # if value != 0.0, it should be True
                self._ctx.add_instruction(('f64.const', 0.0))
                self._ctx.add_instruction(('f64.ne',))
        elif node.func_name == 'print':
            # TODO: print
            pass
        else:
            # TODO: Custom functions
            pass

    def infer_Var(self, node: Var):
        return node.type

    def visit_Var(self, node: Var):
        local_index = self._ctx.get_local_index(node.id)
        if local_index == -1:
            raise RuntimeError(f'Unresolved local variable: {node.id}')

        self._ctx.add_instruction(('local.get', local_index))

    def infer_IntLiteral(self, node: IntLiteral):
        return 'int'

    def visit_IntLiteral(self, node: IntLiteral):
        self._ctx.add_instruction(('i32.const', node.value))

    def infer_FloatLiteral(self, node: FloatLiteral):
        return 'float'

    def visit_FloatLiteral(self, node: FloatLiteral):
        self._ctx.add_instruction(('f64.const', node.value))

    def infer_BoolLiteral(self, node: BoolLiteral):
        return 'bool'

    def visit_BoolLiteral(self, node: BoolLiteral):
        self._ctx.add_instruction(('i32.const', int(node.value)))

    def visit_Assign(self, node: Assign):
        target_name = node.target.id
        local_index = self._ctx.get_local_index(target_name)
        if local_index == -1:
            local_index = self._ctx.new_local(target_name, pytype_to_wasmtype(node.type))

        self.visit(node.value)
        self._ctx.add_instruction(('local.set', local_index))

    def infer_Expr(self, node: Expr):
        return self.infer(node)

    def visit_Expr(self, node: Expr):
        self.visit(node.value)

    def infer_Compare(self, node: Compare):
        return 'bool'

    def visit_Compare(self, node: Compare):
        ty = self.infer(node.left)
        wasmty = pytype_to_wasmtype(ty)

        self.visit(node.left)
        self.visit(node.comparator)

        i32_op_map = {
            ast.Eq: 'eq',
            ast.NotEq: 'ne',
            ast.Gt: 'gt_s',
            ast.Lt: 'lt_s',
            ast.GtE: 'ge_s',
            ast.LtE: 'le_s'
        }

        f64_op_map = {
            ast.Eq: 'eq',
            ast.NotEq: 'ne',
            ast.Gt: 'gt',
            ast.Lt: 'lt',
            ast.GtE: 'ge',
            ast.LtE: 'le'
        }

        if ty == 'int':
            wasmop = i32_op_map[node.op.__class__]
        else:
            wasmop = f64_op_map[node.op.__class__]

        instr = f'{wasmty}.{wasmop}'
        self._ctx.add_instruction((instr,))

    def visit_If(self, node: If):
        self.visit(node.expr)

        self._ctx.enter_block('if')
        self._ctx.add_instruction(('if', 'emptyblock'))

        for stmt in node.stmts:
            self.visit(stmt)

        if node.orelse is not None and len(node.orelse) > 0:
            self._ctx.add_instruction(('else',))
            for stmt in node.orelse:
                self.visit(stmt)

        self._ctx.add_instruction(('end',))
        self._ctx.exit_block('if')

    def infer_BinOp(self, node: BinOp):
        ty = self.infer(node.left)
        return ty

    def visit_BinOp(self, node: BinOp):
        left_ty = self.infer(node)
        left_wasm_ty = pytype_to_wasmtype(left_ty)

        op = ''

        if node.op == ast.Add:
            op = 'add'
        elif node.op == ast.Sub:
            op = 'sub'
        elif node.op == ast.Mult:
            op = 'mul'
        elif node.op == ast.Div:
            if left_wasm_ty == 'i32':
                op = 'div_s'
            elif left_wasm_ty == 'f64':
                op = 'div'

        self.visit(node.left)
        self.visit(node.right)

        instr = f'{left_wasm_ty}.{op}'
        self._ctx.add_instruction((instr,))

    def infer_UnaryOp(self, node: UnaryOp):
        ty = self.infer(node.right)
        return ty

    def visit_UnaryOp(self, node: UnaryOp):
        ty = self.infer(node)

        if node.op == ast.USub:
            if ty == 'int':
                self._ctx.add_instruction(('i32.const', 0))
                self.visit(node.right)
                self._ctx.add_instruction(('i32.sub',))
            elif ty == 'float':
                self.visit(node.right)
                self._ctx.add_instruction(('f64.neg',))
        elif node.op == ast.Not:
            if ty == 'bool':
                self.visit(node.right)
                self._ctx.add_instruction(('i32.eqz',))

    def visit_While(self, node: While):
        self._ctx.enter_block('while')
        self._ctx.add_instruction(('block', 'emptyblock'))
        self._ctx.add_instruction(('loop', 'emptyblock'))

        # Test the boolean expression
        self.visit(node.expr)

        # If the boolean expression is false, jump out of the block block
        self._ctx.add_instruction(('i32.eqz',))
        self._ctx.add_instruction(('br_if', 1))

        for stmt in node.stmts:
            self.visit(stmt)

        # jump to the beginning of loop block
        self._ctx.add_instruction(('br', 0))

        self._ctx.add_instruction(('end',))  # End of loop block
        self._ctx.add_instruction(('end',))  # End of block block
        self._ctx.exit_block('while')

    def visit_For(self, node: For):
        loopvar_ty = self.infer(node.loopvar)
        begin_ty = self.infer(node.begin)
        end_ty = self.infer(node.end)
        step_ty = self.infer(node.step)

        loopvar_wasmty = pytype_to_wasmtype(loopvar_ty)

        begin_stub = self._ctx.new_stub(pytype_to_wasmtype(begin_ty))
        end_stub = self._ctx.new_stub(pytype_to_wasmtype(end_ty))
        step_stub = self._ctx.new_stub(pytype_to_wasmtype(step_ty))

        self.visit(node.begin)
        self.visit(node.end)
        self.visit(node.step)
        self._ctx.add_instruction(('local.set', step_stub))
        self._ctx.add_instruction(('local.set', end_stub))
        self._ctx.add_instruction(('local.set', begin_stub))

        loopvar = self._ctx.get_local_index(node.loopvar.id)
        if loopvar == -1:
            loopvar = self._ctx.new_local(node.loopvar.id, loopvar_wasmty)

        self._ctx.enter_block('for')

        self._ctx.add_instruction(('local.get', begin_stub))
        self._ctx.add_instruction(('local.set', loopvar))
        self._ctx.add_instruction(('block', 'emptyblock'))
        self._ctx.add_instruction(('loop', 'emptyblock'))
        self._ctx.add_instruction(('local.get', loopvar))
        self._ctx.add_instruction(('local.get', end_stub))

        ge_op = 'ge' if loopvar_wasmty == 'f64' else 'ge_s'
        self._ctx.add_instruction((f'{loopvar_wasmty}.{ge_op}',))
        self._ctx.add_instruction(('br_if', 1))  # branch to end of block block (break)

        for stmt in node.stmts:
            self.visit(stmt)

        self._ctx.add_instruction(('local.get', loopvar))
        self._ctx.add_instruction(('local.get', step_stub))
        self._ctx.add_instruction((f'{loopvar_wasmty}.add',))
        self._ctx.add_instruction(('local.set', loopvar))
        self._ctx.add_instruction(('br', 0))  # branch to the beginning of loop block

        self._ctx.add_instruction(('end',))  # End of loop block
        self._ctx.add_instruction(('end',))  # End of block block

        self._ctx.exit_block('for')

    def visit_Continue(self, node: Continue):
        loop_level = self._ctx.get_adjacent_loop_block_level()
        self._ctx.add_instruction(('br', loop_level))

    def visit_Break(self, node: Break):
        block_level = self._ctx.get_adjacent_loop_block_level() + 1
        self._ctx.add_instruction(('br', block_level))

    def visit_Return(self, node: Return):
        if node.value is not None:
            self.visit(node.value)
        self._ctx.add_instruction(('return',))

    def visit_Pass(self, node: Pass):
        pass
