import ast


class FuncDef(ast.AST):
    _fields = ['func_name', 'params', 'stmts', 'return_type']

    def __init__(self, func_name: str, params, stmts, return_type=None):
        self.func_name = func_name
        self.params = params
        self.stmts = stmts
        self.return_type = return_type


class FuncCall(ast.AST):
    _fields = ['func_name', 'args']

    def __init__(self, func_name: str, args):
        self.func_name = func_name
        self.args = args


class Var(ast.AST):
    _fields = ['id', 'type']

    def __init__(self, id, type=None):
        self.id = id
        self.type = type


class IntLiteral(ast.AST):
    _fields = ['value']

    def __init__(self, value: int):
        self.value = value


class FloatLiteral(ast.AST):
    _fields = ['value']

    def __init__(self, value: float):
        self.value = value


class BoolLiteral(ast.AST):
    _fields = ['value']

    def __init__(self, value: bool):
        self.value = bool(value)


class Assign(ast.AST):
    _fields = ['target', 'value', 'type']

    def __init__(self, target, value, type=None):
        self.target = target
        self.value = value
        self.type = type


class Expr(ast.AST):
    _fields = ['value']

    def __init__(self, value):
        self.value = value


class Compare(ast.AST):
    _fields = ['left', 'op', 'comparator']

    def __init__(self, left, op, comparator):
        self.left = left
        self.op = op
        self.comparator = comparator


class If(ast.AST):
    _fields = ['expr', 'stmts', 'orelse']

    def __init__(self, expr, stmts, orelse):
        self.expr = expr
        self.stmts = stmts
        self.orelse = orelse


class BinOp(ast.AST):
    _fields = ['left', 'op', 'right']

    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right


class UnaryOp(ast.AST):
    _fields = ['op', 'right']

    def __init__(self, op, right):
        self.op = op
        self.right = right


class While(ast.AST):
    _fields = ['expr', 'stmts']

    def __init__(self, expr, stmts):
        self.expr = expr
        self.stmts = stmts


class For(ast.AST):
    _fields = ['loopvar', 'begin', 'end', 'step', 'stmts']

    def __init__(self, loopvar, begin, end, step, stmts):
        self.loopvar = loopvar
        self.begin = begin
        self.end = end
        self.step = step
        self.stmts = stmts


class Continue(ast.AST):
    _fields = []


class Break(ast.AST):
    _fields = []


class Return(ast.AST):
    _fields = ['value']

    def __init__(self, value):
        self.value = value


class Pass(ast.AST):
    _fields = []
