import numpy as np
import pytest

from collider import Simulation, oxygen, nitrogen, nitric_oxide


def test_scenario_creation():
    width = 500
    height = 500
    num_spheres = 10
    temperature = 100

    # Mock canvas function
    class MockCanvas:
        def __init__(self, width, height):
            self.width = width
            self.height = height

    # Initialize Simulation
    sim = Simulation(MockCanvas, width, height, num_spheres, temperature)

    # Create spheres
    spheres = sim.create_spheres(num_spheres)

    # Check the number of spheres created
    assert len(spheres) == num_spheres

    # Check attributes of each sphere
    for sphere in spheres:
        assert 20 <= sphere.x <= width - 20
        assert 20 <= sphere.y <= height - 20

        assert sphere.radius > 0
        assert sphere.atom in [oxygen, nitrogen]



def test_simulation():
    width = 500
    height = 500
    num_spheres = 20
    temperature = 1000
    np.random.seed(0)

    # Mock canvas function
    class MockCanvas:
        def __init__(self, width, height):
            self.width = width
            self.height = height

    # Initialize Simulation
    sim = Simulation(MockCanvas, width, height, num_spheres, temperature)

    # Check the number of spheres created
    assert len(sim.spheres) == num_spheres

    # Check the number of walls created
    assert len(sim.walls) == 8

    # run simulation steps    
    for _ in range(1000):
        sim.update()

    # at least one reaction should have occurred
    assert any([sphere.atom == nitric_oxide for sphere in sim.spheres])
