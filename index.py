import numpy as np
import matplotlib.pyplot as plt
import requests
import matplotlib.patches as patches
from skyfield.api import Topos, load, Star, load_constellation_names
from skyfield.data import hipparcos
from skyfield.named_stars import named_star_dict

# Load necessary data
planets = load('de421.bsp')
earth = planets['earth']
ts = load.timescale()
constellation_names = dict(load_constellation_names())

with load.open(hipparcos.URL) as f:
    stars = hipparcos.load_dataframe(f)


# Download and parse the constellation lines data
constellation_lines_url = 'https://raw.githubusercontent.com/Stellarium/stellarium/master/skycultures/modern/constellationship.fab'
response = requests.get(constellation_lines_url)
lines = response.text.strip().split('\n')


constellations = {}
for line in lines:
    parts = line.split()
    constellation_name = parts[0]
    num_pairs = int(parts[1])
    star_ids = [int(star_id) for star_id in parts[2:]]
    pairs = [(star_ids[i], star_ids[i + 1])
             for i in range(0, len(star_ids), 2)]
    constellations[constellation_name] = pairs


# Convert magnitudes to relative brightness
stars['brightness'] = 10 ** (-0.4 * stars['magnitude'])
# Normalize the brightness values
sum_brightness = stars['brightness'].sum()
stars['normalized_brightness'] = stars['brightness'] / sum_brightness


# Function to scale size based on normalized brightness
def brightness_to_size(normalized_brightness):
    # Log scale for better differentiation
    return 10 + 800 * np.log1p(normalized_brightness * 100)


# Specify the location and time
location = earth + Topos('21.1619 N', '86.8515 W')
time = ts.utc(2023, 3, 29, 9, 42, 0)  # Example date and time


# Create a reverse lookup dictionary from Hipparcos ID to star names
hip_to_name = {v: k for k, v in named_star_dict.items()}


# Function to plot the sky
def plot_stars():
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.set_facecolor('navy')
    ax.set_aspect('equal')

    labeled_positions = []
    # Dictionary to store midpoint for constellation labeling
    constellation_midpoints = {}

    # Filter stars based on apparent magnitude (selecting stars with magnitude < 5)
    visible_stars = stars[stars['magnitude'] <= 5]

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

            # Determine size of the star based on normalized brightness
            size = brightness_to_size(star.normalized_brightness)

            # print(marker_size.loc[star.Index])
            ax.scatter(x, y, color='white', s=size, marker='.', linewidths=0,
                       zorder=2)

            # # Check if the star has a common name
            # if star.Index in hip_to_name:
            #     star_name = hip_to_name[star.Index]
            #     # print(f"Labeling star: {star_name} at ({x:.2f}, {y:.2f})")

            #     # Adjust label position to avoid overlap
            #     label_x, label_y = x, y + 0.02
            #     too_close = False
            #     for lx, ly in labeled_positions:
            #         if np.hypot(lx - label_x, ly - label_y) < 0.1:
            #             too_close = True
            #             break

            #     if not too_close:
            #         labeled_positions.append((label_x, label_y))
            #         ax.text(label_x, label_y, f"{
            #                 star_name}", color='white', fontsize=6)

    # Plot constellation lines and calculate midpoints for labeling
    for constellation_name, star_pairs in constellations.items():
        for i, (star1, star2) in enumerate(star_pairs):
            if star1 in stars.index and star2 in stars.index:
                star1_data = stars.loc[star1]
                star2_data = stars.loc[star2]

                star1_obj = Star(ra_hours=star1_data.ra_hours,
                                 dec_degrees=star1_data.dec_degrees)
                star2_obj = Star(ra_hours=star2_data.ra_hours,
                                 dec_degrees=star2_data.dec_degrees)

                astrometric1 = location.at(time).observe(star1_obj)
                astrometric2 = location.at(time).observe(star2_obj)

                alt1, az1, distance1 = astrometric1.apparent().altaz()
                alt2, az2, distance2 = astrometric2.apparent().altaz()

                if alt1.degrees > 0 and alt2.degrees > 0:
                    x1 = np.sin(np.deg2rad(az1.degrees)) * \
                        np.cos(np.deg2rad(alt1.degrees))
                    y1 = np.cos(np.deg2rad(az1.degrees)) * \
                        np.cos(np.deg2rad(alt1.degrees))
                    x2 = np.sin(np.deg2rad(az2.degrees)) * \
                        np.cos(np.deg2rad(alt2.degrees))
                    y2 = np.cos(np.deg2rad(az2.degrees)) * \
                        np.cos(np.deg2rad(alt2.degrees))
                    ax.plot([x1, x2], [y1, y2], color='white', lw=0.5)

                    # Calculate the midpoint for labeling the constellation name
                    if i == 0:  # Use the first star pair to place the label
                        label_x = (x1 + x2) / 2
                        label_y = (y1 + y2) / 2
                        constellation_midpoints[constellation_name] = (
                            label_x, label_y)

    # Label constellations
    for constellation_name, (label_x, label_y) in constellation_midpoints.items():
        too_close = False
        for lx, ly in labeled_positions:
            if np.hypot(lx - label_x, ly - label_y) < 0.1:
                too_close = True
                break

        if not too_close:
            labeled_positions.append((label_x, label_y))
            ax.text(label_x, label_y, f"{
                    constellation_names[constellation_name]}", color='white', fontsize=8, ha='center')

    # Draw the horizon circle
    circle = plt.Circle((0, 0), 1, edgecolor='white', facecolor='none', lw=0.5)
    ax.add_patch(circle)

    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_xlim(-1.5, 1.5)
    ax.set_ylim(-1.5, 1.5)

    plt.savefig('stars_only.svg', format='svg')
    plt.savefig('stars_only.png', format='png', dpi=300)
    # plt.show()


plot_stars()
