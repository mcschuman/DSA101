[![pipeline status](https://gitlab.uzh.ch/meredithchristine.schuman/dsa-101-simulation/badges/main/pipeline.svg)](https://gitlab.uzh.ch/meredithchristine.schuman/dsa-101-simulation/-/commits/main)

# DSA 101 simulation
This is a simulation exercise for the course DSA 101: Introduction to Data Analytics and Python. The purpose of this exercise is to practice a collaborative workflow using git.

Module coordinator and main instructor: Prof. Alexandria Deliz Liang

Co-instructor: Prof. Meredith C. Schuman

## Description
The purpose of this exercise is to practice a collaborative workflow using git. Each team member will need to clone, edit, add, commit, and push (and you may check the status).

The simulation is a toy model of atoms from two different elements reacting in the gas phase. It is loosely motivated by the reaction of nitrogen and oxygen to nitrous oxide. It can be improved.

The repository contains the following files:
- README.md: this file
- collider.py: a Python file that simulates particle collisions
- Simulation_interface.ipynb: a Python notebook to run the simulation
- requirements.txt: a requirement file
- test_collider.py: test suite using pytest

To run the initial toy model:
1. Create a Python environment from the environment file.
2. Run the Python notebook (this will call the Python file).

## Assignment
This is an assignment for groups of ca.three persons.

First get set up:
1. Make one private fork of this repository for the entire group.
2. The group member that makes the fork invites all other group members to the fork as owners (all group members must have equal rights).
3. Invite the instructor to the fork as a viewer.
4. All group members should then clone the fork onto their computer using their access tokens. (You will need to create an access token for your computer if you don't already have one.)
5. Each group member should first get the toy model to run before making any changes.

In small groups, assign one task to each person:
1. Add live charts that update as the simulation runs and show the current values of the following parameters: temperature, number of collisions, number of reactions, amounts of "product"
2. Add different versions of the toy model's "reaction vessel": a wall in the middle, walls with holes.
3. Change the simulation such that the reaction products can disassociate again.

## Authors and acknowledgment
Authors of this repository: Prof. Meredith C. Schuman and Dr. Alexander Steppke

Thanks to Dr. Domitille Coq--Etchegaray for help setting up the repository.

## License
CC-BY-NC-SA