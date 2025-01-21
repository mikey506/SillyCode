import cv2
import numpy as np
from collections import defaultdict
import matplotlib.pyplot as plt
import pandas as pd

# Load the image
image_path = "schumann_resonance.png"  # Replace with your image file path
image = cv2.imread(image_path)
image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

# Define color ranges for decoding
color_ranges = {
    "Homeostasis/Calm (Blue)": ([0, 0, 128], [50, 50, 255]),   # Blue
    "Density/Blockages (Red)": ([128, 0, 0], [255, 50, 50]),   # Red
    "3D Purge Energies (Green)": ([0, 128, 0], [50, 255, 50]), # Green
    "5D Light Coding (White)": ([200, 200, 200], [255, 255, 255]), # White
}

# Set time axis parameters (e.g., 24 hours)
start_time = "00:00"  # Start of the day
end_time = "23:59"    # End of the day
num_time_intervals = 24  # Assume 1-hour intervals

# Split the image into time sections
def split_into_time_sections(image, num_intervals):
    height, width, _ = image.shape
    interval_width = width // num_intervals
    sections = []

    for i in range(num_intervals):
        start_x = i * interval_width
        end_x = (i + 1) * interval_width if i < num_intervals - 1 else width
        section = image[:, start_x:end_x]
        sections.append(section)

    return sections

# Analyze each time section
def analyze_time_sections(sections, color_ranges):
    results = []
    for i, section in enumerate(sections):
        pixel_counts, height, width = extract_pixel_counts(section, color_ranges)
        total_pixels = height * width
        proportions = {label: (count / total_pixels) * 100 for label, count in pixel_counts.items()}
        results.append(proportions)
    return results

# Extract pixel counts for a single section
def extract_pixel_counts(image, color_ranges):
    pixel_counts = defaultdict(int)
    height, width, _ = image.shape

    for label, (lower, upper) in color_ranges.items():
        lower_bound = np.array(lower, dtype="uint8")
        upper_bound = np.array(upper, dtype="uint8")
        
        # Create mask for the color range
        mask = cv2.inRange(image, lower_bound, upper_bound)
        count = cv2.countNonZero(mask)
        pixel_counts[label] = count

    return pixel_counts, height, width

# Map intervals to timestamps
def generate_timestamps(start_time, end_time, num_intervals):
    times = pd.date_range(start=start_time, end=end_time, periods=num_intervals).strftime("%H:%M")
    return list(times)

# Plot results dynamically
def plot_time_dynamics(timestamps, results):
    df = pd.DataFrame(results, index=timestamps)
    df.plot(kind="line", figsize=(12, 8), marker="o")
    plt.title("Schumann Resonance Dynamics Over Time")
    plt.xlabel("Time")
    plt.ylabel("Proportion (%)")
    plt.legend(loc="upper left", bbox_to_anchor=(1, 1))
    plt.tight_layout()
    plt.show()

# Main analysis workflow
time_sections = split_into_time_sections(image, num_time_intervals)
analysis_results = analyze_time_sections(time_sections, color_ranges)
timestamps = generate_timestamps(start_time, end_time, num_time_intervals)

# Display results
for time, proportions in zip(timestamps, analysis_results):
    print(f"Time: {time} | Proportions: {proportions}")

# Plot the dynamics
plot_time_dynamics(timestamps, analysis_results)
