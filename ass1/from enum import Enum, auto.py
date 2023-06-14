from enum import Enum, auto
from turtle import pos
from vi import Agent, Simulation
import pygame as pg
from pygame.math import Vector2
from vi import Agent, Simulation
from vi.config import Config, dataclass, deserialize
import random
import numpy as np

(
    Simulation()
    .batch_spawn_agents(100, Agent, images=["images/bird.png"])
    .run()
)

class State(Enum):
    Wandering = auto()
    Joining = auto()
    Still = auto()
    Leaving = auto()


class MyAgent(Agent):

    def wandering(self):
        self.pos += Vector2(np.random.randit(10,2))
        return self.pos

    def probability_join(self, Neighbours):
        
        neighbour_count = 0
        for bird, distance in Neighbours:
            neighbour_count +=1

        probability = 0
        if neighbour_count > 5:
            probability = 1
        else :
            probability = neighbour_count / 5
        return probability

    def joining(self, Neighbours):
        neighbours = list(self.in_proximity_accuracy())
        bird_positions = [bird.pos for bird, distance in neighbours]
        position_sum = sum(bird_positions, Vector2())
        if random.random() < self.probability_joint(neighbours):
            average_pos = position_sum / len(neighbours)
            force_c = average_pos - self.pos
            return force_c - self.move
        else:
            return Vector2()


    def probability_leave(self, Neighbours):
        neighbour_count = 0
        for bird, distance in Neighbours:
            neighbour_count += 1

        probability = 0
        if neighbour_count < 3: #low density = leave high prob
            probability = 1
        else:
            probability = 3/ neighbour_count #low prob
        return probability

    def leaving(self, Neighbours):
        neighbours = list(self.in_proximity_accuracy())
        bird_positions = [bird.pos for bird, distance in neighbours]
        position_sum = sum(bird_positions, Vector2())
        if random.random() < self.probability_leave(neighbours):
            average_pos = position_sum / len(neighbours)
            force_c = self.pos - average_pos
            return force_c - self.move
        else:
            #stay
            return Vector2()

        self.move += self.pos * self.Agent

                 


        

