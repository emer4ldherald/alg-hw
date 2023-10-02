import random


class Job:

    def __init__(self, number: int, deadline: int, penalty: int):
        self.deadline = deadline
        self.penalty = penalty
        self.number = number

    def print(self):
        print("Number: " + str(self.number) + ", deadline: " + str(self.deadline) + ", penalty: " + str(self.penalty))


class DisjointSets:

    def __init__(self, size: int):
        self.parents = [i for i in range(size)]
        self.ranks = [0 for i in range(size)]
        self.size = size
        self.left_bound = False

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
        else:
            self.parents[root_of_x] = root_of_y
            if self.ranks[root_of_x] == self.ranks[root_of_y]:
                self.ranks[root_of_y] += 1

    def union_for_scheduling(self, x, y: int, earliest):
        root_of_x = self.find(x)
        root_of_y = self.find(y)
        if earliest[root_of_x] < earliest[root_of_y]:
            earliest[root_of_y] = earliest[root_of_x]
        else:
            earliest[root_of_x] = earliest[root_of_y]
        self.union(x, y)

    def print(self):
        print(str(self.parents) + "\n")

    def getTime(self, time: int, right: int, earliest):
        t = earliest[self.find(time)]
        if not self.left_bound and t == 0:
            self.left_bound = True
            return t, True
        elif self.left_bound and t == 0:
            self.union_for_scheduling(right, right - 1, earliest)
            return right, False
        elif t == right:
            self.union_for_scheduling(right, right - 1, earliest)
            return right, True
        else:
            self.union_for_scheduling(t, t - 1, earliest)
            return t, True


class JobScheduling:

    def __init__(self, jobs: str):
        jobs = jobs.split("\n")
        self.amount = int(jobs[0])
        self.jobs = []
        self.earliest = [i for i in range(self.amount)]
        for i in range(1, self.amount + 1):
            deadline, penalty = list(map(int, jobs[i].split()))
            self.jobs.append(Job(i - 1, deadline, penalty))
        self.jobs.sort(key=lambda x: x.penalty, reverse=True)
        self.links = [0 for i in range(self.amount)]
        for i in range(self.amount):
            self.links[self.jobs[i].number] = i

    def linkOf(self, x: int):
        return self.links[x]

    def print(self):
        for i in range(self.amount):
            self.jobs[i].print()
        print(str(self.links))

    def solve(self):
        deadlines = DisjointSets(self.amount)
        schedule = [-1 for i in range(self.amount)]
        right_bound = self.amount - 1
        penalty = 0
        for i in range(self.amount):
            job = self.jobs[i]
            time, allowed = deadlines.getTime(job.deadline - 1, right_bound, self.earliest)
            if not allowed:
                right_bound = self.earliest[deadlines.find(time)]
                penalty += job.penalty
            elif right_bound == time:
                right_bound = self.earliest[deadlines.find(time)]
            schedule[time] = job.number
        return schedule, penalty


def test(num: int):
    with open(f"jobs{num}.txt", 'r') as file:
        jobs = file.read()
        js = JobScheduling(jobs)
        s, p = js.solve()
        print(str(s))
        print(str(p))


def generate_problem(amount, number):
    with open(f"jobs{number}.txt", "w") as file:
        file.write(str(amount) + "\n")
        for i in range(amount):
            deadline = random.randint(1, amount)
            penalty = random.randint(3, 50)
            temp = f"{deadline} {penalty}\n"
            file.write(temp)


#generate_problem(1000, 6)
test(5)
