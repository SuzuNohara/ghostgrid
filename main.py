import pygame
import sys
import os
from map import draw_grid
from kore import Kore

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
GRID_COLS = 20
GRID_ROWS = 10
CELL_WIDTH = SCREEN_WIDTH // GRID_COLS
CELL_HEIGHT = SCREEN_HEIGHT // GRID_ROWS

# Set up the screen in fullscreen mode
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("GhostGrid")

# Clock for controlling the frame rate
clock = pygame.time.Clock()

# Loading assets
ghost_path = os.path.join("assets", "ghost.png")
ghost_img = pygame.image.load(ghost_path)
if CELL_WIDTH > CELL_HEIGHT:
    ghost_img = pygame.transform.scale(ghost_img, (CELL_HEIGHT, CELL_HEIGHT))
else:
    ghost_img = pygame.transform.scale(ghost_img, (CELL_WIDTH, CELL_WIDTH))

font = pygame.font.SysFont(None, 24)

# Kore grid setup
kore = Kore(GRID_COLS, GRID_ROWS)
kore.create_connections()

# Set node positions to center of grid squares
for row in kore.nodes:
    for node in row:
        col, layer = map(int, node.id.split(','))
        node.position_x = col * CELL_WIDTH + CELL_WIDTH // 2
        node.position_y = layer * CELL_HEIGHT + CELL_HEIGHT // 2

def main():
    running = True
    ghost_x = (SCREEN_WIDTH - CELL_WIDTH) // 2
    ghost_y = (SCREEN_HEIGHT - CELL_HEIGHT) // 2

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

        screen.fill(BLACK)
        screen.blit(ghost_img, (ghost_x, ghost_y))
        draw_grid(GRID_COLS, GRID_ROWS, CELL_WIDTH, CELL_HEIGHT, SCREEN_WIDTH, SCREEN_HEIGHT, screen)

        # Draw only connection costs
        for row in kore.nodes:
            for node in row:
                for conn in node.connections:
                    if node.id < conn.node_b:
                        # Find neighbor node
                        neighbor = None
                        for r in kore.nodes:
                            for n in r:
                                if n.id == conn.node_b:
                                    neighbor = n
                                    break
                            if neighbor:
                                break
                        if neighbor:
                            start = (node.position_x, node.position_y)
                            end = (neighbor.position_x, neighbor.position_y)
                            # Draw cost at midpoint
                            mid = ((start[0] + end[0]) // 2, (start[1] + end[1]) // 2)
                            cost_surf = font.render(str(conn.cost), True, (255, 255, 0))
                            cost_rect = cost_surf.get_rect(center=mid)
                            screen.blit(cost_surf, cost_rect)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()