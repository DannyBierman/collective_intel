from enum import Enum, auto
from turtle import pos
from vi import Agent, Simulation, probability
import pygame as pg
from pygame.math import Vector2
from vi import Agent, Simulation
from vi.config import Config, dataclass, deserialize
import random
import numpy as np
import math
import polars as pl

class Foxes(Agent):
    energy = 1

    def chase_rabbit(self):
        target_rabbits = []
        for agent in self.in_proximity_accuracy().without_distance().filter_kind(Rabbit):
            target_rabbits.append(agent.pos)
        position_sum = sum(target_rabbits, Vector2())
        if self.in_proximity_accuracy().filter_kind(Rabbit).count() > 0:
            average_pos = position_sum / self.in_proximity_accuracy().filter_kind(Rabbit).count()
            self.move = self.pos-average_pos
            self.move = self.move.normalize()
            self.pos += self.move

    def kill_rabbit(self):
        for agent, distance in self.in_proximity_accuracy().filter_kind(Rabbit):
            if distance < 10:
                agent.kill()
                self.energy += 0.5
                self.reproduce()
                print("killed a rabbit")

    def update(self):
        self.energy -= 0.01  # FOX_ENERGY_DECAY_RATE
        if self.energy <= 0:
            self.kill()
        if self.in_proximity_accuracy():
            self.chase_rabbit()
            self.kill_rabbit()

class Rabbit(Agent):

    def reproducing(self):
        if random.random() < 0.004:
            self.reproduce()

    def update(self):
        self.reproducing()



data_frame = (
    Simulation(
        Config(
                image_rotation=True,
                movement_speed=10,
                # duration= 1*60,
                radius=15,
                seed=1,
                fps_limit=30
        )
    )
        .batch_spawn_agents(50, Rabbit, images=["images/cockroach.png"])
        .batch_spawn_agents(20, Foxes, images=["images/bird.png"])

        .run()
        .snapshots
)