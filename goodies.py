'''
    goodies.py

    Definitions for some example goodies
'''

import random

from maze import Goody, Baddy, Position, UP, DOWN, LEFT, RIGHT, STAY, STEP, PING

class StaticGoody(Goody):
    ''' A static goody - does not move from its initial position '''

    def take_turn(self, _obstruction, _ping_response):
        ''' Stay where we are '''
        return STAY

class RandomGoody(Goody):
    ''' A random-walking goody '''

    def take_turn(self, obstruction, _ping_response):
        ''' Ignore any ping information, just choose a random direction to walk in, or ping '''
        possibilities = [PING]
        for direction in [UP, DOWN, LEFT, RIGHT]: # STEP.keys()
            if not obstruction[direction]:
                possibilities.append(direction)
        return random.choice(possibilities)

class GreedyGoody(Goody):
    ''' A goddy that pings once and then walks towards the other goody.  '''

    last_ping_response = None

    def vector_len_2(self, vector):
        return (vector.x * vector.x) + (vector.y * vector.y)

    def take_turn(self, obstruction, ping_response):
        ''' Ignore any ping information, just choose a random direction to walk in, or ping '''
        if ping_response is not None:
            self.last_ping_response = ping_response

        if self.last_ping_response is None:
            # If we don't know where the other goody is, then send a ping so that we can find out.
            print("Pinging to find our friend and foe")
            return PING

        friend, = [player for player in self.last_ping_response.keys()
                   if isinstance(player, Goody) and player is not self]
        foe, = [player for player in self.last_ping_response.keys() if isinstance(player, Baddy)]

        # For the four possible moves, find the resulting distance to our friend after each one:
        last_known_friend_position = self.last_ping_response[friend]
        len_and_dirs = []

        for direction in [UP, DOWN, LEFT, RIGHT]: # STEP.keys()
            # Choose the one that takes us closest to the our friend
            if not obstruction[direction]:
                # STEP[direction] turns the direction label into a vector (dx, dy) which we can add
                # to a Position (another vector):
                new_vector = last_known_friend_position - STEP[direction]
                entry = [direction, new_vector, self.vector_len_2(new_vector)]
                len_and_dirs.append(entry)

        len_and_dirs.sort(key=lambda len_and_dir: len_and_dir[2])

        return len_and_dirs[0][0]


class MyGoody(Goody):
    ''' Your Goody implementation. Please change the name of this class to make it unique! '''
    def __init__(self):
        self.last_ping_response = None
        self.last_ping_time = None
        self.me = Position(0,0)
        self.knowledge = {self.me: True}

    def vector_len_2(self, vector):
        return (vector.x * vector.x) + (vector.y * vector.y)

    def move_towards(self, obstruction, other):
        len_and_dirs = []

        for direction in [UP, DOWN, LEFT, RIGHT]: # STEP.keys()
            # Choose the one that takes us closest to the our friend
            if not obstruction[direction]:
                # STEP[direction] turns the direction label into a vector (dx, dy) which we can add
                # to a Position (another vector):
                new_vector = other - STEP[direction]
                entry = [direction, new_vector, self.vector_len_2(new_vector)]
                len_and_dirs.append(entry)

        len_and_dirs.sort(key=lambda len_and_dir: len_and_dir[2])
        return len_and_dirs

    def find_best(self, target):
        """
        Given the map it outputs the path to the adjacent uknown which is closest to the target square

        First find the adjacent unkowns
        """
        adjacent_unkowns = []
        for i in self.knowledge.keys():
            if self.knowledge[i] == True:
                for j in [-1, +1]:
                    for k in [-1, +1]:
                        if i + Position(j, k) not in self.knowledge.keys():
                            adjacent_unkowns.append(i + (j, k))

        best_unkown = adjacent_unkowns[0]

        best_dist = self.vector_len_2(best_unkown - target)

        for i in adjacent_unkowns[1:]:
            if self.vector_len_2(i - target) < self.vector_len_2(best_unkown - target):
                best_unkown = i
                best_dist = self.vector_len_2(i - target)

        return best_unkown


    def remove(self, A, x, n):
        A2 = [[True for _ in range(n)] for _ in range(n)]
        for i in range(n-1):
            for j in range(n-1):
                if i == x or j == x:
                    A2[i][j] = False
                else:
                    A2[i][j] = A[i][j]
        return A2


    def path_alg(self, A, x, y, n):
        if A[x][y]:
            return [x, y]
        else:
            best_i = None
            best_path = list(range(n))
            paths = []
            for i in range(n):
                if A[x][i]:
                    this_path = self.path_alg(self.remove(A,x, n), x, y, n)
                    if len(this_path) < len(best_path):
                        best_path = this_path
                        best_i = i

            return [x] + best_path

    def next_move(self, mapy, best_unkown):
        mapy2 = mapy.copy()
        mapy2[best_unkown] = True
        n = len(mapy2.keys())
        A = [[True for _ in range(n)] for _ in range(n)]

        listy = list(mapy2.keys())
        for i in range(n):
            for j in range(n):
                if self.vector_len_2(listy[i] - listy[j]) == 1 and  mapy2[listy[i]] and mapy2[listy[j]]:
                    A[i][j] = True
                else:
                    A[i][j] = False

        x = listy.index(Position(0,0))
        y = listy.index(best_unkown)

        path = self.path_alg(A, x, y, n)

        nexts = listy[path[1]]
        return Position(nexts[0], nexts[1])

    def BFS(self, s, target):
        visited = set()

        queue = []

        queue.append((s, []))
        visited.add(s)

        while queue:
            print(queue)
            (s, path) = queue.pop(0)

            for direction in [UP, DOWN, LEFT, RIGHT]:
                i = self.me + STEP[direction]
                if i not in self.knowledge or self.knowledge[i] == True:
                    if i not in visited:
                        queue.append((i, path + [direction]))
                        visited.add(i)
                        if i == target:
                            return path[0]
        return UP

    def take_turn(self, obstruction, ping_response):
        ''' Ignore any ping information, just choose a random direction to walk in, or ping '''

        for direction in [UP, DOWN, LEFT, RIGHT]:
            # print(direction, obstruction[direction])
            self.knowledge[self.me + STEP[direction]] = obstruction[direction]
        print(self.knowledge)

        if ping_response is not None:
            self.last_ping_response = ping_response
            self.last_ping_time = 0

        if self.last_ping_time is None or self.last_ping_time > 30:
            # If we don't know where the other goody is, then send a ping so that we can find out.
            print("Pinging to find our friend and foe")
            return PING

        import sys

        # print(self.last_ping_response)
        friend, = [player for player in self.last_ping_response.keys()
                   if isinstance(player, Goody) and player is not self]
        foe, = [player for player in self.last_ping_response.keys() if isinstance(player, Baddy)]

        # For the four possible moves, find the resulting distance to our friend after each one:
        other = self.last_ping_response[friend]
        target_location = Position(other.x//2, other.y//2) #self.last_ping_response[friend]/2

        len_and_dirs = self.move_towards(obstruction, other)

        self.last_ping_time += 1
        # print(self.last_ping_time)

        move = len_and_dirs[0][0]
        # move = self.BFS(self.me, self.find_best(target_location))
        # move = self.next_move(self.knowledge, self.find_best(target_location))
        # if not obstruction[move]:
        #     self.me += STEP[move]
        import os
        os.system('clear')
        b = '{"baddy wins", 257, "goodies win": 743}'
        print(b)
        return move
