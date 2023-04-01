"""CSC111 Project: To the Stars!

This file contains the code used to read the dataset that we got via Kaggle,
which contains information on a specific star in our galaxy.

TODO: Reference where we got the data set
"""
import csv
from classes import *


def read_dataset(data: str) -> tuple[Galaxy, list]:
    """Read the dataset csv file and create/return a galaxy made of the stars in the data
    set. Also, create a list of the individual stars to show in pygame.
    """
    with open(data) as csv_file:
        reader = csv.reader(csv_file)

        # skip the header row
        next(reader)

        # create a new galaxy, and add the stars to it
        new_galaxy = Galaxy()

        for row in reader:
            name = row[2]
            distance = float(row[3])
            mass = float(row[4])
            radius = float(row[5])
            new_galaxy.add_star(name, distance, mass, radius)

        stars_so_far = []
        for star in new_galaxy._stars:
            stars_so_far.append(new_galaxy._stars[star])

    return new_galaxy, stars_so_far
