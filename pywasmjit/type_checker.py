from .ast import *


class TypeChecker:
    __slots__ = ['_locals']

    def __init__(self):
        self._locals: dict[str, str] = {}  # name => pytype

    def visit(self, node: ast.AST):
        fn = f'visit_{type(node).__name__}'
        if hasattr(self, fn):
            return getattr(self, fn)(node)
        else:
            return self.generic_visit(node)

    def generic_visit(self, node: ast.AST):
        raise NotImplementedError(ast.dump(node))

    def enter_function(self, func: FuncDef):
        if len(self._locals) > 0:
            raise RuntimeError('Function definition inside function is not allowed')

        # Add parameters as locals
        for param in func.params:
            if param.type is None:
                raise RuntimeError('Function parameters must have type annotation')
            self._locals[param.id] = param.type

        # Record declared return type into locals for future checking
        self._locals['$return_type_declared'] = func.return_type

    def exit_function(self, func: FuncDef):
        if func.return_type is None:
            # None means return type is not specified in declaration by annotation
            if '$return_type_inferred' in self._locals:
                func.return_type = self._locals['$return_type_inferred']
            else:
                # If no '$return_type_inferred' recorded, return statement is not used
                # This could be a void function (no return value)
                func.return_type = 'None'

        self._locals.clear()
        return func.return_type

    def visit_FuncDef(self, node: FuncDef):
        self.enter_function(node)

        for stmt in node.stmts:
            self.visit(stmt)

        self.exit_function(node)

    def visit_FuncCall(self, node: FuncCall):
        if node.func_name == 'int':
            if len(node.args) > 1:
                raise RuntimeError('int() must has only 1 argument')

            arg_ty = self.visit(node.args[0])
            if arg_ty not in ('int', 'float', 'bool'):
                raise RuntimeError(f'Invalid input type: {arg_ty} for int() function')

            return 'int'
        elif node.func_name == 'float':
            if len(node.args) > 1:
                raise RuntimeError('float() must has only 1 argument')

            arg_ty = self.visit(node.args[0])
            if arg_ty not in ('int', 'float', 'bool'):
                raise RuntimeError(f'Invalid input type: {arg_ty} for float() function')

            return 'float'
        elif node.func_name == 'bool':
            if len(node.args) > 1:
                raise RuntimeError('bool() must has only 1 argument')

            arg_ty = self.visit(node.args[0])
            if arg_ty not in ('int', 'bool'):
                raise RuntimeError(f'Invalid input type: {arg_ty} for bool() function')

            return 'bool'
        elif node.func_name == 'print':
            if len(node.args) > 1:
                raise RuntimeError('print() only support 1 argument')

            arg_ty = self.visit(node.args[0])
            if arg_ty not in ('int', 'float', 'bool'):
                raise RuntimeError(f'Invalid input type: {arg_ty} for print() function')

            return None
        else:
            # TODO: Support for custom functions
            return None

    def visit_Var(self, node: Var):
        if node.id not in self._locals:
            raise RuntimeError(f'Unresolved symbol: {node.id}')

        ty = self._locals[node.id]
        node.type = ty
        return ty

    def visit_IntLiteral(self, node: IntLiteral):
        return 'int'

    def visit_FloatLiteral(self, node: FloatLiteral):
        return 'float'

    def visit_BoolLiteral(self, node: BoolLiteral):
        return 'bool'

    def visit_Assign(self, node: Assign):
        target_name = node.target.id
        if target_name in self._locals:
            # Assign to existing variable
            prev_target_ty = self._locals[target_name]
            value_ty = self.visit(node.value)

            if value_ty != prev_target_ty:
                raise RuntimeError(f'RValue type \'{value_ty}\' inconsistent with type of '
                                   f'existing variable {target_name} which is \'{prev_target_ty}\'')

            if node.type is not None and node.type != value_ty:
                raise RuntimeError(f'RValue type \'{value_ty}\' inconsistent with type annotation \'{node.type}\'')

            node.target.type = value_ty
            node.type = value_ty
        else:
            # Assign to new variable
            value_ty = self.visit(node.value)

            if node.type is not None and node.type != value_ty:
                raise RuntimeError(f'RValue type \'{value_ty}\' inconsistent with type annotation \'{node.type}\'')

            self._locals[target_name] = value_ty
            node.target.type = value_ty
            node.type = value_ty

    def visit_Expr(self, node: Expr):
        ty = self.visit(node.value)
        return ty

    def visit_Compare(self, node: Compare):
        if not isinstance(node.op, (ast.Eq, ast.NotEq, ast.Gt, ast.Lt, ast.GtE, ast.LtE)):
            raise NotImplementedError(f'Unsupported compare operator: {node.op.__class__.__name__}')

        left_ty = self.visit(node.left)
        comparator_ty = self.visit(node.comparator)
        if left_ty != comparator_ty:
            raise RuntimeError(f'Compare type mismatch: left is \'{left_ty}\', comparator is \'{comparator_ty}\'')

        return 'bool'

    def visit_If(self, node: If):
        expr_ty = self.visit(node.expr)
        if expr_ty != 'bool':
            raise RuntimeError('If expression must be a boolean expression')

        for stmt in node.stmts:
            self.visit(stmt)

        for stmt in node.orelse:
            self.visit(stmt)

    def visit_BinOp(self, node: BinOp):
        left_ty = self.visit(node.left)
        right_ty = self.visit(node.right)
        if left_ty != right_ty:
            raise RuntimeError(f'Type mismatch: left is \'{left_ty}\', right is \'{right_ty}\'')
        if left_ty not in ('int', 'float'):
            raise RuntimeError(f'Unsupported type for BinOp: \'{left_ty}\'')
        return left_ty

    def visit_UnaryOp(self, node: UnaryOp):
        ty = self.visit(node.right)
        if ty in ('int', 'float'):
            if node.op != ast.USub:
                raise RuntimeError(f'Invalid UnaryOp \'{node.op.__name__}\' for type \'{ty}\'')
        elif ty == 'bool':
            if node.op != ast.Not:
                raise RuntimeError(f'Invalid UnaryOp \'{node.op.__name__}\' for type \'{ty}\'')
        return ty

    def visit_While(self, node: While):
        expr_ty = self.visit(node.expr)
        if expr_ty != 'bool':
            raise RuntimeError('While expression must be a boolean expression')

        for stmt in node.stmts:
            self.visit(stmt)

    def visit_For(self, node: For):
        begin_ty = self.visit(node.begin)
        end_ty = self.visit(node.end)
        step_ty = self.visit(node.step)

        if begin_ty != 'int' or end_ty != 'int' or step_ty != 'int':
            raise RuntimeError('For loop range could only be \'int\'')

        if node.loopvar.type is None:
            # Loop variable is not type-annotated. This is the common case
            # The type of loop variable should be same as begin
            node.loopvar.type = begin_ty
        else:
            # Loop variable is type-annotated. Check the consistency here.
            loopvar_ty = node.loopvar.type
            if loopvar_ty != begin_ty or loopvar_ty != end_ty or loopvar_ty != step_ty:
                raise RuntimeError('For loop variable type mismatch')

        if node.loopvar.type not in ('int', 'float'):
            raise RuntimeError('For loop variable could only be \'int\' or \'float\'')

        self._locals[node.loopvar.id] = node.loopvar.type

        for stmt in node.stmts:
            self.visit(stmt)

    def visit_Continue(self, node: Continue):
        pass

    def visit_Break(self, node: Break):
        pass

    def visit_Return(self, node: Return):
        # Do type checking towards return type annotated in function declaration & previous return statement
        return_type_declared = self._locals['$return_type_declared']

        if node.value is None:
            # There's no return value here (empty return), return type should be None (void function)
            if return_type_declared is None or return_type_declared == 'None':
                self._locals['$return_type_inferred'] = 'None'
            else:
                raise RuntimeError(
                    f'Function declared with return type \'{return_type_declared}\' but return value not provided')
        else:
            # Return value exists, retrieve the type of return value
            ty = self.visit(node.value)

            if return_type_declared is not None and ty != return_type_declared:
                raise RuntimeError(
                    f'Return type inconsistent with that annotated in function declaration: {return_type_declared}')

            if '$return_type_inferred' in self._locals:
                return_type_inferred = self._locals['$return_type_inferred']
                if ty != return_type_inferred:
                    raise RuntimeError(
                        f'Return type inconsistent with type in previous return statement: {return_type_inferred}')
            else:
                self._locals['$return_type_inferred'] = ty
        # We do not need to return any type here

    def visit_Pass(self, node: Pass):
        pass
