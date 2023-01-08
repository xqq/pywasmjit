import time
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

start_time = time.time()
result = bool(is_prime(169941229))
elapsed = (time.time() - start_time) * 1000
print(f'is_prime(169941229) = {result}, elapsed: {elapsed} ms')

start_time = time.time()
result = is_prime_nojit(169941229)
elapsed_nojit = (time.time() - start_time) * 1000
print(f'is_prime_nojit(169941229) = {result}, elapsed: {elapsed_nojit} ms')
print('rate:', 'Infinite' if elapsed == 0 else elapsed_nojit / elapsed)
