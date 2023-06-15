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






class Cockroach(Agent):
 counter = 0
 probability_threshold : float = 0.5
 state = "wandering"
 def wandering(self):
    self.continue_movement()
    if self.probability_join():
        self.state = "joining"



 def joining(self, neighbours):
    neighbours = list(self.in_proximity_accuracy())

    if len(neighbours):
        self.state = "still"

 def probability_join(self) -> bool:
     return probability(1.15 ** (self.in_proximity_accuracy().count() + 1) - 1.15)

 def probability_leave(self, Neighbours):
     return probability(0.1 / (1 + math.exp(0.5 * self.in_proximity_accuracy().count())))

    
 def leaving(self, Neighbours):
    neighbours = list(self.in_proximity_accuracy())

    if self.counter % 110 == 0:

        self.continue_movement()
        self.state = "wandering"

 def still(self):
    if self.counter % 40 == 0 and self.on_site():
        self.freeze_movement()
    if self.probability_leave(self.in_proximity_accuracy):
        self.state = "leaving"

 def update(self):
    if self.state == "wandering":
        print("state wandering")
        self.wandering()
    elif self.state == "joining":
        print("state joining")

        self.joining(self.in_proximity_accuracy())

    elif self.state == "still":
        print("state still")

        self.counter += 1
        self.still()
    elif self.state == "leaving":
        print("state leaving")
        self.counter += 1

        self.leaving(self.in_proximity_accuracy())

data_frame = (
    Simulation(
        Config(
            image_rotation=True,
            movement_speed=10,
            duration= 1*60,
            radius=100,
            seed=1,
            fps_limit=30
        )
    )
    .batch_spawn_agents(50, Cockroach, images=["images/cockroach.png"])
    #.spawn_site("images/red2.png", x=375, y=375)
    .spawn_site("images/red2.png", x=175, y=375)
    .spawn_site("images/red2_copy.png", x=575, y=375)
    .run()
    .snapshots
)
# Stop the simulation after a certain number of iterations???
#max_iterations=1000
#vi function: Simulation.stop()

print(data_frame)
import seaborn as sns
import matplotlib.pyplot as plt

# Calculate the number of agents in each aggregation site
grouped_data = (
    data_frame
    .groupby(["frame", "image_index"])
    .size()
    .reset_index(name="agents")
)

# Plot the data
sns.relplot(x="frame", y="agents", hue="image_index", kind="line", data=grouped_data)
plt.title("Number of Agents in Each Aggregation Site Over Time")
plt.xlabel("Frame")
plt.ylabel("Number of Agents")
plt.show()
plot.savefig("agents.png", dpi = 300)