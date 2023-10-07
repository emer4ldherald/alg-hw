from random import randrange

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import scipy.spatial.distance as sp


class District:

    def __init__(self, amount_of_houses, amount_of_taverns):
        self.amount_of_houses = amount_of_houses
        self.amount_of_taverns = amount_of_taverns


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

        for i in range(1, S + 1):
            data = file.readline()
            temp = data.split()
            prefix = temp[0]
            street_type = temp[1]
            start_x = temp[2]
            start_y = temp[3]
            number_of_houses = temp[4]
            distance_between_houses = temp[5]
            street = Street(prefix, street_type, start_x, start_y, number_of_houses, distance_between_houses)
            streets[prefix + " " + street_type] = street

        for i in range(T):
            data = file.readline()
            temp = data.split(", ")
            streets.get(temp[0]).houses[int(temp[1])].set_tavern()

    return streets, N


def merge_clusters(clusters, x, y):

    min_cl = min(x, y)
    max_cl = max(x, y)
    clusters[min_cl].extend(clusters[max_cl])
    clusters.pop(max_cl)


def update_matrix_of_distances(distances, clusters, min_dist, min_vert, x, y):

    merge_clusters(clusters, x, y)
    x_row = distances[x, :]
    res = np.minimum(x_row, distances[y, :])

    res[y] = np.inf
    res[x] = np.inf
    distances[y] = res
    distances[:, y] = res

    distances = np.delete(distances, x, axis=0)
    distances = np.delete(distances, x, axis=1)

    min_vert[y] = np.argmin(res)
    min_dist[y] = res[min_vert[y]]

    for i in range(min_vert.size):
        if min_vert[i] >= x:
            min_vert[i] -= 1

    return distances, min_dist, min_vert


def merge_step(distances, min_dist, min_vert, clusters):

    x = np.argmin(min_dist)
    y = min_vert[x]
    minimal = min(x, y)
    maximal = max(x, y)

    for i in range(min_vert.size):
        if min_vert[i] == maximal and i != minimal:
            min_vert[i] = minimal

    distances, min_dist, min_vert = update_matrix_of_distances(distances, clusters, min_dist, min_vert, maximal,
                                                               minimal)
    min_dist = np.delete(min_dist, maximal)
    min_vert = np.delete(min_vert, maximal)
    return distances, min_dist, min_vert, x, y, clusters


def slink(houses, N):

    n = len(houses)
    min_dist = np.full(n, np.inf)
    min_vert = np.zeros(n, dtype=int)
    clusters = [[i] for i in range(n)]

    v = np.zeros((n, 2))

    for i in range(n):
        v[i][0] = houses[i].x
        v[i][1] = houses[i].y

    distances = sp.cdist(v, v, metric='euclidean')

    for i in range(n):
        distances[i][i] = np.inf
        min_vert[i] = np.argmin(distances[i])
        min_dist[i] = distances[i][min_vert[i]]

    while distances.shape != (N, N):
        distances, min_dist, min_vert, x, y, clusters = merge_step(distances, min_dist, min_vert, clusters)

    return clusters


def draw_map(n, make_a_plot, windowed_plot, save_png, save_districts):

    streets, N = make_a_map(n)
    temp = {}

    for name, street in streets.items():
        for house in street.houses:
            try:
                if not temp[f"{house.x}, {house.y}"]:
                    temp[f"{house.x}, {house.y}"] = house.tavern
            except KeyError:
                temp[f"{house.x}, {house.y}"] = house.tavern

    houses = []

    for key, tavern in temp.items():
        key = key.split(", ")
        h = House(int(key[0]), int(key[1]))
        if tavern:
            h.set_tavern()
        houses.append(h)

    clusters = slink(houses, N)

    if make_a_plot:
        for key, value in streets.items():
            value.get_plot()

    districts = clusterize(clusters, houses, make_a_plot)

    if save_districts:
        with open(f"./districts/district{n}.txt", "w") as file:
            file.write(f"{len(districts)}\n")
            for d in districts:
                file.write(f"{d.amount_of_houses} {d.amount_of_taverns}\n")

    if save_png:
        plt.savefig(f"./pics/pic{n}.png", format="png", dpi=900)

    if windowed_plot:
        plt.show()

    return districts


def get_colors():

    colors = mcolors.CSS4_COLORS
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
        colors.pop(color, None)

    return list(colors.keys())


def clusterize(clusters, houses, make_a_plot):

    colors = get_colors()
    districts = []

    for cluster in clusters:

        amount_of_houses = 0
        amount_of_taverns = 0
        color = colors.pop(randrange(len(colors)+1))

        for house in cluster:
            if make_a_plot:
                plt.plot([houses[house].x], [houses[house].y], color=color, marker="s", zorder=0)
            amount_of_houses += 1
            if houses[house].tavern:
                amount_of_taverns += 1

        districts.append(District(amount_of_houses, amount_of_taverns))

    return districts


for i in range(1, 11):
    draw_map(i, make_a_plot=False, windowed_plot=False, save_png=False, save_districts=False)
    plt.clf()
