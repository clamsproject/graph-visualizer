# MMIF Graph Visualizer

This repository hosts the code for the Graph Visualizer, a collection-level visualizer for [MMIF](https://mmif.clams.ai/) files which renders MMIF files as nodes in a D3 force-directed graph. For more information, read the project report in the `doc` directory.

## Quick Start

Currently, you can run the server in two ways:
1. Manually, with Python:
    * Install requirements: `pip install -r requirements.txt`
    * Unzip `data/topic_newshour.zip` in the `data` directory
    * Run the mmif visualizer in parallel for access to visualization

2. Using Docker/Podman
* docker-compose up will spin up the Graph Visualizer and the MMIF visualizer, and connect them via a network.
* WARNING: Because the project contains a significant amount of networking, building the container may take a while, and is liable to crash.

