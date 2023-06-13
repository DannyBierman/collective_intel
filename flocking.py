from enum import Enum, auto
import polars as pl
import seaborn as sns
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
        total_vel = Vector2.length(self.move)
        neighbour_count = 0
        for bird, distance in Neighbours:
            total_vel += Vector2.length(self.move)
            neighbour_count +=1
        avg_vel = total_vel/ neighbour_count
        return avg_vel - self.move.length()
        
    
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
            average_pos = position_sum / self.in_proximity_accuracy().count()
            force_c = average_pos - self.pos
            return force_c - self.move
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
            f_total = (self.alignment(self.in_proximity_accuracy()) + 
                       self.cohesion(self.in_proximity_accuracy()) + 
                       self.seperation(self.in_proximity_accuracy()))/FlockingConfig.mass
            self.pos += self.move + f_total
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


data_frame = (
    FlockingLive(
        FlockingConfig(
            image_rotation=True,
            movement_speed=1,
<<<<<<< Updated upstream
            radius=50,
            duration= 5*60,
            seed=1,
            fps_limit= 0
        )
    )
    .batch_spawn_agents(50, Bird, images=["images/bird.png"])
    .run()
    .snapshots
    .groupby(["frame", "image_index"])
    .agg(pl.count("id").alias("agents"))
    .sort(["frame", "image_index"])
    
)
print(data_frame)
plot = sns.relplot(x = data_frame["frame"], y = data_frame["agents"], hue= data_frame["image_index"],kind = "line" )
plot.savefig("agent.png", dpi = 300)
=======
            radius=100,
            duration= 5*60,
            seed=1,
            fps_limit=30
)
)
.batch_spawn_agents(50, Bird, images=["images/bird.png"])
     .run()
     .snapshots
     .groupby(["frame", "image_index"])
     .agg(pl.count("id").alias("agents"))
     .sort(["frame", "image_index"])

)
print(data_frame)
plot = sns.relplot(x=data_frame["frame"], y=data_frame["agents"], hue=data_frame["image_index"], kind="line")
plot.savefig("agent.png", dpi=300)

>>>>>>> Stashed changes
