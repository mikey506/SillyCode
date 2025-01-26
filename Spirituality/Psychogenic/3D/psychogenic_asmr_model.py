#!/usr/bin/env python3
import os
import sys
import http.server
import socketserver

# Plotly / Pandas / NumPy are required
try:
    import plotly
    import plotly.graph_objects as go
except ImportError:
    print("[ERROR] Plotly not installed. Try: pip install plotly")
    sys.exit(1)

try:
    import pandas as pd
except ImportError:
    print("[ERROR] Pandas not installed. Try: pip install pandas")
    sys.exit(1)

try:
    import numpy as np
except ImportError:
    print("[ERROR] NumPy not installed. Try: pip install numpy")
    sys.exit(1)


def build_3d_network(csv_path="Neurotransmitter_Dysregulation_in_Archetypes.csv",
                     output_html="index.html"):
    """
    Reads a CSV file containing data for ASMR or Psychogenic Shivers phenomena,
    each with a 'Trigger' and possible dysregulations in neurotransmitters/hormones.
    
    Steps:
      1) Creates "PT" nodes (Phenomenon-Trigger).
      2) Creates nodes for each non-normal neurotransmitter/hormone (NH).
      3) Builds edges:
         - PT -> NH if that row indicates a dysregulation
         - PT -> PT if they share one or more dysregulated NT/hormones
      4) Assigns random 3D coords.
      5) Builds a Plotly 3D network and writes it to HTML.
    """

    print(f"[INFO] build_3d_network called with csv_path='{csv_path}' -> output '{output_html}'")

    # ----------------------------------------------------
    # 1) Load and Validate CSV
    # ----------------------------------------------------
    if not os.path.isfile(csv_path):
        print(f"[ERROR] CSV file not found: {csv_path}")
        print("       Make sure the CSV path is correct or in the same folder.")
        sys.exit(1)

    print(f"[DEBUG] Reading CSV from: {csv_path}")
    df = pd.read_csv(csv_path)
    print(f"[DEBUG] CSV loaded. Rows: {len(df)}, Columns: {list(df.columns)}")

    # Required columns for this script
    required_cols = {"Phenomenon", "Trigger"}
    missing_cols = required_cols - set(df.columns)
    if missing_cols:
        print(f"[ERROR] Missing required columns: {missing_cols}")
        print("       Make sure the CSV has 'Phenomenon' (ASMR/Psychogenic Shivers) and 'Trigger'.")
        sys.exit(1)

    # Clean up columns (remove trailing spaces, if any)
    df.columns = df.columns.str.strip()

    # Common transmitters/hormones (adjust as needed)
    transmitter_cols = ["Dopamine", "Serotonin", "Norepinephrine", "Glutamate", "GABA"]
    hormone_cols = ["Oxytocin", "Vasopressin"]
    all_nh_cols = transmitter_cols + hormone_cols

    # Log missing or extra columns
    existing_nh_cols = [c for c in all_nh_cols if c in df.columns]
    missing_nh_cols = set(all_nh_cols) - set(existing_nh_cols)
    if missing_nh_cols:
        print(f"[WARNING] The following NT/hormone columns are not in CSV: {missing_nh_cols}")
        print("          They will be ignored if not present at all.")

    # We'll only consider columns that exist in the CSV
    actual_nh_cols = existing_nh_cols

    # ----------------------------------------------------
    # 2) Create Phenomenon-Trigger (PT) nodes
    # ----------------------------------------------------
    print("[DEBUG] Building PT nodes (Phenomenon+Trigger)...")
    pt_nodes = []
    for idx, row in df.iterrows():
        phenomenon = str(row["Phenomenon"]).strip()    # e.g., "ASMR" or "Psychogenic Shivers"
        trigger    = str(row["Trigger"]).strip()       # e.g., "Whispering" or "Music Chills"
        pt_id      = f"{phenomenon}_{trigger}"

        # Build hover text from any non-normal columns
        details = []
        for col in actual_nh_cols:
            val = row.get(col, "")
            if pd.notna(val):
                val_str = str(val).strip()
                if val_str:
                    details.append(f"{col}: {val_str}")

        hover_text = f"<b>{phenomenon} - {trigger}</b><br>" + "<br>".join(details)

        pt_nodes.append({
            "id": pt_id,
            "phenomenon": phenomenon,
            "trigger": trigger,
            "hover": hover_text
        })

    print(f"[DEBUG] Total PT nodes: {len(pt_nodes)}")

    # ----------------------------------------------------
    # 3) Create NH nodes (non-"normal" only)
    # ----------------------------------------------------
    print("[DEBUG] Checking which NT/hormone columns have non-normal data...")

    unique_nh = {}
    for col in actual_nh_cols:
        any_non_normal = False
        for val in df[col].dropna():
            if str(val).strip().lower() != "normal" and str(val).strip() != "":
                any_non_normal = True
                break

        if any_non_normal:
            node_type = "NT"  # default for neurotransmitters
            color = "purple"
            if col in hormone_cols:
                node_type = "H"
                color = "yellow"

            nh_id = f"{node_type}_{col}"
            unique_nh[col] = {
                "id": nh_id,
                "label": col,
                "color": color
            }

    nh_nodes = list(unique_nh.values())
    print(f"[DEBUG] Total NH nodes (non-normal): {len(nh_nodes)} -> {nh_nodes}")

    # ----------------------------------------------------
    # 4) Build Edges: PT->NH & PT->PT
    # ----------------------------------------------------
    print("[DEBUG] Building edges for PT->NH...")

    pt_to_nh_edges = []
    for idx, row in df.iterrows():
        phenomenon = str(row["Phenomenon"]).strip()
        trigger    = str(row["Trigger"]).strip()
        pt_id = f"{phenomenon}_{trigger}"

        for col in unique_nh.keys():
            val = row.get(col, "")
            if pd.notna(val):
                val_str = str(val).strip()
                if val_str.lower() != "normal" and val_str != "":
                    target_id = unique_nh[col]["id"]
                    pt_to_nh_edges.append({
                        "source": pt_id,
                        "target": target_id,
                        "label": f"{col} involvement: {val_str}"
                    })

    print(f"[DEBUG] PT->NH edges: {len(pt_to_nh_edges)}")

    print("[DEBUG] Building edges for PT->PT (shared involvement)...")
    pt_map = {}
    for _, r in df.iterrows():
        pheno = str(r["Phenomenon"]).strip()
        trig  = str(r["Trigger"]).strip()
        pt_map[(pheno, trig)] = r

    pt_pt_edges = []
    for i in range(len(pt_nodes)):
        for j in range(i+1, len(pt_nodes)):
            n1 = pt_nodes[i]
            n2 = pt_nodes[j]
            r1 = pt_map[(n1["phenomenon"], n1["trigger"])]
            r2 = pt_map[(n2["phenomenon"], n2["trigger"])]

            shared = []
            for col in unique_nh.keys():
                v1 = str(r1.get(col, "")).strip().lower()
                v2 = str(r2.get(col, "")).strip().lower()
                if v1 not in ("", "normal") and v2 not in ("", "normal"):
                    shared.append(col)

            if shared:
                pt_pt_edges.append({
                    "source": n1["id"],
                    "target": n2["id"],
                    "label": "Shared NT/H: " + ", ".join(shared)
                })

    print(f"[DEBUG] PT->PT edges: {len(pt_pt_edges)}")

    # ----------------------------------------------------
    # 5) Random 3D Coordinates
    # ----------------------------------------------------
    print("[DEBUG] Generating random 3D coords...")

    all_nodes = pt_nodes + nh_nodes
    cube_size = 30
    coordinates = {}
    for n in all_nodes:
        # For reproducibility, seed or use your own approach
        coordinates[n["id"]] = (np.random.rand(3) - 0.5) * cube_size

    # ----------------------------------------------------
    # 6) Build Plotly 3D Traces
    # ----------------------------------------------------
    print("[DEBUG] Building Plotly traces...")

    # Assign custom colors to phenomena if you want
    phenomenon_colors = {
        "ASMR": "green",
        "Psychogenic Shivers": "red"
    }

    # PT nodes
    PT_x, PT_y, PT_z = [], [], []
    PT_texts, PT_colors, PT_sizes = [], [], []
    for node in pt_nodes:
        x, y, z = coordinates[node["id"]]
        PT_x.append(x)
        PT_y.append(y)
        PT_z.append(z)
        PT_texts.append(node["hover"])

        # Color by phenomenon
        c = phenomenon_colors.get(node["phenomenon"], "gray")
        PT_colors.append(c)
        PT_sizes.append(15)

    PT_trace = go.Scatter3d(
        x=PT_x, y=PT_y, z=PT_z,
        mode='markers+text',
        text=PT_texts,
        hoverinfo='text',
        marker=dict(size=PT_sizes, color=PT_colors, opacity=0.9),
        textposition="top center"
    )

    # NH nodes
    NH_x, NH_y, NH_z = [], [], []
    NH_texts, NH_colors, NH_sizes = [], [], []
    for node in nh_nodes:
        x, y, z = coordinates[node["id"]]
        NH_x.append(x)
        NH_y.append(y)
        NH_z.append(z)
        NH_texts.append(f"<b>{node['label']}</b>")
        NH_colors.append(node["color"])
        NH_sizes.append(10)

    NH_trace = go.Scatter3d(
        x=NH_x, y=NH_y, z=NH_z,
        mode='markers+text',
        text=NH_texts,
        hoverinfo='text',
        marker=dict(size=NH_sizes, color=NH_colors, opacity=0.8),
        textposition="top center"
    )

    edge_traces = []
    def make_edge_trace(coord1, coord2, label):
        return go.Scatter3d(
            x=[coord1[0], coord2[0], None],
            y=[coord1[1], coord2[1], None],
            z=[coord1[2], coord2[2], None],
            mode='lines',
            hoverinfo='text',
            text=[label],
            line=dict(width=2, color='gray')
        )

    # PT->NH edges
    print("[DEBUG] Building Plotly edge traces for PT->NH edges...")
    for edge in pt_to_nh_edges:
        c1 = coordinates[edge["source"]]
        c2 = coordinates[edge["target"]]
        lbl = edge["label"]
        edge_traces.append(make_edge_trace(c1, c2, lbl))

    # PT->PT edges
    print("[DEBUG] Building Plotly edge traces for PT->PT edges...")
    for edge in pt_pt_edges:
        c1 = coordinates[edge["source"]]
        c2 = coordinates[edge["target"]]
        lbl = edge["label"]
        edge_traces.append(make_edge_trace(c1, c2, lbl))

    fig = go.Figure()
    fig.add_trace(PT_trace)
    fig.add_trace(NH_trace)
    for et in edge_traces:
        fig.add_trace(et)

    fig.update_layout(
        scene=dict(
            xaxis=dict(title='X Axis'),
            yaxis=dict(title='Y Axis'),
            zaxis=dict(title='Z Axis')
        ),
        margin=dict(l=0, r=0, b=0, t=30),
        showlegend=False,
        title="3D Model: ASMR & Psychogenic Shivers Network"
    )

    print(f"[DEBUG] Writing figure to HTML: {output_html}")
    fig.write_html(output_html, auto_open=False)
    print(f"[INFO] 3D Figure successfully written to '{output_html}'")


def run_http_server(port=8000):
    """Start a simple HTTP server on the given port, serving the current directory."""
    handler = http.server.SimpleHTTPRequestHandler

    print(f"[INFO] Serving HTTP on 0.0.0.0:{port}")
    print(f"[INFO] Open your browser at http://localhost:{port}/index.html")

    with socketserver.TCPServer(("", port), handler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n[INFO] Server stopped by user (Ctrl+C).")


if __name__ == "__main__":
    # 1) Build the 3D Plotly network from your CSV
    csv_file = "Neurotransmitter_Dysregulation_in_Archetypes.csv"  # rename or adjust if needed
    output_html = "index.html"

    build_3d_network(csv_file, output_html)

    # 2) Start the HTTP server so you can view 'index.html'
    run_http_server(port=8000)
