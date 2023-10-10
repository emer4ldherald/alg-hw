import time
from random import randrange

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import scipy.spatial.distance as sp


class DisjointSets:

    def __init__(self, size: int):
        self.parents = [i for i in range(size)]
        self.ranks = [0]*size
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

    def get_plot(self):

        street_x = []
        street_y = []
        for house in self.houses:
            street_x.append(house.x)
            street_y.append(house.y)
            if house.tavern:
                plt.plot([house.x], [house.y], color="r", marker=".", zorder=2)
        plt.plot(street_x, street_y, color="b", marker=".", zorder=1)


def make_a_map(number):
    with open(f"tests\\{number}-input.txt") as file:

        data = file.readline()
        N, S, T = map(int, data.split())
        streets = {}
        houses = {}

        for i in range(1, S + 1):
            data = file.readline()
            temp = data.split()
            prefix = temp[0]
            street_type = temp[1]
            start_x = int(temp[2])
            start_y = int(temp[3])
            number_of_houses = int(temp[4])
            distance_between_houses = int(temp[5])
            street = Street(prefix, street_type, start_x, start_y, number_of_houses, distance_between_houses)
            streets[prefix + " " + street_type] = street
            for i in range(number_of_houses):
                if street_type.lower() == "avenue":
                    houses[f"{start_x + i*distance_between_houses}, {start_y}"] = False
                if street_type.lower() == "road":
                    houses[f"{start_x}, {start_y + i * distance_between_houses}"] = False

        for i in range(T):
            data = file.readline()
            temp = data.split(", ")
            house = streets.get(temp[0]).houses[int(temp[1])]
            house.set_tavern()
            houses[f"{house.x}, {house.y}"] = True


    return streets, houses, N


def merge_clusters(clusters, x, y):
    clusters.union(x, y)


def upd(distances, clusters, min_dist, min_vert, x, y):
    merge_clusters(clusters, x, y)

    x_row = distances[x, :]
    res = np.minimum(x_row, distances[y, :])

    res[y] = np.inf
    res[x] = np.inf
    distances[y] = res
    distances[:, y] = res
    min_dist[y] = np.inf

    for i in range(clusters.size):
        if res[i] < min_dist[y] and clusters.find(y) != clusters.find(i):
            min_dist[y] = distances[y][i]
            min_vert[y] = i

    return distances, min_dist, min_vert


def merge_step(distances, min_dist, min_vert, clusters):
    x = np.argmin(min_dist)
    y = min_vert[x]
    minimal = min(x, y)
    maximal = max(x, y)

    for i in range(min_vert.size):
        if min_vert[i] == maximal and i != minimal:
            min_vert[i] = minimal

    min_dist[maximal] = np.inf

    distances, min_dist, min_vert = upd(distances, clusters, min_dist, min_vert, maximal,
                                        minimal)

    return distances, min_dist, min_vert, x, y, clusters


def slink(houses, N):

    n = len(houses)
    min_dist = np.full(n, np.inf)
    min_vert = np.zeros(n, dtype=int)
    clusters = DisjointSets(n)

    v = np.zeros((n, 2))

    i = 0
    for key, value in houses.items():
        key = key.split(", ")
        v[i][0] = int(key[0])
        v[i][1] = int(key[1])
        i += 1

    distances = sp.cdist(v, v, metric='euclidean')

    for i in range(n):
        distances[i][i] = np.inf
        min_vert[i] = np.argmin(distances[i])
        min_dist[i] = distances[i][min_vert[i]]

    while clusters.number_of_sets != N:
        distances, min_dist, min_vert, x, y, clusters = merge_step(distances, min_dist, min_vert, clusters)
    return clusters


def draw_map(n, make_a_plot, windowed_plot, save_png, save_districts):

    streets, houses, N = make_a_map(n)

    clusters = slink(houses, N)

    districts = clusterize(clusters, houses, make_a_plot)

    if make_a_plot:
        for key, value in streets.items():
            value.get_plot()

    if save_districts:
        with open(f"./districts/district{n}.txt", "w") as file:
            file.write(f"{len(districts)}\n")
            for key, district in districts.items():
                file.write(f"{district.amount_of_houses} {district.amount_of_taverns}\n")

    if save_png:
        plt.savefig(f"./pics/pic{n}.png", format="png", dpi=1200)

    if windowed_plot:
        plt.show()

    return districts


def get_colors(names_of_clusters):
    available_colors = mcolors.CSS4_COLORS
    to_pop = ["dimgrey", "grey", "darkgrey", "lightgrey", "silver", "gainsboro",
              "whitesmoke", "white", "snow", "brown", "maroon", "mistyrose",
              "seashell", "linen", "tan", "papayawhip", "blanchedalmond", "oldlace",
              "floralwhite", "cornsilk", "ivory", "beige", "lightyellow", "lightgoldenrodyellow",
              "honeydew", "chartreuse", "palegreen", "forestgreen", "mintcream", "azure", "lightcyan",
              "darkslategrey", "teal", "aqua", "powderblue", "lightskyblue", "aliceblue", "lightslategrey",
              "stategrey", "stategray", "ghostwhite", "lavender", "navy", "darkblue", "darkviolet", "plum",
              "purple", "fuchsia", "lightpink", "lavenderbrush", "white", "red", "blue", "bisque", "antiquewhite",
              "moccasin", "lemonchiffon", "wheat", "palegoldenrod"]

    for color in to_pop:
        available_colors.pop(color, None)

    available_colors = list(available_colors.keys())

    colors = {f"{names_of_clusters[i]}": available_colors.pop(randrange(len(available_colors))) for i in range(len(names_of_clusters))}

    return colors


def clusterize(clusters, houses, make_a_plot):

    c = []

    for i in range(clusters.size):
        if clusters.parents[i] == i:
            c.append(i)

    colors = get_colors(c)
    districts = {}

    i = 0
    for point, tavern in houses.items():

        point = point.split(", ")
        x = int(point[0])
        y = int(point[1])

        try:
            districts[f"{clusters.find(i)}"].add_house()
        except KeyError:
            districts[f"{clusters.find(i)}"] = District(1, 0)
        if tavern:
            districts[f"{clusters.find(i)}"].add_tavern()

        if make_a_plot:
            plt.plot([x], [y], color=colors[f"{clusters.find(i)}"], marker="s", zorder=0)
        i += 1

    return districts


"""t = time.time()
for i in range(1, 11):
    t1 = time.time()
    draw_map(i, make_a_plot=True, windowed_plot=False, save_png=True, save_districts=True)
    print(f"test: {i}, time: {time.time() - t1}")
    plt.clf()
print(str(time.time() - t))"""
draw_map(10, make_a_plot=True, windowed_plot=False, save_png=True, save_districts=True)
