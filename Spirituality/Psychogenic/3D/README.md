# 3D Neurotransmitter Interaction with ASMR & Psychogenic Shivers

![Preview of 3D Model](https://i.imgur.com/3d-model-of-neurotransmitter-interaction-with-asmr-psychogenic-shivers-2Px60Y0.jpg)

This repository provides a **Plotly 3D visualization** of how **ASMR** (Autonomous Sensory Meridian Response) and **Psychogenic Shivers** may share or differ in **neurotransmitter/hormonal** involvement. It's a **network-style** model, showing nodes for phenomenon-trigger pairs (like “ASMR - Whispering” or “Psychogenic Shivers - AweInMusic”) and linking them to the relevant neurotransmitters and hormones (e.g., Dopamine, Serotonin, Oxytocin). Edges represent **dysregulation** or **involvement**.

## Features

- **Mock CSV Data** (`Neurotransmitter_Dysregulation_in_Phenomena.csv`)  
  - Lists rows for ASMR triggers, Psychogenic Shivers triggers, and potential **Shared** cases.  
  - Each row assigns “Increased,” “Decreased,” or “Normal” for each transmitter/hormone.  

- **Plotly 3D Script** (`psychogenic.py`)  
  - Loads the CSV.  
  - Creates **nodes** for each (Phenomenon, Trigger) combo.  
  - Creates **nodes** for any **non-normal** neurotransmitter/hormone.  
  - **Edges** link phenomenon-trigger nodes to transmitter/hormone nodes (and to each other, if they share the same dysregulations).  
  - Assigns **random 3D positions**, then renders an interactive **scatter3d** graph with edges.  
  - Saves the visualization as **`index.html`** and serves it on port **8000** (via a simple HTTP server).

## Getting Started

1. **Clone/Download** this repository.
2. Ensure you have **Python 3** and install required libraries:
   ```bash
   pip install plotly pandas numpy
