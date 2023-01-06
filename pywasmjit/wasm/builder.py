from typing import Optional
from collections import OrderedDict
from .components import *
from .instructions import OPCODES


class FunctionContext:
    __slots__ = ['func_name', 'is_export', 'return_type', 'params',
                 'instructions', 'locals', '_local_count', '_block_stack']

    def __init__(self, func_name: str, is_export: bool, return_type: Optional[str], params: list[tuple[str, WASMType]]):
        self.func_name = func_name
        self.is_export = is_export
        self.return_type = return_type
        self.params = params

        self.instructions: list[tuple[str, ...]] = []
        self.locals: OrderedDict[str, [int, WASMType]] = OrderedDict()  # name => (index, type)
        self._local_count: int = 0
        self._block_stack: list[str] = []

        # Parameters are visited through local.get / local.set
        for param in params:
            self.new_local(param[0], param[1])

    def new_local(self, name: str, vartype: WASMType) -> int:
        index = self._local_count
        self.locals[name] = (index, vartype)
        self._local_count += 1
        return index

    def new_stub(self, vartype: WASMType) -> int:
        name = f'stub_{self._local_count}'
        return self.new_local(name, vartype)

    def get_local_index(self, name: str) -> int:
        if name not in self.locals:
            return -1
        return self.locals[name][0]

    def get_local_wasmtype(self, name: str) -> WASMType:
        assert name in self.locals
        return self.locals[name][1]

    def add_instruction(self, instruction: tuple):
        assert instruction[0] in OPCODES
        self.instructions.append(instruction)

    def enter_block(self, kind: str):
        assert kind in ('if', 'for', 'while')
        self._block_stack.append(kind)

    def exit_block(self, kind: str):
        assert self._block_stack.pop() == kind

    def get_adjacent_loop_block_level(self) -> int:
        for i, kind in enumerate(reversed(self._block_stack)):
            if kind in ('for', 'while'):
                return i
        return 0

    def dump_locals(self):
        print('-------locals-------')
        for name, value in self.locals.items():
            print(f'{name}: index={value[0]}, type={value[1]}')

    def dump_instructions(self):
        print('----instructions----')
        for instr in self.instructions:
            print(instr)


class Builder:
    __slots__ = ['_functions', '_imported_functions', '_module', '_buffer']

    def __init__(self):
        self._functions: list[Function] = []
        self._imported_functions: list[ImportedFunction] = []
        self._module: Optional[Module] = None
        self._buffer: Optional[bytes] = None
        pass

    def add_function(self, ctx: FunctionContext):
        wasm_params = [param[1] for param in ctx.params]
        wasm_return = []
        if ctx.return_type is not None and ctx.return_type != 'None':
            wasm_return = [ctx.return_type]

        wasm_locals = []

        for i, (name, local) in enumerate(ctx.locals.items()):
            if i < len(wasm_params):
                # Skip parameters (they are treated as local variables)
                continue
            wasm_locals.append(local[1])

        func = Function(idname=ctx.func_name,
                        params=wasm_params,
                        returns=wasm_return,
                        locals=wasm_locals,
                        instructions=ctx.instructions,
                        export=True)
        self._functions.append(func)

    def add_imported_function(self, func_name: str, params: list[WASMType],
                              return_type: Optional[WASMType], modname: str, fieldname: str):
        wasm_returns = []
        if return_type is not None and return_type != 'None':
            wasm_returns = [return_type]

        func = ImportedFunction(idname=func_name,
                                params=params,
                                returns=wasm_returns,
                                modname=modname,
                                fieldname=fieldname)
        self._imported_functions.append(func)

    def build(self):
        sections = []
        sections.extend(self._imported_functions)
        sections.extend(self._functions)
        self._module = Module(*sections)
        self._buffer = None

    def get_bytes(self):
        if self._buffer is None:
            self._buffer = self._module.to_bytes()
        return self._buffer
