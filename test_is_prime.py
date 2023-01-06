import time
import pywasmjit
from pywasmjit import wasmjit


@wasmjit
def is_prime(x: int):
    for i in range(2, x):
        if x % i == 0:
            return False
    return True


def is_prime_nojit(x: int):
    for i in range(2, x):
        if x % i == 0:
            return False
    return True


pywasmjit.warmup()

start_time = time.time()
result = bool(is_prime(169941229))
cost_time_ms = (time.time() - start_time) * 1000
print('is_prime(169941229) =', result, f'(elapsed time: {cost_time_ms} ms)')

start_time = time.time()
result = bool(is_prime_nojit(169941229))
cost_time_ms_nojit = (time.time() - start_time) * 1000
print('is_prime_nojit(169941229) =', result, f'(elapsed time: {cost_time_ms_nojit} ms)')
print('rate:', 'Infinite' if cost_time_ms == 0 else cost_time_ms_nojit / cost_time_ms)
