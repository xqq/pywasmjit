import time
from pywasmjit import wasmjit


@wasmjit
def fibonacci(x: int) -> int:
    if x < 3:
        return 1
    return fibonacci(x - 1) + fibonacci(x - 2)


def fibonacci_nojit(x: int) -> int:
    if x < 3:
        return 1
    return fibonacci_nojit(x - 1) + fibonacci_nojit(x - 2)


ret = fibonacci(0)
print(ret)

start_time = time.time()
ret = fibonacci(40)
elapsed = (time.time() - start_time) * 1000
print(f'fibonacci(40) = {ret}, elapsed: {elapsed} ms')

start_time = time.time()
ret = fibonacci_nojit(40)
elapsed_nojit = (time.time() - start_time) * 1000
print(f'fibonacci_nojit(40) = {ret}, elapsed: {elapsed_nojit} ms')
print('rate:', 'Infinite' if elapsed == 0 else elapsed_nojit / elapsed)
