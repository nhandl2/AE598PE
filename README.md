# AE598PE
Repository for AE 598 Planetary Entry Final Project

Title: Zirconium Carbide Oxidation Modeling with SPARTA

Contributors: Liam Heuser, Nayan Jangid, Brendan Jones, and Nathan Lam.

Using SPARTA, this project simulates chemical reactions on ZrC (Zirconium Carbide) surfaces exposed to oxidizing gases. It analyzes surface reactions and gas-phase behavior in hypersonic entry scenarios. Post-processing is done using Python to extract physical insights and generate visualizations.

## 📁 Repository Structure


## 🔬 Simulation Overview

- **Physics**: The simulation models reactive flow over a solid ZrC surface using Direct Simulation Monte Carlo (DSMC).
- **Species Modeled**:
  - O₂ (reactant)
  - Ar (inert)
  - CO₂ (reaction product)
  - ZrO₂ (surface reaction products)
  - ZrC (bulk solid surface)

- **Surface Reactions Include**:
  - ZrC oxidation

## 📊 Python Post-processing

All scripts are inside the `python/` directory:

- `generating_plots.py`: Reads SPARTA `dump.allpart.*` files and generates:
  - Species-specific frame images
  - Aggregated plots of particle counts
  - Videos from frame images using `ffmpeg`
- `count.py`: Efficiently counts particle type distribution across time.


## 📂 Results

The `results/` folder includes:

- PNG files visualizing particle positions and type densities
- MP4 videos showing particle movement over time

