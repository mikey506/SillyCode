import tkinter as tk
from tkinter import filedialog, messagebox
import cv2
import numpy as np
from collections import defaultdict
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import pandas as pd

# Define color ranges for decoding
color_ranges = {
    "Homeostasis/Calm (Blue)": ([0, 0, 128], [50, 50, 255]),   # Blue
    "Density/Blockages (Red)": ([128, 0, 0], [255, 50, 50]),   # Red
    "3D Purge Energies (Green)": ([0, 128, 0], [50, 255, 50]), # Green
    "5D Light Coding (White)": ([200, 200, 200], [255, 255, 255]), # White
}

# Global variable to hold the image
image = None

# Functions for decoding
def load_image():
    global image
    file_path = filedialog.askopenfilename(
        filetypes=[("PNG Files", "*.png")],
        title="Select a PNG Image"
    )
    if not file_path:
        messagebox.showerror("Error", "No file selected!")
        return None
    try:
        image = cv2.imread(file_path)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        messagebox.showinfo("Success", "Image loaded successfully!")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to load image: {e}")

def extract_pixel_counts(image, color_ranges):
    pixel_counts = defaultdict(int)
    height, width, _ = image.shape
    for label, (lower, upper) in color_ranges.items():
        lower_bound = np.array(lower, dtype="uint8")
        upper_bound = np.array(upper, dtype="uint8")
        mask = cv2.inRange(image, lower_bound, upper_bound)
        count = cv2.countNonZero(mask)
        pixel_counts[label] = count
    return pixel_counts, height, width

def split_into_time_sections(image, num_intervals):
    height, width, _ = image.shape
    interval_width = width // num_intervals
    sections = []
    for i in range(num_intervals):
        start_x = i * interval_width
        end_x = (i + 1) * interval_width if i < num_intervals - 1 else width
        sections.append(image[:, start_x:end_x])
    return sections

def analyze_time_sections(sections, color_ranges):
    results = []
    for section in sections:
        pixel_counts, height, width = extract_pixel_counts(section, color_ranges)
        total_pixels = height * width
        proportions = {label: (count / total_pixels) * 100 for label, count in pixel_counts.items()}
        results.append(proportions)
    return results

def generate_timestamps(start_time, end_time, num_intervals):
    return pd.date_range(start=start_time, end=end_time, periods=num_intervals).strftime("%H:%M").tolist()

# Visualization functions
def show_overall_stats():
    if image is None:
        messagebox.showerror("Error", "No image loaded!")
        return
    pixel_counts, height, width = extract_pixel_counts(image, color_ranges)
    total_pixels = height * width
    overall_proportions = {label: (count / total_pixels) * 100 for label, count in pixel_counts.items()}
    
    plt.figure(figsize=(10, 6))
    plt.bar(overall_proportions.keys(), overall_proportions.values(), alpha=0.8)
    plt.title("Overall Schumann Resonance Stats")
    plt.ylabel("Proportion (%)")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.show()

def show_time_based_stats():
    if image is None:
        messagebox.showerror("Error", "No image loaded!")
        return
    num_intervals = 24
    time_sections = split_into_time_sections(image, num_intervals)
    analysis_results = analyze_time_sections(time_sections, color_ranges)
    timestamps = generate_timestamps("00:00", "23:59", num_intervals)

    df = pd.DataFrame(analysis_results, index=timestamps)
    df.plot(kind="line", figsize=(12, 8), marker="o")
    plt.title("Time-Based Schumann Resonance Stats")
    plt.xlabel("Time")
    plt.ylabel("Proportion (%)")
    plt.xticks(rotation=45, ha="right")
    plt.legend(loc="upper left", bbox_to_anchor=(1, 1))
    plt.tight_layout()
    plt.show()

def show_3d_model():
    if image is None:
        messagebox.showerror("Error", "No image loaded!")
        return
    num_intervals = 24
    time_sections = split_into_time_sections(image, num_intervals)
    analysis_results = analyze_time_sections(time_sections, color_ranges)
    timestamps = generate_timestamps("00:00", "23:59", num_intervals)

    fig = plt.figure(figsize=(12, 8))
    ax = fig.add_subplot(111, projection='3d')

    x = np.arange(len(timestamps))
    y = np.arange(len(color_ranges))
    X, Y = np.meshgrid(x, y)

    Z = np.array([[res[label] for res in analysis_results] for label in color_ranges.keys()])
    ax.plot_surface(X, Y, Z, cmap='viridis', edgecolor='k')

    ax.set_xticks(x)
    ax.set_xticklabels(timestamps, rotation=45, ha="right")
    ax.set_yticks(range(len(color_ranges)))
    ax.set_yticklabels(color_ranges.keys())
    ax.set_xlabel("Time")
    ax.set_ylabel("Category")
    ax.set_zlabel("Proportion (%)")

    plt.title("3D Visualization of Schumann Resonance Dynamics")
    plt.tight_layout()
    plt.show()

def show_effects():
    effects = """
    Detailed Effects of Schumann Resonance on Body/Mind:
    1. Homeostasis/Calm (Blue): Promotes emotional stability, stress relief, and physical grounding.
    2. Density/Blockages (Red): Indicates emotional or energetic resistance, often linked to fatigue or anxiety.
    3. 3D Purge Energies (Green): Represents detoxification and healing. Encourages emotional release and renewal.
    4. 5D Light Coding (White): Symbolizes clarity, spiritual awakening, and higher consciousness. Can be energizing or overwhelming.
    """
    messagebox.showinfo("Detailed Effects", effects)

# GUI Setup
def main():
    root = tk.Tk()
    root.title("Schumann Resonance Analyzer")

    tk.Button(root, text="Load PNG Image", command=load_image).pack(pady=10)
    tk.Button(root, text="View Overall Stats", command=show_overall_stats).pack(pady=10)
    tk.Button(root, text="View Time-Based Stats", command=show_time_based_stats).pack(pady=10)
    tk.Button(root, text="View 3D Model", command=show_3d_model).pack(pady=10)
    tk.Button(root, text="View Detailed Effects", command=show_effects).pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    main()
