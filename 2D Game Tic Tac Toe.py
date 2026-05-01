import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import math

# TIC-TAC-TOE LOGIC AND AI IMPLEMENTATION

class TicTacToe:
    """Tic-Tac-Toe game implementation with Minimax AI"""

    def __init__(self):
        self.board = [[' ' for _ in range(3)] for _ in range(3)]
        self.current_player = 'X'  # X is AI (maximizer), O is Human (minimizer)

    def is_winner(self, player):
        for row in self.board:
            if all(cell == player for cell in row): return True
        for col in range(3):
            if all(self.board[row][col] == player for row in range(3)): return True
        if all(self.board[i][i] == player for i in range(3)): return True
        if all(self.board[i][2-i] == player for i in range(3)): return True
        return False

    def is_full(self):
        return all(cell != ' ' for row in self.board for cell in row)

    def is_terminal(self):
        return self.is_winner('X') or self.is_winner('O') or self.is_full()

    def evaluate(self):
        if self.is_winner('X'): return 10
        elif self.is_winner('O'): return -10
        else: return 0

    def get_available_moves(self):
        moves = []
        for i in range(3):
            for j in range(3):
                if self.board[i][j] == ' ':
                    moves.append((i, j))
        return moves

    def make_move(self, row, col, player):
        if self.board[row][col] == ' ':
            self.board[row][col] = player
            return True
        return False

    def undo_move(self, row, col):
        self.board[row][col] = ' '

    def minimax_decision(self, depth=9, use_alpha_beta=True):
        best_score = -math.inf
        best_move = None

        for row, col in self.get_available_moves():
            self.make_move(row, col, 'X')
            
            if use_alpha_beta:
                score = self._alpha_beta(depth - 1, -math.inf, math.inf, False)
            else:
                score = self._minimax(depth - 1, False)
                
            self.undo_move(row, col)

            if score > best_score:
                best_score = score
                best_move = (row, col)

        return best_move

    def _minimax(self, depth, is_maximizing):
        """Internal minimax function without pruning"""
        if depth == 0 or self.is_terminal():
            return self.evaluate()

        if is_maximizing:
            max_eval = -math.inf
            for row, col in self.get_available_moves():
                self.make_move(row, col, 'X')
                eval_score = self._minimax(depth - 1, False)
                self.undo_move(row, col)
                max_eval = max(max_eval, eval_score)
            return max_eval
        else:
            min_eval = math.inf
            for row, col in self.get_available_moves():
                self.make_move(row, col, 'O')
                eval_score = self._minimax(depth - 1, True)
                self.undo_move(row, col)
                min_eval = min(min_eval, eval_score)
            return min_eval

    def _alpha_beta(self, depth, alpha, beta, is_maximizing):
        """Internal alpha-beta function with pruning"""
        if depth == 0 or self.is_terminal():
            return self.evaluate()

        if is_maximizing:
            max_eval = -math.inf
            for row, col in self.get_available_moves():
                self.make_move(row, col, 'X')
                eval_score = self._alpha_beta(depth - 1, alpha, beta, False)
                self.undo_move(row, col)
                max_eval = max(max_eval, eval_score)
                alpha = max(alpha, eval_score)
                if beta <= alpha: break
            return max_eval
        else:
            min_eval = math.inf
            for row, col in self.get_available_moves():
                self.make_move(row, col, 'O')
                eval_score = self._alpha_beta(depth - 1, alpha, beta, True)
                self.undo_move(row, col)
                min_eval = min(min_eval, eval_score)
                beta = min(beta, eval_score)
                if beta <= alpha: break
            return min_eval


# OPENGL GRAPHICS & MAIN LOOP 

def draw_grid():
    """Draws the 3x3 Tic-Tac-Toe grid with a neon glow effect"""
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    
    # Glow layer
    glColor4f(0.27, 0.28, 0.35, 0.3)
    glLineWidth(8)
    glBegin(GL_LINES)
    glVertex2f(150, 100); glVertex2f(150, 400)
    glVertex2f(250, 100); glVertex2f(250, 400)
    glVertex2f(50, 200); glVertex2f(350, 200)
    glVertex2f(50, 300); glVertex2f(350, 300)
    glEnd()
    
    # Core layer
    glColor4f(0.35, 0.36, 0.45, 1.0)
    glLineWidth(3)
    glBegin(GL_LINES)
    glVertex2f(150, 100); glVertex2f(150, 400)
    glVertex2f(250, 100); glVertex2f(250, 400)
    glVertex2f(50, 200); glVertex2f(350, 200)
    glVertex2f(50, 300); glVertex2f(350, 300)
    glEnd()
    glDisable(GL_BLEND)

def draw_x(row, col):
    """Draws an X at the specified grid position with neon glow"""
    x1 = 50 + col * 100 + 20
    y1 = 100 + row * 100 + 20
    x2 = 50 + col * 100 + 80
    y2 = 100 + row * 100 + 80

    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    
    # Glow
    glColor4f(0.95, 0.54, 0.65, 0.4) # Pinkish Red
    glLineWidth(8)
    glBegin(GL_LINES)
    glVertex2f(x1, y1); glVertex2f(x2, y2)
    glVertex2f(x2, y1); glVertex2f(x1, y2)
    glEnd()
    
    # Core
    glColor4f(1.0, 0.7, 0.8, 1.0)
    glLineWidth(4)
    glBegin(GL_LINES)
    glVertex2f(x1, y1); glVertex2f(x2, y2)
    glVertex2f(x2, y1); glVertex2f(x1, y2)
    glEnd()
    glDisable(GL_BLEND)

def draw_o(row, col):
    """Draws an O at the specified grid position with neon glow"""
    cx = 50 + col * 100 + 50
    cy = 100 + row * 100 + 50
    radius = 30
    
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    
    # Glow
    glColor4f(0.53, 0.7, 0.98, 0.4) # Soft Blue
    glLineWidth(8)
    glBegin(GL_LINE_LOOP)
    for i in range(40):
        theta = 2.0 * math.pi * i / 40.0
        glVertex2f(cx + radius * math.cos(theta), cy + radius * math.sin(theta))
    glEnd()
    
    # Core
    glColor4f(0.7, 0.85, 1.0, 1.0)
    glLineWidth(4)
    glBegin(GL_LINE_LOOP)
    for i in range(40):
        theta = 2.0 * math.pi * i / 40.0
        glVertex2f(cx + radius * math.cos(theta), cy + radius * math.sin(theta))
    glEnd()
    glDisable(GL_BLEND)

def draw_board(game):
    """Iterates through the game state and draws X and O shapes"""
    draw_grid()
    for row in range(3):
        for col in range(3):
            if game.board[row][col] == 'X':
                draw_x(row, col)
            elif game.board[row][col] == 'O':
                draw_o(row, col)

def draw_rect(x, y, w, h, color):
    """Draw a solid colored rectangle"""
    glColor4f(color[0], color[1], color[2], 1.0)
    glBegin(GL_QUADS)
    glVertex2f(x, y)
    glVertex2f(x+w, y)
    glVertex2f(x+w, y+h)
    glVertex2f(x, y+h)
    glEnd()

def draw_text_centered(y, text, font, color=(255, 255, 255), window_width=400):
    """Render transparent text centered horizontally using Pygame tobytes and OpenGL"""
    text_surface = font.render(text, True, color)
    text_data = pygame.image.tobytes(text_surface, "RGBA", True)
    x = (window_width - text_surface.get_width()) // 2
    
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glRasterPos2d(x, y + text_surface.get_height())
    glDrawPixels(text_surface.get_width(), text_surface.get_height(), GL_RGBA, GL_UNSIGNED_BYTE, text_data)
    glDisable(GL_BLEND)

def main():
    pygame.init()
    pygame.font.init()
    
    # Slightly larger display to fit UI nicely
    display = (400, 500)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
    pygame.display.set_caption("Neon Tic-Tac-Toe AI")

    # Load fonts
    try:
        font = pygame.font.SysFont('Arial', 24, bold=True)
        font_large = pygame.font.SysFont('Arial', 40, bold=True)
        font_title = pygame.font.SysFont('Arial', 50, bold=True)
    except:
        font = pygame.font.Font(None, 36)
        font_large = pygame.font.Font(None, 56)
        font_title = pygame.font.Font(None, 70)

    # Setup 2D projection
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(0, 400, 500, 0)
    glMatrixMode(GL_MODELVIEW)

    game = TicTacToe()
    game_over = False
    game_over_screen = False
    winner = None
    
    menu_active = True
    use_alpha_beta = True

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = event.pos
                
                if menu_active:
                    # Check if clicked Easy (100, 200, 200, 60)
                    if 100 <= mouse_x <= 300 and 200 <= mouse_y <= 260:
                        use_alpha_beta = False
                        menu_active = False
                    # Check if clicked Hard (100, 300, 200, 60)
                    elif 100 <= mouse_x <= 300 and 300 <= mouse_y <= 360:
                        use_alpha_beta = True
                        menu_active = False
                elif game_over_screen:
                    # Check if clicked Restart (100, 300, 200, 60)
                    if 100 <= mouse_x <= 300 and 300 <= mouse_y <= 360:
                        game = TicTacToe()
                        game_over = False
                        game_over_screen = False
                        menu_active = True
                        winner = None
                elif game.current_player == 'O' and not game_over:
                    # Check if clicked within the 300x300 board area offset by (50, 100)
                    if 50 <= mouse_x <= 350 and 100 <= mouse_y <= 400:
                        col = (mouse_x - 50) // 100
                        row = (mouse_y - 100) // 100
                        
                        if game.make_move(row, col, 'O'):
                            game.current_player = 'X'

        # Background color
        glClearColor(0.12, 0.12, 0.18, 1.0) # Dark rich background
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        if menu_active:
            draw_text_centered(80, "TIC TAC TOE", font_title, (205, 214, 244))
            
            # Easy Button (Teal)
            draw_rect(100, 200, 200, 60, (0.16, 0.63, 0.60))
            draw_text_centered(215, "EASY", font, (255, 255, 255))
            
            # Hard Button (Red)
            draw_rect(100, 300, 200, 60, (0.87, 0.35, 0.45))
            draw_text_centered(315, "HARD", font, (255, 255, 255))
            
            pygame.display.flip()
            pygame.time.wait(10)
            continue

        # AI Turn
        if game.current_player == 'X' and not game.is_terminal() and not game_over:
            # Render board immediately so user sees their own move
            draw_board(game)
            pygame.display.flip()
            
            move = game.minimax_decision(use_alpha_beta=use_alpha_beta)
            if move:
                game.make_move(move[0], move[1], 'X')
                game.current_player = 'O'
            
            # Clear again so the main render phase handles the new state properly
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Check for game end
        if game.is_terminal() and not game_over:
            game_over = True
            game_over_screen = True
            if game.is_winner('X'):
                winner = 'X'
            elif game.is_winner('O'):
                winner = 'O'
            else:
                winner = 'Draw'

        # Render Core Game
        draw_board(game)

        # End Screen Overlay
        if game_over_screen:
            # Dark transparent overlay
            glEnable(GL_BLEND)
            glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
            glColor4f(0, 0, 0, 0.8)
            glBegin(GL_QUADS)
            glVertex2f(0, 0); glVertex2f(400, 0)
            glVertex2f(400, 500); glVertex2f(0, 500)
            glEnd()
            glDisable(GL_BLEND)
            
            # Display Winner Text
            if winner == 'X':
                draw_text_centered(120, "AI WINS!", font_large, (243, 139, 168))
            elif winner == 'O':
                draw_text_centered(120, "YOU WIN!", font_large, (137, 180, 250))
            else:
                draw_text_centered(120, "IT'S A TIE!", font_large, (205, 214, 244))
                
            # Restart Button (Green)
            draw_rect(100, 300, 200, 60, (0.65, 0.89, 0.63))
            draw_text_centered(315, "RESTART", font, (30, 30, 46))

        pygame.display.flip()
        pygame.time.wait(10)

if __name__ == "__main__":
    main()