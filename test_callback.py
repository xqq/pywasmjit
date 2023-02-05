import sys
from pywasmjit import wasmjit, wasmreg


@wasmreg
def print_two_int(x: int, y: int) -> int:
    sys.stdout.write(f'{x}, {y}\n')
    sys.stdout.write(f'{x} + {y} == {x + y}\n')
    return x + y


@wasmreg
def print_result(x: int):
    sys.stdout.write(f'result: {x}\n')


@wasmjit
def test_callback(x: int, y: int):
    result = print_two_int(x, y)
    print_result(result)
    return result


ret = test_callback(114, 514)
print(ret)

ret = test_callback(1919, 810)
print(ret)
