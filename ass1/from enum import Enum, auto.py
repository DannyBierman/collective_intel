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

            radius=100,
            seed=1,
            fps_limit=30
        )
    )
    .batch_spawn_agents(50, Cockroach, images=["images/bird.png"])
    .spawn_site("images/red2.png", x=375, y=375)
    .run()
    .snapshots

)
print(data_frame)
