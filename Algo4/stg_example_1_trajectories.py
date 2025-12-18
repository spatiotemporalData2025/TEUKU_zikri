import numpy as np
import matplotlib.pyplot as plt


def node_id(i: int, t: int, n_entities: int) -> int:
    """Map (entity i, time t) -> global node index."""
    return t * n_entities + i


def build_temporal_edges(n_entities: int, T: int):
    """Temporal edges: (i,t) -> (i,t+1)."""
    src, dst = [], []
    for t in range(T - 1):
        for i in range(n_entities):
            src.append(node_id(i, t, n_entities))
            dst.append(node_id(i, t + 1, n_entities))
    src = np.array(src, dtype=np.int64)
    dst = np.array(dst, dtype=np.int64)
    etype = np.ones_like(src, dtype=np.int64)  # 1 = temporal
    return src, dst, etype


def build_spatial_edges_knn(positions: np.ndarray, k: int = 2, symmetric: bool = True):
    """
    Spatial edges per time via kNN.
    positions: [T, N, 2]
    """
    T, N, D = positions.shape
    src, dst = [], []

    for t in range(T):
        X = positions[t]  # [N,2]
        diff = X[:, None, :] - X[None, :, :]
        dist2 = np.sum(diff * diff, axis=-1)  # [N,N]

        for i in range(N):
            order = np.argsort(dist2[i])
            order = order[order != i]  # remove self
            nbrs = order[:k]
            u = node_id(i, t, N)
            for j in nbrs:
                v = node_id(int(j), t, N)
                src.append(u)
                dst.append(v)
                if symmetric:
                    src.append(v)
                    dst.append(u)

    src = np.array(src, dtype=np.int64)
    dst = np.array(dst, dtype=np.int64)
    etype = np.zeros_like(src, dtype=np.int64)  # 0 = spatial
    return src, dst, etype


def merge_edges(*blocks):
    src = np.concatenate([b[0] for b in blocks])
    dst = np.concatenate([b[1] for b in blocks])
    etype = np.concatenate([b[2] for b in blocks])
    return src, dst, etype


def generate_trajectories(T: int = 25, N: int = 6, noise: float = 0.02, seed: int = 0):
    """Synthetic smooth trajectories: positions[t,i] = [x,y]."""
    rng = np.random.default_rng(seed)
    t = np.linspace(0, 2 * np.pi, T).astype(np.float32)
    phases = np.linspace(0, np.pi, N).astype(np.float32)

    pos = np.zeros((T, N, 2), dtype=np.float32)
    for i in range(N):
        x = np.cos(t + phases[i]) * (1.0 + 0.15 * i)
        y = np.sin(t * (1.0 + 0.08 * i) + phases[i]) * (1.0 + 0.10 * i)
        traj = np.stack([x, y], axis=1)
        traj += rng.normal(0, noise, size=traj.shape).astype(np.float32)
        pos[:, i, :] = traj
    return pos


def plot_spatial_snapshot(positions: np.ndarray, spatial_src: np.ndarray, spatial_dst: np.ndarray, t_vis: int):
    """Plot positions at time t_vis with spatial edges drawn."""
    T, N, _ = positions.shape
    X = positions[t_vis]

    plt.figure()
    plt.scatter(X[:, 0], X[:, 1])
    for i in range(N):
        plt.text(X[i, 0], X[i, 1], f"{i}")

    # Draw only edges belonging to this timestep
    # spatial edges use nodes with IDs in [t*N, (t+1)*N)
    lo = t_vis * N
    hi = (t_vis + 1) * N
    mask = (spatial_src >= lo) & (spatial_src < hi) & (spatial_dst >= lo) & (spatial_dst < hi)

    for u, v in zip(spatial_src[mask], spatial_dst[mask]):
        iu = u - lo
        iv = v - lo
        plt.plot([X[iu, 0], X[iv, 0]], [X[iu, 1], X[iv, 1]])

    plt.title(f"Trajectory STG: Spatial edges (kNN) at time t={t_vis}")
    plt.xlabel("x")
    plt.ylabel("y")
    plt.axis("equal")
    plt.tight_layout()
    plt.savefig("traj_stg_timestep.png", dpi=160)
    plt.close()


def plot_3d_trajectories(positions: np.ndarray):
    """3D plot: x-y-time curves (shows temporal structure visually)."""
    from mpl_toolkits.mplot3d import Axes3D  # noqa: F401

    T, N, _ = positions.shape
    fig = plt.figure()
    ax = fig.add_subplot(111, projection="3d")

    for i in range(N):
        xs = positions[:, i, 0]
        ys = positions[:, i, 1]
        ts = np.arange(T)
        ax.plot(xs, ys, ts)

    ax.set_title("Trajectory STG: x-y-time paths (temporal structure)")
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_zlabel("time index")
    plt.tight_layout()
    plt.savefig("traj_stg_3d.png", dpi=160)
    plt.close()


def main():
    positions = generate_trajectories(T=25, N=6)
    T, N, _ = positions.shape

    # Build STG
    s_src, s_dst, s_type = build_spatial_edges_knn(positions, k=2, symmetric=True)
    t_src, t_dst, t_type = build_temporal_edges(N, T)
    src, dst, etype = merge_edges((s_src, s_dst, s_type), (t_src, t_dst, t_type))

    print("=== Example 1: Trajectory STG ===")
    print("Nodes:", T * N)
    print("Edges:", len(src))
    print("Spatial edges:", int(np.sum(etype == 0)))
    print("Temporal edges:", int(np.sum(etype == 1)))

    # Visualizations
    plot_spatial_snapshot(positions, s_src, s_dst, t_vis=T // 2)
    plot_3d_trajectories(positions)


if __name__ == "__main__":
    main()
