from random import randint
from time import time


def f(x):
    return (x + 1) & x


def g(x):
    return (x + 1) | x


class BIT2dim:
    def __init__(self, size_x, size_y):
        self.s = [[0]*size_x for _ in range(size_y)]
        self.size_x = size_x
        self.size_y = size_y

    def get_prefix_sum(self, x, y):
        ans = 0
        curr_x = x
        while curr_x >= 0:
            curr_y = y
            while curr_y >= 0:
                ans += self.s[curr_x][curr_y]
                curr_y = f(curr_y) - 1
            curr_x = f(curr_x) - 1
        return ans

    def increment(self, x, y, val):
        i = x
        while i < self.size_y:
            j = y
            while j < self.size_x:
                self.s[i][j] += val
                j = g(j)
            i = g(i)

    def increment_in_range(self, x_1, y_1, x_2, y_2, val):
        self.increment(x_1, y_1, val)
        self.increment(x_1, y_2 + 1, -val)
        self.increment(x_2 + 1, y_1, -val)
        self.increment(x_2 + 1, y_2 + 1, val)


def update(bit_xy, bit_x, bit_y, bit_c, x_1, y_1, x_2, y_2, val):
    bit_xy.increment_in_range(x_1, y_1, x_2, y_2, val)
    bit_x.increment_in_range(x_1, y_1, x_2, y_2, val*(1-y_1))
    bit_y.increment_in_range(x_1, y_1, x_2, y_2, val*(1-x_1))
    bit_c.increment_in_range(x_1, y_1, x_2, y_2, val*(1-y_1)*(1-x_1))

    bit_x.increment_in_range(x_1, y_2+1, x_2, bit_x.size_y, val*(1-y_1+y_2))
    bit_c.increment_in_range(x_1, y_2+1, x_2, bit_c.size_y, val*(1-y_1+y_2)*(1-x_1))

    bit_y.increment_in_range(x_2+1, y_1, bit_y.size_x, y_2, val*(1-x_1+x_2))
    bit_c.increment_in_range(x_2+1, y_1, bit_c.size_x, y_2, val*(1-x_1+x_2)*(1-y_1))

    bit_c.increment_in_range(x_2+1, y_2+1, bit_c.size_x, bit_c.size_y, val*(1-y_1+y_2)*(1-x_1+x_2))


def prefix_sum(bit_xy, bit_x, bit_y, bit_c, x, y):
    a = bit_xy.get_prefix_sum(x, y)
    b = bit_x.get_prefix_sum(x, y)
    c = bit_y.get_prefix_sum(x, y)
    d = bit_c.get_prefix_sum(x, y)
    print(f"obtained: {a*x*y + b*x + c*y + d}")
    return a*x*y + b*x + c*y + d


def test_incr(list, x_1, y_1, x_2, y_2, val):
    for i in range(x_1, x_2+1):
        for j in range(y_1, y_2+1):
            list[i][j] += val


def test_sum(list, x, y):
    ans = 0
    for i in range(x+1):
        for j in range(y+1):
            ans += list[i][j]
    print(f"true: {ans}")
    return ans


def test(size_x, size_y):
    l = [[0] * size_x for _ in range(size_y)]
    bit_xy = BIT2dim(size_x, size_y)
    bit_x = BIT2dim(size_x, size_y)
    bit_y = BIT2dim(size_x, size_y)
    bit_c = BIT2dim(size_x, size_y)

    for i in range(1000):
        x_1 = randint(0, size_x-1)
        y_1 = randint(0, size_y-1)
        x_2 = randint(x_1, size_x-1)
        y_2 = randint(y_1, size_y-1)
        val = randint(1, 100)

        update(bit_xy, bit_x, bit_y, bit_c, x_1, y_1, x_2, y_2, val)
        test_incr(l, x_1, y_1, x_2, y_2, val)


    t1 = time()
    for i in range(1000):
        x = randint(0, size_x-1)
        y = randint(0, size_y-1)

        prefix_sum(bit_xy, bit_x, bit_y, bit_c, x, y)
    bit_time = time() - t1

    t1 = time()
    for i in range(1000):
        x = randint(0, size_x-1)
        y = randint(0, size_y-1)

        test_sum(l, x, y)
    naive_time = time() - t1

    print(f"bit: {bit_time}")
    print(f"naive: {naive_time}")
    print(f"diff: {bit_time-naive_time}")


size_x = 23
size_y = 32
l = [[0]*size_x for _ in range(size_y)]
bit_xy = BIT2dim(size_x, size_y)
bit_x = BIT2dim(size_x, size_y)
bit_y = BIT2dim(size_x, size_y)
bit_c = BIT2dim(size_x, size_y)


update(bit_xy, bit_x, bit_y, bit_c, 0, 0, 3, 3, 3)
test_incr(l, 0, 0, 3, 3, 3)

prefix_sum(bit_xy, bit_x, bit_y, bit_c, 9, 9)
test_sum(l, 9, 9)

test(1000, 1000)