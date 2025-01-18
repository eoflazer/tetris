import pygame
import random

# Initialize Pygame
pygame.init()

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
CYAN = (0, 255, 255)
YELLOW = (255, 255, 0)
MAGENTA = (255, 255, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
ORANGE = (255, 165, 0)
GRAY = (128, 128, 128)

# Game dimensions
BLOCK_SIZE = 30
GRID_WIDTH = 10
GRID_HEIGHT = 20
SCREEN_WIDTH = BLOCK_SIZE * (GRID_WIDTH + 6)
SCREEN_HEIGHT = BLOCK_SIZE * GRID_HEIGHT

# Tetromino shapes
SHAPES = [
    [[1, 1, 1, 1]],  # I
    [[1, 1], [1, 1]],  # O
    [[1, 1, 1], [0, 1, 0]],  # T
    [[1, 1, 1], [1, 0, 0]],  # L
    [[1, 1, 1], [0, 0, 1]],  # J
    [[1, 1, 0], [0, 1, 1]],  # S
    [[0, 1, 1], [1, 1, 0]]   # Z
]

SHAPE_COLORS = [CYAN, YELLOW, MAGENTA, ORANGE, BLUE, GREEN, RED]

class Tetris:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption('Tetris')
        self.clock = pygame.time.Clock()
        
        # Load and scale background image
        self.background = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.background.fill((40, 44, 52))
        for i in range(GRID_HEIGHT):
            for j in range(GRID_WIDTH):
                pygame.draw.rect(self.background, (50, 54, 62),
                               (j * BLOCK_SIZE, i * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 1)
        
        self.reset_game()
        self.paused = False
        self.line_clear_animation = None
        self.line_clear_frames = 0

    def reset_game(self):
        self.grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.current_piece = self.new_piece()
        self.game_over = False
        self.score = 0
        self.fall_time = 0
        self.fall_speed = 500
        self.next_piece = self.new_piece()

    def new_piece(self):
        shape = random.randint(0, len(SHAPES) - 1)
        return {
            'shape': SHAPES[shape],
            'color': SHAPE_COLORS[shape],
            'x': GRID_WIDTH // 2 - len(SHAPES[shape][0]) // 2,
            'y': 0
        }

    def valid_move(self, piece, x, y):
        for i, row in enumerate(piece['shape']):
            for j, cell in enumerate(row):
                if cell:
                    if (not 0 <= x + j < GRID_WIDTH or
                        not 0 <= y + i < GRID_HEIGHT or
                        self.grid[y + i][x + j]):
                        return False
        return True

    def place_piece(self):
        for i, row in enumerate(self.current_piece['shape']):
            for j, cell in enumerate(row):
                if cell:
                    self.grid[self.current_piece['y'] + i][self.current_piece['x'] + j] = self.current_piece['color']
        self.clear_lines()
        self.current_piece = self.next_piece
        self.next_piece = self.new_piece()
        if not self.valid_move(self.current_piece, self.current_piece['x'], self.current_piece['y']):
            self.game_over = True

    def clear_lines(self):
        lines_to_clear = []
        for i in range(GRID_HEIGHT):
            if all(self.grid[i]):
                lines_to_clear.append(i)
        
        if lines_to_clear:
            self.line_clear_animation = lines_to_clear
            self.line_clear_frames = 10
            self.score += len(lines_to_clear) * 100

    def update_line_clear_animation(self):
        if self.line_clear_animation and self.line_clear_frames > 0:
            self.line_clear_frames -= 1
            if self.line_clear_frames == 0:
                for line in sorted(self.line_clear_animation, reverse=True):
                    del self.grid[line]
                    self.grid.insert(0, [0 for _ in range(GRID_WIDTH)])
                self.line_clear_animation = None
            return True
        return False

    def draw_block(self, x, y, color, alpha=255):
        s = pygame.Surface((BLOCK_SIZE - 2, BLOCK_SIZE - 2))
        s.fill(color)
        if alpha != 255:
            s.set_alpha(alpha)
        
        # Add gradient effect
        pygame.draw.line(s, (min(color[0] + 50, 255), min(color[1] + 50, 255), min(color[2] + 50, 255)), 
                        (0, 0), (BLOCK_SIZE - 2, 0), 2)
        pygame.draw.line(s, (max(color[0] - 50, 0), max(color[1] - 50, 0), max(color[2] - 50, 0)), 
                        (0, BLOCK_SIZE - 3), (BLOCK_SIZE - 2, BLOCK_SIZE - 3), 2)
        
        self.screen.blit(s, (x * BLOCK_SIZE + 1, y * BLOCK_SIZE + 1))

    def draw(self):
        # Draw background
        self.screen.blit(self.background, (0, 0))
        
        # Draw grid
        for i in range(GRID_HEIGHT):
            for j in range(GRID_WIDTH):
                if self.grid[i][j]:
                    # If line is being cleared, make it flash
                    if self.line_clear_animation and i in self.line_clear_animation:
                        alpha = int(255 * (self.line_clear_frames / 10))
                        self.draw_block(j, i, self.grid[i][j], alpha)
                    else:
                        self.draw_block(j, i, self.grid[i][j])

        # Draw current piece
        if self.current_piece and not self.game_over and not self.paused:
            for i, row in enumerate(self.current_piece['shape']):
                for j, cell in enumerate(row):
                    if cell:
                        self.draw_block(self.current_piece['x'] + j, 
                                      self.current_piece['y'] + i, 
                                      self.current_piece['color'])

        # Draw score
        font = pygame.font.Font(None, 36)
        score_text = font.render(f'Score: {self.score}', True, WHITE)
        self.screen.blit(score_text, (GRID_WIDTH * BLOCK_SIZE + 10, 20))

        # Draw pause screen
        if self.paused:
            s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            s.set_alpha(128)
            s.fill((0, 0, 0))
            self.screen.blit(s, (0, 0))
            
            pause_font = pygame.font.Font(None, 74)
            pause_text = pause_font.render('PAUSED', True, WHITE)
            pause_rect = pause_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2))
            self.screen.blit(pause_text, pause_rect)
            
            instruction_font = pygame.font.Font(None, 36)
            instruction_text = instruction_font.render('Press P to resume', True, WHITE)
            instruction_rect = instruction_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2 + 50))
            self.screen.blit(instruction_text, instruction_rect)

        # Draw game over screen
        if self.game_over:
            s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            s.set_alpha(128)
            s.fill((0, 0, 0))
            self.screen.blit(s, (0, 0))
            
            game_over_font = pygame.font.Font(None, 74)
            game_over_text = game_over_font.render('GAME OVER', True, WHITE)
            game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2 - 50))
            self.screen.blit(game_over_text, game_over_rect)
            
            score_text = font.render(f'Final Score: {self.score}', True, WHITE)
            score_rect = score_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2 + 10))
            self.screen.blit(score_text, score_rect)
            
            restart_text = font.render('Press R to restart', True, WHITE)
            restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2 + 50))
            self.screen.blit(restart_text, restart_rect)

        pygame.display.flip()

    def run(self):
        running = True
        while running:
            self.clock.tick(60)
            current_time = pygame.time.get_ticks()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_p:  # Pause
                        self.paused = not self.paused
                    if event.key == pygame.K_r and self.game_over:  # Restart
                        self.reset_game()
                    if not self.paused and not self.game_over:
                        if event.key == pygame.K_LEFT:
                            if self.valid_move(self.current_piece, self.current_piece['x'] - 1, self.current_piece['y']):
                                self.current_piece['x'] -= 1
                        elif event.key == pygame.K_RIGHT:
                            if self.valid_move(self.current_piece, self.current_piece['x'] + 1, self.current_piece['y']):
                                self.current_piece['x'] += 1
                        elif event.key == pygame.K_DOWN:
                            if self.valid_move(self.current_piece, self.current_piece['x'], self.current_piece['y'] + 1):
                                self.current_piece['y'] += 1
                        elif event.key == pygame.K_UP:
                            self.rotate_piece()
                        elif event.key == pygame.K_SPACE:
                            while self.valid_move(self.current_piece, self.current_piece['x'], self.current_piece['y'] + 1):
                                self.current_piece['y'] += 1
                            self.place_piece()

            if not self.paused and not self.game_over:
                # Handle piece falling
                if not self.update_line_clear_animation():  # Only fall if not animating
                    if current_time - self.fall_time > self.fall_speed:
                        self.fall_time = current_time
                        if self.valid_move(self.current_piece, self.current_piece['x'], self.current_piece['y'] + 1):
                            self.current_piece['y'] += 1
                        else:
                            self.place_piece()

            self.draw()

    def rotate_piece(self):
        # Get the rotated shape (rotate 90 degrees clockwise)
        rotated_shape = list(zip(*reversed(self.current_piece['shape'])))
        
        # Check if the rotation is valid
        if self.valid_move({'shape': rotated_shape, 
                           'x': self.current_piece['x'], 
                           'y': self.current_piece['y']},
                          self.current_piece['x'], 
                          self.current_piece['y']):
            self.current_piece['shape'] = rotated_shape

if __name__ == '__main__':
    game = Tetris()
    game.run()
    pygame.quit() 