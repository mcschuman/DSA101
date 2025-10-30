import numpy as np
import time
from dataclasses import dataclass

from ipycanvas import Canvas, hold_canvas


@dataclass
class Color:
    fill: str
    outline: str


@dataclass
class Molecule:
    name: str
    reaction_partner: str
    activation_energy: float
    color: Color
    radius: int
    mass: float = None


oxygen = Molecule(
    "oxygen", "nitrogen", activation_energy=200, color=Color(fill="#fdd835", outline="#ff8f00"), radius=16
)
nitrogen = Molecule(
    "nitrogen", "oxygen", activation_energy=200, color=Color(fill="#1e88e5", outline="#0d47a1"), radius=14
)
nitric_oxide = Molecule(
    "NO", None, activation_energy=0, color=Color(fill="#1abc9c", outline="#148f77"), radius=22
)


class Sphere:
    """A class to represent a sphere in a 2D space."""

    def __init__(self, x, y, vx, vy, radius, color: Color, mass=None, gravity=0.001):
        """Initialize the sphere with position, velocity, radius, color, mass, and gravity."""
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.radius = radius
        self.color = color
        self.mass = radius**2 if mass is None else mass
        self.gravity = gravity

    def move(self):
        self.vy += self.gravity  # Apply gravity to vertical velocity
        self.x += self.vx
        self.y += self.vy

    def check_wall_collision(self, width, height):
        if self.x - self.radius < 0 or self.x + self.radius > width:
            self.vx = -self.vx
        if self.y - self.radius < 0 or self.y + self.radius > height:
            self.vy = -self.vy

    def check_sphere_collision(self, other):
        dx = self.x - other.x
        dy = self.y - other.y
        distance = np.sqrt(dx**2 + dy**2)
        if distance < self.radius + other.radius:
            # Calculate new velocities based on conservation of momentum and kinetic energy
            nx = dx / distance
            ny = dy / distance
            p = 2 * (self.vx * nx + self.vy * ny - other.vx * nx - other.vy * ny) / (self.mass + other.mass)
            self.vx -= p * other.mass * nx
            self.vy -= p * other.mass * ny
            other.vx += p * self.mass * nx
            other.vy += p * self.mass * ny

            # Separate the spheres to prevent overlap
            overlap = 0.5 * (self.radius + other.radius - distance + 1)
            self.x += overlap * nx
            self.y += overlap * ny
            other.x -= overlap * nx
            other.y -= overlap * ny

    def equilibriate_temperature(self, temperature):
        # on average kb*T energy per degree of freedom
        kb = 1
        v_equilibrium = np.sqrt(2 * kb * temperature / self.mass)
        alpha = 0.01
        direction = np.arctan2(self.vy, self.vx)
        self.vx = alpha * v_equilibrium * np.cos(direction) + self.vx * (1 - alpha)
        self.vy = alpha * v_equilibrium * np.sin(direction) + self.vy * (1 - alpha)


class ChemicalSphere(Sphere):
    """Extends sphere, so that it can react with other spheres."""

    def __init__(self, x, y, vx, vy, atom: Molecule, gravity=0.001):
        self.atom = atom
        super().__init__(x, y, vx, vy, atom.radius, atom.color, atom.mass, gravity)

    def check_sphere_collision(self, other):
        if (
            not isinstance(other, ChemicalSphere)
            or self.atom == other.atom
            or not self.atom.reaction_partner == other.atom.name
        ):
            super().check_sphere_collision(other)
            return

        # Pacman version:
        # if not isinstance(other, ChemicalSphere) or \
        #    self.atom == other.atom:
        #     super().check_sphere_collision(other)
        #     return

        # calculate total kinetic energy
        self_kinetic_energy = 0.5 * self.mass * (self.vx**2 + self.vy**2)
        other_kinetic_energy = 0.5 * other.mass * (other.vx**2 + other.vy**2)
        total_kinetic_energy = self_kinetic_energy + other_kinetic_energy

        if total_kinetic_energy < self.atom.activation_energy:
            super().check_sphere_collision(other)
            return

        # determine if the spheres collide and react
        dx = self.x - other.x
        dy = self.y - other.y
        distance = np.sqrt(dx**2 + dy**2)
        if distance < self.radius + other.radius:

            self.atom = nitric_oxide
            self.x = (self.x + other.x) / 2
            self.y = (self.y + other.y) / 2
            self.vx = self.vx / 2
            self.vy = self.vy / 2
            self.radius = self.atom.radius
            self.color = self.atom.color
            self.mass = self.radius**2 if self.atom.mass is None else self.atom.mass

            other.x = -1000
            other.y = -1000


class Wall:
    """A class to represent a wall on our canvas."""

    def __init__(self, x1, y1, x2, y2):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2

    def check_collision(self, sphere):
        # TODO: The logic is a bit convoluted.
        # We only reverse directions if a collision occured and not
        # if we are already moving away from the wall and got "shoved" into
        # by another sphere collision and then reverse course into the wall.

        # Check for vertical walls
        if self.x1 == self.x2:
            if self.x1 - sphere.radius < sphere.x < self.x1 + sphere.radius:
                if self.y1 < sphere.y < self.y2 or self.y2 < sphere.y < self.y1:
                    if (sphere.x < self.x1) and sphere.vx > 0:
                        sphere.vx = -sphere.vx
                    elif (sphere.x > self.x1) and sphere.vx < 0:
                        sphere.vx = -sphere.vx

        # Check for horizontal walls
        elif self.y1 == self.y2:
            if self.y1 - sphere.radius < sphere.y < self.y1 + sphere.radius:
                if self.x1 < sphere.x < self.x2 or self.x2 < sphere.x < self.x1:
                    if (sphere.y < self.y1) and sphere.vy > 0:
                        sphere.vy = -sphere.vy
                    elif (sphere.y > self.y1) and sphere.vy < 0:
                        sphere.vy = -sphere.vy


class Simulation:
    """The main simulation class that contains the canvas, spheres, and walls."""

    def __init__(self, canvas, width, height, num_spheres, temperature=100):
        self.width = width
        self.height = height
        self.temperature = temperature
        self.canvas = canvas(width=width, height=height)
        self.spheres = self.create_spheres(num_spheres)
        self.walls = self.create_side_walls()

    def create_spheres(self, num_spheres):
        spheres = []
        for _ in range(num_spheres):
            x = np.random.randint(20, self.width - 20)
            y = np.random.randint(20, self.height - 20)
            vx = np.sqrt(self.temperature) / 20 * np.random.uniform(-0.5, 0.5)
            vy = np.sqrt(self.temperature) / 20 * np.random.uniform(-0.5, 0.5)
            radius = np.random.randint(15, 20)
            atom = np.random.choice([oxygen, nitrogen])
            spheres.append(ChemicalSphere(x, y, vx, vy, atom))
        return spheres

    def create_side_walls(self):
        walls = [
            Wall(0, 0, self.width, 0),  # Top wall
            Wall(0, self.height, self.width, self.height),  # Bottom wall
            Wall(0, 0, 0, self.height),  # Left wall
            Wall(self.width, 0, self.width, self.height),  # Right wall
        ]
        return walls

    def update(self):
        for sphere in self.spheres:
            sphere.move()
            for wall in self.walls:
                wall.check_collision(sphere)
            for other in self.spheres:
                if sphere != other:
                    sphere.check_sphere_collision(other)

            sphere.equilibriate_temperature(self.temperature)

        # remove spheres that are out of bounds (inplace, https://stackoverflow.com/questions/1207406)
        self.spheres[:] = [
            sp for sp in self.spheres if not (abs(sp.x) > self.width * 2 or abs(sp.y) > self.height * 2)
        ]

    def draw(self):
        with hold_canvas():
            self.canvas.clear()
            for sphere in self.spheres:
                self.canvas.fill_style = sphere.color.fill
                self.canvas.fill_circle(sphere.x, sphere.y, sphere.radius)
                self.canvas.stroke_style = sphere.color.outline
                self.canvas.stroke_circle(sphere.x, sphere.y, sphere.radius)

            self.canvas.stroke_style = "black"
            self.canvas.line_width = 2
            for wall in self.walls:
                self.canvas.stroke_line(wall.x1, wall.y1, wall.x2, wall.y2)

    def run(self):
        while True:
            self.update()
            self.draw()
            time.sleep(0.002)
