import copy
import random


class TreapNode:

    def __init__(self, val):
        self.pr = random.randint(1, 100)
        self.c = 1
        self.s = val
        self.val = val
        self.left = None
        self.right = None
        self.parent = None

    def refresh(self):
        c = 1
        s = self.val
        if self.left is not None:
            c += self.left.c
            s += self.left.s
        if self.right is not None:
            c += self.right.c
            s += self.right.s
        self.c = c
        self.s = s

    def update(self):
        curr = self
        while curr is not None:
            curr.refresh()
            curr = curr.parent


class Treap:
    def __init__(self, array):
        self.size = 0
        self.head = None
        self.last = None
        for val in array:
            self.push(val)

    def push(self, val):
        node = TreapNode(val)
        self.size += 1
        prev = None
        if self.last is None:
            node.update()
            self.last = node
            self.head = node
            return
        else:
            curr = self.last
            while curr.pr > node.pr:
                if curr.parent is not None:
                    prev = curr
                    curr = curr.parent
                else:
                    node.left = curr
                    curr.parent = node
                    node.update()
                    self.last = node
                    self.head = node
                    return

            if prev is not None:
                prev.parent = node
            node.left = prev
            node.parent = curr
            curr.right = node
            node.update()
            self.last = node

    def getSum(self, fr, to):
        tr = copy.deepcopy(self.head)
        L, R = splitBySize(tr, fr - 1)
        RL, RR = splitBySize(R, to - fr + 1)
        return RL.s


def merge(t_1, t_2):
    if not t_1:
        return t_2
    if not t_2:
        return t_1

    if t_1.head.pr < t_2.head.pr:
        t_1.right = merge(t_1.head.right, t_2)
        t_1.head.refresh()
        return t_1
    else:
        t_2.left = merge(t_1, t_2.head.left)
        t_2.head.refresh()
        return t_2


def splitBySize(T, k):
    t = copy.deepcopy(T)
    if not t:
        return None, None

    if t.left is not None:
        l = t.left.c
    else:
        l = 0

    if k <= l:
        LL, LR = splitBySize(t.left, k)
        t.left = copy.deepcopy(LR)
        t.update()
        return LL, t
    else:
        RL, RR = splitBySize(t.right, k - l - 1)
        t.right = copy.deepcopy(RL)
        t.update()
        return t, RR


def printTreap(t):
    if t is None:
        return

    printTreap(t.left)
    printTreap(t.right)
    l = ''
    r = ''

    if t.left is not None:
        l += f"left: {t.left.val}, {t.left.pr}, "
    if t.right is not None:
        r += f"right: {t.right.val}, {t.right.pr}, "
    print(f"{t.val}, pr: {t.pr}, sum: {t.s}, " + l + r)


def test(n):
    arr = [0]*n
    for i in range(n):
        arr[i] = random.randint(1, n)

    print(str(arr))
    t = Treap(arr)

    for i in range(100):
        x = random.randint(1, n)
        y = random.randint(x, n)

        s = 0
        for i in range(x-1, y):
            s += arr[i]

        s_t = t.getSum(x, y)

        print(f"from {x} to {y}")
        print(f"expected: {s}, obtained: {s_t}\n")

        if(s != s_t):
            print("test failed!")
            return

    print("test passed!")


test(100)

