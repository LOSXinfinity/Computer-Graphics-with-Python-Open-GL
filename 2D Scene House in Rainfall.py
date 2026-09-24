from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random

# Size
W_WIDTH, W_HEIGHT = 800, 450

# Rain drops
rain_bend = 0
rain_speed = 4
num_drops = 150
drops = [[random.randint(0, W_WIDTH), random.randint(0, W_HEIGHT)] for _ in range(num_drops)]

# Day / Night colors
bg_r, bg_g, bg_b = 0.05, 0.05, 0.15   # start night

def draw_rect(x, y, w, h, r, g, b):
    glColor3f(r, g, b)
    glBegin(GL_TRIANGLES)
    glVertex2f(x, y)
    glVertex2f(x + w, y)
    glVertex2f(x + w, y + h)

    glVertex2f(x, y)
    glVertex2f(x + w, y + h)
    glVertex2f(x, y + h)
    glEnd()

def draw_tri(x1, y1, x2, y2, x3, y3, r, g, b):
    glColor3f(r, g, b)
    glBegin(GL_TRIANGLES)
    glVertex2f(x1, y1)
    glVertex2f(x2, y2)
    glVertex2f(x3, y3)
    glEnd()

def draw_line(x1, y1, x2, y2, r, g, b):
    glColor3f(r, g, b)
    glBegin(GL_LINES)
    glVertex2f(x1, y1)
    glVertex2f(x2, y2)
    glEnd()

# Tree
def tree(x, y):
    glColor3f(0.0, 0.8, 0.0)
    glBegin(GL_TRIANGLES)
    glVertex2f(x - 25, y)
    glVertex2f(x + 25, y)
    glVertex2f(x, y + 70)
    glEnd()

def draw_scene():

    # Sky
    draw_rect(0, 330, 800, 120, bg_r, bg_g, bg_b)

    # Ground
    draw_rect(0, 0, 800, 330, 0.6, 0.4, 0.1)

    # Trees
    for x in range(0, 850, 50):
        tree(x, 250)

    # House Body
    draw_rect(230, 140, 340, 120, 1, 1, 0.9)

    # Roof
    draw_tri(210, 260, 590, 260, 400, 350, 0.3, 0.2, 0.6)

    # Door
    draw_rect(385, 140, 40, 80, 0.2, 0.5, 0.9)

    # Door Handle
    glPointSize(4)
    glColor3f(0, 0, 0)
    glBegin(GL_POINTS)
    glVertex2f(418, 180)
    glEnd()

    # Windows
    draw_rect(260, 190, 50, 40, 0.4, 0.6, 1.0)
    draw_line(260, 210, 310, 210, 0, 0, 0)
    draw_line(285, 190, 285, 230, 0, 0, 0)

    draw_rect(490, 190, 50, 40, 0.4, 0.6, 1.0)
    draw_line(490, 210, 540, 210, 0, 0, 0)
    draw_line(515, 190, 515, 230, 0, 0, 0)

# Rain
def draw_rain():
    for i in range(num_drops):
        draw_line(
            drops[i][0],
            drops[i][1],
            drops[i][0] + rain_bend,
            drops[i][1] - 12,
            0.6, 0.8, 1.0
        )

# Animation
def animate():
    global drops
    for i in range(num_drops):
        drops[i][1] -= rain_speed
        drops[i][0] += rain_bend * 0.1
        if drops[i][1] < 0:
            drops[i][1] = W_HEIGHT
            drops[i][0] = random.randint(-100, W_WIDTH + 100)
    glutPostRedisplay()

def special_input(key, x, y):
    global rain_bend
    if key == GLUT_KEY_LEFT:
        rain_bend -= 1
    if key == GLUT_KEY_RIGHT:
        rain_bend += 1

def keyboard_input(key, x, y):
    global bg_r, bg_g, bg_b
    # Day
    if key == b'd':
        bg_r = min(0.6, bg_r + 0.05)
        bg_g = min(0.8, bg_g + 0.05)
        bg_b = min(1.0, bg_b + 0.05)
    # Night
    if key == b'n':
        bg_r = max(0.05, bg_r - 0.05)
        bg_g = max(0.05, bg_g - 0.05)
        bg_b = max(0.15, bg_b - 0.05)

def display():
    glClearColor(bg_r, bg_g, bg_b, 1)
    glClear(GL_COLOR_BUFFER_BIT)
    glLoadIdentity()
    draw_scene()
    draw_rain()
    glutSwapBuffers()

def setup():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(0, W_WIDTH, 0, W_HEIGHT, -1, 1)
    glMatrixMode(GL_MODELVIEW)

def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
    glutInitWindowSize(W_WIDTH, W_HEIGHT)
    glutCreateWindow(b"Assignment 1 Task 1 - Building a House in Rainfall")
    setup()
    glutDisplayFunc(display)
    glutIdleFunc(animate)
    glutSpecialFunc(special_input)
    glutKeyboardFunc(keyboard_input)
    glutMainLoop()

if __name__ == "__main__":
    main()