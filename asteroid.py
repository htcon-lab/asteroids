import pygame
import random
import math
from circleshape import CircleShape
from constants import LINE_WIDTH, ASTEROID_MIN_RADIUS
from logger import log_event

class Asteroid(CircleShape):
    def __init__(self, x: float, y: float, radius: float) -> None:
        super().__init__(x, y, radius)

    def draw(self, screen: pygame.Surface) -> None:
        pygame.draw.circle(screen, "white", self.position, self.radius, LINE_WIDTH)

    def update(self, dt: float) -> None:
        self.position += self.velocity * dt

    def split(self) -> None:
        self.kill()
        if self.radius <= ASTEROID_MIN_RADIUS:
            return

        log_event("asteroid_split")

        random_angle = random.uniform(20, 50)

        new_velocity_vector_1 = self.velocity.rotate(random_angle)
        new_velocity_vector_2 =self.velocity.rotate(-random_angle)
        new_radius = self.radius - ASTEROID_MIN_RADIUS

        offset_1 = new_velocity_vector_1.normalize() * new_radius / math.sin(math.radians(random_angle))
        offset_2 = new_velocity_vector_2.normalize() * new_radius / math.sin(math.radians(random_angle))

        spawn_position_1 = self.position + offset_1
        spawn_position_2 = self.position + offset_2

        new_asteroid_1 = Asteroid(spawn_position_1.x, spawn_position_1.y, new_radius)
        new_asteroid_2 = Asteroid(spawn_position_2.x, spawn_position_2.y, new_radius)

        new_asteroid_1.velocity = new_velocity_vector_1 * 1.2
        new_asteroid_2.velocity = new_velocity_vector_2 * 1.2

    def collision(self, other):
        mass_self = self.radius ** 2
        mass_other = other.radius ** 2

        normal = other.position - self.position
        normal = normal.normalize()

        self_along_normal = self.velocity.dot(normal)
        other_along_normal = other.velocity.dot(normal)

        new_self_normal = (
            (mass_self - mass_other) * self_along_normal
            + 2 * mass_other * other_along_normal
        ) / (mass_self + mass_other)

        new_other_normal = (
            (mass_other - mass_self) * other_along_normal
            + 2 * mass_self * self_along_normal
        ) / (mass_self + mass_other)

        self_normal_velocity = normal * self_along_normal
        other_normal_velocity = normal * other_along_normal

        self_tangent_velocity = self.velocity - self_normal_velocity
        other_tangent_velocity = other.velocity - other_normal_velocity

        self.velocity = self_tangent_velocity + normal * new_self_normal
        other.velocity = other_tangent_velocity + normal * new_other_normal

    def merge_with(self, other):
        mass_self = self.radius ** 2
        mass_other = other.radius ** 2
        total_mass = mass_self + mass_other

        # Center of mass: gives the merged asteroid a sensible position.
        merged_position = (
            self.position * mass_self + other.position * mass_other
        ) / total_mass

        # Momentum conservation: large asteroids influence motion more.
        merged_velocity = (
            self.velocity * mass_self + other.velocity * mass_other
        ) / total_mass

        merged_radius = math.sqrt(total_mass)

        self.kill()
        other.kill()

        merged = Asteroid(
            merged_position.x,
            merged_position.y,
            merged_radius,
        )
        merged.velocity = merged_velocity
        return merged
