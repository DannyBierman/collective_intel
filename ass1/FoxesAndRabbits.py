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
    #do not change:
    Fox_population_counter = 20
    Rabbit_population_counter = 50
    Grass_counter = 0
    rabbit_energy_decay_rate = 0.004
    fox_energy_decay_rate = 0.01
    fox_kill_dist = 10
    fox_kill_dist_male = 15 #killing advantage
    rabbit_eat_dist = 10

    #only change:
    fox_reproduce_2_thr = 4#3
    fox_reproduce_3_thr=6#5
    rabbit_reproduce_2_thr = 1
    rabbit_reproduce_3_thr=2

    fox_mate_dist = 25
    rabbit_mate_dist = 65

    Fox_population = []
    Rabbit_population = []

    pass


class Foxes_male(Agent):
    energy = 1 #can adjust for survival adv

    def kill_rabbit(self):
        for agent, distance in self.in_proximity_accuracy().filter_kind(Rabbit_male):
            if distance < Configure.fox_kill_dist_male and agent.alive():
                agent.kill()
                self.energy += 0.5
                Configure.Rabbit_population_counter -= 1
        for agent, distance in self.in_proximity_accuracy().filter_kind(Rabbit_female):
            if distance < Configure.fox_kill_dist_male and agent.alive():
                agent.kill()
                self.energy += 0.5
                Configure.Rabbit_population_counter -= 1

    def update(self):
        self.energy -= Configure.fox_energy_decay_rate  # FOX_ENERGY_DECAY_RATE
        if self.energy <= 0:
            self.kill()
            Configure.Fox_population_counter -= 1
        if self.in_proximity_accuracy().filter_kind(Rabbit_male) or self.in_proximity_accuracy().filter_kind(Rabbit_female) :
            self.kill_rabbit()
        Configure.Fox_population.append(Configure.Fox_population_counter)
        Configure.Rabbit_population.append(Configure.Rabbit_population_counter)

class Foxes_female(Agent):
    energy = 1
    fertility_timer = 1
    reproduction_timer = 1
    fertile = False

    def mating(self):
        for agent, distance in self.in_proximity_accuracy().filter_kind(Foxes_male):
            if distance < Configure.fox_mate_dist and agent.alive():
                self.freeze_movement()
                #agent.freeze_movement()
                print("freeze")
                self.reproduction_timer += 1
                if self.reproduction_timer % 50 == 0:
                    if random.random() < 0.5:
                        self.reproduce()  # female offspring
                    else:
                        agent.reproduce()  # male offspring
                    Configure.Fox_population_counter += 1
                    self.fertility_timer = 1
                    # print("energy fox at reproduce:")
                    # print(self.energy)
                    # print("reproduced fox")
                    if self.energy > Configure.fox_reproduce_2_thr:  # 3:
                        if random.random() < 0.5:
                            self.reproduce()  # female offspring
                        else:
                            agent.reproduce()  # male offspring
                        Configure.Fox_population_counter += 1
                        print("reproduced another fox")
                        if self.energy > Configure.fox_reproduce_3_thr:  # 5:
                            if random.random() < 0.5:
                                self.reproduce()  # female offspring
                            else:
                                agent.reproduce()  # male offspring
                            Configure.Fox_population_counter += 1
                            print("reproduced 3 foxes")
                    self.fertile = False
                    self.continue_movement()
                    #agent.continue_movement()

    def kill_rabbit(self):
        for agent, distance in self.in_proximity_accuracy().filter_kind(Rabbit_male):
            if distance < Configure.fox_kill_dist and agent.alive():
                agent.kill()
                self.energy += 0.5
                Configure.Rabbit_population_counter -= 1
        for agent, distance in self.in_proximity_accuracy().filter_kind(Rabbit_female):
            if distance < Configure.fox_kill_dist and agent.alive():
                agent.kill()
                self.energy += 0.5
                Configure.Rabbit_population_counter -= 1

    def update(self):
        self.fertility_timer += 1
        self.energy -= Configure.fox_energy_decay_rate  # FOX_ENERGY_DECAY_RATE
        if self.energy <= 0:
            self.kill()
            Configure.Fox_population_counter -= 1
        if self.in_proximity_accuracy().filter_kind(Rabbit_male) or self.in_proximity_accuracy().filter_kind(Rabbit_female):
            self.kill_rabbit()
        if self.fertility_timer % 100 == 0:
            self.fertile = True
        if self.in_proximity_accuracy().filter_kind(Foxes_male) and self.fertile:
            self.mating()
        Configure.Fox_population.append(Configure.Fox_population_counter)
        Configure.Rabbit_population.append(Configure.Rabbit_population_counter)

class Rabbit_male(Agent):
    energy = 1
    timer = 1
    fertile = False

    def eating_grass(self):
        for agent, distance in self.in_proximity_accuracy().filter_kind(Grass):
            if distance < Configure.rabbit_eat_dist and self.in_proximity_accuracy().filter_kind(Rabbit_male).count() == 0  and self.in_proximity_accuracy().filter_kind(Rabbit_female).count() == 0 and self.in_proximity_accuracy().filter_kind(Rabbit_female).count() == 0 and agent._image_index == 0:
                self.freeze_movement()
                Configure.Grass_counter += 1
                if Configure.Grass_counter % 50 == 0:
                    agent.change_image(1)
                    agent.timer = 1
                    self.energy += 0.5
                    # print("Ate grass")
                    self.continue_movement()
                    Configure.Grass_counter = 1


    def update(self):
        self.timer += 1
        self.energy -= Configure.rabbit_energy_decay_rate
        if self.energy<0:
            self.kill()
        if self.in_proximity_accuracy().filter_kind(Grass):
            self.eating_grass()
        Configure.Fox_population.append(Configure.Fox_population_counter)
        Configure.Rabbit_population.append(Configure.Rabbit_population_counter)

class Rabbit_female(Agent):
    energy = 1
    timer = 1
    fertile = False

    def eating_grass(self):
        for agent, distance in self.in_proximity_accuracy().filter_kind(Grass):
            if distance < Configure.rabbit_eat_dist and self.in_proximity_accuracy().filter_kind(Rabbit_male).count() == 0 and self.in_proximity_accuracy().filter_kind(Rabbit_female).count() == 0 and agent._image_index == 0:
                self.freeze_movement()
                Configure.Grass_counter += 1
                if Configure.Grass_counter % 50 == 0:
                    agent.change_image(1)
                    agent.timer = 1
                    self.energy += 0.5
                    # print("Ate grass")
                    self.continue_movement()
                    Configure.Grass_counter = 1

    def mating(self):
        for agent, distance in self.in_proximity_accuracy().filter_kind(Rabbit_male):
            if distance < Configure.rabbit_mate_dist and agent.alive():
                if random.random() <0.5:
                    self.reproduce() #female offspring
                else:
                    agent.reproduce() #male offspring
                #print("energy rabbit at reproduce:")
                #print(self.energy)
                Configure.Rabbit_population_counter += 1
                self.timer = 1
                self.fertile = False
                #print("reproduced rabbit")
                if self.energy > Configure.rabbit_reproduce_2_thr:#3:
                    if random.random() < 0.5:
                        self.reproduce()  # female offspring
                    else:
                        agent.reproduce()  # male offspring
                    Configure.Rabbit_population_counter += 1
                    print("reproduced another rabbit")
                    if self.energy > Configure.rabbit_reproduce_3_thr: #5:
                        if random.random() < 0.5:
                            self.reproduce()  # female offspring
                        else:
                            agent.reproduce()  # male offspring
                        Configure.Rabbit_population_counter += 1
                        print("reproduced 3 rabbits")


    def update(self):
        self.timer += 1
        self.energy -= Configure.rabbit_energy_decay_rate
        if self.energy<0:
            self.kill()
        if self.timer % 40 == 0:
            self.fertile = True
        if self.in_proximity_accuracy().filter_kind(Rabbit_female).count()<3 and not self.eating_grass() and self.fertile:
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
        .batch_spawn_agents(25, Rabbit_female, images=["images/rabbit head.png"])
        .batch_spawn_agents(25, Rabbit_male, images=["images/rabbit head.png"])
        .batch_spawn_agents(10, Foxes_male, images=["images/fox head.png"])
        .batch_spawn_agents(10, Foxes_female, images=["images/fox head.png"])
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
