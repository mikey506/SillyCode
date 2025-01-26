# 3D Neurotransmitter Interaction with ASMR & Psychogenic Shivers

**Preview Video**  
[Watch the 3D Model in Action on Imgur](https://imgur.com/gallery/3d-model-of-neurotransmitter-interaction-with-asmr-psychogenic-shivers-2Px60Y0)

This repository provides a **Plotly 3D visualization** of how **ASMR** (Autonomous Sensory Meridian Response) and **Psychogenic Shivers** may overlap or differ in terms of **neurotransmitter/hormone** involvement. The visualization is rendered as a **network-style** 3D model, with nodes for phenomenon-trigger pairs (e.g., “ASMR - Whispering” or “Psychogenic Shivers - AweInMusic”) and neurotransmitter/hormone nodes (Dopamine, Serotonin, GABA, etc.).

## Features

- **Mock CSV Data** (`Neurotransmitter_Dysregulation_in_Phenomena.csv`)  
  - Lists rows for ASMR triggers, Psychogenic Shivers triggers, and **Shared** scenarios.  
  - Each row indicates whether neurotransmitters/hormones are “Increased,” “Decreased,” or “Normal.”  

- **Plotly 3D Script** (`psychogenic.py`)  
  - Loads the CSV and creates a **3D scatter** network.  
  - **Nodes**: (Phenomenon, Trigger) pairs and neurotransmitter/hormone nodes.  
  - **Edges**: Link phenomenon-trigger nodes to neurotransmitter/hormone nodes with non-“normal” entries, plus cross-links for phenomenon-trigger pairs that share the same dysregulations.  
  - **Random 3D positions** for each node; results saved to **`index.html`**.  
  - A simple HTTP server is launched on port **8000** so you can view your 3D model in the browser.

## Installation and Usage

1. **Clone or Download** this repository.
2. Ensure **Python 3** is installed, then install the dependencies:
   ```bash
   pip install plotly pandas numpy
