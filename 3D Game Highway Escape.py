import math
import random
import time
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

# WINDOW SIZE
W_WIDTH = 1000
W_HEIGHT = 800

# GAME STATE VARIABLES
game_state = "menu"  # menu, playing, game_over
selected_vehicle = 0  # 0=Car, 1=Bus, 2=Truck
vehicle_names = ["Car", "Bus", "Truck"]
menu_rotation = 0.0

# LANES AND ROAD
LANE_X = [-150, 0, 150]
LANE_WIDTH = 120
ROAD_LEFT = -270
ROAD_RIGHT = 270

# PLAYER STATE
player_x = 0.0
player_target_lane = 1 
player_y = -300.0 
player_z = 0.0
player_lives = 3
LANE_SWITCH_SPEED = 8.0

# SCROLLING / SPEED 
scroll_speed = 1.0
base_scroll_speed = 1.5
MAX_SPEED = 4.0
MIN_SPEED = 0.0
road_scroll_offset = 0.0

# SCORE AND DISTANCE
score = 0.0

# FUEL SYSTEM
player_fuel = 100.0
FUEL_DRAIN_RATE = 0.02
FUEL_PICKUP_AMOUNT = 30.0
fuel_pickups = []
FUEL_SPAWN_INTERVAL = 300  # frames
fuel_spawn_timer = 0

# SPEED BOOST 
boost_active = False
boost_timer = 0.0
boost_start_time = 0.0
BOOST_DURATION = 5.0
boost_pickups = []
BOOST_SPAWN_INTERVAL = 500
boost_spawn_timer = 0
pre_boost_speed = 3.0

# GHOST MODE (invincibility)
ghost_mode_active = False
ghost_timer = 0.0
ghost_start_time = 0.0
GHOST_DURATION = 5.0
ghost_pickups = []
GHOST_SPAWN_INTERVAL = 600
ghost_spawn_timer = 0

# ENEMIES 
enemies = []
ENEMY_SPAWN_INTERVAL = 60  # frames
enemy_spawn_timer = 0
MAX_ENEMIES = 8
ENEMY_BASE_SPEED = 1.0

# TYRE MARKS 
tyre_marks = []
is_braking = False
MAX_TYRE_MARKS = 200

# ZEBRA CROSSING 
zebra_crossings = []
ZEBRA_SPAWN_INTERVAL = 800
zebra_spawn_timer = 0
ZEBRA_WIDTH = 60

# AUTOPLAY 
autoplay_enabled = False

# BRAKING 
braking_frames = 0
BRAKING_DURATION = 15  # frames of tyre marks after a brake press

# FRAME TIMER 
last_time = 0.0

# draw 2D HUD text
def draw_text(x, y, text, r=1.0, g=1.0, b=1.0, font=GLUT_BITMAP_HELVETICA_18):
    glDisable(GL_DEPTH_TEST)
    glColor3f(r, g, b)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, W_WIDTH, 0, W_HEIGHT)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    glRasterPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(font, ord(ch))
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    glEnable(GL_DEPTH_TEST)

def draw_wheel(x, y, z, radius=8, length=10):
    glPushMatrix()
    glTranslatef(x, y, z)
    glRotatef(90, 0, 1, 0)  # rotate cylinder to lie along x-axis
    glColor3f(0.15, 0.15, 0.15)
    gluCylinder(gluNewQuadric(), radius, radius, length, 12, 4)
    glPopMatrix()


def draw_headlight(x, y, z, radius=5):
    glPushMatrix()
    glTranslatef(x, y, z)
    glColor3f(1.0, 1.0, 0.7)
    gluSphere(gluNewQuadric(), radius, 10, 10)
    glPopMatrix()


def draw_tail_light(x, y, z, brake=False, radius=5):
    glPushMatrix()
    glTranslatef(x, y, z)
    if brake:
        glColor3f(1.0, 0.0, 0.0)
        gluSphere(gluNewQuadric(), radius + 2, 12, 12)
    else:
        glColor3f(0.45, 0.0, 0.0)
        gluSphere(gluNewQuadric(), radius, 10, 10)
    glPopMatrix()

    if brake:
        glPushMatrix()
        glTranslatef(x, y - 1, z)
        glColor3f(1.0, 0.15, 0.05)
        glScalef(radius * 2.5, 2, radius * 1.5)
        glutSolidCube(1)
        glPopMatrix()


def draw_car(color=(0.1, 0.4, 0.9), ghost=False, brake=False):
    if ghost:
        color = (0.3, 1.0, 1.0)

    # Main body (lower)
    glPushMatrix()
    glTranslatef(0, 0, 20)
    glColor3f(*color)
    glScalef(60, 90, 25)
    glutSolidCube(1)
    glPopMatrix()

    # Cabin (upper)
    glPushMatrix()
    glTranslatef(0, -5, 42)
    glColor3f(color[0] * 0.8, color[1] * 0.8, color[2] * 0.8)
    glScalef(50, 55, 20)
    glutSolidCube(1)
    glPopMatrix()

    # Wheels
    draw_wheel(-35, 25, 8)    # front-left
    draw_wheel(25, 25, 8)     # front-right
    draw_wheel(-35, -25, 8)   # rear-left
    draw_wheel(25, -25, 8)    # rear-right

    # Headlights
    draw_headlight(-18, 46, 18)
    draw_headlight(18, 46, 18)

    # Rear tail lights / brake lights
    draw_tail_light(-18, -46, 18, brake=brake, radius=5)
    draw_tail_light(18, -46, 18, brake=brake, radius=5)


def draw_bus(color=(0.9, 0.75, 0.1), ghost=False, brake=False):
    if ghost:
        color = (0.3, 1.0, 1.0)

    # Main body
    glPushMatrix()
    glTranslatef(0, 0, 30)
    glColor3f(*color)
    glScalef(65, 130, 50)
    glutSolidCube(1)
    glPopMatrix()

    # Window strip
    glPushMatrix()
    glTranslatef(0, 0, 45)
    glColor3f(0.6, 0.85, 1.0)
    glScalef(67, 100, 15)
    glutSolidCube(1)
    glPopMatrix()

    # Roof
    glPushMatrix()
    glTranslatef(0, 0, 58)
    glColor3f(color[0] * 0.7, color[1] * 0.7, color[2] * 0.7)
    glScalef(65, 130, 8)
    glutSolidCube(1)
    glPopMatrix()

    # Wheels (larger)
    draw_wheel(-38, 40, 10, 12, 12)
    draw_wheel(26, 40, 10, 12, 12)
    draw_wheel(-38, -40, 10, 12, 12)
    draw_wheel(26, -40, 10, 12, 12)

    # Headlights
    draw_headlight(-22, 66, 22, 6)
    draw_headlight(22, 66, 22, 6)

    # Rear tail lights / brake lights
    draw_tail_light(-24, -68, 24, brake=brake, radius=6)
    draw_tail_light(24, -68, 24, brake=brake, radius=6)


def draw_truck(color=(0.85, 0.15, 0.1), ghost=False, brake=False):
    if ghost:
        color = (0.3, 1.0, 1.0)

    # Cabin
    glPushMatrix()
    glTranslatef(0, 35, 28)
    glColor3f(*color)
    glScalef(60, 45, 45)
    glutSolidCube(1)
    glPopMatrix()

    # Windshield
    glPushMatrix()
    glTranslatef(0, 52, 38)
    glColor3f(0.6, 0.85, 1.0)
    glScalef(50, 5, 20)
    glutSolidCube(1)
    glPopMatrix()

    # Cargo box
    glPushMatrix()
    glTranslatef(0, -25, 32)
    glColor3f(0.5, 0.5, 0.55)
    glScalef(65, 80, 55)
    glutSolidCube(1)
    glPopMatrix()

    # Wheels — 6 total (2 front, 4 rear double)
    draw_wheel(-35, 40, 8, 10, 10)   # front-left
    draw_wheel(25, 40, 8, 10, 10)    # front-right
    draw_wheel(-35, -15, 8, 10, 10)  # mid-left
    draw_wheel(25, -15, 8, 10, 10)   # mid-right
    draw_wheel(-35, -45, 8, 10, 10)  # rear-left
    draw_wheel(25, -45, 8, 10, 10)   # rear-right

    # Headlights
    draw_headlight(-20, 58, 18, 5)
    draw_headlight(20, 58, 18, 5)

    # Rear tail lights / brake lights
    draw_tail_light(-22, -68, 20, brake=brake, radius=6)
    draw_tail_light(22, -68, 20, brake=brake, radius=6)


def draw_vehicle(vehicle_type, ghost=False, brake=False):
    if vehicle_type == 0:
        draw_car(ghost=ghost, brake=brake)
    elif vehicle_type == 1:
        draw_bus(ghost=ghost, brake=brake)
    elif vehicle_type == 2:
        draw_truck(ghost=ghost, brake=brake)


#  BOOSTER EXHAUST FLAMES
def draw_booster_flames(vehicle_type):
    # Rear exhaust position changes a little based on vehicle size
    if vehicle_type == 0:      # car
        rear_y = -52
        flame_z = 18
        exhaust_gap = 18
        flame_length = 38
    elif vehicle_type == 1:    # bus
        rear_y = -78
        flame_z = 22
        exhaust_gap = 22
        flame_length = 45
    else:                      # truck
        rear_y = -72
        flame_z = 20
        exhaust_gap = 20
        flame_length = 42

    # Small flicker effect, so the flame does not look static
    flicker = random.uniform(-6, 8)
    outer_length = flame_length + flicker
    inner_length = flame_length * 0.55 + flicker * 0.4

    for exhaust_x in [-exhaust_gap, exhaust_gap]:
        # Exhaust pipe
        glPushMatrix()
        glTranslatef(exhaust_x, rear_y + 5, flame_z)
        glRotatef(90, 1, 0, 0)  # point cylinder toward the back of the car
        glColor3f(0.08, 0.08, 0.08)
        gluCylinder(gluNewQuadric(), 4, 4, 12, 12, 4)
        glPopMatrix()

        # Outer orange flame cone
        glPushMatrix()
        glTranslatef(exhaust_x, rear_y - 2, flame_z)
        glRotatef(90, 1, 0, 0)  # cone shoots backward along negative y-axis
        glColor3f(1.0, 0.28, 0.0)
        gluCylinder(gluNewQuadric(), 9, 0, outer_length, 16, 4)
        glPopMatrix()

        # Inner yellow flame cone
        glPushMatrix()
        glTranslatef(exhaust_x, rear_y - 4, flame_z)
        glRotatef(90, 1, 0, 0)
        glColor3f(1.0, 0.9, 0.05)
        gluCylinder(gluNewQuadric(), 5, 0, inner_length, 16, 4)
        glPopMatrix()
#  ENEMY VEHICLES
ENEMY_COLORS = [
    (0.9, 0.2, 0.2),
    (0.2, 0.8, 0.2),
    (0.9, 0.5, 0.1),
    (0.7, 0.1, 0.7),
    (0.2, 0.6, 0.9),
]


def draw_enemy_car(color): # Simple enemy car model 
    # Body
    glPushMatrix()
    glTranslatef(0, 0, 20)
    glColor3f(*color)
    glScalef(55, 80, 24)
    glutSolidCube(1)
    glPopMatrix()

    # Cabin
    glPushMatrix()
    glTranslatef(0, 5, 40)
    glColor3f(color[0] * 0.7, color[1] * 0.7, color[2] * 0.7)
    glScalef(45, 45, 18)
    glutSolidCube(1)
    glPopMatrix()

    # Wheels
    draw_wheel(-32, 22, 8)
    draw_wheel(22, 22, 8)
    draw_wheel(-32, -22, 8)
    draw_wheel(22, -22, 8)

    # Tail lights (red spheres at back)
    glPushMatrix()
    glTranslatef(-18, -41, 18)
    glColor3f(1.0, 0.0, 0.0)
    gluSphere(gluNewQuadric(), 4, 8, 8)
    glPopMatrix()

    glPushMatrix()
    glTranslatef(18, -41, 18)
    glColor3f(1.0, 0.0, 0.0)
    gluSphere(gluNewQuadric(), 4, 8, 8)
    glPopMatrix()

#  PEDESTRIAN MODEL
def draw_pedestrian(ped):
    glPushMatrix()
    glTranslatef(ped["x"], ped["y"], 0)

    # Head
    glPushMatrix()
    glTranslatef(0, 0, 55)
    glColor3f(1.0, 0.85, 0.65)
    gluSphere(gluNewQuadric(), 7, 10, 10)
    glPopMatrix()

    # Torso
    glPushMatrix()
    glTranslatef(0, 0, 38)
    glColor3f(0.9, 0.3, 0.3)
    glScalef(18, 10, 25)
    glutSolidCube(1)
    glPopMatrix()

    # Left leg
    glPushMatrix()
    glTranslatef(-5, 0, 0)
    glColor3f(0.2, 0.2, 0.6)
    gluCylinder(gluNewQuadric(), 4, 3, 25, 8, 4)
    glPopMatrix()

    # Right leg
    glPushMatrix()
    glTranslatef(5, 0, 0)
    glColor3f(0.2, 0.2, 0.6)
    gluCylinder(gluNewQuadric(), 4, 3, 25, 8, 4)
    glPopMatrix()

    # Left arm
    glPushMatrix()
    glTranslatef(-13, 0, 35)
    glColor3f(1.0, 0.85, 0.65)
    gluCylinder(gluNewQuadric(), 3, 2, 18, 8, 4)
    glPopMatrix()

    # Right arm
    glPushMatrix()
    glTranslatef(13, 0, 35)
    glColor3f(1.0, 0.85, 0.65)
    gluCylinder(gluNewQuadric(), 3, 2, 18, 8, 4)
    glPopMatrix()

    glPopMatrix()

#  ROAD DRAWING
def draw_road(): # Draw the highway surface, lane markings, and grass
    # Grass — left side
    glColor3f(0.15, 0.55, 0.15)
    glBegin(GL_QUADS)
    glVertex3f(-800, -600, -1)
    glVertex3f(ROAD_LEFT, -600, -1)
    glVertex3f(ROAD_LEFT, 1200, -1)
    glVertex3f(-800, 1200, -1)
    glEnd()

    # Grass — right side
    glBegin(GL_QUADS)
    glVertex3f(ROAD_RIGHT, -600, -1)
    glVertex3f(800, -600, -1)
    glVertex3f(800, 1200, -1)
    glVertex3f(ROAD_RIGHT, 1200, -1)
    glEnd()

    # Road surface
    glColor3f(0.25, 0.25, 0.28)
    glBegin(GL_QUADS)
    glVertex3f(ROAD_LEFT, -600, 0)
    glVertex3f(ROAD_RIGHT, -600, 0)
    glVertex3f(ROAD_RIGHT, 1200, 0)
    glVertex3f(ROAD_LEFT, 1200, 0)
    glEnd()

    # Road edges (white lines)
    glColor3f(1.0, 1.0, 1.0)
    edge_w = 4
    for ex in [ROAD_LEFT, ROAD_RIGHT]:
        glBegin(GL_QUADS)
        glVertex3f(ex - edge_w, -600, 0.5)
        glVertex3f(ex + edge_w, -600, 0.5)
        glVertex3f(ex + edge_w, 1200, 0.5)
        glVertex3f(ex - edge_w, 1200, 0.5)
        glEnd()

    # Dashed lane dividers
    dash_len = 40
    gap_len = 30
    total = dash_len + gap_len
    offset = road_scroll_offset % total

    for lx in [-75, 75]:  # between lanes
        y = -600 - offset
        while y < 1200:
            glColor3f(1.0, 1.0, 0.9)
            glBegin(GL_QUADS)
            glVertex3f(lx - 2, y, 0.5)
            glVertex3f(lx + 2, y, 0.5)
            glVertex3f(lx + 2, y + dash_len, 0.5)
            glVertex3f(lx - 2, y + dash_len, 0.5)
            glEnd()
            y += total


#  TYRE MARKS while braking
def draw_tyre_marks():
    glColor3f(0.1, 0.1, 0.1)
    for mark in tyre_marks:
        mx, my = mark["x"], mark["y"]
        # Two thin strips (left and right tyre)
        for offset_x in [-15, 15]:
            glBegin(GL_QUADS)
            glVertex3f(mx + offset_x - 3, my - 5, 0.3)
            glVertex3f(mx + offset_x + 3, my - 5, 0.3)
            glVertex3f(mx + offset_x + 3, my + 5, 0.3)
            glVertex3f(mx + offset_x - 3, my + 5, 0.3)
            glEnd()


#  ZEBRA CROSSING
def draw_zebra_crossing(zc): # Draw alternating white/grey stripes across the road."""
    y_base = zc["y"]
    stripe_w = 25
    num_stripes = int((ROAD_RIGHT - ROAD_LEFT) / stripe_w)
    for i in range(num_stripes):
        x0 = ROAD_LEFT + i * stripe_w
        x1 = x0 + stripe_w
        if i % 2 == 0:
            glColor3f(0.95, 0.95, 0.95)
        else:
            glColor3f(0.6, 0.6, 0.6)
        glBegin(GL_QUADS)
        glVertex3f(x0, y_base, 0.4)
        glVertex3f(x1, y_base, 0.4)
        glVertex3f(x1, y_base + ZEBRA_WIDTH, 0.4)
        glVertex3f(x0, y_base + ZEBRA_WIDTH, 0.4)
        glEnd()

#  PICKUP DRAWING
def draw_fuel_pickup(fp):
    """Green spinning cube."""
    glPushMatrix()
    glTranslatef(fp["x"], fp["y"], 18)
    glRotatef(fp.get("rot", 0), 0, 0, 1)
    glColor3f(0.1, 0.9, 0.2)
    glScalef(20, 20, 20)
    glutSolidCube(1)
    glPopMatrix()
    #  "F" label sphere on top
    glPushMatrix()
    glTranslatef(fp["x"], fp["y"], 32)
    glColor3f(0.0, 1.0, 0.0)
    gluSphere(gluNewQuadric(), 6, 8, 8)
    glPopMatrix()


def draw_boost_pickup(bp): # Yellow spinning cube with sphere
    glPushMatrix()
    glTranslatef(bp["x"], bp["y"], 18)
    glRotatef(bp.get("rot", 0), 0, 0, 1)
    glColor3f(1.0, 0.9, 0.0)
    glScalef(18, 18, 18)
    glutSolidCube(1)
    glPopMatrix()

    glPushMatrix()
    glTranslatef(bp["x"], bp["y"], 32)
    glColor3f(1.0, 1.0, 0.3)
    gluSphere(gluNewQuadric(), 7, 8, 8)
    glPopMatrix()


def draw_ghost_pickup(gp): # Cyan spinning cube with sphere
    glPushMatrix()
    glTranslatef(gp["x"], gp["y"], 18)
    glRotatef(gp.get("rot", 0), 0, 0, 1)
    glColor3f(0.2, 0.9, 0.9)
    glScalef(18, 18, 18)
    glutSolidCube(1)
    glPopMatrix()

    glPushMatrix()
    glTranslatef(gp["x"], gp["y"], 35)
    glColor3f(0.5, 1.0, 1.0)
    gluSphere(gluNewQuadric(), 8, 8, 8)
    glPopMatrix()

#  SPAWNING
def spawn_enemy(): # Spawn an enemy car far ahead in a random lane.
    lane = random.choice([0, 1, 2])
    color = random.choice(ENEMY_COLORS)
    return {
        "x": LANE_X[lane],
        "y": 900 + random.uniform(0, 300),
        "lane": lane,
        "color": color,
        "speed": ENEMY_BASE_SPEED + random.uniform(0, 1.5),
    }


def spawn_fuel_pickup():
    lane = random.choice([0, 1, 2])
    return {"x": LANE_X[lane], "y": 900 + random.uniform(0, 200), "rot": 0}


def spawn_boost_pickup():
    lane = random.choice([0, 1, 2])
    return {"x": LANE_X[lane], "y": 900 + random.uniform(0, 200), "rot": 0}


def spawn_ghost_pickup():
    lane = random.choice([0, 1, 2])
    return {"x": LANE_X[lane], "y": 900 + random.uniform(0, 200), "rot": 0}


def spawn_zebra_crossing():
    return {
        "y": 900 + random.uniform(100, 400),
        "ped": {
            "x": ROAD_LEFT - 30,
            "y": 0,  # will be set relative to crossing
            "dir": 1,
            "speed": 1.5 + random.uniform(0, 1.0),
            "active": True,
        },
    }

#  RESET / INIT
def reset_game():
    global player_x, player_target_lane, player_lives
    global scroll_speed, base_scroll_speed, road_scroll_offset, score
    global player_fuel, fuel_pickups, fuel_spawn_timer
    global boost_active, boost_timer, boost_start_time, boost_pickups, boost_spawn_timer, pre_boost_speed
    global ghost_mode_active, ghost_timer, ghost_start_time, ghost_pickups, ghost_spawn_timer
    global enemies, enemy_spawn_timer
    global tyre_marks, is_braking
    global zebra_crossings, zebra_spawn_timer
    global autoplay_enabled
    global braking_frames
    global last_time

    player_x = 0.0
    player_target_lane = 1
    player_lives = 3
    scroll_speed = 1.5
    base_scroll_speed = 1.5
    road_scroll_offset = 0.0
    score = 0.0

    player_fuel = 100.0
    fuel_pickups = []
    fuel_spawn_timer = 0

    boost_active = False
    boost_timer = 0.0
    boost_start_time = 0.0
    boost_pickups = []
    boost_spawn_timer = 0
    pre_boost_speed = 1.5

    ghost_mode_active = False
    ghost_timer = 0.0
    ghost_start_time = 0.0
    ghost_pickups = []
    ghost_spawn_timer = 0

    enemies = []
    enemy_spawn_timer = 0

    tyre_marks = []
    is_braking = False

    zebra_crossings = []
    zebra_spawn_timer = 0

    autoplay_enabled = False
    braking_frames = 0

    last_time = time.time()

    # Initial enemies
    for _ in range(3):
        enemies.append(spawn_enemy())


#  Game LOGIC
def update_game():
    global player_x, scroll_speed, road_scroll_offset, score
    global player_fuel, fuel_spawn_timer
    global boost_active, boost_timer, boost_spawn_timer, pre_boost_speed, boost_start_time
    global ghost_mode_active, ghost_timer, ghost_spawn_timer, ghost_start_time
    global enemy_spawn_timer, player_lives, game_state
    global is_braking, zebra_spawn_timer, braking_frames
    global last_time, base_scroll_speed

    current_time = time.time()
    dt = current_time - last_time
    last_time = current_time

    if game_state != "playing":
        return

    # Braking frames countdown 
    if braking_frames > 0:
        braking_frames -= 1
        is_braking = True
    else:
        is_braking = False

    # Fuel drain 
    player_fuel -= FUEL_DRAIN_RATE
    if player_fuel <= 0:
        player_fuel = 0
        base_scroll_speed = max(base_scroll_speed - 0.03, 0)

    # Apply boost 
    if boost_active:
        scroll_speed = min(base_scroll_speed * 2, MAX_SPEED * 2)
        remaining = BOOST_DURATION - (current_time - boost_start_time)
        if remaining <= 0:
            boost_active = False
            scroll_speed = base_scroll_speed
        else:
            boost_timer = remaining
    else:
        scroll_speed = base_scroll_speed

    # Ghost mode timer 
    if ghost_mode_active:
        remaining = GHOST_DURATION - (current_time - ghost_start_time)
        if remaining <= 0:
            ghost_mode_active = False
        else:
            ghost_timer = remaining

    # Lane interpolation for smooth movement
    target_x = LANE_X[player_target_lane]
    diff = target_x - player_x
    if abs(diff) > 1:
        player_x += diff * 0.15
    else:
        player_x = target_x

    # Road scroll 
    road_scroll_offset += scroll_speed
    score += scroll_speed * 0.1

    # Tyre marks 
    if is_braking and scroll_speed > 0.5:
        tyre_marks.append({"x": player_x, "y": player_y})
        if len(tyre_marks) > MAX_TYRE_MARKS:
            tyre_marks.pop(0)

    # tyre mark movement and cleanup
    for mark in tyre_marks:
        mark["y"] -= scroll_speed
    # Remove old marks that are way behind
    tyre_marks[:] = [m for m in tyre_marks if m["y"] > player_y - 400]

    # Enemy spawning 
    enemy_spawn_timer += 1
    if enemy_spawn_timer >= ENEMY_SPAWN_INTERVAL and len(enemies) < MAX_ENEMIES:
        enemies.append(spawn_enemy())
        enemy_spawn_timer = 0

    # Update enemies 
    enemies_to_remove = []
    for e in enemies:
        e_speed = e["speed"] + scroll_speed
        # If braking, slow down enemies in front of player
        if is_braking and e["y"] > player_y:
            e_speed *= 0.6
        e["y"] -= e_speed
        if e["y"] < player_y - 200:
            enemies_to_remove.append(e)

    for e in enemies_to_remove:
        enemies.remove(e)

    # Enemy-player collision 
    if not ghost_mode_active:
        for e in enemies[:]:
            dist = math.hypot(e["x"] - player_x, e["y"] - player_y)
            if dist < 55:
                player_lives -= 1
                enemies.remove(e)
                if player_lives <= 0:
                    game_state = "game_over"
                    return

    # Fuel pickups 
    fuel_spawn_timer += 1
    if fuel_spawn_timer >= FUEL_SPAWN_INTERVAL:
        fuel_pickups.append(spawn_fuel_pickup())
        fuel_spawn_timer = 0

    for fp in fuel_pickups:
        fp["y"] -= scroll_speed
        fp["rot"] = (fp.get("rot", 0) + 3) % 360

    # Collision with fuel pickup
    for fp in fuel_pickups[:]:
        dist = math.hypot(fp["x"] - player_x, fp["y"] - player_y)
        if dist < 40:
            player_fuel = min(player_fuel + FUEL_PICKUP_AMOUNT, 100.0)
            fuel_pickups.remove(fp)

    # Remove off-screen
    fuel_pickups[:] = [fp for fp in fuel_pickups if fp["y"] > player_y - 200]

    # Boost pickups 
    boost_spawn_timer += 1
    if boost_spawn_timer >= BOOST_SPAWN_INTERVAL:
        boost_pickups.append(spawn_boost_pickup())
        boost_spawn_timer = 0

    for bp in boost_pickups:
        bp["y"] -= scroll_speed
        bp["rot"] = (bp.get("rot", 0) + 4) % 360

    for bp in boost_pickups[:]:
        dist = math.hypot(bp["x"] - player_x, bp["y"] - player_y)
        if dist < 40:
            boost_active = True
            boost_start_time = current_time
            pre_boost_speed = base_scroll_speed
            boost_pickups.remove(bp)

    boost_pickups[:] = [bp for bp in boost_pickups if bp["y"] > player_y - 200]

    # Ghost pickups 
    ghost_spawn_timer += 1
    if ghost_spawn_timer >= GHOST_SPAWN_INTERVAL:
        ghost_pickups.append(spawn_ghost_pickup())
        ghost_spawn_timer = 0

    for gp in ghost_pickups:
        gp["y"] -= scroll_speed
        gp["rot"] = (gp.get("rot", 0) + 5) % 360

    for gp in ghost_pickups[:]:
        dist = math.hypot(gp["x"] - player_x, gp["y"] - player_y)
        if dist < 40:
            ghost_mode_active = True
            ghost_start_time = current_time
            ghost_pickups.remove(gp)

    ghost_pickups[:] = [gp for gp in ghost_pickups if gp["y"] > player_y - 200]

    # Zebra crossings 
    zebra_spawn_timer += 1
    if zebra_spawn_timer >= ZEBRA_SPAWN_INTERVAL:
        zc = spawn_zebra_crossing()
        zebra_crossings.append(zc)
        zebra_spawn_timer = 0

    for zc in zebra_crossings:
        zc["y"] -= scroll_speed
        ped = zc["ped"]
        if ped["active"]:
            ped["y"] = zc["y"] + ZEBRA_WIDTH / 2
            ped["x"] += ped["dir"] * ped["speed"]
            if ped["x"] > ROAD_RIGHT + 50:
                ped["active"] = False
            elif ped["x"] < ROAD_LEFT - 50:
                ped["active"] = False

    # Pedestrian collision fatal!
    for zc in zebra_crossings:
        ped = zc["ped"]
        if ped["active"]:
            dist = math.hypot(ped["x"] - player_x, ped["y"] - player_y)
            if dist < 45:
                game_state = "game_over"
                return

    zebra_crossings[:] = [zc for zc in zebra_crossings if zc["y"] > player_y - 300]

    # Autoplay / Cheat mode
    if autoplay_enabled:
        run_autoplay()


def run_autoplay():
    global player_target_lane, base_scroll_speed, braking_frames

    LOOK_AHEAD   = 400   # how far ahead (in y) to consider threats
    DANGER_ZONE  = 80    # y-distance considered immediately dangerous
    LANE_THRESH  = 60    # x-tolerance for "in this lane"

    def lane_danger(lane_idx):
        lx = LANE_X[lane_idx]
        closest = LOOK_AHEAD

        for e in enemies:
            dy = e["y"] - player_y
            if 0 < dy < LOOK_AHEAD and abs(e["x"] - lx) < LANE_THRESH:
                closest = min(closest, dy)

        for zc in zebra_crossings:
            ped = zc["ped"]
            if not ped["active"]:
                continue
            dy = ped["y"] - player_y
            if 0 < dy < LOOK_AHEAD and abs(ped["x"] - lx) < LANE_THRESH:
                closest = min(closest, dy)

        return closest  # higher = safer

    lane_scores = [lane_danger(i) for i in range(3)]
    safest_lane  = max(range(3), key=lambda i: lane_scores[i])
    current_danger = lane_scores[player_target_lane]

    if current_danger < DANGER_ZONE:
        # Imminent collision — brake hard
        base_scroll_speed = max(base_scroll_speed - 0.3, 1.0)
        braking_frames = BRAKING_DURATION
    elif current_danger < 180:
        # Moderate threat ahead — ease off
        base_scroll_speed = max(base_scroll_speed - 0.1, 1.5)
    else:
        # Road is clear — accelerate toward a comfortable cruise speed
        base_scroll_speed = min(base_scroll_speed + 0.1, 2.5)

    def nearest_pickup_lane():
        best_lane, best_dist = None, float("inf")
        pickups = (
            [(fp["x"], fp["y"]) for fp in fuel_pickups   if player_fuel < 60] +
            [(bp["x"], bp["y"]) for bp in boost_pickups] +
            [(gp["x"], gp["y"]) for gp in ghost_pickups]
        )
        for px, py in pickups:
            dy = py - player_y
            if 0 < dy < LOOK_AHEAD:
                for li, lx in enumerate(LANE_X):
                    if abs(px - lx) < LANE_THRESH and dy < best_dist:
                        best_dist = dy
                        best_lane = li
        return best_lane, best_dist

    pickup_lane, pickup_dist = nearest_pickup_lane() 
    
    # Always move away from immediate danger first
    if current_danger < DANGER_ZONE:
        player_target_lane = safest_lane
    elif pickup_lane is not None and lane_scores[pickup_lane] > DANGER_ZONE:
        # Safe pickup available — go collect it
        player_target_lane = pickup_lane
    elif lane_scores[player_target_lane] < lane_scores[safest_lane] - 30:
        # Current lane is noticeably worse than the best — switch
        player_target_lane = safest_lane

#  CAMERA
def setup_camera():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(60, W_WIDTH / W_HEIGHT, 1.0, 3000)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    # Chase camera — behind and above the player
    eye_x = player_x
    eye_y = player_y - 350
    eye_z = 250

    look_x = player_x
    look_y = player_y + 200
    look_z = 30

    gluLookAt(eye_x, eye_y, eye_z,
              look_x, look_y, look_z,
              0, 0, 1)

#  HUD
def draw_hud(): # Draw all HUD elemente
    # Lives - using normal numbers because GLUT bitmap font may not show heart symbols
    lives_text = f"Lives Left: {player_lives}/3"
    draw_text(15, 770, lives_text, 1.0, 0.3, 0.3)

    # Draw small life boxes so the remaining lives are clearly visible
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, W_WIDTH, 0, W_HEIGHT)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    life_box_x = 145
    life_box_y = 768
    life_box_size = 18
    life_gap = 6
    for i in range(3):
        if i < player_lives:
            glColor3f(1.0, 0.1, 0.1)
        else:
            glColor3f(0.25, 0.25, 0.25)
        x0 = life_box_x + i * (life_box_size + life_gap)
        y0 = life_box_y
        glBegin(GL_QUADS)
        glVertex3f(x0, y0, 0)
        glVertex3f(x0 + life_box_size, y0, 0)
        glVertex3f(x0 + life_box_size, y0 + life_box_size, 0)
        glVertex3f(x0, y0 + life_box_size, 0)
        glEnd()

    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

    # Score
    draw_text(420, 770, f"Score: {int(score)}", 1.0, 1.0, 0.5)

    # Speed
    speed_pct = int((scroll_speed / MAX_SPEED) * 100)
    draw_text(15, 740, f"Speed: {speed_pct}%", 0.8, 0.8, 1.0)

    # Fuel bar background
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, W_WIDTH, 0, W_HEIGHT)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    # Fuel bar outline
    bar_x = 750
    bar_y = 765
    bar_w = 200
    bar_h = 18

    # Background
    glColor3f(0.3, 0.3, 0.3)
    glBegin(GL_QUADS)
    glVertex3f(bar_x, bar_y, 0)
    glVertex3f(bar_x + bar_w, bar_y, 0)
    glVertex3f(bar_x + bar_w, bar_y + bar_h, 0)
    glVertex3f(bar_x, bar_y + bar_h, 0)
    glEnd()

    # Fill
    fill_w = (player_fuel / 100.0) * bar_w
    if player_fuel > 50:
        glColor3f(0.1, 0.9, 0.2)
    elif player_fuel > 25:
        glColor3f(0.9, 0.8, 0.1)
    else:
        glColor3f(0.9, 0.2, 0.1)

    glBegin(GL_QUADS)
    glVertex3f(bar_x, bar_y, 0)
    glVertex3f(bar_x + fill_w, bar_y, 0)
    glVertex3f(bar_x + fill_w, bar_y + bar_h, 0)
    glVertex3f(bar_x, bar_y + bar_h, 0)
    glEnd()

    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

    draw_text(750, 745, f"Fuel: {int(player_fuel)}%", 1.0, 1.0, 1.0)

    # Boost timer
    if boost_active:
        draw_text(400, 720, f"BOOST: {boost_timer:.1f}s", 1.0, 1.0, 0.0)

    # Ghost mode timer
    if ghost_mode_active:
        draw_text(400, 695, f"GHOST MODE: {ghost_timer:.1f}s", 0.3, 1.0, 1.0)

    # Autoplay indicator
    if autoplay_enabled:
        draw_text(15, 715, "AUTOPLAY", 0.3, 1.0, 0.3)

    # Brake indicator
    if is_braking:
        draw_text(15, 690, "BRAKE LIGHTS ON", 1.0, 0.15, 0.15)

#  MENU SCREEN
def draw_menu(): # Draw the landing page / menu.
    global menu_rotation
    menu_rotation = (menu_rotation + 0.5) % 360

    # Clear and set up 3D for vehicle preview 
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(50, W_WIDTH / W_HEIGHT, 1.0, 2000)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    gluLookAt(0, -250, 150,
              0, 0, 30,
              0, 0, 1)

    glEnable(GL_DEPTH_TEST)

    # Platform
    glPushMatrix()
    glColor3f(0.2, 0.2, 0.25)
    glScalef(200, 200, 5)
    glutSolidCube(1)
    glPopMatrix()

    # Draw spinning vehicle
    glPushMatrix()
    glTranslatef(0, 0, 5)
    glRotatef(menu_rotation, 0, 0, 1)
    draw_vehicle(selected_vehicle)
    glPopMatrix()

    # Title
    draw_text(350, 720, "HIGHWAY  ESCAPE", 1.0, 0.85, 0.2, GLUT_BITMAP_TIMES_ROMAN_24)

    # Vehicle name
    vname = vehicle_names[selected_vehicle]
    draw_text(470, 650, f"{vname}", 0.9, 0.9, 0.9)

    # Draw arrow buttons and start button using 2D shapes
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, W_WIDTH, 0, W_HEIGHT)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    # Left arrow button (triangle)
    glColor3f(0.8, 0.3, 0.3)
    glBegin(GL_TRIANGLES)
    glVertex3f(440, 660, 0)
    glVertex3f(460, 675, 0)
    glVertex3f(460, 645, 0)
    glEnd()

    # Right arrow button (triangle)
    glColor3f(0.8, 0.3, 0.3)
    glBegin(GL_TRIANGLES)
    glVertex3f(560, 660, 0)
    glVertex3f(540, 675, 0)
    glVertex3f(540, 645, 0)
    glEnd()

    # Start button (Centered, larger)
    glColor3f(0.1, 0.7, 0.2)
    glBegin(GL_QUADS)
    glVertex3f(400, 100, 0)
    glVertex3f(600, 100, 0)
    glVertex3f(600, 160, 0)
    glVertex3f(400, 160, 0)
    glEnd()

    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

    # Start Button label
    draw_text(450, 125, "START GAME", 1.0, 1.0, 1.0)

    # Instructions
    draw_text(400, 50, "Arrow Keys: Steer and Speed", 0.7, 0.7, 0.7)
    draw_text(400, 30, "A: Toggle Autoplay", 0.7, 0.7, 0.7)
    draw_text(400, 10, "R: Restart Game", 0.7, 0.7, 0.7)


def draw_game_over():
    """Draw game over overlay."""
    draw_text(340, 450, "GAME  OVER", 1.0, 0.2, 0.2)
    draw_text(370, 400, f"Final Score: {int(score)}", 1.0, 1.0, 0.5)
    draw_text(330, 350, "Press R to return to menu", 0.8, 0.8, 0.8)

#  DISPLAY CALLBACK
def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glViewport(0, 0, W_WIDTH, W_HEIGHT)

    if game_state == "menu":
        draw_menu()

    elif game_state == "playing":
        setup_camera()
        glEnable(GL_DEPTH_TEST)

        # Draw road
        draw_road()

        # Draw tyre marks
        draw_tyre_marks()

        # Draw zebra crossings and pedestrians
        for zc in zebra_crossings:
            draw_zebra_crossing(zc)
            if zc["ped"]["active"]:
                draw_pedestrian(zc["ped"])

        # Draw fuel pickups
        for fp in fuel_pickups:
            draw_fuel_pickup(fp)

        # Draw boost pickups
        for bp in boost_pickups:
            draw_boost_pickup(bp)

        # Draw ghost pickups
        for gp in ghost_pickups:
            draw_ghost_pickup(gp)

        # Draw enemies
        for e in enemies:
            glPushMatrix()
            glTranslatef(e["x"], e["y"], 0)
            glRotatef(180, 0, 0, 1)  # face toward player
            draw_enemy_car(e["color"])
            glPopMatrix()

        # Draw player
        glPushMatrix()
        glTranslatef(player_x, player_y, 0)
        draw_vehicle(selected_vehicle, ghost=ghost_mode_active, brake=is_braking)
        if boost_active:
            draw_booster_flames(selected_vehicle)
        glPopMatrix()

        # Draw HUD
        draw_hud()

    elif game_state == "game_over":
        # Draw the road scene frozen
        setup_camera()
        glEnable(GL_DEPTH_TEST)
        draw_road()
        draw_tyre_marks()

        for zc in zebra_crossings:
            draw_zebra_crossing(zc)
            if zc["ped"]["active"]:
                draw_pedestrian(zc["ped"])

        for e in enemies:
            glPushMatrix()
            glTranslatef(e["x"], e["y"], 0)
            glRotatef(180, 0, 0, 1)
            draw_enemy_car(e["color"])
            glPopMatrix()

        glPushMatrix()
        glTranslatef(player_x, player_y, 0)
        draw_vehicle(selected_vehicle)
        if boost_active:
            draw_booster_flames(selected_vehicle)
        glPopMatrix()

        draw_hud()
        draw_game_over()

    glutSwapBuffers()

#  KEYBOARD 
def keyboard_listener(key, x, y):
    global game_state, autoplay_enabled

    if game_state == "game_over":
        if key == b'r' or key == b'R':
            game_state = "menu"
        return

    if game_state == "playing":
        if key == b'a' or key == b'A':
            autoplay_enabled = not autoplay_enabled
        elif key == b'r' or key == b'R':
            game_state = "menu"

    glutPostRedisplay()


def special_key_listener(key, x, y):
    global player_target_lane, base_scroll_speed, braking_frames

    if game_state == "playing":
        if key == GLUT_KEY_LEFT:
            if player_target_lane > 0:
                player_target_lane -= 1
        elif key == GLUT_KEY_RIGHT:
            if player_target_lane < 2:
                player_target_lane += 1
        elif key == GLUT_KEY_UP:
            base_scroll_speed = min(base_scroll_speed + 0.5, MAX_SPEED)
        elif key == GLUT_KEY_DOWN:
            base_scroll_speed = max(base_scroll_speed - 0.5, MIN_SPEED)
            braking_frames = BRAKING_DURATION

    glutPostRedisplay()

#  MOUSE 
def mouse_listener(button, state, x, y):
    global selected_vehicle, game_state

    if state != GLUT_DOWN or button != GLUT_LEFT_BUTTON:
        return

    # Convert GLUT coords: (x, y) where y is from top
    mx = x
    my = W_HEIGHT - y

    if game_state == "menu":
        # Left arrow button: 400-480, 630-690
        if 400 <= mx <= 480 and 630 <= my <= 690:
            selected_vehicle = (selected_vehicle - 1) % 3

        # Right arrow button: 520-600, 630-690
        elif 520 <= mx <= 600 and 630 <= my <= 690:
            selected_vehicle = (selected_vehicle + 1) % 3

        # Start button: 400-600, 100-160
        elif 400 <= mx <= 600 and 100 <= my <= 160:
            reset_game()
            game_state = "playing"

    glutPostRedisplay()

#  TIMER CALLBACK 
FRAME_INTERVAL_MS = 16  # ~60 FPS


def timer_callback(value):
    update_game()
    glutPostRedisplay()
    glutTimerFunc(FRAME_INTERVAL_MS, timer_callback, 0)

#  MAIN
def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(W_WIDTH, W_HEIGHT)
    glutInitWindowPosition(100, 50)
    glutCreateWindow(b"Highway Escape")

    # Set up Sunset Sky Background and Fog
    glClearColor(0.6, 0.8, 0.9, 1.0)
    glEnable(GL_FOG)
    glFogi(GL_FOG_MODE, GL_LINEAR)
    glFogfv(GL_FOG_COLOR, [0.6, 0.8, 0.9, 1.0])
    glFogf(GL_FOG_START, 400.0)
    glFogf(GL_FOG_END, 1300.0)

    glEnable(GL_DEPTH_TEST)

    glutDisplayFunc(display)
    glutKeyboardFunc(keyboard_listener)
    glutSpecialFunc(special_key_listener)
    glutMouseFunc(mouse_listener)
    glutTimerFunc(FRAME_INTERVAL_MS, timer_callback, 0)

    glutMainLoop()


if __name__ == "__main__":
    main()
