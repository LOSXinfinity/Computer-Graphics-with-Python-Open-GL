import sys
import random
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

choices = ["rock", "paper", "scissors"]
result_text = "Click a button to start playing"

# Button definitions: [x, y, width, height, name, base_color]
# The window is 500 pixels wide and 500 pixels tall.
btn_rock = [50, 350, 100, 50, "Rock", (0.9, 0.3, 0.3)]
btn_paper = [200, 350, 100, 50, "Paper", (0.3, 0.8, 0.5)]
btn_scissors = [350, 350, 100, 50, "Scissors", (0.3, 0.5, 0.9)]

# Store all buttons in a list for easy access
buttons = [btn_rock, btn_paper, btn_scissors]

# Mouse tracking for hover effects
mouse_x = 0
mouse_y = 0
result_state = "none" # "none", "win", "lose", "tie"

def determine_winner(player, computer):
    global result_state
    # Core game logic
    if player == computer:
        result_state = "tie"
        return "Tie! Computer chose " + computer
    elif (player == "rock" and computer == "scissors") or \
         (player == "paper" and computer == "rock") or \
         (player == "scissors" and computer == "paper"):
        result_state = "win"
        return "You Win! Computer chose " + computer
    else:
        result_state = "lose"
        return "You Lose! Computer chose " + computer

def draw_text(x, y, text):
    # Set the start position for the text
    glRasterPos2f(x, y)
    # Draw each character one by one
    for character in text:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(character))

def draw_button(btn):
    # Unpack the button data
    x, y, w, h, name, base_color = btn
    
    # Check for hover
    is_hovered = (x <= mouse_x <= x + w) and (y <= mouse_y <= y + h)
    
    # Brighten color if hovered
    r, g, b = base_color
    if is_hovered:
        r = min(1.0, r + 0.2)
        g = min(1.0, g + 0.2)
        b = min(1.0, b + 0.2)
    
    # Draw subtle shadow
    glColor3f(0.0, 0.0, 0.0)
    glBegin(GL_QUADS)
    glVertex2f(x + 3, y + 3)
    glVertex2f(x + w + 3, y + 3)
    glVertex2f(x + w + 3, y + h + 3)
    glVertex2f(x + 3, y + h + 3)
    glEnd()

    # Draw button background
    glColor3f(r, g, b) 
    glBegin(GL_QUADS)
    glVertex2f(x, y)           # Top-left corner
    glVertex2f(x + w, y)       # Top-right corner
    glVertex2f(x + w, y + h)   # Bottom-right corner
    glVertex2f(x, y + h)       # Bottom-left corner
    glEnd()
    
    # Draw the text (white for better contrast on colors)
    glColor3f(1.0, 1.0, 1.0) 
    draw_text(x + 15, y + 30, name)

def draw_gradient_background():
    glBegin(GL_QUADS)
    # Top color (dark blue)
    glColor3f(0.05, 0.1, 0.2)
    glVertex2f(0, 0)
    glVertex2f(500, 0)
    # Bottom color (darker blue/black)
    glColor3f(0.01, 0.02, 0.05)
    glVertex2f(500, 500)
    glVertex2f(0, 500)
    glEnd()

def display():
    # Clear the screen
    glClear(GL_COLOR_BUFFER_BIT)
    
    draw_gradient_background()

    # Draw Title Text
    glColor3f(1.0, 0.8, 0.0) # Gold
    draw_text(150, 100, "ROCK PAPER SCISSORS")
    
    # Draw each button from our list
    for btn in buttons:
        draw_button(btn)
        
    # Draw the game result text with colors
    if result_state == "win":
        glColor3f(0.2, 1.0, 0.2) # Green
    elif result_state == "lose":
        glColor3f(1.0, 0.2, 0.2) # Red
    elif result_state == "tie":
        glColor3f(1.0, 1.0, 0.2) # Yellow
    else:
        glColor3f(1.0, 1.0, 1.0) # White
        
    draw_text(100, 250, result_text)
    
    # Swap buffers to show the graphics
    glutSwapBuffers()

def mouse_motion(x, y):
    global mouse_x, mouse_y
    mouse_x = x
    mouse_y = y
    glutPostRedisplay()

def mouse_click(button, state, x, y):
    global result_text
    
    # We only want to trigger logic when the left mouse button is pressed down
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        
        # Loop through all buttons to see if the mouse clicked inside one
        for btn in buttons:
            bx, by, bw, bh, name, _ = btn
            
            # Check if mouse X and Y are inside the button boundaries
            if bx <= x <= bx + bw and by <= y <= by + bh:
                
                # Convert button name to lowercase to match logic
                player_choice = name.lower() 
                computer_choice = random.choice(choices)
                
                # Update the result text
                result_text = determine_winner(player_choice, computer_choice)
                
                # Tell OpenGL to redraw the screen
                glutPostRedisplay()
                return

def init():
    # Set a dark gray background color
    glClearColor(0.2, 0.2, 0.2, 1.0) 
    
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    
    # Set up a 2D coordinate system matching the window size
    # Top-left is (0,0) and bottom-right is (500,500)
    gluOrtho2D(0.0, 500.0, 500.0, 0.0)
    
    glMatrixMode(GL_MODELVIEW)

def main():
    # Initialize the OpenGL window
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE)
    glutInitWindowSize(500, 500)
    glutCreateWindow(b"Rock Paper Scissors GUI")
    
    # Run our setup function
    init()
    
    # Connect our functions to OpenGL events
    glutDisplayFunc(display)
    glutMouseFunc(mouse_click) # Listen for mouse clicks
    glutPassiveMotionFunc(mouse_motion) # Listen for mouse movements
    
    # Start the continuous loop
    glutMainLoop()

if __name__ == "__main__":
    main()