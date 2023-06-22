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
                self.reproduce()
                #print("killed a rabbit")
                Configure.Fox_population_counter += 1
                Configure.Rabbit_population_counter -= 1

    def update(self):
        self.energy -= 0.01  # FOX_ENERGY_DECAY_RATE
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
        if random.random() < 0.004:
            self.reproduce()
            Configure.Rabbit_population_counter += 1

    def eating_grass(self):
        for agent, distance in self.in_proximity_accuracy().filter_kind(Grass):
            if distance < 10 and self.in_proximity_accuracy().filter_kind(Rabbit).count() == 0 and agent._image_index == 0:
                self.freeze_movement()
                Configure.Grass_counter += 1
                if Configure.Grass_counter % 50 == 0:
                    agent.change_image(1)
                    agent.timer = 1
                    self.energy += 0.5
                    #print("Ate grass")
                    self.continue_movement()
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
        self.energy -= 0.001
        if not self.eating_grass():
            self.reproducing()
        self.eating_grass()
        #if self.in_proximity_accuracy().without_distance().filter_kind(Foxes):
            #self.running()

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
                # duration= 1*60,
                radius=15,
                seed=1,
                fps_limit=30

        )
    )
        .batch_spawn_agents(50, Rabbit, images=["ass1/images/rabbit head.png"])
        .batch_spawn_agents(20, Foxes, images=["ass1/images/fox head.png"])
        .batch_spawn_agents(20, Grass, images=["ass1/images/green2.png","ass1/images/green.png"])
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






