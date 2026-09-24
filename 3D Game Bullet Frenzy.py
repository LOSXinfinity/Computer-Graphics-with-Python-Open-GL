import math
import random
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

camera_angle = 45.0
camera_height = 400.0
camera_radius = 700.0
fovY = 80
first_person = False

GRID_LENGTH  = 600
CELL_SIZE    = 100
WALL_HEIGHT  = 100

player_pos   = [0.0, 0.0]
gun_angle    = 0.0
player_life  = 5
game_over    = False
game_score   = 0
MOVE_SPEED   = 5.0
ROTATE_SPEED = 3.0

bullets        = []
missed_bullets = 0
BULLET_SPEED   = 8.0
BULLET_SIZE    = 10

NUM_ENEMIES  = 5
ENEMY_SPEED  = 0.01
enemies      = []

cheat_mode       = False
cheat_vision     = False
cheat_fire_timer = 0
CHEAT_FIRE_DELAY = 20

ENEMY_RADIUS  = 30
BULLET_RADIUS = 8
PLAYER_RADIUS = 20

# Spawn one new enemy
def spawn_enemy():
    while True:
        x = random.uniform(-GRID_LENGTH + 50, GRID_LENGTH - 50)
        y = random.uniform(-GRID_LENGTH + 50, GRID_LENGTH - 50)
        dist = math.hypot(x - player_pos[0], y - player_pos[1])
        if dist > 150:
            return {"x": x, "y": y, "scale": 1.0, "scale_dir": 1}


def init_enemies():
    global enemies
    enemies = [spawn_enemy() for _ in range(NUM_ENEMIES)]

# Reset game
def reset_game():
    global player_pos, gun_angle, player_life, game_over
    global game_score, bullets, missed_bullets
    global cheat_mode, cheat_vision, cheat_fire_timer
    player_pos        = [0.0, 0.0]
    gun_angle         = 0.0
    player_life       = 5
    game_over         = False
    game_score        = 0
    bullets           = []
    missed_bullets    = 0
    cheat_mode        = False
    cheat_vision      = False
    cheat_fire_timer  = 0
    init_enemies()

# Draw 2D HUD text
def draw_text(x, y, text, font=GLUT_BITMAP_HELVETICA_18):
    glColor3f(1, 1, 1)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 1000, 0, 800)
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

# DRAW floor
def draw_grid():
    steps = int((2 * GRID_LENGTH) / CELL_SIZE)
    start = -GRID_LENGTH

    for i in range(steps):
        for j in range(steps):
            x0 = start + i * CELL_SIZE
            y0 = start + j * CELL_SIZE
            x1 = x0 + CELL_SIZE
            y1 = y0 + CELL_SIZE

            if (i + j) % 2 == 0:
                glColor3f(1.0, 1.0, 1.0)
            else:
                glColor3f(0.7, 0.5, 0.95)

            glBegin(GL_QUADS)
            glVertex3f(x0, y0, 0)
            glVertex3f(x1, y0, 0)
            glVertex3f(x1, y1, 0)
            glVertex3f(x0, y1, 0)
            glEnd()

# DRAW: boundary wall
def draw_walls():
    G = GRID_LENGTH
    H = WALL_HEIGHT

    wall_data = [
        ((-G, -G, 0), ( G, -G, H), (0.2, 0.2, 1.0)),  # south
        ((-G,  G, 0), ( G,  G, H), (0.0, 0.9, 0.0)),  # north
        ((-G, -G, 0), (-G,  G, H), (0.0, 0.9, 0.9)),  # west
        (( G, -G, 0), ( G,  G, H), (0.9, 0.5, 0.0)),  # east
    ]

    for (x0, y0, z0), (x1, y1, z1), color in wall_data:
        glColor3f(*color)
        glBegin(GL_QUADS)
        glVertex3f(x0, y0, z0)
        glVertex3f(x1, y1, z0)
        glVertex3f(x1, y1, z1)
        glVertex3f(x0, y0, z1)
        glEnd()

# DRAW: player model
def draw_player():
    if first_person:
        return

    glPushMatrix()
    glTranslatef(player_pos[0], player_pos[1], 0)
    glRotatef(gun_angle, 0, 0, 1)

    if game_over:
        glRotatef(90, 1, 0, 0)

    # head
    glPushMatrix()
    glTranslatef(0, 0, 90)
    glColor3f(1.0, 0.85, 0.65)
    gluSphere(gluNewQuadric(), 15, 12, 12)
    glPopMatrix()

    # torso
    glPushMatrix()
    glTranslatef(0, 0, 60)
    glColor3f(0.3, 0.5, 0.3)
    glScalef(30, 20, 40)
    glutSolidCube(1)
    glPopMatrix()

    # left leg
    glPushMatrix()
    glTranslatef(-10, 0, 0)
    glColor3f(0.1, 0.1, 0.8)
    gluCylinder(gluNewQuadric(), 8, 6, 40, 8, 4)
    glPopMatrix()

    # right leg
    glPushMatrix()
    glTranslatef(10, 0, 0)
    glColor3f(0.1, 0.1, 0.8)
    gluCylinder(gluNewQuadric(), 8, 6, 40, 8, 4)
    glPopMatrix()

    # arm
    glPushMatrix()
    glTranslatef(20, 0, 72)
    glColor3f(0.3, 0.5, 0.3)
    glScalef(20, 10, 12)
    glutSolidCube(1)
    glPopMatrix()

    # gun barrel
    glPushMatrix()
    glTranslatef(20, 10, 72)
    glColor3f(0.2, 0.2, 0.2)
    glScalef(6, 40, 6)
    glutSolidCube(1)
    glPopMatrix()

    glPopMatrix()

# DRAW: enemy
def draw_enemy(e):
    glPushMatrix()
    glTranslatef(e["x"], e["y"], 0)
    glScalef(e["scale"], e["scale"], e["scale"])

    glPushMatrix()
    glTranslatef(0, 0, 30)
    glColor3f(0.9, 0.1, 0.1)
    gluSphere(gluNewQuadric(), 30, 12, 12)
    glPopMatrix()

    glPushMatrix()
    glTranslatef(0, 0, 72)
    glColor3f(0.05, 0.05, 0.05)
    gluSphere(gluNewQuadric(), 12, 10, 10)
    glPopMatrix()

    glPopMatrix()

# DRAW: bullets
def draw_bullets():
    for b in bullets:
        glPushMatrix()
        glTranslatef(b["x"], b["y"], 15)
        glColor3f(1.0, 1.0, 0.0)
        glutSolidCube(BULLET_SIZE)
        glPopMatrix()

# DRAW HUD text
def draw_hud():
    draw_text(10, 775, f"Player Life Remaining: {player_life}")
    draw_text(10, 750, f"Game Score: {game_score}")
    draw_text(10, 725, f"Player Bullet Missed: {missed_bullets}")
    if cheat_mode:
        draw_text(10, 700, "CHEAT MODE ON")
    if first_person:
        draw_text(10, 675, "FIRST PERSON VIEW")
    if game_over:
        draw_text(350, 400, "GAME OVER  -  Press R to restart")

# CAMERA
def setupCamera():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(fovY, 1.25, 0.1, 3000)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    if first_person:
        rad = math.radians(gun_angle)
        dx = -math.sin(rad)   # forward X in world space
        dy =  math.cos(rad)   # forward Y in world space

        eye_x = player_pos[0] - dx * 50
        eye_y = player_pos[1] - dy * 50
        eye_z = 90

        look_x = player_pos[0] + dx * 200
        look_y = player_pos[1] + dy * 200
        look_z = 70

        gluLookAt(eye_x, eye_y, eye_z,
                  look_x, look_y, look_z,
                  0, 0, 1)   # Z is up

    else:
        # Third-person orbit camera
        rad = math.radians(camera_angle)
        cx = camera_radius * math.cos(rad)
        cy = camera_radius * math.sin(rad)
        cz = camera_height

        gluLookAt(cx, cy, cz,
                  0,  0,  0,
                  0,  0,  1)
        
# enemies move toward player
def update_enemies():
    for e in enemies:
        dx = player_pos[0] - e["x"]
        dy = player_pos[1] - e["y"]
        dist = math.hypot(dx, dy)

        if dist > 1:
            e["x"] += (dx / dist) * ENEMY_SPEED
            e["y"] += (dy / dist) * ENEMY_SPEED

        # scale oscillation
        e["scale"] += 0.01 * e["scale_dir"]
        if e["scale"] >= 1.5:
            e["scale_dir"] = -1
        elif e["scale"] <= 0.5:
            e["scale_dir"] = 1

# move bullets and check for out-of-bounds to count missed shots
def update_bullets():
    global missed_bullets, game_over
    to_remove = []
    for b in bullets:
        b["x"] += b["dx"]
        b["y"] += b["dy"]
        if abs(b["x"]) > GRID_LENGTH or abs(b["y"]) > GRID_LENGTH:
            to_remove.append(b)
            missed_bullets += 1
            if missed_bullets >= 10:
                game_over = True

    for b in to_remove:
        if b in bullets:
            bullets.remove(b)

# bullet-enemy collision detection
def check_bullet_enemy_collisions():
    global game_score
    bullets_to_remove = []
    for b in bullets:
        for e in enemies:
            dist = math.hypot(b["x"] - e["x"], b["y"] - e["y"])
            if dist < ENEMY_RADIUS + BULLET_RADIUS:
                new_e = spawn_enemy()
                e["x"] = new_e["x"]
                e["y"] = new_e["y"]
                bullets_to_remove.append(b)
                game_score += 1
                break
    for b in bullets_to_remove:
        if b in bullets:
            bullets.remove(b)

# player-enemy collision detection
def check_player_enemy_collisions():
    global player_life, game_over
    for e in enemies:
        dist = math.hypot(e["x"] - player_pos[0], e["y"] - player_pos[1])
        if dist < ENEMY_RADIUS + PLAYER_RADIUS:
            player_life -= 1
            new_pos = spawn_enemy()
            e["x"] = new_pos["x"]
            e["y"] = new_pos["y"]
            if player_life <= 0:
                game_over = True

# FIRE bullet
def fire_bullet():
    rad = math.radians(gun_angle)
    dx  = -math.sin(rad) * BULLET_SPEED
    dy  =  math.cos(rad) * BULLET_SPEED
    bullets.append({"x": player_pos[0], "y": player_pos[1], "dx": dx, "dy": dy})

# cheat mode auto fire
def update_cheat_mode():
    global gun_angle, cheat_fire_timer
    if not cheat_mode or game_over:
        return

    gun_angle = (gun_angle + 1.5) % 360

    if cheat_fire_timer > 0:
        cheat_fire_timer -= 1
        return

    rad = math.radians(gun_angle)
    gx = -math.sin(rad)
    gy =  math.cos(rad)

    for e in enemies:
        ex = e["x"] - player_pos[0]
        ey = e["y"] - player_pos[1]
        dist = math.hypot(ex, ey)
        if dist < 1:
            continue
        dot = (gx * ex / dist) + (gy * ey / dist)
        if dot > 0.985:
            fire_bullet()
            cheat_fire_timer = CHEAT_FIRE_DELAY
            break

# KEYBOARD
def keyboardListener(key, x, y):
    global gun_angle, cheat_mode, cheat_vision

    if game_over:
        if key == b'r':
            reset_game()
        return

    if key == b'w':
        rad = math.radians(gun_angle)
        player_pos[0] += -math.sin(rad) * MOVE_SPEED
        player_pos[1] +=  math.cos(rad) * MOVE_SPEED
        player_pos[0] = max(-GRID_LENGTH + 20, min(GRID_LENGTH - 20, player_pos[0]))
        player_pos[1] = max(-GRID_LENGTH + 20, min(GRID_LENGTH - 20, player_pos[1]))

    elif key == b's':
        rad = math.radians(gun_angle)
        player_pos[0] -= -math.sin(rad) * MOVE_SPEED
        player_pos[1] -=  math.cos(rad) * MOVE_SPEED
        player_pos[0] = max(-GRID_LENGTH + 20, min(GRID_LENGTH - 20, player_pos[0]))
        player_pos[1] = max(-GRID_LENGTH + 20, min(GRID_LENGTH - 20, player_pos[1]))

    elif key == b'a':
        gun_angle = (gun_angle - ROTATE_SPEED) % 360

    elif key == b'd':
        gun_angle = (gun_angle + ROTATE_SPEED) % 360

    elif key == b'c':
        cheat_mode = not cheat_mode

    elif key == b'v':
        cheat_vision = not cheat_vision

    elif key == b'r':
        reset_game()

    glutPostRedisplay()


#arrow keys
def specialKeyListener(key, x, y):
    global camera_angle, camera_height

    if key == GLUT_KEY_UP:
        camera_height += 10

    elif key == GLUT_KEY_DOWN:
        camera_height -= 10
        camera_height = max(50, camera_height)

    elif key == GLUT_KEY_LEFT:
        camera_angle = (camera_angle - 2) % 360

    elif key == GLUT_KEY_RIGHT:
        camera_angle = (camera_angle + 2) % 360

    glutPostRedisplay()


# MOUSE
def mouseListener(button, state, x, y):
    global first_person

    if state != GLUT_DOWN:
        return

    if button == GLUT_LEFT_BUTTON:
        if not game_over:
            fire_bullet()

    elif button == GLUT_RIGHT_BUTTON:
        first_person = not first_person

    glutPostRedisplay()

def idle():
    if not game_over:
        update_enemies()
        update_bullets()
        check_bullet_enemy_collisions()
        check_player_enemy_collisions()
        update_cheat_mode()
    glutPostRedisplay()

# DISPLAY
def showScreen():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glViewport(0, 0, 1000, 800)

    setupCamera()
    glEnable(GL_DEPTH_TEST)

    draw_grid()
    draw_walls()
    draw_player()

    for e in enemies:
        draw_enemy(e)

    draw_bullets()
    draw_hud()

    glutSwapBuffers()

def main():
    reset_game()

    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(1000, 800)
    glutInitWindowPosition(0, 0)
    glutCreateWindow(b"Bullet Frenzy")

    glEnable(GL_DEPTH_TEST)

    glutDisplayFunc(showScreen)
    glutKeyboardFunc(keyboardListener)
    glutSpecialFunc(specialKeyListener)
    glutMouseFunc(mouseListener)
    glutIdleFunc(idle)

    glutMainLoop()


if __name__ == "__main__":
    main()