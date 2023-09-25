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
        self.size = size
        self.left_bound = False

    def find(self, x: int):
        parent_of_x = self.parents[x]
        if parent_of_x != x:
            parent_of_x = self.find(parent_of_x)
        return parent_of_x

    def union(self, x, y: int):  # x to y
        self.parents[self.find(x)] = self.find(y)

    def print(self):
        print(str(self.parents) + "\n")

    def getTime(self, time: int, right: int, penalty: int):
        t = self.find(time)
        if not self.left_bound and t == 0:
            self.left_bound = True
            return t, True
        elif self.left_bound and t == 0:
            self.union(right, right-1)
            return right, False
        else:
            self.union(t, t-1)
            return t, True


class JobScheduling:

    def __init__(self, jobs: str):
        jobs = jobs.split("\n")
        self.amount = int(jobs[0])
        self.jobs = []
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
            time, allowed = deadlines.getTime(job.deadline - 1, right_bound, penalty)
            if not allowed:
                right_bound -= 1
                penalty += job.penalty
            elif right_bound == time:
                right_bound -= 1
            schedule[time] = job.number
        return schedule, penalty

def test(num: int):
    with open(f"jobs{num}.txt", 'r') as file:
        jobs = file.read()
        js = JobScheduling(jobs)
        s, p = js.solve()
        print(str(s))
        print(str(p))
      
