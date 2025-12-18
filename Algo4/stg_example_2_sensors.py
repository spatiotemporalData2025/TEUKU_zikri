import numpy as np
import matplotlib.pyplot as plt


def node_id(i: int, t: int, n_nodes: int) -> int:
    return t * n_nodes + i


def make_grid_graph(w: int, h: int):
    """
    Create a 2D grid adjacency (4-neighborhood).
    Returns:
      positions: [N,2]
      edges: list of (u,v) undirected
    """
    positions = []
    idx = lambda x, y: y * w + x
    for y in range(h):
        for x in range(w):
            positions.append([x, y])
    positions = np.array(positions, dtype=np.float32)

    edges = []
    for y in range(h):
        for x in range(w):
            u = idx(x, y)
            if x + 1 < w:
                v = idx(x + 1, y)
                edges.append((u, v))
            if y + 1 < h:
                v = idx(x, y + 1)
                edges.append((u, v))
    return positions, edges


def simulate_sensor_timeseries(positions: np.ndarray, T: int = 40, seed: int = 0):
    """
    Create a toy wave moving across the grid, like a congestion wave.
    Returns:
      values: [T, N]
    """
    rng = np.random.default_rng(seed)
    N = positions.shape[0]
    values = np.zeros((T, N), dtype=np.float32)

    for t in range(T):
        # wave center moves with time
        cx = 0.1 * t
        cy = 0.05 * t
        d2 = (positions[:, 0] - cx) ** 2 + (positions[:, 1] - cy) ** 2
        base = np.exp(-0.4 * d2)  # gaussian bump
        noise = rng.normal(0, 0.03, size=N).astype(np.float32)
        values[t] = base + noise

    # Normalize to 0..1 for nicer plots
    vmin, vmax = values.min(), values.max()
    values = (values - vmin) / (vmax - vmin + 1e-9)
    return values


def build_spatial_edges_from_adjacency(edges_undirected, T: int, N: int, symmetric: bool = True):
    """
    Expand static adjacency into spatial edges for each time t.
    """
    src, dst = [], []
    for t in range(T):
        offset = t * N
        for (u, v) in edges_undirected:
            src.append(offset + u)
            dst.append(offset + v)
            if symmetric:
                src.append(offset + v)
                dst.append(offset + u)
    src = np.array(src, dtype=np.int64)
    dst = np.array(dst, dtype=np.int64)
    etype = np.zeros_like(src, dtype=np.int64)  # 0 = spatial
    return src, dst, etype


def build_temporal_edges(N: int, T: int):
    src, dst = [], []
    for t in range(T - 1):
        for i in range(N):
            src.append(node_id(i, t, N))
            dst.append(node_id(i, t + 1, N))
    src = np.array(src, dtype=np.int64)
    dst = np.array(dst, dtype=np.int64)
    etype = np.ones_like(src, dtype=np.int64)  # 1 = temporal
    return src, dst, etype


def merge_edges(*blocks):
    src = np.concatenate([b[0] for b in blocks])
    dst = np.concatenate([b[1] for b in blocks])
    etype = np.concatenate([b[2] for b in blocks])
    return src, dst, etype


def plot_sensor_graph_snapshot(positions: np.ndarray, edges_undirected, values_t: np.ndarray, t_vis: int):
    plt.figure()
    # draw undirected edges
    for (u, v) in edges_undirected:
        x1, y1 = positions[u]
        x2, y2 = positions[v]
        plt.plot([x1, x2], [y1, y2])

    sc = plt.scatter(positions[:, 0], positions[:, 1], c=values_t)
    plt.title(f"Sensor network snapshot at time t={t_vis} (node color=value)")
    plt.xlabel("x")
    plt.ylabel("y")
    plt.axis("equal")
    plt.colorbar(sc, label="value")
    plt.tight_layout()
    plt.savefig("sensor_graph.png", dpi=160)
    plt.close()


def plot_sensor_heatmap(values: np.ndarray):
    """
    values: [T, N]
    """
    plt.figure()
    plt.imshow(values.T, aspect="auto", origin="lower")
    plt.title("Sensor values over time (heatmap)")
    plt.xlabel("time index")
    plt.ylabel("node index")
    plt.colorbar(label="value")
    plt.tight_layout()
    plt.savefig("sensor_heatmap.png", dpi=160)
    plt.close()


def main():
    # Build a small grid "road/sensor" topology
    pos, edges = make_grid_graph(w=6, h=4)  # 24 sensors
    N = pos.shape[0]
    T = 40

    # Simulated readings over time
    values = simulate_sensor_timeseries(pos, T=T)

    # Build STG edges
    s_src, s_dst, s_type = build_spatial_edges_from_adjacency(edges, T=T, N=N, symmetric=True)
    t_src, t_dst, t_type = build_temporal_edges(N=N, T=T)
    src, dst, etype = merge_edges((s_src, s_dst, s_type), (t_src, t_dst, t_type))

    print("=== Example 2: Sensor/Traffic STG ===")
    print("Nodes:", T * N)
    print("Edges:", len(src))
    print("Spatial edges:", int(np.sum(etype == 0)))
    print("Temporal edges:", int(np.sum(etype == 1)))

    # Visualizations
    t_vis = 20
    plot_sensor_graph_snapshot(pos, edges, values[t_vis], t_vis=t_vis)
    plot_sensor_heatmap(values)


if __name__ == "__main__":
    main()
