from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

import math
import time
import random

# Size
W, H = 450, 700

BTN_AREA_H = 60 # Leave space at the top for Play/ Pause/ Restart/ Exit buttons

#  Midpoint Line Algorithm with Zone Handling
def find_zone(dx, dy):
    if abs(dx) >= abs(dy):
        if dx >= 0 and dy >= 0: return 0
        if dx <= 0 and dy >= 0: return 3
        if dx <= 0 and dy <= 0: return 4
        if dx >= 0 and dy <= 0: return 7
    else:
        if dx >= 0 and dy >= 0: return 1
        if dx <= 0 and dy >= 0: return 2
        if dx <= 0 and dy <= 0: return 5
        if dx >= 0 and dy <= 0: return 6
    return 0

def to_zone0(x, y, zone):
    if zone == 0: return  x,  y
    if zone == 1: return  y,  x
    if zone == 2: return  y, -x
    if zone == 3: return -x,  y
    if zone == 4: return -x, -y
    if zone == 5: return -y, -x
    if zone == 6: return -y,  x
    if zone == 7: return  x, -y

def from_zone0(x, y, zone):
    if zone == 0: return  x,  y
    if zone == 1: return  y,  x
    if zone == 2: return -y,  x
    if zone == 3: return -x,  y
    if zone == 4: return -x, -y
    if zone == 5: return -y, -x
    if zone == 6: return  y, -x
    if zone == 7: return  x, -y

def draw_line_zone0(x1, y1, x2, y2, zone):
    dx = x2 - x1
    dy = y2 - y1
    d  = 2*dy - dx
    incE  = 2*dy
    incNE = 2*(dy - dx)
    y = y1
    for x in range(x1, x2 + 1):
        rx, ry = from_zone0(x, y, zone)
        glVertex2i(rx, ry)
        if d > 0:
            d += incNE
            y += 1
        else:
            d += incE

def draw_line(x1, y1, x2, y2):
    dx = x2 - x1
    dy = y2 - y1
    zone = find_zone(dx, dy)
    zx1, zy1 = to_zone0(x1, y1, zone)
    zx2, zy2 = to_zone0(x2, y2, zone)
    if zx1 > zx2:
        zx1, zy1, zx2, zy2 = zx2, zy2, zx1, zy1
    glBegin(GL_POINTS)
    draw_line_zone0(zx1, zy1, zx2, zy2, zone)
    glEnd()

# Drawing shapes:
def draw_diamond(cx, cy, hw, hh):
    draw_line(cx, cy + hh, cx + hw, cy) # top right
    draw_line(cx + hw, cy, cx, cy - hh) # bottom right
    draw_line(cx, cy - hh, cx - hw, cy) # bottom left
    draw_line(cx - hw, cy, cx, cy + hh) # top left

def draw_catcher(cx, cy, hw, hh):
    bottom_hw = int(hw * 0.45)
    draw_line(cx - bottom_hw, cy, cx + bottom_hw, cy) # bottom
    draw_line(cx - bottom_hw, cy, cx - hw, cy + hh) # left
    draw_line(cx - hw, cy + hh, cx + hw, cy + hh) # Top
    draw_line(cx + hw, cy + hh, cx + bottom_hw, cy) # right

def draw_left_arrow(cx, cy, size):
    draw_line(cx - size, cy, cx + size, cy) # horizontal line
    draw_line(cx - size, cy, cx - size + 8, cy + 11) # top arrow
    draw_line(cx - size, cy, cx - size + 8, cy - 11) # bottom arrow

def draw_play_icon(cx, cy, size):
    draw_line(cx - size//2, cy - size, cx - size//2, cy + size)
    draw_line(cx - size//2, cy + size, cx + size, cy)
    draw_line(cx + size, cy, cx - size//2, cy - size)

def draw_pause_icon(cx, cy, size):
    s = size // 2
    draw_line(cx - s + 3, cy - size, cx - s + 3, cy + size)
    draw_line(cx + s - 3, cy - size, cx + s - 3, cy + size)

def draw_cross(cx, cy, size):
    draw_line(cx - size, cy - size, cx + size, cy + size)
    draw_line(cx + size, cy - size, cx - size, cy + size)

DIAMOND_HW, DIAMOND_HH = 14, 20
CATCHER_HW, CATCHER_HH = 45, 14

class Diamond:
    def __init__(self):
        self.x = random.randint(60, W - 60)
        self.y = H - BTN_AREA_H - 10
        self.vy = 120.0 # pixels per second (starting speed) 120 fps
        self.color = (random.uniform(0.4, 1.0), random.uniform(0.4, 1.0), random.uniform(0.4, 1.0),)

class GameState:
    def __init__(self):
        self.reset()

    def reset(self):
        self.score       = 0
        self.over        = False
        self.paused      = False
        self.cheat       = False
        self.catcher_x   = W // 2
        self.catcher_y   = 50
        self.catcher_vx  = 0          # for smooth cheat movement
        self.diamond     = Diamond()
        self.speed_mult  = 1.0
        self.last_time   = time.time()
        self.elapsed     = 0.0        # total game time for speed up

gs = GameState()

# Button regions  (x/y center half-width, half-height) even though we only draw icons, we want a slightly larger clickable area for better experience here.
BTN_RESTART = (W//4,     H - BTN_AREA_H//2, 60, 25)
BTN_PAUSE   = (W//2,     H - BTN_AREA_H//2, 60, 25)
BTN_QUIT    = (3*W//4,   H - BTN_AREA_H//2, 60, 25)

def in_button(mx, my, btn):
    cx, cy, hw, hh = btn
    return abs(mx - cx) <= hw and abs(my - cy) <= hh

def draw_buttons():
    # Restart
    glColor3f(0.0, 0.9, 0.9)
    cx, cy, _, _ = BTN_RESTART
    draw_left_arrow(cx, cy, 14)

    # Play/Pause color
    glColor3f(1.0, 0.75, 0.0)
    cx, cy, _, _ = BTN_PAUSE
    if gs.paused:
        draw_play_icon(cx, cy, 14)
    else:
        draw_pause_icon(cx, cy, 14)

    # Quit – red cross
    glColor3f(1.0, 0.2, 0.2)
    cx, cy, _, _ = BTN_QUIT
    draw_cross(cx, cy, 14)

    # Divider line between button area and play area
    glColor3f(0.3, 0.3, 0.3)
    draw_line(0, H - BTN_AREA_H, W, H - BTN_AREA_H)

def draw_scene():
    glClear(GL_COLOR_BUFFER_BIT)
    draw_buttons()
    d = gs.diamond
    # random color diamond
    if not gs.over:
        glColor3f(*d.color)
        draw_diamond(int(d.x), int(d.y), DIAMOND_HW, DIAMOND_HH)

    # Color catcher
    if gs.over:
        glColor3f(1.0, 0.0, 0.0) # Red color
    else:
        glColor3f(1.0, 1.0, 1.0) # White color
    draw_catcher(gs.catcher_x, gs.catcher_y, CATCHER_HW, CATCHER_HH)
    glutSwapBuffers()

def check_collision():
    d = gs.diamond
    d_left  = d.x - DIAMOND_HW
    d_right = d.x + DIAMOND_HW
    d_bot   = d.y - DIAMOND_HH
    d_top   = d.y + DIAMOND_HH
    c_left  = gs.catcher_x - CATCHER_HW
    c_right = gs.catcher_x + CATCHER_HW
    c_bot   = gs.catcher_y
    c_top   = gs.catcher_y + CATCHER_HH + 8 
    return (d_left < c_right and d_right > c_left and
            d_bot  < c_top  and d_top  > c_bot)
CATCHER_SPEED = 200  

def update(value):
    glutTimerFunc(16, update, 0)
    now = time.time()
    dt  = now - gs.last_time
    gs.last_time = now
    if gs.over or gs.paused:
        glutPostRedisplay()
        return
    gs.elapsed += dt
    #  speed up every 5 seconds
    gs.speed_mult = 1.0 + gs.elapsed * 0.04
    d = gs.diamond

    # Cheat mode: press C
    if gs.cheat:
        diff = d.x - gs.catcher_x
        step = CATCHER_SPEED * dt
        if abs(diff) <= step:
            gs.catcher_x = int(d.x)
        else:
            gs.catcher_x += int(step * (1 if diff > 0 else -1))
    else:
        gs.catcher_x += int(gs.catcher_vx * dt)
        gs.catcher_x = max(CATCHER_HW, min(W - CATCHER_HW, gs.catcher_x))

    # Move diamond downward
    d.y -= d.vy * gs.speed_mult * dt

    # Collision
    if check_collision():
        gs.score += 1
        print(f"Caught! Score: {gs.score}")
        gs.diamond = Diamond()
        gs.diamond.vy = 120.0 + gs.score * 5 # accelerate with score too

    # Missed
    elif d.y + DIAMOND_HH < gs.catcher_y:
        gs.over = True
        print(f"Game Over! Final Score: {gs.score}")

    glutPostRedisplay()

# Input controls:
def key_down(key, x, y):
    if key == b'c' or key == b'C':
        if not gs.over:
            gs.cheat = not gs.cheat
            print("Cheat mode", "ON" if gs.cheat else "OFF")

def special_down(key, x, y):
    if gs.over or gs.paused or gs.cheat:
        return
    if key == GLUT_KEY_LEFT:
        gs.catcher_vx = -CATCHER_SPEED
    elif key == GLUT_KEY_RIGHT:
        gs.catcher_vx =  CATCHER_SPEED

def special_up(key, x, y):
    if key in (GLUT_KEY_LEFT, GLUT_KEY_RIGHT):
        gs.catcher_vx = 0

def mouse_click(button, state, mx, my):
    if button != GLUT_LEFT_BUTTON or state != GLUT_DOWN:
        return
    my = H - my # OpenGL y is flipped

    if in_button(mx, my, BTN_RESTART):
        print("Starting Over")
        gs.reset()

    elif in_button(mx, my, BTN_PAUSE):
        if not gs.over:
            gs.paused = not gs.paused

    elif in_button(mx, my, BTN_QUIT):
        print(f"Your score was: {gs.score}")
        glutLeaveMainLoop()

def init_gl():
    glClearColor(0.05, 0.05, 0.1, 1.0)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(0, W, 0, H)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    glPointSize(2.0)

def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
    glutInitWindowSize(W, H)
    glutInitWindowPosition(100, 100)
    glutCreateWindow(b"Catch the Diamonds!")
    init_gl()
    glutDisplayFunc(draw_scene)
    glutKeyboardFunc(key_down)
    glutSpecialFunc(special_down)
    glutSpecialUpFunc(special_up)
    glutMouseFunc(mouse_click)
    glutTimerFunc(16, update, 0)
    glutMainLoop()

if __name__ == "__main__":
    main()