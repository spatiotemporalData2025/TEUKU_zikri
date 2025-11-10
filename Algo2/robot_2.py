import pygame
import math
import random
import sys
from dataclasses import dataclass
from typing import List, Any, Tuple, Optional

# ===================== R-TREE 2D (X-Z) =====================

@dataclass
class Rect:
    xmin: float
    ymin: float
    xmax: float
    ymax: float

    def area(self) -> float:
        return max(0.0, self.xmax - self.xmin) * max(0.0, self.ymax - self.ymin)

    def union(self, other: "Rect") -> "Rect":
        return Rect(
            xmin=min(self.xmin, other.xmin),
            ymin=min(self.ymin, other.ymin),
            xmax=max(self.xmax, other.xmax),
            ymax=max(self.ymax, other.ymax),
        )

    def enlarge_area_needed(self, other: "Rect") -> float:
        new_rect = self.union(other)
        return new_rect.area() - self.area()

    def intersects(self, other: "Rect") -> bool:
        return not (
            self.xmax < other.xmin or self.xmin > other.xmax or
            self.ymax < other.ymin or self.ymin > other.ymax
        )


class RTreeNode:
    def __init__(self, leaf: bool = True, parent: "RTreeNode" = None):
        self.leaf = leaf
        self.entries: List[Tuple[Rect, Any]] = []
        self.parent: Optional["RTreeNode"] = parent

    def mbr(self) -> Optional[Rect]:
        if not self.entries:
            return None
        r = self.entries[0][0]
        for rect, _ in self.entries[1:]:
            r = r.union(rect)
        return r


class RTree:
    """R-tree sederhana:
       - index obstacle dengan MBR di XZ
       - dipakai untuk target aman + obstacle pruning
    """

    def __init__(self, max_entries: int = 8, min_entries: int = 4):
        assert 1 < min_entries <= max_entries // 2
        self.M = max_entries
        self.m = min_entries
        self.root = RTreeNode(leaf=True)

    def insert(self, rect: Rect, obj: Any):
        leaf = self._choose_leaf(self.root, rect)
        leaf.entries.append((rect, obj))
        self._adjust_tree(leaf)

    def search_range(self, query: Rect) -> List[Any]:
        res: List[Any] = []
        self._search_node(self.root, query, res)
        return res

    # ---------- internal ----------

    def _choose_leaf(self, node: RTreeNode, rect: Rect) -> RTreeNode:
        if node.leaf:
            return node

        best_entry = None
        best_inc = None
        best_area = None

        for r, child in node.entries:
            inc = r.enlarge_area_needed(rect)
            area = r.area()
            if (best_inc is None or
                inc < best_inc or
                (inc == best_inc and area < best_area)):
                best_inc = inc
                best_area = area
                best_entry = (r, child)

        _, child = best_entry
        return self._choose_leaf(child, rect)

    def _adjust_tree(self, node: RTreeNode):
        while True:
            if len(node.entries) > self.M:
                node, new_node = self._split_node(node)

                if node.parent is None:
                    new_root = RTreeNode(leaf=False)
                    node.parent = new_root
                    new_node.parent = new_root
                    new_root.entries = [
                        (node.mbr(), node),
                        (new_node.mbr(), new_node),
                    ]
                    self.root = new_root
                    return
                else:
                    parent = node.parent
                    for i, (r, ch) in enumerate(parent.entries):
                        if ch is node:
                            parent.entries[i] = (node.mbr(), node)
                            break
                    parent.entries.append((new_node.mbr(), new_node))
                    node = parent
                    continue
            else:
                parent = node.parent
                while parent is not None:
                    for i, (r, ch) in enumerate(parent.entries):
                        if ch is node:
                            parent.entries[i] = (node.mbr(), node)
                            break
                    node = parent
                    parent = node.parent
                return

    def _split_node(self, node: RTreeNode):
        entries = list(node.entries)
        s1, s2 = self._pick_seeds(entries)

        node1 = node
        node1.entries = [entries[s1]]
        node2 = RTreeNode(leaf=node.leaf, parent=node.parent)
        node2.entries = [entries[s2]]

        used = {s1, s2}
        n = len(entries)

        for i in range(n):
            if i in used:
                continue

            rect, obj = entries[i]
            remaining = n - len(used)

            if len(node1.entries) + remaining == self.m:
                node1.entries.append((rect, obj))
                used.add(i)
                continue
            if len(node2.entries) + remaining == self.m:
                node2.entries.append((rect, obj))
                used.add(i)
                continue

            m1 = node1.mbr()
            m2 = node2.mbr()
            inc1 = m1.enlarge_area_needed(rect)
            inc2 = m2.enlarge_area_needed(rect)

            if inc1 < inc2:
                node1.entries.append((rect, obj))
            elif inc2 < inc1:
                node2.entries.append((rect, obj))
            else:
                if m1.area() < m2.area():
                    node1.entries.append((rect, obj))
                else:
                    node2.entries.append((rect, obj))
            used.add(i)

        if not node1.leaf:
            for _, ch in node1.entries:
                ch.parent = node1
        if not node2.leaf:
            for _, ch in node2.entries:
                ch.parent = node2

        return node1, node2

    def _pick_seeds(self, entries: List[Tuple[Rect, Any]]):
        max_d = -1.0
        s1, s2 = 0, 1
        n = len(entries)
        for i in range(n):
            for j in range(i + 1, n):
                r1 = entries[i][0]
                r2 = entries[j][0]
                u = r1.union(r2)
                d = u.area() - r1.area() - r2.area()
                if d > max_d:
                    max_d = d
                    s1, s2 = i, j
        return s1, s2

    def _search_node(self, node: RTreeNode, query: Rect, res: List[Any]):
        for rect, child in node.entries:
            if rect.intersects(query):
                if node.leaf:
                    res.append(child)
                else:
                    self._search_node(child, query, res)

# ========= CONFIG =========
WIDTH, HEIGHT = 600, 600
BG_COLOR = (10, 10, 15)

FOV = 500
VIEWER_DISTANCE = 150
FLOOR_SIZE = 180
ROT_SPEED = 1.8

COLOR_FLOOR = (255, 255, 255)
COLOR_BOX_FACE = (255, 0, 0)
COLOR_BOX_EDGE = (150, 0, 0)
COLOR_ROBOT = (0, 0, 255)
COLOR_ROBOT_EDGE = (0, 0, 80)
COLOR_TARGET = (0, 255, 0)

ROBOT_RADIUS = 4.0
ROBOT_HEIGHT = 3.0
ROBOT_SPEED = 12.0
AVOID_STRENGTH = 80.0
HIT_THRESHOLD = 5

JUMP_DURATION = 1.0
JUMP_HEIGHT = 15.0

BOUNCE_MULTIPLIER = 1.3  # efek mantul

BOX_FACES = [
    (0, 1, 5, 4),
    (3, 2, 6, 7),
    (4, 5, 6, 7),
    (0, 1, 2, 3),
    (0, 3, 7, 4),
    (1, 2, 6, 5),
]

def get_box_vertices(cx, cy, cz, sx, sy, sz):
    x0, x1 = cx - sx / 2, cx + sx / 2
    y0, y1 = cy - sy / 2, cy + sy / 2
    z0, z1 = cz - sz / 2, cz + sz / 2
    return [
        (x0, y0, z0),
        (x1, y0, z0),
        (x1, y1, z0),
        (x0, y1, z0),
        (x0, y0, z1),
        (x1, y0, z1),
        (x1, y1, z1),
        (x0, y1, z1),
    ]

def rotate_point(x, y, z, angle_x, angle_y):
    cosx = math.cos(angle_x)
    sinx = math.sin(angle_x)
    y2 = y * cosx - z * sinx
    z2 = y * sinx + z * cosx

    cosy = math.cos(angle_y)
    siny = math.sin(angle_y)
    x3 = x * cosy + z2 * siny
    z3 = -x * siny + z2 * cosy

    return x3, y2, z3

def project_point(x, y, z, fov, viewer_distance):
    z += viewer_distance
    if z <= 0.1:
        z = 0.1
    factor = fov / z
    px = x * factor + WIDTH / 2
    py = -y * factor + HEIGHT / 2
    return int(px), int(py)

def should_hide_edges(angle_x, angle_y):
    deg_x = math.degrees(angle_x)
    deg_y = math.degrees(angle_y)
    return abs(abs(deg_x) - 90.0) < 0.5 and abs(deg_y) < 0.5

# ========= OBSTACLES =========
num_obstacles = 50
obstacles = []

sx = 11.5
sz = 11.5
sy = 4.0

half_floor = FLOOR_SIZE / 2.0
half_box_xz = max(sx, sz) / 2.0

min_pos = -half_floor + half_box_xz
max_pos =  half_floor - half_box_xz

for _ in range(num_obstacles):
    cx = random.uniform(min_pos, max_pos)
    cz = random.uniform(min_pos, max_pos)
    cy = sy / 2.0
    obstacles.append((cx, cy, cz, sx, sy, sz))

# ========= R-TREE INDEX =========
obstacle_index = RTree(max_entries=8, min_entries=4)
for i, (cx, cy, cz, sx, sy, sz) in enumerate(obstacles):
    halfx = sx / 2.0
    halfz = sz / 2.0
    rect = Rect(cx - halfx, cz - halfz, cx + halfx, cz + halfz)
    obstacle_index.insert(rect, i)

# ========= HELPERS =========
def random_pos_on_floor(margin=20.0):
    return (
        random.uniform(-half_floor + margin, half_floor - margin),
        random.uniform(-half_floor + margin, half_floor - margin),
    )

def position_collides_obstacles(x, z, radius) -> bool:
    """Cek lingkaran (x,z,radius) vs obstacle pakai R-tree."""
    query = Rect(x - radius, z - radius, x + radius, z + radius)
    candidates = obstacle_index.search_range(query)
    for idx in candidates:
        cx, cy, cz, sx, sy, sz = obstacles[idx]
        halfx = sx / 2.0
        halfz = sz / 2.0
        closest_x = max(cx - halfx, min(x, cx + halfx))
        closest_z = max(cz - halfz, min(z, cz + halfz))
        dx = x - closest_x
        dz = z - closest_z
        if dx * dx + dz * dz < radius * radius:
            return True
    return False

def choose_target_not_touching():
    """Pilih target baru yang tidak menyinggung obstacle (pakai R-tree)."""
    for _ in range(1000):
        x, z = random_pos_on_floor(20.0)
        if not position_collides_obstacles(x, z, ROBOT_RADIUS + 2.0):
            return [x, z]
    return [0.0, 0.0]

def find_nearest_obstacle_idx():
    """Cari obstacle terdekat dari robot (pakai R-tree untuk pruning)."""
    rx, rz = robot_pos
    sense = 60.0
    query = Rect(rx - sense, rz - sense, rx + sense, rz + sense)
    candidates = obstacle_index.search_range(query)

    if not candidates:
        # fallback: cek semua
        candidates = list(range(len(obstacles)))

    best_idx = None
    best_d = None
    for idx in candidates:
        cx, cy, cz, sx, sy, sz = obstacles[idx]
        d = math.hypot(rx - cx, rz - cz)
        if best_d is None or d < best_d:
            best_d = d
            best_idx = idx
    return best_idx

# ========= ROBOT & TARGET STATE =========
robot_pos = [-half_floor + 20.0, -half_floor + 20.0]
if position_collides_obstacles(robot_pos[0], robot_pos[1], ROBOT_RADIUS + 2.0):
    robot_pos = choose_target_not_touching()

target_pos = choose_target_not_touching()

collision_counts = [0] * num_obstacles
collision_active = [False] * num_obstacles

jump_active = False
jump_t = 0.0
jump_start = [0.0, 0.0]
jump_end = [0.0, 0.0]
jump_y_offset = 0.0

robot_vel = [0.0, 0.0]

# tracking stuck
idle_time = 0.0

# ========= JUMP =========
def start_jump_over_obstacle(idx):
    global jump_active, jump_t, jump_start, jump_end

    if idx is None:
        return

    cx, cy, cz, sx, sy, sz = obstacles[idx]
    rx, rz = robot_pos
    tx, tz = target_pos

    dx = tx - rx
    dz = tz - rz
    dist = math.hypot(dx, dz)

    if dist < 1e-6:
        dx = rx - cx
        dz = rz - cz
        dist = math.hypot(dx, dz)
        if dist < 1e-6:
            dx, dz = 1.0, 0.0

    dx /= dist
    dz /= dist

    margin = ROBOT_RADIUS + 1.0
    half_len = max(sx, sz) / 2.0
    jump_dist = half_len + margin

    new_x = cx + dx * jump_dist
    new_z = cz + dz * jump_dist

    new_x = max(-half_floor + ROBOT_RADIUS, min(half_floor - ROBOT_RADIUS, new_x))
    new_z = max(-half_floor + ROBOT_RADIUS, min(half_floor - ROBOT_RADIUS, new_z))

    jump_start = [rx, rz]
    jump_end = [new_x, new_z]
    jump_active = True
    jump_t = 0.0

    collision_counts[idx] = 0
    collision_active[idx] = False

def update_jump(dt):
    global jump_active, jump_t, jump_y_offset

    if not jump_active:
        jump_y_offset = 0.0
        return

    jump_t += dt
    t = jump_t / JUMP_DURATION

    if t >= 1.0:
        robot_pos[0], robot_pos[1] = jump_end
        jump_active = False
        jump_y_offset = 0.0
    else:
        robot_pos[0] = (1 - t) * jump_start[0] + t * jump_end[0]
        robot_pos[1] = (1 - t) * jump_start[1] + t * jump_end[1]
        jump_y_offset = 4 * JUMP_HEIGHT * t * (1 - t)

# ========= AVOID (R-TREE, RADIUS + BOUNCE) =========
def avoid_obstacles(robot_pos, dt):
    global jump_active, robot_vel

    if jump_active:
        return

    rx, rz = robot_pos
    r = ROBOT_RADIUS

    sense_radius = 30.0
    avoid_radius = 18.0

    query = Rect(rx - sense_radius, rz - sense_radius,
                 rx + sense_radius, rz + sense_radius)
    candidate_ids = obstacle_index.search_range(query)

    for idx in candidate_ids:
        cx, cy, cz, sx, sy, sz = obstacles[idx]
        halfx = sx / 2.0
        halfz = sz / 2.0

        closest_x = max(cx - halfx, min(rx, cx + halfx))
        closest_z = max(cz - halfz, min(rz, cz + halfz))

        dx = rx - closest_x
        dz = rz - closest_z
        dist_sq = dx * dx + dz * dz

        if dist_sq == 0.0:
            dx = rx - cx
            dz = rz - cz
            dist_sq = dx * dx + dz * dz
        if dist_sq == 0.0:
            dx, dz = 1.0, 0.0
            dist_sq = 1.0

        dist = math.sqrt(dist_sq)
        nx = dx / dist
        nz = dz / dist

        # --- tabrakan keras: no tembus + bounce ---
        if dist < r:
            if not collision_active[idx]:
                collision_counts[idx] += 1
            collision_active[idx] = True

            if collision_counts[idx] >= HIT_THRESHOLD:
                start_jump_over_obstacle(idx)
                return

            overlap = r - dist
            rx += nx * (overlap + 0.3)
            rz += nz * (overlap + 0.3)

            # refleksi velocity kalau lagi menuju obstacle
            dot = robot_vel[0] * nx + robot_vel[1] * nz
            if dot < 0:
                robot_vel[0] -= 2 * dot * nx * BOUNCE_MULTIPLIER
                robot_vel[1] -= 2 * dot * nz * BOUNCE_MULTIPLIER

        else:
            collision_active[idx] = False

            # --- dekat: repulsive halus ---
            if dist < avoid_radius:
                strength = (avoid_radius - dist) / avoid_radius
                push = (AVOID_STRENGTH * strength * dt) / 30.0
                rx += nx * push
                rz += nz * push

    rx = max(-half_floor + r, min(half_floor - r, rx))
    rz = max(-half_floor + r, min(half_floor - r, rz))
    robot_pos[0], robot_pos[1] = rx, rz

# ========= MOVE TO TARGET + RESPAWN =========
def move_towards_target(dt):
    """
    Gerak ke target.
    Jika sampai → spawn target baru aman.
    Simpan velocity buat efek bounce.
    """
    global robot_vel, target_pos

    if jump_active:
        return

    rx, rz = robot_pos
    tx, tz = target_pos

    dx = tx - rx
    dz = tz - rz
    dist = math.hypot(dx, dz)

    reach_eps = 1.5

    if dist < reach_eps:
        robot_pos[0], robot_pos[1] = tx, tz
        target_pos = choose_target_not_touching()
        robot_vel = [0.0, 0.0]
        return

    step = ROBOT_SPEED * dt

    if step >= dist:
        move_x = dx
        move_z = dz
        robot_pos[0], robot_pos[1] = tx, tz
        target_pos = choose_target_not_touching()
    else:
        nx = dx / dist
        nz = dz / dist
        move_x = nx * step
        move_z = nz * step
        robot_pos[0] += move_x
        robot_pos[1] += move_z

    if dt > 0:
        robot_vel[0] = move_x / dt
        robot_vel[1] = move_z / dt

# ========= DRAW =========
def draw_floor(screen, angle_x, angle_y):
    corners_world = [
        (-half_floor, 0, -half_floor),
        ( half_floor, 0, -half_floor),
        ( half_floor, 0,  half_floor),
        (-half_floor, 0,  half_floor),
    ]
    pts = []
    for x, y, z in corners_world:
        rx, ry, rz = rotate_point(x, y, z, angle_x, angle_y)
        px, py = project_point(rx, ry, rz, FOV, VIEWER_DISTANCE)
        pts.append((px, py))
    pygame.draw.polygon(screen, COLOR_FLOOR, pts)

def draw_box(screen, box_params, angle_x, angle_y, face_color, edge_color):
    cx, cy, cz, sx, sy, sz = box_params
    vertices = get_box_vertices(cx, cy, cz, sx, sy, sz)
    rotated = [rotate_point(x, y, z, angle_x, angle_y) for (x, y, z) in vertices]

    faces = []
    for face in BOX_FACES:
        pts2d = []
        avg_z = 0.0
        for idx in face:
            rx, ry, rz = rotated[idx]
            px, py = project_point(rx, ry, rz, FOV, VIEWER_DISTANCE)
            pts2d.append((px, py))
            avg_z += rz
        avg_z /= len(face)
        faces.append((avg_z, pts2d))

    faces.sort(key=lambda f: f[0], reverse=True)
    hide_edges = should_hide_edges(angle_x, angle_y)

    for _, pts in faces:
        pygame.draw.polygon(screen, face_color, pts)
        if not hide_edges and edge_color is not None:
            pygame.draw.polygon(screen, edge_color, pts, 1)

def draw_robot(screen, angle_x, angle_y):
    rx, rz = robot_pos
    sx = sz = ROBOT_RADIUS * 2.0
    sy_box = ROBOT_HEIGHT
    cy = sy_box / 2.0 + jump_y_offset
    draw_box(screen, (rx, cy, rz, sx, sy_box, sz),
             angle_x, angle_y, COLOR_ROBOT, COLOR_ROBOT_EDGE)

def draw_target(screen, angle_x, angle_y):
    tx, tz = target_pos
    rx, ry, rz = rotate_point(tx, 0.1, tz, angle_x, angle_y)
    px, py = project_point(rx, ry, rz, FOV, VIEWER_DISTANCE)
    pygame.draw.circle(screen, COLOR_TARGET, (px, py), 6)

# ========= MAIN LOOP =========
def main():
    global idle_time

    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("3D Robot + R-tree: Auto Target, Bounce, Jump-if-Stuck")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("consolas", 14)

    angle_x = -math.radians(90)
    angle_y = 0.0

    running = True
    while running:
        dt = clock.tick(60) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE]:
            running = False
        if keys[pygame.K_UP]:
            angle_x -= ROT_SPEED * dt
        if keys[pygame.K_DOWN]:
            angle_x += ROT_SPEED * dt
        if keys[pygame.K_LEFT]:
            angle_y -= ROT_SPEED * dt
        if keys[pygame.K_RIGHT]:
            angle_y += ROT_SPEED * dt

        max_pitch = math.radians(90)
        angle_x = max(-max_pitch, min(max_pitch, angle_x))

        # simpan posisi sebelum update untuk cek diam
        prev_rx, prev_rz = robot_pos[0], robot_pos[1]

        # update perilaku
        move_towards_target(dt)
        avoid_obstacles(robot_pos, dt)
        update_jump(dt)

        # cek apakah robot stuck (diam) > 1 detik
        if not jump_active:
            moved = math.hypot(robot_pos[0] - prev_rx, robot_pos[1] - prev_rz)
            if moved < 0.05:      # threshold diam (bisa kamu tweak)
                idle_time += dt
            else:
                idle_time = 0.0

            if idle_time > 1.0:   # kalau diam > 1 detik → lompat
                idx = find_nearest_obstacle_idx()
                start_jump_over_obstacle(idx)
                idle_time = 0.0

        # render
        screen.fill(BG_COLOR)
        draw_floor(screen, angle_x, angle_y)

        for obs in obstacles:
            draw_box(screen, obs, angle_x, angle_y,
                     COLOR_BOX_FACE, COLOR_BOX_EDGE)

        draw_robot(screen, angle_x, angle_y)
        draw_target(screen, angle_x, angle_y)

        msg = (
            "Arrow: rotate | ESC: quit | "
            "Target auto-respawn (R-tree safe) | "
            "Avoid: R-tree radius + bounce | "
            "Stuck >1s: auto jump"
        )
        text = font.render(msg, True, (230, 230, 230))
        screen.blit(text, (10, 10))

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
