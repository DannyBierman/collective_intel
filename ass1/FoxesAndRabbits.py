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
import seaborn as sns
import matplotlib.pyplot as plt

class Configure():
    Fox_population_counter= 20
    Rabbit_population_counter = 50
    Fox_population = []
    Rabbit_population = []
    pass

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
            if distance < 10 and agent.alive():
                agent.kill()
                self.energy += 0.5
                self.reproduce()
                Configure.Fox_population_counter += 1
                Configure.Rabbit_population_counter -= 1
          


    def update(self):
        self.energy -= 0.01  # FOX_ENERGY_DECAY_RATE
        if self.energy <= 0:
            self.kill()
            Configure.Fox_population_counter -= 1
        if self.in_proximity_accuracy():
            self.chase_rabbit()
            self.kill_rabbit()
            
        Configure.Fox_population.append(Configure.Fox_population_counter)
        Configure.Rabbit_population.append(Configure.Rabbit_population_counter)
        

class Rabbit(Agent):
    
    def reproducing(self):
        if random.random() < 0.004:
            self.reproduce()
            Configure.Rabbit_population_counter += 1

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
        .batch_spawn_agents(50, Rabbit, images=["ass1/images/cockroach.png"])
        .batch_spawn_agents(20, Foxes, images=["ass1/images/bird.png"])

        .run()
        .snapshots
)

indices = range(0, len(Configure.Fox_population), 100)
population_subset = [Configure.Fox_population[i] for i in indices]
plt.plot(indices, population_subset, label='Fox population')

r_indices = range(0, len(Configure.Rabbit_population), 100)
r_population_subset = [Configure.Rabbit_population[i] for i in r_indices]
plt.plot(r_indices, r_population_subset, label='Rabbit population')

plt.xlabel('Time')
plt.ylabel('Population')
plt.title('Population Over Time')

plt.legend()

plt.show()
