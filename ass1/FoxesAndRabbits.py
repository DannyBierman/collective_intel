from enum import Enum, auto
from turtle import pos
from vi import Agent, Simulation, probability
import pygame as pg
from pygame.math import Vector2
from vi import Agent, Simulation
from vi.config import Config, dataclass, deserialize, Window
import random
import numpy as np
import math
import polars as pl
import seaborn as sns
import matplotlib.pyplot as plt

class Configure():
    Fox_population_counter= 20
    Rabbit_population_counter = 50
    Grass_counter = 0
    rabbit_energy_decay_rate = 0.001
    fox_energy_decay_rate = 0.03
    rabbit_reproduce_rate = 0.02
    fox_reproduce_rate = 0.01
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
            self.move = (self.pos-average_pos)
            self.move = self.move.normalize()
            self.pos += self.move

    def kill_rabbit(self):
        for agent, distance in self.in_proximity_accuracy().filter_kind(Rabbit):
            if distance < 10 and agent.alive():
                agent.kill()
                self.energy += 0.5
                if self.energy > 1 or random.random() < Configure.fox_reproduce_rate:                    
                    self.reproduce()
                    Configure.Fox_population_counter += 1
                Configure.Rabbit_population_counter -= 1

    def update(self):
        self.energy -= Configure.fox_energy_decay_rate  # FOX_ENERGY_DECAY_RATE
        if self.energy <= 0:
            self.kill()
            Configure.Fox_population_counter -= 1
        if self.in_proximity_accuracy().filter_kind(Rabbit):
            self.kill_rabbit()
        Configure.Fox_population.append(Configure.Fox_population_counter)
        Configure.Rabbit_population.append(Configure.Rabbit_population_counter)
            #self.chase_rabbit()


class Rabbit(Agent):
    energy = 1
    def reproducing(self):
        if random.random() < Configure.rabbit_reproduce_rate:
            self.reproduce()
            Configure.Rabbit_population_counter += 1

    def eating_grass(self):
        for agent, distance in self.in_proximity_accuracy().filter_kind(Grass):
            if distance < 10 and self.in_proximity_accuracy().filter_kind(Rabbit).count() == 0 and agent._image_index == 0:
                self.freeze_movement()
                if Configure.Grass_counter % 50 == 0:
                    agent.change_image(1)
                    agent.timer = 1
                    self.energy += 0.5
                    #print("Ate grass")
                    self.continue_movement()
                    if self.energy>1:
                        self.reproduce()
                        Configure.Rabbit_population_counter+=1
                    Configure.Grass_counter += 1
    def running(self):
        foxes = []
        for agent in self.in_proximity_accuracy().without_distance().filter_kind(Foxes):
            foxes.append(agent.pos)
        position_sum = sum(foxes, Vector2())
        if self.in_proximity_accuracy().filter_kind(Foxes).count() > 0:
            average_pos = position_sum / self.in_proximity_accuracy().filter_kind(Foxes).count()
            self.move = self.pos-average_pos
            self.move = self.move.normalize()
            self.pos -= self.move

    def update(self):
        self.energy -= Configure.rabbit_energy_decay_rate
        if not self.eating_grass():
            self.reproducing()
        self.eating_grass()

class Grass(Agent):
    timer = 0

    def change_position(self):
        pass

    def update(self):
        self.timer += 1
        if self._image_index == 1 and self.timer % 180 == 0:
            self.reproduce()


data_frame = (
    Simulation(
        Config(
                image_rotation=True,
                movement_speed=8,
                duration= 60*30,
                radius=15,
                seed=19,
                fps_limit=30

        )
    )
        .batch_spawn_agents(50, Rabbit, images=["images/rabbit head.png"])
        .batch_spawn_agents(20, Foxes, images=["images/fox head.png"])
        .batch_spawn_agents(20, Grass, images=["images/green2.png","images/green.png"])
        .run()
        .snapshots

)
# Calculate variance of fox population
fox_population_variance = np.var(Configure.Fox_population)

# Calculate variance of rabbit population
rabbit_population_variance = np.var(Configure.Rabbit_population)

print("Variance of Fox population:", fox_population_variance)
print("Variance of Rabbit population:", rabbit_population_variance)

indices = list(range(0, len(Configure.Fox_population), 100))
max_index = max(indices)
population_subset = [Configure.Fox_population[i] for i in indices]
second = [x*60/max_index for x in indices]
plt.plot(second, population_subset, label='Fox population')


r_indices = list(range(0, len(Configure.Rabbit_population), 100))
r_population_subset = [Configure.Rabbit_population[i] for i in r_indices]
r_second = [x*60/max_index for x in indices]
plt.plot(r_second, r_population_subset, label='Rabbit population')

plt.xlabel('Time (Seconds)')
plt.ylabel('Population')
plt.title('Population Over Time')

plt.legend()

plt.show()






