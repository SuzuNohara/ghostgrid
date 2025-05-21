import pygame

def draw_grid(GRID_COLS, GRID_ROWS, CELL_WIDTH, CELL_HEIGHT, SCREEN_WIDTH, SCREEN_HEIGHT, screen):
    # Draw map
    for col in range(GRID_COLS + 1):
        x = col * CELL_WIDTH
        pygame.draw.line(screen, (50, 50, 50), (x, 0), (x, SCREEN_HEIGHT), 1)

    for row in range(GRID_ROWS + 1):
        y = row * CELL_HEIGHT
        pygame.draw.line(screen, (50, 50, 50), (0, y), (SCREEN_WIDTH, y), 1)