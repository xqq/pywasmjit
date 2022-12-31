import ast
import types
import inspect
from textwrap import dedent

from .utils import debug_print

from .ast import (FuncDef, FuncCall, Var, IntLiteral, FloatLiteral, BoolLiteral, Assign, Expr,
                  Compare, If, BinOp, UnaryOp, While, For, Continue, Break, Return, Pass)

def get_typehint(var):
    if hasattr(var, 'annotation') and hasattr(var.annotation, 'id'):
        return var.annotation.id
    return None


class ASTTransformer(ast.NodeTransformer):
    def __init__(self):
        pass

    def transform(self, source):
        if isinstance(source, types.ModuleType)\
                or isinstance(source, types.FunctionType)\
                or isinstance(source, types.LambdaType):
            source = dedent(inspect.getsource(source))
        elif isinstance(source, str):
            source = dedent(source)
        else:
            raise NotImplementedError(ast.dump(source))

        tree = ast.parse(source)
        return self.visit(tree)

    def visit_Module(self, node: ast.Module):
        body = list(map(self.visit, node.body))
        return body[0]

    def visit_FunctionDef(self, node: ast.FunctionDef):
        stmts = list(node.body)
        stmts = list(map(self.visit, stmts))
        params = [Var(a.arg, get_typehint(a)) for a in node.args.args]

        return_type = None
        if hasattr(node, 'returns') and node.returns is not None:
            if hasattr(node.returns, 'id'):
                return_type = node.returns.id
            else:
                return_type = 'None'

        return FuncDef(node.name, params, stmts, return_type)

    def visit_Call(self, node: ast.Call):
        func_name = node.func.id
        args = list(map(self.visit, node.args))
        return FuncCall(func_name, args)

    def visit_Return(self, node: ast.Return):
        value = None
        if node.value is not None:
            value = self.visit(node.value)
        return Return(value)

    def visit_Pass(self, node: ast.Pass):
        return Pass()

    def visit_Name(self, node: ast.Name):
        return Var(node.id)

    def visit_Num(self, node: ast.Num):
        if isinstance(node.n, float):
            return FloatLiteral(node.n)
        else:
            return IntLiteral(node.n)

    def visit_Constant(self, node: ast.Constant):
        value = node.value
        if isinstance(node.n, bool):
            return BoolLiteral(value)
        elif isinstance(node.n, int):
            return IntLiteral(value)
        elif isinstance(node.n, float):
            return FloatLiteral(value)
        else:
            raise NotImplementedError(ast.dump(node))

    def visit_Assign(self, node: ast.Assign):
        if len(node.targets) > 1:
            raise NotImplementedError(ast.dump(node))
        target = self.visit(node.targets[0])
        value = self.visit(node.value)
        return Assign(target, value, get_typehint(target))

    def visit_AnnAssign(self, node: ast.AnnAssign):
        target = self.visit(node.target)
        typehint = node.annotation.id
        value = self.visit(node.value)
        return Assign(target, value, typehint)

    def visit_AugAssign(self, node: ast.AugAssign):
        if isinstance(node.op, ast.Add):
            target = self.visit(node.target)
            value = self.visit(node.value)
            return Assign(target, BinOp(target, ast.Add, value))
        elif isinstance(node.op, ast.Mult):
            target = self.visit(node.target)
            value = self.visit(node.value)
            return Assign(target, BinOp(target, ast.Mult, value))
        # TODO: ast.Sub, ast.Div
        else:
            raise NotImplementedError(ast.dump(node))

    def visit_Compare(self, node: ast.Compare):
        if len(node.ops) > 1 or len(node.comparators) > 1:
            raise NotImplementedError('Compare operation only supports at maximum 1 op and 1 comparator')

        left = self.visit(node.left)
        op = node.ops[0]
        comparator = self.visit(node.comparators[0])
        return Compare(left, op, comparator)

    def visit_BinOp(self, node: ast.BinOp):
        op = node.op.__class__
        left = self.visit(node.left)
        right = self.visit(node.right)
        return BinOp(left, op, right)

    def visit_UnaryOp(self, node: ast.UnaryOp):
        op = node.op.__class__
        if op not in (ast.USub, ast.Not):
            raise NotImplementedError(f'Unsupported unary operator: {op.__name__}')
        right = self.visit(node.operand)
        return UnaryOp(op, right)

    def visit_Expr(self, node: ast.Expr):
        return Expr(self.visit(node.value))

    def visit_If(self, node: ast.If):
        expr = self.visit(node.test)
        stmts = list(map(self.visit, node.body))
        orelse = list(map(self.visit, node.orelse))
        return If(expr, stmts, orelse)

    def visit_While(self, node: ast.While):
        if node.orelse:
            raise NotImplementedError(f'While does not support orelse: {ast.dump(node)}')
        expr = self.visit(node.test)
        stmts = list(map(self.visit, node.body))
        return While(expr, stmts)

    def visit_For(self, node: ast.For):
        loopvar = self.visit(node.target)

        if node.iter.func.id in ['range', 'xrange']:
            args = list(map(self.visit, node.iter.args))
        else:
            raise RuntimeError('For loop muse use range/xrange')

        begin = IntLiteral(0)
        end = IntLiteral(0)
        step = IntLiteral(1)

        if len(args) == 1:  # range(stop)
            begin = IntLiteral(0)
            end = args[0]
        elif len(args) == 2:  # range(start, stop)
            begin = args[0]
            end = args[1]
        elif len(args) == 3:  # range(start, stop, step)
            begin = args[0]
            end = args[1]
            step = args[2]

        stmts = list(map(self.visit, node.body))
        return For(loopvar, begin, end, step, stmts)

    def visit_Continue(self, node: ast.Continue):
        return Continue()

    def visit_Break(self, node: ast.Break):
        return Break()

    def generic_visit(self, node: ast.AST):
        raise NotImplementedError(ast.dump(node))


def fuck(src: str) -> str:
    transformer = ASTTransformer()
    tree = transformer.transform(src)
    return ast.dump(tree, indent=2)
