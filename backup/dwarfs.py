import sys
import numpy as np
import scipy.spatial.distance as sp


class DisjointSets:

    def __init__(self, size: int):

        self.parents = [i for i in range(size)]
        self.ranks = [0] * size
        self.size = size
        self.number_of_sets = size

    def find(self, x: int):

        parent_of_x = self.parents[x]

        if parent_of_x != x:
            parent_of_x = self.find(parent_of_x)
        return parent_of_x

    def union(self, x, y: int):

        root_of_x = self.find(x)
        root_of_y = self.find(y)

        if root_of_x == root_of_y:
            return

        if self.ranks[root_of_x] > self.ranks[root_of_y]:
            self.parents[root_of_y] = root_of_x
            self.number_of_sets -= 1
        else:
            self.parents[root_of_x] = root_of_y
            self.number_of_sets -= 1

            if self.ranks[root_of_x] == self.ranks[root_of_y]:
                self.ranks[root_of_y] += 1


class District:

    def __init__(self, amount_of_houses, amount_of_taverns):

        self.amount_of_houses = amount_of_houses
        self.amount_of_taverns = amount_of_taverns

    def add_house(self):

        self.amount_of_houses += 1

    def add_tavern(self):

        self.amount_of_taverns += 1


class House:

    def __init__(self, x, y):

        self.x = x
        self.y = y
        self.tavern = False

    def set_tavern(self):

        self.tavern = True


class Street:

    def __init__(self, prefix, street_type, start_x, start_y, number_of_houses, distance_between_houses):

        self.prefix = prefix
        self.street_type = street_type
        self.start_x = int(start_x)
        self.start_y = int(start_y)
        self.number_of_houses = int(number_of_houses)
        self.distance_between_houses = int(distance_between_houses)
        self.houses = []

        if self.street_type.lower() == "avenue":
            for i in range(self.number_of_houses):
                x = self.start_x + self.distance_between_houses * i
                y = self.start_y
                self.houses.append(House(x, y))
        else:
            for i in range(self.number_of_houses):
                x = self.start_x
                y = self.start_y + self.distance_between_houses * i
                self.houses.append(House(x, y))

    def get_house(self, n):

        if self.street_type.lower() == "avenue":
            x = self.start_x + self.distance_between_houses * n
            y = self.start_y
        else:
            x = self.start_x
            y = self.start_y + self.distance_between_houses * n

        return x, y


def make_a_map(data):

    data = data.split("\n")
    number_of_districts, number_of_streets, number_of_taverns = map(int, data[0].split())
    streets = {}
    houses = {}

    for i in range(1, number_of_streets + 1):

        temp = data[i].split()
        prefix = temp[0]
        street_type = temp[1]
        start_x = int(temp[2])
        start_y = int(temp[3])
        number_of_houses = int(temp[4])
        distance_between_houses = int(temp[5])
        street = Street(prefix, street_type, start_x, start_y, number_of_houses, distance_between_houses)
        streets[prefix + " " + street_type] = street

        for j in range(number_of_houses):

            if street_type.lower() == "avenue":
                houses[f"{start_x + j * distance_between_houses}, {start_y}"] = False
            if street_type.lower() == "road":
                houses[f"{start_x}, {start_y + j * distance_between_houses}"] = False

    for i in range(number_of_streets + 1, number_of_streets + number_of_taverns + 1):

        temp = data[i].split(", ")
        house = streets.get(temp[0]).houses[int(temp[1])]
        house.set_tavern()
        houses[f"{house.x}, {house.y}"] = True

    return streets, houses, number_of_districts


def merge_clusters(clusters, x, y):

    clusters.union(x, y)


def upd(distances, clusters, min_dist, min_vert, maximal, minimal):

    merge_clusters(clusters, maximal, minimal)

    #Слили два кластера, а далее вычисляем минимум среди расстояний от двух кластеров до остальных
    #и переписываем его в строку и столбец с минимальным номером, обновим и min_dist[minimal]

    x_row = distances[maximal, :]
    res = np.minimum(x_row, distances[minimal, :])
    distances[minimal] = res
    distances[:, minimal] = res
    min_dist[minimal] = np.inf

    for i in range(clusters.size):
        if res[i] < min_dist[minimal] and clusters.find(minimal) != clusters.find(i):
            min_dist[minimal] = distances[minimal][i]
            min_vert[minimal] = i


def merge_step(distances, min_dist, min_vert, clusters):

    x = np.argmin(min_dist)
    y = min_vert[x]

    #Выбираем вершину (x) с минимальным расстоянием до остальных кластеров,
    #фиксируем номер строки (y) в матрице растояний, который ей соответствует.
    #Поскольку номером кластера после слияния полагаем минимум среди соответствующих строк, зафиксируем и его

    minimal = min(x, y)
    maximal = max(x, y)

    #Перепишем ссылки на maximal на minimal, maximal сольется с minimal, запомнится только minimal.
    #Полагая расстояние от maximal до остальных кластеров сколь угодно большим, помечаем, что эту точку 
    #больше не рассматриваем

    for i in range(min_vert.size):
        if min_vert[i] == maximal and i != minimal:
            min_vert[i] = minimal
    min_dist[maximal] = np.inf

    upd(distances, clusters, min_dist, min_vert, maximal, minimal)


def slink(houses, number_of_districts):

    number_of_houses = len(houses)

    #min_dist[i] содержит расстояние от i-ой точки до ближайшего кластера
    #min_vert[i] содержит номер строки в матрице расстояний, которой соответствует ближайший к i-му дому кластер

    min_dist = np.full(number_of_houses, np.inf)
    min_vert = np.zeros(number_of_houses, dtype=int)
    clusters = DisjointSets(number_of_houses)

    #Вычисляем матрицу расстояний

    points = np.zeros((number_of_houses, 2))
    i = 0
    for key, value in houses.items():
        key = key.split(", ")
        points[i][0] = int(key[0])
        points[i][1] = int(key[1])
        i += 1

    distances = sp.cdist(points, points, metric='euclidean')

    #Для удобства полагаем диагональные элементы сколь угодно большими. Заполняем min_vert и min_dist

    for i in range(number_of_houses):
        distances[i][i] = np.inf
        min_vert[i] = np.argmin(distances[i])
        min_dist[i] = distances[i][min_vert[i]]

    #Сливаем, пока не получим нужное число кластеров

    while clusters.number_of_sets != number_of_districts:
        merge_step(distances, min_dist, min_vert, clusters)

    return clusters


def solution(data: str) -> str:

    streets, houses, number_of_districts = make_a_map(data)
    clusters = slink(houses, number_of_districts)
    districts = get_districts(clusters, houses)

    return str(calculate_penalty(districts))


def get_districts(clusters, houses):

    districts = {}

    i = 0
    for point, tavern in houses.items():

        try:
            districts[f"{clusters.find(i)}"].add_house()
        except KeyError:
            districts[f"{clusters.find(i)}"] = District(1, 0)
        if tavern:
            districts[f"{clusters.find(i)}"].add_tavern()
        i += 1

    return districts


def calculate_penalty(districts):

    dis = list(districts.values())
    dis.sort(key=lambda x: x.amount_of_taverns / x.amount_of_houses, reverse=True)
    penalty = 0
    current_number_of_houses = 0

    for district in dis:
        current_number_of_houses += district.amount_of_houses
        penalty += current_number_of_houses*district.amount_of_taverns

    return penalty


def run():
    if len(sys.argv) <= 2:
        print("Wrong number of arguments: please specify input and output files.")
        return

    input_name, output_name = sys.argv[1], sys.argv[2]
    with open(input_name, "r") as inp:
        with open(output_name, "w") as out:
            data = inp.read()
            result = solution(data)
            out.write(result)


run()
