from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random

WINDOW_WIDTH, WINDOW_HEIGHT = 800, 450
points = []   # Each point: {'x','y','dx','dy','color'}

speed_multiplier = 1.0
is_frozen = False
is_blinking = False

blink_state = True
blink_counter = 0

def convert_coordinate(x, y):
    # Convert screen (top-left origin) to OpenGL center origin
    a = x - (WINDOW_WIDTH / 2)
    b = (WINDOW_HEIGHT / 2) - y
    return a, b

def draw_points():
    glPointSize(5)
    glBegin(GL_POINTS)
    for p in points:
        if is_blinking and not blink_state:
            glColor3f(0, 0, 0)
        else:
            glColor3f(p['color'][0], p['color'][1], p['color'][2])
        glVertex2f(p['x'], p['y'])
    glEnd()

def draw_boundary():
    glColor3f(1.0, 1.0, 1.0)
    glLineWidth(2)
    glBegin(GL_LINES)

    glVertex2f(-245, -245); glVertex2f(245, -245)
    glVertex2f(245, -245);  glVertex2f(245, 245)
    glVertex2f(245, 245);   glVertex2f(-245, 245)
    glVertex2f(-245, 245);  glVertex2f(-245, -245)
    glEnd()

def animate():
    global blink_counter, blink_state

    if not is_frozen:

        # Move points
        for p in points:
            p['x'] += p['dx'] * speed_multiplier
            p['y'] += p['dy'] * speed_multiplier

            # Bounce from wall
            if p['x'] >= 245 or p['x'] <= -245:
                p['dx'] *= -1
            if p['y'] >= 245 or p['y'] <= -245:
                p['dy'] *= -1
        # Blinking control
        if is_blinking:
            blink_counter += 1
            if blink_counter > 60:  # roughly one second
                blink_state = not blink_state
                blink_counter = 0
    glutPostRedisplay()


# Input Keyboard: Spacebar to freeze/unfreeze, Up/Down to change speed
def keyboard_listener(key, x, y):
    global is_frozen
    if key == b' ':   # Spacebar
        is_frozen = not is_frozen
        print("Frozen" if is_frozen else "Resumed")


def special_key_listener(key, x, y):
    global speed_multiplier
    if not is_frozen:
        if key == GLUT_KEY_UP:
            speed_multiplier += 0.5
            print("Speed:", speed_multiplier)
        elif key == GLUT_KEY_DOWN:
            speed_multiplier = max(0.1, speed_multiplier - 0.5)
            print("Speed:", speed_multiplier)

# Input: Mouse Click
def mouse_listener(button, state, x, y):
    global is_blinking
    if is_frozen:
        return
    mx, my = convert_coordinate(x, y)

    # Right Click create new moving point
    if button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:
        new_point = {
            'x': mx,
            'y': my,
            'dx': random.choice([-1, 1]) * random.uniform(0.5, 2.0),
            'dy': random.choice([-1, 1]) * random.uniform(0.5, 2.0),
            'color': (random.random(), random.random(), random.random())
        }
        points.append(new_point)
        print("Point added at:", mx, my)

    # Left Click toggle blinking
    elif button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        is_blinking = not is_blinking
        print("Blinking:", is_blinking)

def setup_projection():
    glViewport(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(-250, 250, -250, 250, 0, 1)
    glMatrixMode(GL_MODELVIEW)

def display():
    glClear(GL_COLOR_BUFFER_BIT)
    glLoadIdentity()
    setup_projection()
    draw_boundary()
    draw_points()
    glutSwapBuffers()

def main():
    glutInit()
    glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE)
    glutInitWindowSize(WINDOW_WIDTH, WINDOW_HEIGHT)
    glutInitWindowPosition(100, 100)
    glutCreateWindow(b"Assignment 1 Task 2 - Building the Amazing Box")
    glutDisplayFunc(display)
    glutIdleFunc(animate)
    glutKeyboardFunc(keyboard_listener)
    glutSpecialFunc(special_key_listener)
    glutMouseFunc(mouse_listener)
    glClearColor(0, 0, 0, 1)
    glutMainLoop()

if __name__ == "__main__":
    main()