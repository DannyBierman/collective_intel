from enum import Enum, auto
from turtle import pos
from vi import Agent, Simulation
import pygame as pg
from pygame.math import Vector2
from vi import Agent, Simulation
from vi.config import Config, dataclass, deserialize
import random
import numpy as np

@deserialize
@dataclass

class CockroachConfig(Config):

 time: int = np.random.randint(0,1,1)
 probability_threshold : float = 0.5



class Cockroach(Agent):
 config:CockroachConfig
    
 def wandering(self):
    self.pos += Vector2(np.random.randint(10,2))
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
        
    if probability > CockroachConfig.probability_threshold:
            return True
        
    elif probability == CockroachConfig.probability_threshold: 
        probability = np.random.randint(0, 1)
        if probability == 1:
            return True 
        else :
            return False
    
    elif probability < CockroachConfig.probability_threshold:
            return False
          
    
 def probability_leave(self, Neighbours):
    
    neighbour_count = 0
    for bird, distance in Neighbours:
        neighbour_count +=1

    probability = 0
    if neighbour_count > 5:
        probability = 1
    else :
        probability = neighbour_count / 5

    if probability < CockroachConfig.probability_threshold:
        return True

    elif probability == CockroachConfig.probability_threshold: 
        probability = np.random.randint(0, 1)
        if probability == 1:
            return True 
        else :
            return False

    elif probability > CockroachConfig.probability_threshold:
        return False
      		

 def joining(self, Neighbours):
    neighbours = list(self.in_proximity_accuracy())
    bird_positions = [bird.pos for bird, distance in neighbours]
    position_sum = sum(bird_positions, Vector2())
    if self.probability_joint(neighbours):
        average_pos = position_sum / len(neighbours)
        force_c = average_pos - self.pos
        print("joining")
        return force_c - self.move  
    else:
        return Vector2()

    
 def leaving(self, Neighbours):
    neighbours = list(self.in_proximity_accuracy())
    bird_positions = [bird.pos for bird, distance in neighbours]
    position_sum = sum(bird_positions, Vector2())
    if random.random() < self.probability_leave(neighbours):
        average_pos = position_sum / len(neighbours)
        force_c = self.pos - average_pos
        print("leaving")
        return force_c - self.move
    else:
        #stay
        return Vector2()
            
 def still(self):
     if self.on_site():
        self.freeze_movement()
        print("still")
        
 def update(self):
    if self.wandering :
        self.continue_movement()
    elif self.wandering and self.probability_join:
        self.joining

    


data_frame = (
    Simulation(
        CockroachConfig(
            image_rotation=True,
            movement_speed=1,

            radius=100,
            seed=1,
            fps_limit=30
        )
    )
    .batch_spawn_agents(50, Cockroach, images=["images/bird.png"])
    .spawn_site("images/red_big.png", x=375, y=375)
    .run()
    .snapshots

)
print(data_frame)
