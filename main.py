import pygame
import sys
import os
from map import draw_grid

# Initialize pygame
pygame.init()

# Constants
FPS = 30
BLACK = (0, 0, 0)
MOVE_SPEED = 10

# Getting screen dimensions
screen_info = pygame.display.Info()
SCREEN_WIDTH = screen_info.current_w
SCREEN_HEIGHT = screen_info.current_h

# Generating grid dimensions
GRID_COLS = 30
GRID_ROWS = 15
CELL_WIDTH = SCREEN_WIDTH // GRID_COLS
CELL_HEIGHT = SCREEN_HEIGHT // GRID_ROWS

# Set up the screen in fullscreen mode
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("GhostGrid")

# Clock for controlling the frame rate
clock = pygame.time.Clock()

# Loading assets
ghost_path = os.path.join("assets", "ghost.png")
sentinel_path = os.path.join("assets", "sentinel.png")
node_path = os.path.join("assets", "node.png")
connection_path = os.path.join("assets", "connection.png")

ghost_img = pygame.image.load(ghost_path)
if CELL_WIDTH > CELL_HEIGHT:
    ghost_img = pygame.transform.scale(ghost_img, (CELL_HEIGHT, CELL_HEIGHT))
else:
    ghost_img = pygame.transform.scale(ghost_img, (CELL_WIDTH, CELL_WIDTH))

def main():
    running = True
    ghost_x = (SCREEN_WIDTH - CELL_WIDTH) // 2
    ghost_y = (SCREEN_HEIGHT - CELL_HEIGHT) // 2

    while running:
        # Exit mechanism
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

        # Movement controls (uncomment to enable)
        # keys = pygame.key.get_pressed()
        # if keys[pygame.K_LEFT] or keys[pygame.K_a]:
        #     ghost_x -= MOVE_SPEED
        # if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        #     ghost_x += MOVE_SPEED
        # if keys[pygame.K_UP] or keys[pygame.K_w]:
        #     ghost_y -= MOVE_SPEED
        # if keys[pygame.K_DOWN] or keys[pygame.K_s]:
        #     ghost_y += MOVE_SPEED

        # Keep ghost within screen bounds
        # ghost_x = max(0, min(ghost_x, SCREEN_WIDTH - CELL_WIDTH))
        # ghost_y = max(0, min(ghost_y, SCREEN_HEIGHT - CELL_HEIGHT))

        screen.fill(BLACK)
        screen.blit(ghost_img, (ghost_x, ghost_y))
        draw_grid(GRID_COLS, GRID_ROWS, CELL_WIDTH, CELL_HEIGHT, SCREEN_WIDTH, SCREEN_HEIGHT, screen)
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()