import os
import glob
import numpy as np
import matplotlib.pyplot as plt
import re
from tqdm import tqdm

# Species info: id -> (label, color)
species_info = {
    1: ('O2 (reactant)', 'blue'),
    2: ('Ar (inert)', 'cyan'),
    3: ('CO2 (from ZrC oxidation)', 'red'),
    4: ('ZrO2 (from ZrC oxidation)', 'orange'),
    5: ('Zr (from Zr sublimation)', 'green'),
    6: ('C (from C sublimation)', 'black'),
    7: ('ZrC (bulk surface)', 'purple'),
}

# Helper to sort files naturally
def natural_key(s):
    return int(re.search(r'\d+$', s).group())

# Load and sort dump files
dump_files = sorted(glob.glob("gas/dump.allpart.*"), key=natural_key)[:3500]
num_frames = len(dump_files)

# Initialize particle count dictionary
particle_counts = {t: [] for t in species_info}

# Process each frame with progress bar
for dump_file in tqdm(dump_files, desc="Processing frames", ncols=80):
    with open(dump_file, 'r') as f:
        lines = f.readlines()

    atom_start = next(i for i, line in enumerate(lines) if line.startswith("ITEM: ATOMS")) + 1
    data = np.array([line.strip().split() for line in lines[atom_start:]], dtype=object)

    types = data[:, 1].astype(int)
    x = data[:, 2].astype(float)
    y = data[:, 3].astype(float)
    z = data[:, 4].astype(float)

    # Filter particles inside the simulation box
    in_box_mask = (
        (x >= -0.55) & (x <= 0.55) &
        (y >= -0.55) & (y <= 0.55) &
        (z >= -0.55) & (z <= 0.55)
    )

    for t in species_info:
        type_mask = (types == t)
        count = np.sum(type_mask & in_box_mask)
        particle_counts[t].append(count)

# Create output folder for plots
os.makedirs("particle_plots", exist_ok=True)

# Generate separate plots per species
for t, (label, color) in species_info.items():
    plt.figure(figsize=(10, 5))
    plt.plot(range(num_frames), particle_counts[t], color=color)
    plt.xlabel("Frame Number")
    plt.ylabel("Number of Particles (inside box)")
    plt.title(f"Particle Count per Frame - {label}")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(f"particle_plots/{label.replace(' ', '_')}_count.png", dpi=150)
    plt.close()
