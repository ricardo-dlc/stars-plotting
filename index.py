import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from skyfield.api import Topos, load, Star
from skyfield.data import hipparcos

# Load necessary data
planets = load('de421.bsp')
earth = planets['earth']
ts = load.timescale()

with load.open(hipparcos.URL) as f:
    stars = hipparcos.load_dataframe(f)


# Define a simplified version of constellation lines
# (Using Hipparcos star IDs and a few example lines)
constellation_lines = [
    # Example for a simplified constellation
    (677, 1021), (677, 3092), (1021, 3092),
    # Example for another simplified constellation
    (21421, 21683), (21421, 22061), (21683, 22061)
]

# Specify the location and time
# San Francisco coordinates
location = earth + Topos('37.7749 N', '122.4194 W')
time = ts.utc(2024, 5, 14, 22, 0, 0)  # Example date and time

# Function to plot the sky


def plot_stars():
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.set_facecolor('black')
    ax.set_aspect('equal')

    # Filter stars based on apparent magnitude (selecting stars with magnitude < 5)
    visible_stars = stars[stars['magnitude'] < 5]

    for star in visible_stars.itertuples():
        # Create a Star object using the RA and DEC
        star_obj = Star(ra_hours=star.ra_hours, dec_degrees=star.dec_degrees)
        astrometric = location.at(time).observe(star_obj)
        alt, az, distance = astrometric.apparent().altaz()

        # Convert alt/az to plot coordinates
        if alt.degrees > 0:  # Only plot stars above the horizon
            x = np.sin(np.deg2rad(az.degrees)) * \
                np.cos(np.deg2rad(alt.degrees))
            y = np.cos(np.deg2rad(az.degrees)) * \
                np.cos(np.deg2rad(alt.degrees))
            ax.scatter(x, y, color='white', s=1)
            if 'proper_name' in stars.columns and isinstance(star.proper_name, str) and star.proper_name.strip():
                ax.text(x, y, f"{star.proper_name}", color='white', fontsize=6)

    # Draw the horizon circle
    circle = plt.Circle((0, 0), 1, edgecolor='white', facecolor='none', lw=0.5)
    ax.add_patch(circle)

    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_xlim(-1.5, 1.5)
    ax.set_ylim(-1.5, 1.5)

    plt.savefig('stars_only.svg', format='svg')
    plt.show()


plot_stars()
