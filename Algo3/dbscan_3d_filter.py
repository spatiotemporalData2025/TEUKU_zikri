import open3d as o3d
import numpy as np
import copy

# =========================
# PARAMETERS
# =========================
PCD_FILE = "map.pcd"

USE_DOWNSAMPLE = False      # Set True if you want to voxel downsample
VOXEL_SIZE = 0.05           # Voxel size for downsampling

# DBSCAN parameters
EPS = 0.2                   # Neighborhood radius for DBSCAN (try: 0.02, 0.05, 0.1, etc.)
MIN_POINTS = 40             # Minimum number of points within EPS to form a core point

# PRUNING SMALL CLUSTERS
MIN_CLUSTER_SIZE = 100      # Remove clusters whose size is smaller than this

# WIREFRAME (used for before & after)
RADIUS_NEIGHBOR = 0.1       # Maximum distance for connecting points with a line


# =========================
# FUNCTION: FULL RADIUS-BASED WIREFRAME
# =========================
def build_wireframe_full_radius(pcd_input, radius, name="wire"):
    """
    Build a wireframe by connecting EVERY point to ALL neighbors within a radius.
    - No subsampling
    - No neighbor limit per point
    This can be heavy but creates a dense, nice-looking graph.
    """
    points = np.asarray(pcd_input.points)
    n = points.shape[0]
    print(f"  [{name}] number of points = {n}")

    if n == 0:
        print(f"  [{name}] no points available.")
        return None

    kdtree = o3d.geometry.KDTreeFlann(pcd_input)
    lines = []

    for i in range(n):
        if i % 500 == 0:
            print(f"  [{name}] processing point {i}/{n}")

        # Find all neighbors within the given radius
        k, idxs, dists2 = kdtree.search_radius_vector_3d(points[i], radius)

        if k <= 1:
            # Only itself in the neighborhood
            continue

        # idxs[0] is the point itself; the rest are neighbors
        neighbors = idxs[1:]

        for j in neighbors:
            if j == i:
                continue
            # Use i < j to avoid duplicate edges (i->j and j->i)
            if i < j:
                lines.append([i, j])

    print(f"  [{name}] total lines = {len(lines)}")

    if len(lines) == 0:
        print(f"  [{name}] no lines were created.")
        return None

    line_set = o3d.geometry.LineSet()
    line_set.points = o3d.utility.Vector3dVector(points)
    line_set.lines = o3d.utility.Vector2iVector(np.asarray(lines, dtype=np.int32))

    # Set line color to green
    line_colors = np.tile(np.array([[0.0, 1.0, 0.0]]), (len(lines), 1))
    line_set.colors = o3d.utility.Vector3dVector(line_colors)

    return line_set


# =========================
# 1. LOAD POINT CLOUD
# =========================
pcd = o3d.io.read_point_cloud(PCD_FILE)
points = np.asarray(pcd.points)

print("Number of points (original):", points.shape[0])

if points.shape[0] == 0:
    print("Point cloud is empty. Exiting.")
    raise SystemExit

if USE_DOWNSAMPLE:
    print(f"Applying voxel downsample with voxel_size = {VOXEL_SIZE}")
    pcd = pcd.voxel_down_sample(voxel_size=VOXEL_SIZE)
    points = np.asarray(pcd.points)
    print("Number of points after downsample:", points.shape[0])

# pcd_original = base point cloud used for the 'before' wireframe
pcd_original = copy.deepcopy(pcd)


# =========================
# 2. DBSCAN SEGMENTATION
# =========================
print(f"\nRunning DBSCAN (eps={EPS}, min_points={MIN_POINTS}) ...")
labels = np.array(
    pcd.cluster_dbscan(
        eps=EPS,
        min_points=MIN_POINTS,
        print_progress=True
    )
)

unique_labels = set(labels.tolist())
print("Unique labels:", unique_labels)

if len(unique_labels) == 1 and (-1 in unique_labels):
    print("All points are considered noise by DBSCAN. Try changing EPS / MIN_POINTS.")
    raise SystemExit

num_clusters = max(labels) + 1 if max(labels) >= 0 else 0
num_noise = np.sum(labels == -1)

print("Number of clusters (excluding noise):", num_clusters)
print("Number of noise points:", num_noise)

# Colorized point cloud by cluster
pcd_segmented = copy.deepcopy(pcd)
colors = np.zeros((points.shape[0], 3))

if num_clusters > 0:
    cluster_colors = np.random.rand(num_clusters, 3)
    for c in range(num_clusters):
        colors[labels == c] = cluster_colors[c]

# Noise → black
colors[labels == -1] = [0.0, 0.0, 0.0]
pcd_segmented.colors = o3d.utility.Vector3dVector(colors)

print("\n[1] Showing original point cloud...")
o3d.visualization.draw_geometries(
    [pcd_original],
    window_name="Point Cloud - Original"
)

print("\n[2] Showing DBSCAN segmentation (colored by cluster)...")
o3d.visualization.draw_geometries(
    [pcd_segmented],
    window_name="Point Cloud - DBSCAN Segmentation"
)


# =========================
# 3. PRUNE SMALL CLUSTERS
# =========================
print(f"\n[3] Pruning clusters with size < {MIN_CLUSTER_SIZE} ...")

valid_indices_list = []
for c in range(num_clusters):
    idx = np.where(labels == c)[0]
    cluster_size = idx.size
    print(f"  Cluster {c}: {cluster_size} points")
    if cluster_size >= MIN_CLUSTER_SIZE:
        valid_indices_list.append(idx)

if not valid_indices_list:
    print("No clusters satisfy MIN_CLUSTER_SIZE. Exiting.")
    raise SystemExit

valid_indices = np.concatenate(valid_indices_list)
print("Total points after pruning:", valid_indices.size)

# Point cloud after pruning (using the colored segmented cloud)
pcd_pruned = pcd_segmented.select_by_index(valid_indices)

print("\n[3] Showing point cloud after pruning (no wireframe)...")
o3d.visualization.draw_geometries(
    [pcd_pruned],
    window_name="Point Cloud - After Pruning (No Wire)"
)


# =========================
# 4. FULL WIREFRAME "BEFORE" = FROM ORIGINAL PCD
# =========================
print("\n[4] Building FULL wireframe from ORIGINAL point cloud...")

wire_before = build_wireframe_full_radius(
    pcd_original,
    radius=RADIUS_NEIGHBOR,
    name="before_orig"
)

if wire_before is not None:
    print("\n[4] Showing: FULL wireframe (ORIGINAL point cloud)...")
    o3d.visualization.draw_geometries(
        [wire_before],
        window_name="BEFORE (Original): Full Wireframe Only"
    )
else:
    print("Wireframe BEFORE (original) is empty.")


# =========================
# 5. FULL WIREFRAME "AFTER" = FROM PRUNED POINT CLOUD
# =========================
print("\n[5] Building FULL wireframe AFTER pruning...")

wire_after = build_wireframe_full_radius(
    pcd_pruned,
    radius=RADIUS_NEIGHBOR,
    name="after_pruned"
)

if wire_after is not None:
    print("\n[5] Showing: FULL wireframe (AFTER pruning)...")
    o3d.visualization.draw_geometries(
        [wire_after],
        window_name="AFTER (Pruned): Full Wireframe Only"
    )
else:
    print("Wireframe AFTER (pruned) is empty.")

print("\nDone.")
