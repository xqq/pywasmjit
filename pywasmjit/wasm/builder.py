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
        print('locals:')
        for name, value in self.locals.items():
            print(f'{name}: index={value[0]}, type={value[1]}')

    def dump_instructions(self):
        print('instructions:')
        for instr in self.instructions:
            print(instr)


class Builder:
    __slots__ = ['_functions', '_imported_functions', '_current_func_ctx']

    def __init__(self):
        self._functions: list[Function] = []
        self._imported_functions: list[ImportedFunction] = []
        self._current_func_ctx: Optional[FunctionContext] = None
        pass

    # TODO: Useless?
    def start_function(self, name: str, is_export: bool, return_type: str,
                       params: list[tuple[str, WASMType]]) -> FunctionContext:
        assert self._current_func_ctx is None
        ctx = self._current_func_ctx = FunctionContext(name, is_export, return_type, params)
        return ctx

    # TODO: Useless?
    def end_function(self, ctx: FunctionContext):
        assert self._current_func_ctx is not None
        assert ctx == self._current_func_ctx
        # TODO: Build FunctionContext into wf.Function
        # TODO: Set self._current_func_ctx into None

    def set_entrypoint(self, name: str):
        pass

    def build(self):
        pass

    def get_bytes(self):
        pass
