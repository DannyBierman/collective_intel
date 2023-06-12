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
    alignment_weight: float = 1
    cohesion_weight: float = 0.2
    separation_weight: float = 0.2

    delta_time: float = 3

    mass: int = 20

    max_velocity: float = 5

    def weights(self) -> tuple[float, float, float]:
        return (self.alignment_weight, self.cohesion_weight, self.separation_weight)


class Bird(Agent):
    config: FlockingConfig
    
    def alignment(self, neighbors):
        total_vel = Vector2()
        neighbor_count = 0
        for bird, distance in neighbors:
            total_vel += bird.move
            neighbor_count += 1
        if neighbor_count > 0:
            avg_vel = total_vel / neighbor_count
            return avg_vel - self.move
        else:
            return Vector2()
        
    
    def separation(self, neighbors):
        total_force = Vector2()
        for bird, distance in neighbors:
            total_force += self.pos - bird.pos
        return total_force / len(neighbors)
    
        
    def cohesion(self, neighbors):
        bird_positions = [bird.pos for bird, distance in neighbors]
        position_sum = sum(bird_positions, Vector2())

        if len(neighbors) > 0:
            average_pos = position_sum / len(neighbors)
            force_c = average_pos - self.pos
            return force_c - self.move
        else:
            return Vector2()
        
    

    

    #get weights methods
    def get_alignment_weight(self)->float:
        return self.config.alignment_weight

    def get_cohesion_weight(self)->float:
        return self.config.cohesion_weight

    def get_separation_weight(self)->float:
        return self.config.separation_weight

    def change_position(self):
        # Pac-man-style teleport to the other end of the screen when trying to escape
        self.there_is_no_escape()

        # Check neighbors in radius R
        neighbors = list(self.in_proximity_accuracy())

        if len(neighbors) == 0:
            # No neighbors, perform wandering
            self.wandering()
        else:
            # Calculate alignment, separation, and cohesion forces
            alignment_force = self.alignment(neighbors)
            separation_force = self.separation(neighbors)
            cohesion_force = self.cohesion(neighbors)

            # Calculate total force
            f_total = (
                              self.config.alignment_weight * alignment_force +
                              self.config.separation_weight * separation_force +
                              self.config.cohesion_weight * cohesion_force
                      ) / self.config.mass

            # Update the move vector
            self.move += f_total

            # Limit the maximum velocity
            if self.move.length() > self.config.max_velocity:
                self.move.scale_to_length(self.config.max_velocity)

            # Update the position
            self.pos += self.move * self.config.delta_time

    def wandering(self):
        # Perform wandering behavior
        # Your wandering logic goes here
        pass

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

        # Ensure the weights stay within the range of 0.0 to 1.0
        self.config.alignment_weight = max(0.0, min(1.0, self.config.alignment_weight))
        self.config.cohesion_weight = max(0.0, min(1.0, self.config.cohesion_weight))
        self.config.separation_weight = max(0.0, min(1.0, self.config.separation_weight))

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
            radius=50,
            duration= 5*60,
            seed=1,
            fps_limit=33
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
