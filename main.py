from ghost_method import get_move_command, ghost_turn
import pygame
import sys
import os
import random
from map import draw_grid
from kore import Kore
from Sentinel import Sentinel
from Node import Node, Connection
from Ghost import Ghost
from sentinel_method import a_star_search, sentinel_turn

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


def test_agent(kore, agent_type, num_agents=1):
    """
    Crea un número específico de agentes de un tipo y los coloca en sus
    capas de inicio correctas, distribuyéndolos aleatoriamente dentro de esa capa.
    """
    if agent_type == "ghost":
        # REGLA 1: Los Ghosts solo pueden aparecer en la capa 0.
        layer_index = 0
        spawn_nodes = [row[layer_index] for row in kore.nodes]
        
        # Reparte el botín inicial entre el número de Ghosts a crear.
        initial_money = 100 // num_agents if num_agents > 0 else 100

        for i in range(num_agents):
            # Elige un nodo aleatorio DIFERENTE para cada Ghost dentro de la capa 0.
            node = random.choice(spawn_nodes)
            ghost_id = f"ghost_{i+1}"
            ghost = Ghost(ghost_id, node.position_x, node.position_y, initial_money)
            node.ghosts.append(ghost)
            print(f"-> Ghost '{ghost_id}' añadido en el nodo {node.id} (Capa {layer_index})")

    elif agent_type == "sentinel":
        # REGLA 2: Los Sentinels solo pueden aparecer en la capa n-1.
        # El índice de la penúltima capa. Se resta 2 porque los índices empiezan en 0.
        layer_index = len(kore.nodes[0]) - 2 
        
        # Nos aseguramos de que el índice no sea negativo si el mapa es muy pequeño.
        if layer_index < 0:
            layer_index = 0
            
        spawn_nodes = [row[layer_index] for row in kore.nodes]

        for i in range(num_agents):
            # Elige un nodo aleatorio DIFERENTE para cada Sentinel dentro de su capa.
            node = random.choice(spawn_nodes)
            sentinel_id = f"sentinel_{i+1}"
            sentinel = Sentinel(sentinel_id, node.position_x, node.position_y)
            node.sentinels.append(sentinel)
            print(f"-> Sentinel '{sentinel_id}' añadido en el nodo {node.id} (Capa {layer_index})")

def build_environment(grid_cols, grid_rows, cell_width, cell_height):
    kore = Kore(grid_cols, grid_rows)
    kore.create_connections()
    for row in kore.nodes:
        for node in row:
            col, layer = map(int, node.id.split(','))
            node.position_x = col * cell_width + cell_width // 2
            node.position_y = layer * cell_height + cell_height // 2

    testing_set(kore)
    # test_agent(kore, "ghost")
    # test_agent(kore, "sentinel") 
    return kore

def draw_environment(screen, kore, ghost_img, sentinel_img, deathghost_img, sleepingghost_img, restingsentinel_img, greedysentinel_img, money_img, cell_width, cell_height, font):
    draw_grid(GRID_COLS, GRID_ROWS, cell_width, cell_height, screen.get_width(), screen.get_height(), screen)
    drawn_connections = set()
    bar_width = 6
    bar_height = cell_height
    bar_offset = - 20

    for row in kore.nodes:
        for node in row:
            for idx, ghost in enumerate(node.ghosts):
                if hasattr(ghost, "death") and ghost.death:
                    img = deathghost_img
                elif hasattr(ghost, "sleeping") and ghost.sleeping:
                    img = sleepingghost_img
                else:
                    img = ghost_img
                sprite_x = node.position_x - cell_width // 2
                sprite_y = node.position_y - cell_height // 2
                screen.blit(img, (sprite_x, sprite_y))

                # Draw stamina (red) and money (green) bars
                stamina = max(0, min(ghost.stamina, 100))
                money = max(0, min(getattr(ghost, "money", 0), 100))
                bar_x = sprite_x + img.get_width() + bar_offset
                bar_y = sprite_y

                # Stamina bar (red)
                stamina_bar_height = int(bar_height * (stamina / 100))
                pygame.draw.rect(screen, (255, 0, 0),
                                 (bar_x, bar_y + bar_height - stamina_bar_height, bar_width, stamina_bar_height))
                pygame.draw.rect(screen, (100, 100, 100), (bar_x, bar_y, bar_width, bar_height), 1)

                # Money bar (green)
                money_bar_height = int(bar_height * (money / 100))
                pygame.draw.rect(screen, (0, 200, 0), (
                bar_x + bar_width + 2, bar_y + bar_height - money_bar_height, bar_width, money_bar_height))
                pygame.draw.rect(screen, (100, 100, 100), (bar_x + bar_width + 2, bar_y, bar_width, bar_height), 1)

            for idx, sentinel in enumerate(node.sentinels):
                if hasattr(sentinel, "resting") and sentinel.resting:
                    img = restingsentinel_img
                elif hasattr(sentinel, "greedy") and sentinel.greedy:
                    img = greedysentinel_img
                else:
                    img = sentinel_img
                sprite_x = node.position_x - cell_width // 2
                sprite_y = node.position_y - cell_height // 2
                screen.blit(img, (sprite_x, sprite_y))

                # Draw stamina (red) and money (green) bars
                stamina = max(0, min(sentinel.stamina, 100))
                money = max(0, min(getattr(sentinel, "money", 0), 100))
                bar_x = sprite_x + img.get_width() + bar_offset
                bar_y = sprite_y

                # Stamina bar (red)
                stamina_bar_height = int(bar_height * (stamina / 100))
                pygame.draw.rect(screen, (255, 0, 0),
                                 (bar_x, bar_y + bar_height - stamina_bar_height, bar_width, stamina_bar_height))
                pygame.draw.rect(screen, (100, 100, 100), (bar_x, bar_y, bar_width, bar_height), 1)

                # Money bar (green)
                money_bar_height = int(bar_height * (money / 100))
                pygame.draw.rect(screen, (0, 200, 0), (
                bar_x + bar_width + 2, bar_y + bar_height - money_bar_height, bar_width, money_bar_height))
                pygame.draw.rect(screen, (100, 100, 100), (bar_x + bar_width + 2, bar_y, bar_width, bar_height), 1)

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

            id_surf = font.render(str(node.id), True, (255, 255, 255))
            id_rect = id_surf.get_rect()
            id_rect.topleft = (
            node.position_x - cell_width // 2 + 4, node.position_y + cell_height // 2 - id_rect.height - 4)
            screen.blit(id_surf, id_rect)

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

    dest_node = kore.get_node_by_move(current_node.id, 0, direction)
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

def ghost_command_processor(agent, command, kore):
    current_agent = kore.get_agent_by_id(agent)
    current_node = kore.get_node_by_position(current_agent.position_x, current_agent.position_y)

    move_map = {
        "move-r": (0, 1),
        "move-l": (0, -1),
        "move-d": (1, 0),
        "move-u": (-1, 0),
        "move-ur": (-1, 1),
        "move-dr": (1, 1),
        "move-ul": (-1, -1),
        "move-ud": (1, -1),
    }

    if command in move_map:
        v, h = move_map[command]
        dest_node = kore.get_node_by_move(current_node.id, v, h)
        if dest_node:
            moved = kore.move(current_node.id, dest_node.id, current_agent.id)
            print(f"Moved {current_agent.id} from {current_node.id} to {dest_node.id}: {moved}")
        else:
            print("Invalid move.")
    elif command == "rest":
        current_agent.stamina = min(100, current_agent.stamina + 10)
        print(f"{current_agent.id} rested. Stamina: {current_agent.stamina}")
    elif command.startswith("drop-"):
        try:
            amount = int(command.split("-")[1])
            if hasattr(current_agent, "money") and current_agent.money >= amount:
                current_agent.money -= amount
                current_node.money += amount
                print(f"{current_agent.id} dropped {amount} money.")
            else:
                print("Not enough money to drop.")
        except Exception:
            print("Invalid drop command.")
    elif command.startswith("take-"):
        try:
            amount = int(command.split("-")[1])
            if current_node.money >= amount:
                current_node.money -= amount
                if hasattr(current_agent, "money"):
                    current_agent.money += amount
                else:
                    current_agent.money = amount
                print(f"{current_agent.id} took {amount} money.")
            else:
                print("Not enough money in node.")
        except Exception:
            print("Invalid take command.")
    else:
        print("Unknown command.")

def sentinel_command_processor(agent, command, kore):
    current_agent = kore.get_agent_by_id(agent)
    current_node = kore.get_node_by_position(current_agent.position_x, current_agent.position_y)

    move_map = {
        "move-r": (0, 1),
        "move-l": (0, -1),
        "move-d": (1, 0),
        "move-u": (-1, 0),
        "move-ur": (-1, 1),
        "move-dr": (1, 1),
        "move-ul": (-1, -1),
        "move-ud": (1, -1),
    }

    if command in move_map:
        v, h = move_map[command]
        dest_node = kore.get_node_by_move(current_node.id, v, h)
        if dest_node:
            moved = kore.move(current_node.id, dest_node.id, current_agent.id)
            print(f"Moved {current_agent.id} from {current_node.id} to {dest_node.id}: {moved}")
        else:
            print("Invalid move.")
    elif command == "rest":
        current_agent.stamina = min(100, current_agent.stamina + 10)
        print(f"{current_agent.id} rested. Stamina: {current_agent.stamina}")
    elif command.startswith("drop-"):
        try:
            amount = int(command.split("-")[1])
            if hasattr(current_agent, "money") and current_agent.money >= amount:
                current_agent.money -= amount
                current_node.money += amount
                print(f"{current_agent.id} dropped {amount} money.")
            else:
                print("Not enough money to drop.")
        except Exception:
            print("Invalid drop command.")
    elif command.startswith("take-"):
        try:
            amount = int(command.split("-")[1])
            if current_node.money >= amount:
                current_node.money -= amount
                if hasattr(current_agent, "money"):
                    current_agent.money += amount
                else:
                    current_agent.money = amount
                print(f"{current_agent.id} took {amount} money.")
            else:
                print("Not enough money in node.")
        except Exception:
            print("Invalid take command.")
    else:
        print("Unknown command.")

def command_processor(agent_id, agent_type, command, kore):
    """
    Procesa un comando para un agente específico, manejando acciones especiales
    como la replicación antes de delegar a los procesadores específicos.
    """
    # --- MANEJO DE COMANDOS ESPECIALES ---
    
    # El comando 'replicate' es manejado aquí directamente porque altera
    # el estado del juego creando un nuevo agente.
    if command == "replicate" and agent_type == "ghost":
        ghost = kore.get_agent_by_id(agent_id)
        # Verifica que el Ghost exista y tenga suficiente botín para dividirse
        if ghost and ghost.money > 1:
            # Divide el botín entre el original y la réplica
            original_money = ghost.money // 2
            replica_money = ghost.money - original_money
            ghost.money = original_money

            # Crea la nueva réplica con un ID único
            replica_id = f"{ghost.id}_r{random.randint(1, 999)}"
            replica = Ghost(replica_id, ghost.position_x, ghost.position_y, replica_money)
            
            # Añade la réplica al mismo nodo en el que se encuentra el original
            current_node = kore.get_node_by_position(ghost.position_x, ghost.position_y)
            if current_node:
                current_node.ghosts.append(replica)
                print(f"      -> ¡ACCIÓN! {ghost.id} se ha replicado en {replica_id} en el nodo {current_node.id}.")
        
        # Una vez manejada la replicación, no se hace nada más en este turno.
        return

    # --- DELEGACIÓN A PROCESADORES ESPECÍFICOS ---
    
    # Si el comando no es uno especial, se delega al procesador correspondiente.
    if agent_type == "ghost":
        ghost_command_processor(agent_id, command, kore)
    elif agent_type == "sentinel":
        sentinel_command_processor(agent_id, command, kore)

def check_game_over(kore, turn_count, max_turns=100):
    """
    Verifica si se ha cumplido alguna condición de fin de juego.
    Versión corregida para evitar el IndexError.
    """
    # Escanea el estado actual del juego
    active_ghosts = [g for row in kore.nodes for node in row for g in node.ghosts if not g.captured]
    total_loot_sentinels = sum(s.money for row in kore.nodes for node in row for s in node.sentinels)
    
    # --- CÓDIGO CORREGIDO ---
    # Se calcula el índice de la capa final (última columna)
    final_layer_index = len(kore.nodes[0]) - 1
    # Se obtienen todos los nodos de esa última capa (columna)
    final_layer_nodes = [row[final_layer_index] for row in kore.nodes]
    # Se suma el botín solo de los nodos en esa capa
    total_loot_ghosts_goal = sum(node.money for node in final_layer_nodes)
    # Condición 1: Sentinels ganan por captura total
    if not active_ghosts:
        return "¡VICTORIA PARA LOS SENTINELS! (Todos los Ghosts capturados)"

    # Condición 2: Sentinels ganan por recuperar la mayoría del botín
    if total_loot_sentinels > 50:
        return f"¡VICTORIA PARA LOS SENTINELS! (Han recuperado {total_loot_sentinels} de botín)"

    # Condición 3: Ghosts ganan por asegurar la mayoría del botín
    if total_loot_ghosts_goal > 50:
        return f"¡VICTORIA PARA LOS GHOSTS! (Han asegurado {total_loot_ghosts_goal} de botín en la meta)"

    # Condición 4: El juego termina por límite de turnos
    if turn_count >= max_turns:
        # Se determina el ganador por puntos al final de los turnos
        print(f"FIN DEL JUEGO POR LÍMITE DE TURNOS ({max_turns}).")
        if total_loot_sentinels > total_loot_ghosts_goal:
            return f"VICTORIA PARA SENTINELS POR PUNTOS ({total_loot_sentinels} vs {total_loot_ghosts_goal})"
        elif total_loot_ghosts_goal > total_loot_sentinels:
            return f"VICTORIA PARA GHOSTS POR PUNTOS ({total_loot_ghosts_goal} vs {total_loot_sentinels})"
        else:
            return f"¡EMPATE! ({total_loot_sentinels} vs {total_loot_ghosts_goal})"

    # Si no se cumple ninguna condición, el juego continúa
    return None

def main():
    print("Iniciando main")  # <-- Agrega esto
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
    turn_count = 1
    running = True
    while running:
        # ===============================================================
        # 1. MANEJO DE EVENTOS (Se ejecuta en cada fotograma)
        # ===============================================================
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                running = False

        # ===============================================================
        # 2. LÓGICA DEL JUEGO (Se ejecuta solo una vez por segundo)
        # ===============================================================
        current_time = pygame.time.get_ticks()
        if current_time - last_action_time >= 1000:
            print(f"\n===== INICIO DEL TURNO {turn_count} =====")

            # Escanea el mapa para obtener listas frescas de agentes
            active_ghosts = [g for row in kore.nodes for node in row for g in node.ghosts]
            active_sentinels = [s for row in kore.nodes for node in row for s in node.sentinels]
            
            # --- FASE GHOST (Lógica individual) ---
            print(f"--- FASE GHOST --- ({len(active_ghosts)} activos)")
            for ghost in active_ghosts:
                command = ghost_turn(ghost.id, kore, turn_count)
                print(f"  - Ghost '{ghost.id}' decide: {command}")
                command_processor(ghost.id, "ghost", command, kore)

            # --- FASE SENTINEL (NUEVA LÓGICA DE COORDINACIÓN) ---
            print(f"--- FASE SENTINEL --- ({len(active_sentinels)} activos)")
            
            # 2a. Identificar objetivos primarios (nodos con Ghosts)
            ghost_nodes_as_targets = [node for row in kore.nodes for node in row if node.ghosts]
            
            for i, sentinel in enumerate(active_sentinels):
                command = "rest" # Comando por defecto si no se puede hacer nada
                
                # 2b. Asignar objetivo si hay Ghosts disponibles
                if ghost_nodes_as_targets:
                    # Se asigna un objetivo usando el operador módulo para distribuir la carga
                    target_node = ghost_nodes_as_targets[i % len(ghost_nodes_as_targets)]
                    start_node = kore.get_node_by_position(sentinel.position_x, sentinel.position_y)
                    
                    if start_node and target_node:
                        # La IA calcula la ruta al objetivo ASIGNADO
                        path = a_star_search(kore, start_node, target_node)
                        if path and len(path) > 1:
                            # Si hay ruta, se genera el comando de movimiento
                            command = get_move_command(start_node, path[1])
                else:
                    # 2c. Si no hay Ghosts, cada Sentinel usa su propia lógica individual
                    # (buscar botín, explorar, etc.)
                    command = sentinel_turn(sentinel.id, kore)
                
                print(f"  - Sentinel '{sentinel.id}' decide: {command}")
                command_processor(sentinel.id, "sentinel", command, kore)

            # --- VERIFICACIÓN DE FIN DE JUEGO ---
            winner = check_game_over(kore, turn_count)
            if winner:
                print("\n########################################")
                print(winner)
                print("########################################")
                running = False
            # Actualiza para el siguiente turno
            turn_count += 1
            last_action_time = current_time
            print("=" * 25)

        screen.fill(BLACK)
        draw_environment(screen, kore, ghost_img, sentinel_img, deathghost_img, sleepingghost_img, restingsentinel_img, greedysentinel_img, money_img, cell_width, cell_height, font)
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()

