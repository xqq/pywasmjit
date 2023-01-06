import time

import pywasmjit
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


pywasmjit.warmup()

ret = fibonacci(0)
print(ret)

start_time = time.time()
ret = fibonacci(40)
cost_time_ms = (time.time() - start_time) * 1000
print('fibonacci(40) =', ret, f'(elapsed time: {cost_time_ms} ms)')

start_time = time.time()
ret = fibonacci_nojit(40)
cost_time_ms_nojit = (time.time() - start_time) * 1000
print('fibonacci_nojit(40) =', ret, f'(elapsed time: {cost_time_ms_nojit} ms)')
print('rate:', 'Infinite' if cost_time_ms == 0 else cost_time_ms_nojit / cost_time_ms)
