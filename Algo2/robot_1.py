import pygame
import math
import random
import sys

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

half_floor = FLOOR_SIZE / 2.0

# ========= GEOMETRI BOX =========
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

# ========= OBSTACLES (TANPA R-TREE) =========
num_obstacles = 50
obstacles = []

sx = 11.5
sz = 11.5
sy = 4.0

half_box_xz = max(sx, sz) / 2.0
min_pos = -half_floor + half_box_xz
max_pos =  half_floor - half_box_xz

for _ in range(num_obstacles):
    cx = random.uniform(min_pos, max_pos)
    cz = random.uniform(min_pos, max_pos)
    cy = sy / 2.0
    # tidak dicek overlap, pure random
    obstacles.append((cx, cy, cz, sx, sy, sz))

# ========= HELPERS (NAIVE, TANPA R-TREE) =========
def random_pos_on_floor(margin=20.0):
    return (
        random.uniform(-half_floor + margin, half_floor - margin),
        random.uniform(-half_floor + margin, half_floor - margin),
    )

def position_collides_obstacles(x, z, radius) -> bool:
    """Cek lingkaran (x,z,radius) vs semua obstacle (loop biasa)."""
    for (cx, cy, cz, sx, sy, sz) in obstacles:
        halfx = sx / 2.0
        halfz = sz / 2.0
        closest_x = max(cx - halfx, min(x, cx + halfx))
        closest_z = max(cz - halfz, min(z, cz + halfz))
        dx = x - closest_x
        dz = z - closest_z
        if dx * dx + dz * dz < radius * radius:
            return True
    return False

def choose_target_no_check():
    """Target random tanpa cek terhadap obstacle (benar-benar no R-tree)."""
    x, z = random_pos_on_floor(20.0)
    return [x, z]

def find_nearest_obstacle_idx():
    """Cari obstacle terdekat dari robot (loop semua, no index)."""
    if not obstacles:
        return None
    rx, rz = robot_pos
    best_idx = 0
    best_d = None
    for i, (cx, cy, cz, sx, sy, sz) in enumerate(obstacles):
        d = math.hypot(rx - cx, rz - cz)
        if best_d is None or d < best_d:
            best_d = d
            best_idx = i
    return best_idx

# ========= ROBOT & TARGET STATE =========
robot_pos = [-half_floor + 20.0, -half_floor + 20.0]

# kalau kebetulan spawn di dalam obstacle, biarkan saja (tanpa R-tree) → contoh buruk
target_pos = choose_target_no_check()

collision_counts = [0] * len(obstacles)
collision_active = [False] * len(obstacles)

jump_active = False
jump_t = 0.0
jump_start = [0.0, 0.0]
jump_end = [0.0, 0.0]
jump_y_offset = 0.0

robot_vel = [0.0, 0.0]
idle_time = 0.0  # deteksi diam > 1s

# ========= JUMP =========
def start_jump_over_obstacle(idx):
    global jump_active, jump_t, jump_start, jump_end

    if idx is None or idx < 0 or idx >= len(obstacles):
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

    margin_jump = ROBOT_RADIUS + 1.0
    half_len = max(sx, sz) / 2.0
    jump_dist = half_len + margin_jump

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

# ========= AVOID (NAIVE, TANPA R-TREE) =========
def avoid_obstacles(robot_pos, dt):
    global jump_active, robot_vel

    if jump_active or not obstacles:
        return

    rx, rz = robot_pos
    r = ROBOT_RADIUS

    sense_radius = 30.0
    avoid_radius = 18.0

    for idx, (cx, cy, cz, sx, sy, sz) in enumerate(obstacles):
        halfx = sx / 2.0
        halfz = sz / 2.0

        # skip kalau jauh di luar sense_radius (cek cepat)
        if abs(rx - cx) > sense_radius + halfx or abs(rz - cz) > sense_radius + halfz:
            continue

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

        # tabrakan: resolve + bounce
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

            dot = robot_vel[0] * nx + robot_vel[1] * nz
            if dot < 0:
                robot_vel[0] -= 2 * dot * nx * BOUNCE_MULTIPLIER
                robot_vel[1] -= 2 * dot * nz * BOUNCE_MULTIPLIER

        else:
            collision_active[idx] = False

            # dekat: repulsive halus
            if dist < avoid_radius:
                strength = (avoid_radius - dist) / avoid_radius
                push = (AVOID_STRENGTH * strength * dt) / 30.0
                rx += nx * push
                rz += nz * push

    rx = max(-half_floor + r, min(half_floor - r, rx))
    rz = max(-half_floor + r, min(half_floor - r, rz))
    robot_pos[0], robot_pos[1] = rx, rz

# ========= MOVE TO TARGET + RESPAWN (TARGET TANPA R-TREE) =========
def move_towards_target(dt):
    """
    Gerak ke target.
    Jika sampai → spawn target baru random (tidak dicek obstacle).
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
        target_pos = choose_target_no_check()
        robot_vel = [0.0, 0.0]
        return

    step = ROBOT_SPEED * dt

    if step >= dist:
        move_x = dx
        move_z = dz
        robot_pos[0], robot_pos[1] = tx, tz
        target_pos = choose_target_no_check()
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
    pygame.display.set_caption("3D Robot NO R-tree: Random Obstacles & Targets")
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

        prev_rx, prev_rz = robot_pos[0], robot_pos[1]

        move_towards_target(dt)
        avoid_obstacles(robot_pos, dt)
        update_jump(dt)

        # deteksi stuck > 1s → lompat obstacle terdekat (tanpa R-tree cari dengan loop)
        if not jump_active:
            moved = math.hypot(robot_pos[0] - prev_rx, robot_pos[1] - prev_rz)
            if moved < 0.05:
                idle_time += dt
            else:
                idle_time = 0.0

            if idle_time > 1.0:
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
            "NO R-tree: obstacles & targets random | "
            "Arrow: rotate | ESC: quit"
        )
        text = font.render(msg, True, (230, 230, 230))
        screen.blit(text, (10, 10))

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
