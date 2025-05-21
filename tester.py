import pygame
from kore import Kore

# Get screen size
pygame.init()
screen_info = pygame.display.Info()
WIDTH = screen_info.current_w
HEIGHT = screen_info.current_h

# Grid and display settings
NODES_PER_LAYER = 10
LAYERS = 6
NODE_RADIUS = 16
LINE_COLOR = (100, 200, 255)
NODE_COLOR = (255, 100, 100)
BG_COLOR = (30, 30, 30)

PX = WIDTH // (NODES_PER_LAYER + 1)
PY = HEIGHT // (LAYERS + 1)

screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("Kore Node Grid Tester")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 24)

# Create Kore grid and connections
kore = Kore(NODES_PER_LAYER, LAYERS)
kore.create_connections()

def get_screen_pos(node):
    return (node.position_x * PX + PX, node.position_y * PY + PY)

# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT or \
           (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            running = False

    screen.fill(BG_COLOR)

    # Draw connections and costs
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
                        start = get_screen_pos(node)
                        end = get_screen_pos(neighbor)
                        pygame.draw.line(screen, LINE_COLOR, start, end, 2)
                        # Draw cost at midpoint
                        mid = ((start[0] + end[0]) // 2, (start[1] + end[1]) // 2)
                        cost_surf = font.render(str(conn.cost), True, (255, 255, 0))
                        cost_rect = cost_surf.get_rect(center=mid)
                        screen.blit(cost_surf, cost_rect)

    # Draw nodes
    for row in kore.nodes:
        for node in row:
            pygame.draw.circle(screen, NODE_COLOR, get_screen_pos(node), NODE_RADIUS)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()