
def f(x):
    return (x + 1) & x


def g(x):
    return (x + 1) | x


class BIT2dim:
    def __init__(self, size_x, size_y):
        self.s = [[0]*size_y for _ in range(size_x)]
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
        while i < self.size_x:
            j = y
            while j < self.size_y:
                self.s[i][j] += val
                j = g(j)
            i = g(i)

    def increment_in_range(self, x_1, y_1, x_2, y_2, val):
        self.increment(x_1, y_1, val)
        self.increment(x_1, y_2 + 1, -val)
        self.increment(x_2 + 1, y_1, -val)
        self.increment(x_2 + 1, y_2 + 1, val)


class Emptiness:
    def __init__(self, x_1, y_1, x_2, y_2):
        self.x_1 = x_1
        self.y_1 = y_1
        self.x_2 = x_2
        self.y_2 = y_2

    def get_intersection(self, x_1, y_1, x_2, y_2):

        x1 = max(self.x_1, x_1)
        y1 = max(self.y_1, y_1)
        x2 = min(self.x_2, x_2+1)
        y2 = min(self.y_2, y_2+1)


        if x1 >= x2 or y1 >= y2:
            return None
        else:
            return [x1, y1, x2, y2]



class Device:
    def __init__(self, name, x_1, y_1, x_2, y_2, health):
        self.name = name
        self.x_1 = x_1
        self.y_1 = y_1
        self.x_2 = x_2
        self.y_2 = y_2
        self.health = health

    def intersects(self, x_1, y_1, x_2, y_2):

        x1 = max(self.x_1, x_1)
        y1 = max(self.y_1, y_1)
        x2 = min(self.x_2, x_2)
        y2 = min(self.y_2, y_2)


        if x1 >= x2 or y1 >= y2:
            return False
        else:
            return True


class Move:
    def __init__(self, x_1, y_1, x_2, y_2, damage):
        self.x_1 = x_1
        self.y_1 = y_1
        self.x_2 = x_2
        self.y_2 = y_2
        self.damage = damage


class Spaceship:
    def __init__(self, N, M, H, L, C, emptiness, devices):
        self.size_x = N-1
        self.size_y = M-1
        self.health = H
        self.L = L
        self.C = C
        self.emptiness = emptiness
        self.devices = devices

        self.bit_xy = BIT2dim(N, M)
        self.bit_x = BIT2dim(N, M)
        self.bit_y = BIT2dim(N, M)
        self.bit_c = BIT2dim(N, M)

    def calc_prefix_damage(self, x, y):
        a = self.bit_xy.get_prefix_sum(x, y)
        b = self.bit_x.get_prefix_sum(x, y)
        c = self.bit_y.get_prefix_sum(x, y)
        d = self.bit_c.get_prefix_sum(x, y)
        return a * x * y + b * x + c * y + d

    def incr_damage(self, x_1, y_1, x_2, y_2, val):
        self.bit_xy.increment_in_range(x_1, y_1, x_2, y_2, val)
        self.bit_x.increment_in_range(x_1, y_1, x_2, y_2, val * (1 - y_1))
        self.bit_y.increment_in_range(x_1, y_1, x_2, y_2, val * (1 - x_1))
        self.bit_c.increment_in_range(x_1, y_1, x_2, y_2, val * (1 - y_1) * (1 - x_1))

        self.bit_x.increment_in_range(x_1, y_2 + 1, x_2, self.bit_x.size_y, val * (1 - y_1 + y_2))
        self.bit_c.increment_in_range(x_1, y_2 + 1, x_2, self.bit_c.size_y, val * (1 - y_1 + y_2) * (1 - x_1))

        self.bit_y.increment_in_range(x_2 + 1, y_1, self.bit_y.size_x, y_2, val * (1 - x_1 + x_2))
        self.bit_c.increment_in_range(x_2 + 1, y_1, self.bit_c.size_x, y_2, val * (1 - x_1 + x_2) * (1 - y_1))

        self.bit_c.increment_in_range(x_2 + 1, y_2 + 1, self.bit_c.size_x, self.bit_c.size_y, val * (1 - y_1 + y_2) * (1 - x_1 + x_2))

    def get_damage(self, x_1, y_1, x_2, y_2, val):
        self.incr_damage(x_1, y_1, x_2, y_2, val)
        hollow = False
        for e in self.emptiness:
            intersection = e.get_intersection(x_1, y_1, x_2, y_2)
            if intersection is not None:
                hollow = True
                x1 = intersection[0]
                y1 = intersection[1]
                x2 = intersection[2]-1
                y2 = intersection[3]-1
                self.incr_damage(x1, y1, x2, y2, -val)
        return hollow

    def calculate_damage(self, x_1, y_1, x_2, y_2):
        damage = self.calc_prefix_damage(x_2, y_2)
        if x_1 != 0:
            damage -= self.calc_prefix_damage(x_1 - 1, y_2)
        if y_1 != 0:
            damage -= self.calc_prefix_damage(x_2, y_1 - 1)
        if x_1 != 0 and y_1 != 0:
            damage += self.calc_prefix_damage(x_1 - 1, y_1 - 1)
        return damage

    def check_devices(self):
        destroyed = []
        for device in self.devices:
            if self.calculate_damage(device.x_1, device.y_1, device.x_2 - 1, device.y_2 - 1) >= device.health:
                destroyed.append(device)
        if len(destroyed) != 0:
            destroyed.sort(key=lambda x: x.name[0], reverse=False)
            print(f"{destroyed[0].name} exploded! Ship is destroyed.")
            return False
        else:
            return True

    def check_devices_after_crash(self, x_1, y_1, x_2, y_2):
        destroyed = []
        for device in self.devices:
            if device.intersects(x_1, y_1, x_2, y_2):
                destroyed.append(device)
        if len(destroyed) != 0:
            destroyed.sort(key=lambda x: x.name[0], reverse=False)
            print(f"Because of that {destroyed[0].name} exploded! Ship is destroyed.")
            return False
        else:
            return True


def read(n):
    with open(f"./tests/{n}-input.txt") as file:
        temp = list(map(int, file.readline().split()))
        N = temp[0]
        M = temp[1]
        E = temp[2]
        R = temp[3]

        temp = list(map(int, file.readline().split()))
        H = temp[0]
        L = temp[1]
        C = temp[2]

        emptiness = [None]*E
        for i in range(E):
            temp = list(map(int, file.readline().split()))
            emptiness[i] = Emptiness(temp[0], temp[1], temp[2], temp[3])

        devices = [None]*R
        for i in range(R):
            temp = file.readline().split()
            name = temp[0]
            temp = list(map(int, temp[1:6]))
            devices[i] = Device(name, temp[0], temp[1], temp[2], temp[3], temp[4])

        K = int(file.readline())
        moves = [None]*K
        for i in range(K):
            temp = list(map(int, file.readline().split()))
            moves[i] = Move(temp[0], temp[1], temp[2], temp[3], temp[4])

        ship = Spaceship(N, M, H, L, C, emptiness, devices)

    return ship, moves


def decision(n):
    ship, moves = read(n)
    crashes = 0
    for move in moves:
        x_1 = move.x_1
        y_1 = move.y_1
        x_2 = move.x_2 - 1
        y_2 = move.y_2 - 1
        d = move.damage
        hollow = ship.get_damage(x_1, y_1, x_2, y_2, d)
        if not ship.check_devices():
            break
        damage_received = ship.calc_prefix_damage(ship.size_x, ship.size_y)
        if damage_received >= ship.health:
            print(f"Received {damage_received} damage in total, total damage limit {ship.health} exceeded. Ship is destroyed.")
            break
        if not hollow and ship.calculate_damage(x_1, y_1, x_2, y_2) >= (x_2-x_1+1)*(y_2-y_1+1)*ship.L:
            crashes += 1
            ship.emptiness.append(Emptiness(x_1, y_1, x_2+1, y_2+1))
            print(f"Received {damage_received} damage in total, section {{{x_1}, {y_1}, {x_2+1}, {y_2+1}}} collapsed.")
            if not ship.check_devices_after_crash(x_1, y_1, x_2+1, y_2+1):
                break
            elif crashes >= ship.C:
                print("And it was the last collapse the ship can handle. It was destroyed.")
                break
        else:
            print(f"Received {damage_received} damage in total.")


decision(10)