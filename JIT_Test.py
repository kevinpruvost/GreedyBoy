from numba import jit
import random
import time

@jit(nopython=True, cache=True)
def monte_carlo_pi(nsamples):
    acc = 0
    for i in range(nsamples):
        x = random.random()
        y = random.random()
        if (x ** 2 + y ** 2) < 1.0:
            acc += 1
    return 4.0 * acc / nsamples

begin = time.perf_counter()
monte_carlo_pi.py_func(5000)
print("Took " + str(time.perf_counter() - begin) + "seconds.")

begin = time.perf_counter()
monte_carlo_pi(5000)
print("Took " + str(time.perf_counter() - begin) + "seconds.")

begin = time.perf_counter()
monte_carlo_pi(5000)
print("Took " + str(time.perf_counter() - begin) + "seconds.")