from enum import Enum, auto
from turtle import pos
from vi import Agent, Simulation
import pygame as pg
from pygame.math import Vector2
from vi import Agent, Simulation
from vi.config import Config, dataclass, deserialize
import random
import numpy as np






class Cockroach(Agent):
 counter = 0
 probability_threshold : float = 0.5
 state = "wandering"
 def wandering(self):
    self.continue_movement()
    #if prob joining is true: join
    self.state = "joining"
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
        
    if probability > self.probability_threshold:
            return True
        
    elif probability == self.probability_threshold:
        probability = np.random.randint(0, 1)
        if probability == 1:
            return True 
        else :
            return False
    
    elif probability < self.probability_threshold:
            return False

 def joining(self, Neighbours):
    neighbours = list(self.in_proximity_accuracy())
    bird_positions = [bird.pos for bird, distance in neighbours]
    position_sum = sum(bird_positions, Vector2())
    if self.probability_join(neighbours):
        average_pos = position_sum / len(neighbours)
        force_c = average_pos - self.pos
        self.state = "still"
        return force_c - self.move
    else:
        return Vector2()
 # def probability_leave(self, Neighbours):
 #
 #    neighbour_count = 0
 #    for bird, distance in Neighbours:
 #        neighbour_count +=1
 #
 #    probability = 0
 #    if neighbour_count > 5:
 #        probability = 1
 #    else :
 #        probability = neighbour_count / 5
 #
 #    if probability < CockroachConfig.probability_threshold:
 #        return True
 #
 #    elif probability == CockroachConfig.probability_threshold:
 #        probability = np.random.randint(0, 1)
 #        if probability == 1:
 #            return True
 #        else :
 #            return False
 #
 #    elif probability > CockroachConfig.probability_threshold:
 #        return False
 #



    
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
            
 def still(self):
    if self.counter == 80:
        self.freeze_movement()

 # def update(self):
 #    if self.on_site():
 #        self.counter += 1
 #        self.still()
 #    elif self.wandering :
 #        self.continue_movement()
 #    elif self.wandering and self.probability_join:
 #        self.joining
 def update(self):
    if self.state == "wandering":

        self.wandering()
    elif self.state == "joining":
        self.joining(self.in_proximity_accuracy())
    elif self.state == "still":
        self.counter += 1
        self.still
    elif self.state == "leaving":
        self.leave(self.in_proximity_accuracy())



    


data_frame = (
    Simulation(
        Config(
            image_rotation=True,
            movement_speed=1,

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
