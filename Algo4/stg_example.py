from __future__ import annotations
import numpy as np


def node_id(entity_idx: int, time_idx: int, num_entities: int) -> int:
    """Map (entity, time) -> global node index."""
    return time_idx * num_entities + entity_idx


def build_temporal_edges(num_entities: int, num_timesteps: int, bidirectional: bool = False):
    """
    Temporal edges: (i,t) -> (i,t+1)

    Returns:
      src, dst: int arrays shape [E]
      etype:    int arrays shape [E] (1 for temporal)
      eweight:  float arrays shape [E] (all ones)
    """
    src_list = []
    dst_list = []

    for t in range(num_timesteps - 1):
        for i in range(num_entities):
            u = node_id(i, t, num_entities)
            v = node_id(i, t + 1, num_entities)
            src_list.append(u)
            dst_list.append(v)
            if bidirectional:
                src_list.append(v)
                dst_list.append(u)

    src = np.array(src_list, dtype=np.int64)
    dst = np.array(dst_list, dtype=np.int64)
    etype = np.ones_like(src, dtype=np.int64)  # 1 = temporal
    eweight = np.ones_like(src, dtype=np.float32)
    return src, dst, etype, eweight


def build_spatial_edges_knn(
    positions: np.ndarray,
    k: int = 2,
    self_loops: bool = False,
    symmetric: bool = True,
    weight_mode: str = "inverse",
):
    """
    Build spatial edges per time step using kNN.

    positions: shape [T, N, D] (D=2 or 3 typically)
    k: neighbors per node (excluding itself unless self_loops=True)
    symmetric: if True, add both directions u->v and v->u
    weight_mode: "inverse" | "gaussian" | "ones"

    Returns:
      src, dst: int arrays
      etype:    int arrays (0 for spatial)
      eweight:  float arrays
    """
    T, N, D = positions.shape
    src_list = []
    dst_list = []
    w_list = []

    eps = 1e-9
    sigma = 1.0  # for gaussian weights

    for t in range(T):
        X = positions[t]  # [N, D]

        # Pairwise squared distances: dist2[i,j] = ||X[i]-X[j]||^2
        diff = X[:, None, :] - X[None, :, :]
        dist2 = np.sum(diff * diff, axis=-1)

        for i in range(N):
            idx = np.argsort(dist2[i])  # nearest first
            if not self_loops:
                idx = idx[idx != i]

            nbrs = idx[:k]
            u = node_id(i, t, N)

            for j in nbrs:
                v = node_id(int(j), t, N)
                d = float(np.sqrt(dist2[i, j] + eps))

                if weight_mode == "inverse":
                    w = 1.0 / (d + 1e-6)
                elif weight_mode == "gaussian":
                    w = float(np.exp(-(d * d) / (2.0 * sigma * sigma)))
                else:
                    w = 1.0

                src_list.append(u)
                dst_list.append(v)
                w_list.append(w)

                if symmetric:
                    src_list.append(v)
                    dst_list.append(u)
                    w_list.append(w)

    src = np.array(src_list, dtype=np.int64)
    dst = np.array(dst_list, dtype=np.int64)
    etype = np.zeros_like(src, dtype=np.int64)  # 0 = spatial
    eweight = np.array(w_list, dtype=np.float32)
    return src, dst, etype, eweight


def build_node_features(positions: np.ndarray, add_time_feature: bool = True) -> np.ndarray:
    """
    Node features for expanded STG:
      features[(i,t)] = [pos..., t_norm(optional)]

    positions: [T, N, D]
    returns:   [T*N, D(+1)]
    """
    T, N, D = positions.shape
    feats = positions.reshape(T * N, D).astype(np.float32)

    if add_time_feature:
        t_idx = np.repeat(np.arange(T, dtype=np.float32), N)  # [T*N]
        t_norm = (t_idx / max(T - 1, 1)).reshape(-1, 1)
        feats = np.concatenate([feats, t_norm], axis=1)

    return feats


def merge_edges(*edge_blocks):
    """
    Merge multiple edge blocks: each block is (src, dst, etype, eweight)
    Returns merged arrays.
    """
    src = np.concatenate([b[0] for b in edge_blocks], axis=0)
    dst = np.concatenate([b[1] for b in edge_blocks], axis=0)
    etype = np.concatenate([b[2] for b in edge_blocks], axis=0)
    eweight = np.concatenate([b[3] for b in edge_blocks], axis=0)
    return src, dst, etype, eweight


def summary(num_nodes: int, src: np.ndarray, dst: np.ndarray, etype: np.ndarray):
    num_edges = src.shape[0]
    spatial = int(np.sum(etype == 0))
    temporal = int(np.sum(etype == 1))
    print("=== STG Summary ===")
    print(f"Nodes      : {num_nodes}")
    print(f"Edges      : {num_edges}")
    print(f"  spatial  : {spatial}")
    print(f"  temporal : {temporal}")
    print("Edge sample (first 10):")
    for i in range(min(10, num_edges)):
        print(f"  {src[i]} -> {dst[i]}   type={etype[i]}")


def generate_synthetic_trajectories(T: int = 20, N: int = 4, noise: float = 0.02, seed: int = 0):
    """
    Generate simple synthetic 2D trajectories.
    Returns positions [T, N, 2]
    """
    rng = np.random.default_rng(seed)
    t = np.linspace(0, 2 * np.pi, T, dtype=np.float32)

    positions = np.zeros((T, N, 2), dtype=np.float32)
    phases = np.linspace(0, np.pi, N, dtype=np.float32)

    for i in range(N):
        x = np.cos(t + phases[i]) * (1.0 + 0.2 * i)
        y = np.sin(t * (1.0 + 0.1 * i) + phases[i]) * (1.0 + 0.1 * i)
        traj = np.stack([x, y], axis=1)
        traj += rng.normal(0, noise, size=traj.shape).astype(np.float32)
        positions[:, i, :] = traj

    return positions


def main():
    # 1) Data: positions[t, i] = [x, y]
    positions = generate_synthetic_trajectories(T=15, N=5)

    T, N, D = positions.shape
    num_nodes = T * N

    # 2) Node features
    X = build_node_features(positions, add_time_feature=True)  # [T*N, D+1]

    # 3) Spatial edges (kNN per time)
    s_src, s_dst, s_type, s_w = build_spatial_edges_knn(
        positions, k=2, symmetric=True, weight_mode="inverse"
    )

    # 4) Temporal edges
    t_src, t_dst, t_type, t_w = build_temporal_edges(N, T, bidirectional=False)

    # 5) Merge
    src, dst, etype, eweight = merge_edges(
        (s_src, s_dst, s_type, s_w),
        (t_src, t_dst, t_type, t_w),
    )

    # 6) Print summary
    summary(num_nodes, src, dst, etype)
    print("\nNode feature shape:", X.shape)
    print("Edge arrays shape  :", src.shape, dst.shape, etype.shape, eweight.shape)

    # Common GNN format: edge_index [2, E]
    edge_index = np.stack([src, dst], axis=0)
    print("edge_index shape   :", edge_index.shape)


if __name__ == "__main__":
    main()
