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
# GRID_COLS = 25
# GRID_ROWS = 15
GRID_COLS = 15
GRID_ROWS = 10

def load_assets(cell_width, cell_height):
    ghost_path = os.path.join("assets", "ghost.png")
    ghost_img = pygame.image.load(ghost_path)
    ghost_img = pygame.transform.scale(ghost_img, (cell_width, cell_height))

    sentinel_path = os.path.join("assets", "sentinel.png")
    sentinel_img = pygame.image.load(sentinel_path)
    sentinel_img = pygame.transform.scale(sentinel_img, (cell_width, cell_height))

    deathghost_path = os.path.join("assets", "deathghost.png")
    deathghost_img = pygame.image.load(deathghost_path)
    deathghost_img = pygame.transform.scale(deathghost_img, (cell_width, cell_height))

    greedysentinel_path = os.path.join("assets", "greedysentinel.png")
    greedysentinel_img = pygame.image.load(greedysentinel_path)
    greedysentinel_img = pygame.transform.scale(greedysentinel_img, (cell_width, cell_height))

    money_path = os.path.join("assets", "money.png")
    money_img = pygame.image.load(money_path)
    money_img = pygame.transform.scale(money_img, (cell_width, cell_height))

    restingsentinel_path = os.path.join("assets", "restingsentinel.png")
    restingsentinel_img = pygame.image.load(restingsentinel_path)
    restingsentinel_img = pygame.transform.scale(restingsentinel_img, (cell_width, cell_height))

    sleepingghost_path = os.path.join("assets", "sleepingghost.png")
    sleepingghost_img = pygame.image.load(sleepingghost_path)
    sleepingghost_img = pygame.transform.scale(sleepingghost_img, (cell_width, cell_height))

    return ghost_img, sentinel_img, deathghost_img, greedysentinel_img, money_img, restingsentinel_img, sleepingghost_img

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

def testing_set(kore):
    all_nodes = [node for row in kore.nodes for node in row]
    ghost_nodes = random.sample(all_nodes, 12)
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
    sleeping_ghosts = random.choices(ghost_nodes, k=2)
    for node in sleeping_ghosts:
        node.ghosts[0].sleeping = True

    deathghosts = random.choices(ghost_nodes, k=2)
    for node in deathghosts:
        node.ghosts[0].death = True

    sentinel_nodes = random.choices(all_nodes, k=10)
    for node in sentinel_nodes:
        sentinel = Sentinel(gen_name("sentinel"), node.position_x, node.position_y, 0, False, False, 100)
        node.sentinels.append(sentinel)

    if len(sentinel_nodes) >= 4:
        sentinel_nodes[0].sentinels[0].resting = True
        sentinel_nodes[1].sentinels[0].resting = True
        sentinel_nodes[2].sentinels[0].greedy = True
        sentinel_nodes[3].sentinels[0].greedy = True

    money_nodes = random.sample(all_nodes, 5)
    for node in money_nodes:
        node.money += random.randint(10, 50)

def test_agent(kore, agent_type):
    all_nodes = [node for row in kore.nodes for node in row]
    node = random.choice(all_nodes)
    if agent_type == "sentinel":
        sentinel = Sentinel(gen_name("sentinel"), node.position_x, node.position_y, 0, False, False, 100)
        node.sentinels.append(sentinel)
        print(f"Added Sentinel {sentinel.id} at node {node.id}")
    elif agent_type == "ghost":
        ghost = Ghost(gen_name("ghost"), node.position_x, node.position_y, 0, False, False, 100)
        node.ghosts.append(ghost)
        print(f"Added Ghost {ghost.id} at node {node.id}")

def build_environment(grid_cols, grid_rows, cell_width, cell_height):
    kore = Kore(grid_cols, grid_rows)
    kore.create_connections()
    for row in kore.nodes:
        for node in row:
            col, layer = map(int, node.id.split(','))
            node.position_x = col * cell_width + cell_width // 2
            node.position_y = layer * cell_height + cell_height // 2

    # testing_set(kore)
    test_agent(kore, "ghost")
    return kore

def draw_environment(screen, kore, ghost_img, sentinel_img, deathghost_img, sleepingghost_img, restingsentinel_img, greedysentinel_img, money_img, cell_width, cell_height, font):
    draw_grid(GRID_COLS, GRID_ROWS, cell_width, cell_height, screen.get_width(), screen.get_height(), screen)
    drawn_connections = set()
    for row in kore.nodes:
        for node in row:
            for ghost in node.ghosts:
                if hasattr(ghost, "death") and ghost.death:
                    img = deathghost_img
                elif hasattr(ghost, "sleeping") and ghost.sleeping:
                    img = sleepingghost_img
                else:
                    img = ghost_img
                screen.blit(img, (node.position_x - cell_width // 2, node.position_y - cell_height // 2))
            for sentinel in node.sentinels:
                if hasattr(sentinel, "resting") and sentinel.resting:
                    img = restingsentinel_img
                elif hasattr(sentinel, "greedy") and sentinel.greedy:
                    img = greedysentinel_img
                else:
                    img = sentinel_img
                screen.blit(img, (node.position_x - cell_width // 2, node.position_y - cell_height // 2))
            if node.money > 0:
                screen.blit(money_img, (node.position_x - cell_width // 2, node.position_y - cell_height // 2))
                money_surf = font.render(str(node.money), True, (0, 0, 0))
                money_rect = money_surf.get_rect(center=(node.position_x, node.position_y + cell_height // 6))
                screen.blit(money_surf, money_rect)
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
                        if (node.ghosts or node.sentinels or node.money > 0 or
                            neighbor.ghosts or neighbor.sentinels or neighbor.money > 0):
                            mid = ((node.position_x + neighbor.position_x) // 2, (node.position_y + neighbor.position_y) // 2)
                            cost_surf = font.render(str(conn.cost), True, (255, 255, 0))
                            cost_rect = cost_surf.get_rect(center=mid)
                            screen.blit(cost_surf, cost_rect)
                    drawn_connections.add(pair)

def loop_turn(kore, current_time):
    agent = None
    current_node = None
    for row in kore.nodes:
        for node in row:
            if node.ghosts:
                agent = node.ghosts[0]
                current_node = node
                break
        if agent:
            break
    if not agent or not current_node:
        return

    # Determine direction: even turn = left, odd turn = right
    direction = -1 if current_time % 2 == 0 else 1
    new_x = (current_node.position_x // (kore.n if kore.n else 1)) + direction
    new_y = current_node.position_y // (kore.m if kore.m else 1)

    dest_node = kore.get_node_by_position(current_node.id, 0, direction)
    if dest_node:
        print(f"moving from {current_node.id} to {dest_node.id}")
        for row in kore.nodes:
            for node in row:
                if (node.position_x // (kore.n if kore.n else 1)) == new_x and \
                   (node.position_y // (kore.m if kore.m else 1)) == new_y:
                    dest_node = node
                    break
            if dest_node:
                break

    if dest_node:
        print(f"Current node: {current_node.id}, Destination node: {dest_node.id}, agent: {agent.id}")
        moved = kore.move(current_node.id, dest_node.id, agent.id)
        print(f"Turn {current_time}: Moved ghost {agent.id} {'left' if direction == -1 else 'right'}: {moved}")

def main():
    pygame.init()
    screen_info = pygame.display.Info()
    screen = pygame.display.set_mode((screen_info.current_w, screen_info.current_h), pygame.FULLSCREEN)
    pygame.display.set_caption("GhostGrid")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 24)
    cell_width = screen_info.current_w // GRID_COLS
    cell_height = screen_info.current_h // GRID_ROWS

    ghost_img, sentinel_img, deathghost_img, greedysentinel_img, money_img, restingsentinel_img, sleepingghost_img = load_assets(cell_width, cell_height)
    kore = build_environment(GRID_COLS, GRID_ROWS, cell_width, cell_height)

    last_action_time = pygame.time.get_ticks()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                running = False

        current_time = pygame.time.get_ticks()
        if current_time - last_action_time >= 1000:
            loop_turn(kore, current_time // 1000)
            last_action_time = current_time

        screen.fill(BLACK)
        draw_environment(screen, kore, ghost_img, sentinel_img, deathghost_img, sleepingghost_img, restingsentinel_img, greedysentinel_img, money_img, cell_width, cell_height, font)
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()