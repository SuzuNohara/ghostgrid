import pygame
import sys
import os
import random
from map import draw_grid
from kore import Kore
from Sentinel import Sentinel
from Node import Node, Connection
from Ghost import Ghost

# Constants
FPS = 30
BLACK = (0, 0, 0)
GRID_COLS = 20
GRID_ROWS = 10

def load_assets(cell_width, cell_height):
    ghost_path = os.path.join("assets", "ghost.png")
    ghost_img = pygame.image.load(ghost_path)
    ghost_img = pygame.transform.scale(ghost_img, (cell_width, cell_height))

    sentinel_path = os.path.join("assets", "sentinel.png")
    sentinel_img = pygame.image.load(sentinel_path)
    sentinel_img = pygame.transform.scale(sentinel_img, (cell_width, cell_height))

    return ghost_img, sentinel_img

def gen_name(kind="ghost"):
    if kind == "ghost":
        ADJECTIVES = [
            "Spooky", "Misty", "Creepy", "Silent", "Ghastly", "Shadow", "Eerie", "Phantom", "Wailing", "Flickering"
        ]
        NOUNS = [
            "Wisp", "Shade", "Specter", "Spirit", "Apparition", "Haunt", "Poltergeist", "Banshee", "Revenant", "Shade"
        ]
    elif kind == "sentinel":
        ADJECTIVES = [
            "Iron", "Brave", "Steadfast", "Vigilant", "Bold", "Silent", "Stalwart", "Fierce", "Lone", "Swift"
        ]
        NOUNS = [
            "Guardian", "Watcher", "Protector", "Warden", "Sentinel", "Defender", "Keeper", "Patroller", "Scout", "Shield"
        ]
    else:
        raise ValueError("Unknown kind for name generation")
    adjective = random.choice(ADJECTIVES)
    noun = random.choice(NOUNS)
    number = random.randint(1, 99)
    return f"{adjective}{noun}{number}"

def build_environment(grid_cols, grid_rows, cell_width, cell_height):
    kore = Kore(grid_cols, grid_rows)
    kore.create_connections()
    for row in kore.nodes:
        for node in row:
            col, layer = map(int, node.id.split(','))
            node.position_x = col * cell_width + cell_width // 2
            node.position_y = layer * cell_height + cell_height // 2

    all_nodes = [node for row in kore.nodes for node in row]
    ghost_nodes = random.sample(all_nodes, 5)
    for node in ghost_nodes:
        ghost = Ghost(gen_name("ghost"), node.position_x, node.position_y, 0, False, False, 100)
        node.ghosts.append(ghost)
    money_left = 100
    for i, node in enumerate(ghost_nodes):
        if i == 4:
            node.money += money_left
        else:
            amount = random.randint(0, money_left)
            node.money += amount
            money_left -= amount
    sentinel_nodes = random.choices(all_nodes, k=10)
    for node in sentinel_nodes:
        sentinel = Sentinel(gen_name("sentinel"), node.position_x, node.position_y, 0, False, False, 100)
        node.sentinels.append(sentinel)
    return kore

def draw_environment(screen, kore, ghost_img, sentinel_img, cell_width, cell_height, font):
    draw_grid(GRID_COLS, GRID_ROWS, cell_width, cell_height, screen.get_width(), screen.get_height(), screen)
    drawn_connections = set()
    for row in kore.nodes:
        for node in row:
            for ghost in node.ghosts:
                screen.blit(ghost_img, (node.position_x - cell_width // 2, node.position_y - cell_height // 2))
            for sentinel in node.sentinels:
                screen.blit(sentinel_img, (node.position_x - cell_width // 2, node.position_y - cell_height // 2))
            for conn in node.connections:
                pair = tuple(sorted([node.id, conn.node_b]))
                if pair not in drawn_connections:
                    neighbor = None
                    for r in kore.nodes:
                        for n in r:
                            if n.id == conn.node_b:
                                neighbor = n
                                break
                        if neighbor:
                            break
                    if neighbor:
                        # Only draw if either node or neighbor has ghosts, sentinels, or money
                        if (node.ghosts or node.sentinels or node.money > 0 or
                            neighbor.ghosts or neighbor.sentinels or neighbor.money > 0):
                            mid = ((node.position_x + neighbor.position_x) // 2, (node.position_y + neighbor.position_y) // 2)
                            cost_surf = font.render(str(conn.cost), True, (255, 255, 0))
                            cost_rect = cost_surf.get_rect(center=mid)
                            screen.blit(cost_surf, cost_rect)
                    drawn_connections.add(pair)

def main():
    pygame.init()
    screen_info = pygame.display.Info()
    screen = pygame.display.set_mode((screen_info.current_w, screen_info.current_h), pygame.FULLSCREEN)
    pygame.display.set_caption("GhostGrid")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 24)
    cell_width = screen_info.current_w // GRID_COLS
    cell_height = screen_info.current_h // GRID_ROWS

    ghost_img, sentinel_img = load_assets(cell_width, cell_height)
    kore = build_environment(GRID_COLS, GRID_ROWS, cell_width, cell_height)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                running = False

        screen.fill(BLACK)
        draw_environment(screen, kore, ghost_img, sentinel_img, cell_width, cell_height, font)
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()