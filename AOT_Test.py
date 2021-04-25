import time, random
import my_module

begin = time.perf_counter()
my_module.monte_carlo_pi(5000)
print("Took " + str(time.perf_counter() - begin) + "seconds.")

def monte_carlo_pi(nsamples):
    acc = 0
    for i in range(nsamples):
        x = random.random()
        y = random.random()
        if (x ** 2 + y ** 2) < 1.0:
            acc += 1
    return 4.0 * acc / nsamples

begin = time.perf_counter()
monte_carlo_pi(5000)
print("Took " + str(time.perf_counter() - begin) + "seconds.")