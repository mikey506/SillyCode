#!/usr/bin/env python3
import os
import http.server
import socketserver
import plotly.graph_objects as go
import pandas as pd
import numpy as np

def build_3d_network(csv_path="Neurotransmitter_Dysregulation_in_Archetypes.csv",
                     output_html="index.html"):
    # ----------------------------------------------------
    # 1) Load CSV
    # ----------------------------------------------------
    df = pd.read_csv(csv_path)
    df.columns = df.columns.str.strip()  # Clean up column headers

    transmitter_cols = ["Dopamine","Serotonin","Norepinephrine","Glutamate","GABA"]
    hormone_cols = ["Oxytocin","Vasopressin"]
    all_nh_cols = transmitter_cols + hormone_cols

    # ----------------------------------------------------
    # 2) Create Archetype-Subtype (AS) nodes
    # ----------------------------------------------------
    as_nodes = []
    for idx, row in df.iterrows():
        archetype = str(row["Archetype"]).strip()
        subtype   = str(row["Subtype"]).strip()
        as_id = f"{archetype}_{subtype}"

        details = []
        for col in all_nh_cols:
            val = str(row.get(col, ""))
            if pd.notna(val) and val.strip():
                details.append(f"{col}: {val}")

        hover_text = (
            f"<b>{archetype} - {subtype}</b><br>" +
            "<br>".join(details)
        )

        as_nodes.append({
            "id": as_id,
            "archetype": archetype,
            "subtype": subtype,
            "hover": hover_text
        })

    # ----------------------------------------------------
    # 3) Create ONE node per transmitter/hormone if it appears non-normal
    # ----------------------------------------------------
    unique_nh = {}
    for col in all_nh_cols:
        # Determine if there's any row where col is NOT "normal" or blank
        any_non_normal = False
        for val in df[col].dropna():
            if str(val).strip().lower() != "normal":
                any_non_normal = True
                break

        if any_non_normal:
            node_type = "NT"  # default for neurotransmitter
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

    # ----------------------------------------------------
    # 4) Edges: AS->NH & AS->AS
    # ----------------------------------------------------
    # 4a) AS->NH edges
    as_to_nh_edges = []
    for idx, row in df.iterrows():
        archetype = str(row["Archetype"]).strip()
        subtype   = str(row["Subtype"]).strip()
        as_id = f"{archetype}_{subtype}"

        for col in unique_nh.keys():
            val = row.get(col, "")
            if pd.notna(val):
                val_str = str(val).strip()
                if val_str.lower() != "normal" and val_str != "":
                    target_id = unique_nh[col]["id"]
                    as_to_nh_edges.append({
                        "source": as_id,
                        "target": target_id,
                        "label": f"{col} dysregulation: {val_str}"
                    })

    # 4b) AS->AS edges (shared dysregulation)
    as_as_edges = []
    row_map = {(r["Archetype"].strip(), r["Subtype"].strip()): r
               for _,r in df.iterrows()}
    for i in range(len(as_nodes)):
        for j in range(i+1, len(as_nodes)):
            n1 = as_nodes[i]
            n2 = as_nodes[j]
            r1 = row_map[(n1["archetype"], n1["subtype"])]
            r2 = row_map[(n2["archetype"], n2["subtype"])]

            shared = []
            for col in unique_nh.keys():
                v1 = str(r1.get(col, "")).lower().strip()
                v2 = str(r2.get(col, "")).lower().strip()
                if v1 not in ("", "normal") and v2 not in ("", "normal"):
                    shared.append(col)

            if shared:
                as_as_edges.append({
                    "source": n1["id"],
                    "target": n2["id"],
                    "label": "Shared Dysregulation: " + ", ".join(shared)
                })

    # ----------------------------------------------------
    # 5) Random 3D Coordinates
    # ----------------------------------------------------
    all_nodes = as_nodes + nh_nodes
    cube_size = 30
    coordinates = {}
    for n in all_nodes:
        coordinates[n["id"]] = (np.random.rand(3) - 0.5) * cube_size

    # ----------------------------------------------------
    # 6) Build Plotly Traces
    # ----------------------------------------------------
    # Distinguish AS (archetype-subtype) from NH nodes
    archetype_colors = {"Witches": "red", "Androids": "green", "Mystics": "blue"}

    AS_x, AS_y, AS_z = [], [], []
    AS_texts, AS_colors, AS_sizes = [], [], []
    for node in as_nodes:
        x, y, z = coordinates[node["id"]]
        AS_x.append(x)
        AS_y.append(y)
        AS_z.append(z)
        AS_texts.append(node["hover"])
        c = archetype_colors.get(node["archetype"], "gray")
        AS_colors.append(c)
        AS_sizes.append(15)

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

    AS_trace = go.Scatter3d(
        x=AS_x, y=AS_y, z=AS_z,
        mode='markers+text',
        text=AS_texts,
        hoverinfo='text',
        marker=dict(size=AS_sizes, color=AS_colors, opacity=0.9),
        textposition="top center"
    )

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

    # AS->NH edges
    for edge in as_to_nh_edges:
        c1 = coordinates[edge["source"]]
        c2 = coordinates[edge["target"]]
        lbl = edge["label"]
        edge_traces.append(make_edge_trace(c1, c2, lbl))

    # AS->AS edges
    for edge in as_as_edges:
        c1 = coordinates[edge["source"]]
        c2 = coordinates[edge["target"]]
        lbl = edge["label"]
        edge_traces.append(make_edge_trace(c1, c2, lbl))

    fig = go.Figure()
    fig.add_trace(AS_trace)
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
        title="3D Neurotransmitter/Hormone Network"
    )

    # Write out to HTML
    fig.write_html(output_html, auto_open=False)
    print(f"[INFO] 3D Figure saved to {output_html}")

def run_http_server(port=8000):
    """Start a simple HTTP server on the given port, serving the current directory."""
    handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", port), handler) as httpd:
        print(f"[INFO] Serving HTTP on 0.0.0.0:{port}")
        print(f"[INFO] Open your browser at http://localhost:{port}/index.html")
        httpd.serve_forever()

if __name__ == "__main__":
    # 1) Build the Plotly 3D network from your CSV
    csv_file = "Neurotransmitter_Dysregulation_in_Archetypes.csv"  # edit if needed
    output_html = "index.html"
    if not os.path.isfile(csv_file):
        print(f"[ERROR] CSV file not found: {csv_file}")
        print("Make sure the CSV path is correct or in the same folder.")
        exit(1)

    build_3d_network(csv_file, output_html)

    # 2) Start the HTTP server so you can view index.html
    run_http_server(port=8000)
