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
    Fox_population_counter = 35
    Rabbit_population_counter = 50
    Grass_counter = 0
    rabbit_energy_decay_rate = 0.005
    fox_energy_decay_rate = 0.01
    #rabbit_reproduce_rate = 0.02
    #fox_reproduce_rate = 0.01
    fox_sexual_reproduction = 0.5
    rabbit_sexual_reproduction = 0.5

    fox_reproduce_2_thr = 5#3
    fox_reproduce_3_thr=8#5
    rabbit_reproduce_2_thr = 5
    rabbit_reproduce_3_thr=10

    fox_mate_dist = 25
    fox_kill_dist = 10
    rabbit_mate_dist = 10
    rabbit_eat_dist = 5

    Fox_population = []
    Rabbit_population = []



    pass


class Foxes(Agent):
    energy = 1
    timer = 1
    fertile = False

    def mating(self):
        for agent, distance in self.in_proximity_accuracy().filter_kind(Foxes):
            if distance < Configure.fox_mate_dist and agent.alive() and random.random() < Configure.fox_sexual_reproduction:
                self.reproduce()
                Configure.Fox_population_counter += 1
                self.timer = 1
                #print("energy fox at reproduce:")
                #print(self.energy)
                #print("reproduced fox")
                if self.energy > Configure.fox_reproduce_2_thr: #3:
                    self.reproduce()

                    Configure.Fox_population_counter += 1
                    print("reproduced another fox")
                    if self.energy > Configure.fox_reproduce_3_thr: #5:
                        self.reproduce()
                        Configure.Fox_population_counter += 1
                        print("reproduced 3 foxes")
                self.fertile = False

    def kill_rabbit(self):
        for agent, distance in self.in_proximity_accuracy().filter_kind(Rabbit):
            if distance < Configure.fox_kill_dist and agent.alive():
                agent.kill()
                self.energy += 0.5
                # if self.energy > 1 or random.random() < Configure.fox_reproduce_rate:
                # self.reproduce()
                # Configure.Fox_population_counter += 1
                Configure.Rabbit_population_counter -= 1

    def update(self):
        self.timer += 1
        self.energy -= Configure.fox_energy_decay_rate  # FOX_ENERGY_DECAY_RATE
        if self.energy <= 0:
            self.kill()
            Configure.Fox_population_counter -= 1
        if self.in_proximity_accuracy().filter_kind(Rabbit):
            self.kill_rabbit()
        if self.timer % 100 == 0:
            self.fertile = True
        if self.in_proximity_accuracy().filter_kind(Foxes) and self.fertile:
            self.mating()
        Configure.Fox_population.append(Configure.Fox_population_counter)
        Configure.Rabbit_population.append(Configure.Rabbit_population_counter)


class Rabbit(Agent):
    energy = 1
    timer = 1
    fertile = False

    def eating_grass(self):
        for agent, distance in self.in_proximity_accuracy().filter_kind(Grass):
            if distance < Configure.rabbit_eat_dist and self.in_proximity_accuracy().filter_kind(
                    Rabbit).count() == 0 and agent._image_index == 0:
                self.freeze_movement()
                Configure.Grass_counter += 1
                if Configure.Grass_counter % 50 == 0:
                    agent.change_image(1)
                    agent.timer = 1
                    self.energy += 0.5
                    # print("Ate grass")
                    self.continue_movement()
                    # if self.energy>1:
                    # self.reproduce()
                    # Configure.Rabbit_population_counter+=1
                    Configure.Grass_counter = 1

    def mating(self):
        for agent, distance in self.in_proximity_accuracy().filter_kind(Rabbit):
            if distance < Configure.rabbit_mate_dist and agent.alive() and random.random() < Configure.rabbit_sexual_reproduction:
                self.reproduce()
                #print("energy rabbit at reproduce:")
                #print(self.energy)
                Configure.Rabbit_population_counter += 1
                self.timer = 1
                self.fertile = False
                #print("reproduced rabbit")
                if self.energy > Configure.rabbit_reproduce_2_thr:#3:
                    self.reproduce()
                    Configure.Rabbit_population_counter += 1
                    print("reproduced another rabbit")
                    if self.energy > Configure.rabbit_reproduce_3_thr: #5:
                        self.reproduce()
                        Configure.Rabbit_population_counter += 1
                        print("reproduced 3 rabbits")


    def update(self):
        self.timer += 1
        self.energy -= Configure.rabbit_energy_decay_rate
        if self.energy<0:
            self.kill()
        if self.timer % 40 == 0:
            self.fertile = True
        if self.in_proximity_accuracy().filter_kind(Rabbit).count()<3 and not self.eating_grass() and self.fertile:
            self.mating()
        if self.in_proximity_accuracy().filter_kind(Grass):
            self.eating_grass()
        Configure.Fox_population.append(Configure.Fox_population_counter)
        Configure.Rabbit_population.append(Configure.Rabbit_population_counter)


class Grass(Agent):
    timer = 0

    def change_position(self):
        pass

    def update(self):
        self.timer += 1
        if self._image_index == 1 and self.timer % 80 == 0:
            self.reproduce()


data_frame = (
    Simulation(
        Config(
            image_rotation=True,
            movement_speed=15,
            duration=60 * 30,
            radius=20,
            seed=-1,
            fps_limit=30

        )
    )
        .batch_spawn_agents(50, Rabbit, images=["images/rabbit head.png"])
        .batch_spawn_agents(35, Foxes, images=["images/fox head.png"])
        .batch_spawn_agents(30, Grass, images=["images/green2.png", "images/green.png"])
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
second = [x * 60 / max_index for x in indices]
plt.plot(second, population_subset, label='Fox population')

r_indices = list(range(0, len(Configure.Rabbit_population), 100))
r_population_subset = [Configure.Rabbit_population[i] for i in r_indices]
r_second = [x * 60 / max_index for x in indices]
plt.plot(r_second, r_population_subset, label='Rabbit population')

plt.xlabel('Time (Seconds)')
plt.ylabel('Population')
plt.title('Population Over Time')

plt.legend()

plt.show()
