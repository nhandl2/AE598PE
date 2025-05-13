import os
import glob
import numpy as np
import matplotlib.pyplot as plt
import subprocess
import re

# Define species info (match to your reactants.species order in SPARTA)
species_info = {
    1: ('O2 (reactant)', 'blue'),
    2: ('Ar (inert)', 'cyan'),
    3: ('CO2 (from ZrC oxidation)', 'red'),
    4: ('ZrO2 (from ZrC oxidation)', 'orange'),
    5: ('Zr (from Zr sublimation)', 'green'),
    6: ('C (from C sublimation)', 'black'),
    7: ('ZrC (bulk surface)', 'purple'),
}

# Create output folders
os.makedirs("frames", exist_ok=True)
for species_id in species_info:
    os.makedirs(f"frames/type_{species_id}", exist_ok=True)
os.makedirs("video", exist_ok=True)

# Sort dump files and limit to first 3500
def natural_key(s):
    return int(re.search(r'\d+$', s).group())

dump_files = sorted(glob.glob("gas/dump.allpart.*"), key=natural_key)[:3500]

# Track frames where each species appears
species_frame_indices = {t: set() for t in species_info}

for frame_idx, dump_file in enumerate(dump_files):
    with open(dump_file, 'r') as f:
        lines = f.readlines()

    atom_start = next(i for i, line in enumerate(lines) if line.startswith("ITEM: ATOMS")) + 1
    data = np.array([line.strip().split() for line in lines[atom_start:]], dtype=object)

    types = data[:, 1].astype(int)
    x = data[:, 2].astype(float)
    y = data[:, 3].astype(float)
    z = data[:, 4].astype(float)

    # Filter particles inside the main simulation box
    in_box_mask = (
        (x >= -0.55) & (x <= 0.55) &
        (y >= -0.55) & (y <= 0.55) &
        (z >= -0.55) & (z <= 0.55)
    )

    for t, (label, color) in species_info.items():
        mask = (types == t) & in_box_mask
        if not np.any(mask):
            continue

        species_frame_indices[t].add(frame_idx)

        fig = plt.figure(figsize=(6, 6))
        ax = fig.add_subplot(111, projection='3d')
        ax.scatter(x[mask], y[mask], z[mask], c=color, s=2)
        ax.set_title(f"{label} - Frame {frame_idx} - Count: {np.sum(mask)}")
        ax.set_xlim(-0.55, 0.55)
        ax.set_ylim(-0.55, 0.55)
        ax.set_zlim(-0.55, 0.55)
        ax.set_xlabel("X")
        ax.set_ylabel("Y")
        ax.set_zlabel("Z")

        # Draw simulation box
        box_lines = [
            [(-0.55, -0.55, -0.55), (0.55, -0.55, -0.55)],
            [(0.55, -0.55, -0.55), (0.55, 0.55, -0.55)],
            [(0.55, 0.55, -0.55), (-0.55, 0.55, -0.55)],
            [(-0.55, 0.55, -0.55), (-0.55, -0.55, -0.55)],
            [(-0.55, -0.55, 0.55), (0.55, -0.55, 0.55)],
            [(0.55, -0.55, 0.55), (0.55, 0.55, 0.55)],
            [(0.55, 0.55, 0.55), (-0.55, 0.55, 0.55)],
            [(-0.55, 0.55, 0.55), (-0.55, -0.55, 0.55)],
            [(-0.55, -0.55, -0.55), (-0.55, -0.55, 0.55)],
            [(0.55, -0.55, -0.55), (0.55, -0.55, 0.55)],
            [(0.55, 0.55, -0.55), (0.55, 0.55, 0.55)],
            [(-0.55, 0.55, -0.55), (-0.55, 0.55, 0.55)],
        ]
        for start, end in box_lines:
            xs, ys, zs = zip(start, end)
            ax.plot(xs, ys, zs, color='gray', linewidth=0.5)

        # Draw surface bounding box
        surface_box = [
            [(-0.05, -0.10, -0.05), (0.05, -0.10, -0.05)],
            [(0.05, -0.10, -0.05), (0.05, 0.0, -0.05)],
            [(0.05, 0.0, -0.05), (-0.05, 0.0, -0.05)],
            [(-0.05, 0.0, -0.05), (-0.05, -0.10, -0.05)],
            [(-0.05, -0.10, 0.05), (0.05, -0.10, 0.05)],
            [(0.05, -0.10, 0.05), (0.05, 0.0, 0.05)],
            [(0.05, 0.0, 0.05), (-0.05, 0.0, 0.05)],
            [(-0.05, 0.0, 0.05), (-0.05, -0.10, 0.05)],
            [(-0.05, -0.10, -0.05), (-0.05, -0.10, 0.05)],
            [(0.05, -0.10, -0.05), (0.05, -0.10, 0.05)],
            [(0.05, 0.0, -0.05), (0.05, 0.0, 0.05)],
            [(-0.05, 0.0, -0.05), (-0.05, 0.0, 0.05)],
        ]
        for start, end in surface_box:
            xs, ys, zs = zip(start, end)
            ax.plot(xs, ys, zs, color='purple', linestyle='--', linewidth=1.0, label='_nolegend_')

        plt.tight_layout()
        plt.savefig(f"frames/type_{t}/frame_{frame_idx:04d}.png", dpi=150)
        plt.close()

# Pad missing frames and create videos
for t, (label, _) in species_info.items():
    folder = f"frames/type_{t}"
    present_frames = species_frame_indices[t]

    for i in range(3500):
        frame_path = os.path.join(folder, f"frame_{i:04d}.png")
        if i not in present_frames:
            fig = plt.figure(figsize=(6, 6))
            ax = fig.add_subplot(111, projection='3d')
            ax.set_xlim(-0.55, 0.55)
            ax.set_ylim(-0.55, 0.55)
            ax.set_zlim(-0.55, 0.55)
            ax.set_xlabel("X")
            ax.set_ylabel("Y")
            ax.set_zlabel("Z")
            ax.set_title(f"{label} - Frame {i} - Blank")

            # Draw simulation box
            box_lines = [
                [(-0.55, -0.55, -0.55), (0.55, -0.55, -0.55)],
                [(0.55, -0.55, -0.55), (0.55, 0.55, -0.55)],
                [(0.55, 0.55, -0.55), (-0.55, 0.55, -0.55)],
                [(-0.55, 0.55, -0.55), (-0.55, -0.55, -0.55)],
                [(-0.55, -0.55, 0.55), (0.55, -0.55, 0.55)],
                [(0.55, -0.55, 0.55), (0.55, 0.55, 0.55)],
                [(0.55, 0.55, 0.55), (-0.55, 0.55, 0.55)],
                [(-0.55, 0.55, 0.55), (-0.55, -0.55, 0.55)],
                [(-0.55, -0.55, -0.55), (-0.55, -0.55, 0.55)],
                [(0.55, -0.55, -0.55), (0.55, -0.55, 0.55)],
                [(0.55, 0.55, -0.55), (0.55, 0.55, 0.55)],
                [(-0.55, 0.55, -0.55), (-0.55, 0.55, 0.55)],
            ]
            for start, end in box_lines:
                xs, ys, zs = zip(start, end)
                ax.plot(xs, ys, zs, color='gray', linewidth=0.5)

            # Draw surface bounding box
            surface_box = [
                [(-0.05, -0.10, -0.05), (0.05, -0.10, -0.05)],
                [(0.05, -0.10, -0.05), (0.05, 0.0, -0.05)],
                [(0.05, 0.0, -0.05), (-0.05, 0.0, -0.05)],
                [(-0.05, 0.0, -0.05), (-0.05, -0.10, -0.05)],
                [(-0.05, -0.10, 0.05), (0.05, -0.10, 0.05)],
                [(0.05, -0.10, 0.05), (0.05, 0.0, 0.05)],
                [(0.05, 0.0, 0.05), (-0.05, 0.0, 0.05)],
                [(-0.05, 0.0, 0.05), (-0.05, -0.10, 0.05)],
                [(-0.05, -0.10, -0.05), (-0.05, -0.10, 0.05)],
                [(0.05, -0.10, -0.05), (0.05, -0.10, 0.05)],
                [(0.05, 0.0, -0.05), (0.05, 0.0, 0.05)],
                [(-0.05, 0.0, -0.05), (-0.05, 0.0, 0.05)],
            ]
            for start, end in surface_box:
                xs, ys, zs = zip(start, end)
                ax.plot(xs, ys, zs, color='purple', linestyle='--', linewidth=1.0)

            plt.tight_layout()
            plt.savefig(frame_path, dpi=150)
            plt.close()

    if os.listdir(folder):
        output_video = f"video/{label.replace(' ', '_')}_video.mp4"
        subprocess.run([
            "ffmpeg", "-y", "-framerate", "10",
            "-i", f"{folder}/frame_%04d.png",
            "-vcodec", "libx264", "-pix_fmt", "yuv420p",
            output_video
        ])
        print(f"Created video: {output_video}")

