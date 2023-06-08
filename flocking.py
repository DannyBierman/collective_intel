from enum import Enum, auto

import pygame as pg
from pygame.math import Vector2
from vi import Agent, Simulation
from vi.config import Config, dataclass, deserialize


@deserialize
@dataclass
class FlockingConfig(Config):
    alignment_weight: float = 0.5
    cohesion_weight: float = 0.5
    separation_weight: float = 0.5

    delta_time: float = 3

    mass: int = 20

    def weights(self) -> tuple[float, float, float]:
        return (self.alignment_weight, self.cohesion_weight, self.separation_weight)


class Bird(Agent):
    config: FlockingConfig
    
    def alignment(self, Neighbours):
        total_vel = Vector2()
        for bird, distance in Neighbours:
            total_vel += bird.move.normalize()/ distance
            
        return total_vel
    
    def seperation(self, Neighbours):

        bird_positions = []
        for bird,_ in Neighbours:
            bird_positions.append(bird.pos)
        position_sum = sum(bird_positions,Vector2())
        average_position = position_sum / self.in_proximity_accuracy().count()
        return average_position * (self.pos - bird.pos)
    
        
    def cohesion(self, Neighbours):
        bird_positions = []
        for bird,_ in Neighbours:
            bird_positions.append(bird.pos)
        position_sum = sum(bird_positions,Vector2())

        if self.in_proximity_accuracy().count() > 0:
            average = position_sum / self.in_proximity_accuracy().count()
            return average - self.pos
        else:
            return Vector2()
        
    

    

    def change_position(self):
        # Pac-man-style teleport to the other end of the screen when trying to escape
        self.there_is_no_escape()
        #YOUR CODE HERE -----------
        if self.in_proximity_accuracy().count() == 0:
            self.pos += self.move
        else:
            self.alignment(self.in_proximity_accuracy())
            self.cohesion(self.in_proximity_accuracy())
            self.seperation(self.in_proximity_accuracy())
            self.pos += self.move
        #END CODE -----------------


class Selection(Enum):
    ALIGNMENT = auto()
    COHESION = auto()
    SEPARATION = auto()


class FlockingLive(Simulation):
    selection: Selection = Selection.ALIGNMENT
    config: FlockingConfig

    def handle_event(self, by: float):
        if self.selection == Selection.ALIGNMENT:
            self.config.alignment_weight += by
        elif self.selection == Selection.COHESION:
            self.config.cohesion_weight += by
        elif self.selection == Selection.SEPARATION:
            self.config.separation_weight += by

    def before_update(self):
        super().before_update()

        for event in pg.event.get():
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_UP:
                    self.handle_event(by=0.1)
                elif event.key == pg.K_DOWN:
                    self.handle_event(by=-0.1)
                elif event.key == pg.K_1:
                    self.selection = Selection.ALIGNMENT
                elif event.key == pg.K_2:
                    self.selection = Selection.COHESION
                elif event.key == pg.K_3:
                    self.selection = Selection.SEPARATION

        a, c, s = self.config.weights()
        print(f"A: {a:.1f} - C: {c:.1f} - S: {s:.1f}")


(
    FlockingLive(
        FlockingConfig(
            image_rotation=True,
            movement_speed=1,
            radius=50,
            seed=1,
        )
    )
    .batch_spawn_agents(50, Bird, images=["images/bird.png"])
    .run()
)
