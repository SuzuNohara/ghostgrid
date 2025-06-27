import heapq
import math
import random

# --- Perception Functions ---

def perceive_world_for_ghost(ghost_id, kore):
    ghost_agent = kore.get_agent_by_id(ghost_id)
    if not ghost_agent:
        return None, None, [], 0

    current_node = kore.get_node_by_position(ghost_agent.position_x, ghost_agent.position_y)

    if not hasattr(ghost_agent, "known_loot_nodes"):
        ghost_agent.known_loot_nodes = set()

    if current_node.money > 0 and current_node.id not in ghost_agent.known_loot_nodes:
        ghost_agent.known_loot_nodes.add(current_node.id)

    visible_loot_nodes = []
    if current_node.money > 0:
        visible_loot_nodes.append(current_node)

    for conn in current_node.connections:
        neighbor_node = kore.get_node_by_id(conn.node_b)
        if neighbor_node and neighbor_node.money > 0:
            visible_loot_nodes.append(neighbor_node)

    target_layer_index = len(kore.nodes[0]) - 1
    return ghost_agent, current_node, visible_loot_nodes, target_layer_index

# --- A* Pathfinding Algorithm (Corrected) ---

def ghost_heuristic(node_a, goal_layer_index, kore):
    x1, y1 = map(int, node_a.id.split(','))
    distance_to_goal_layer = abs(goal_layer_index - x1)
    return distance_to_goal_layer + (y1 * 0.1)

def a_star_search_for_ghost(kore, start_node, goal_layer_index):
    open_set = []
    initial_heuristic = ghost_heuristic(start_node, goal_layer_index, kore)
    heapq.heappush(open_set, (initial_heuristic, start_node.id))

    came_from = {}
    g_score = {node.id: float('inf') for row in kore.nodes for node in row}
    g_score[start_node.id] = 0

    while open_set:
        _, current_id = heapq.heappop(open_set)
        current_node = kore.get_node_by_id(current_id)

        if current_node.position_x == goal_layer_index:
            return reconstruct_path(came_from, current_id)

        for conn in current_node.connections:
            neighbor_id = conn.node_b
            neighbor_node = kore.get_node_by_id(neighbor_id)
            if not neighbor_node:
                continue

            tentative_g_score = g_score[current_id] + conn.cost
            if tentative_g_score < g_score.get(neighbor_id, float('inf')):
                came_from[neighbor_id] = current_id  # <- corregido
                g_score[neighbor_id] = tentative_g_score
                f_score = tentative_g_score + ghost_heuristic(neighbor_node, goal_layer_index, kore)
                heapq.heappush(open_set, (f_score, neighbor_id))
    return None

def reconstruct_path(came_from, current_id):
    total_path = [current_id]
    while current_id in came_from:
        current_id = came_from[current_id]
        total_path.insert(0, current_id)
    return total_path

# --- Move Decision ---

def get_move_command(current_node, next_node_id):
    cx, cy = map(int, current_node.id.split(','))
    nx, ny = map(int, next_node_id.split(','))

    h_move = nx - cx
    v_move = ny - cy

    move_map = {
        (-1, -1): "move-ul", (-1, 0): "move-u", (-1, 1): "move-ur",
        (0, -1): "move-l", (0, 0): "rest", (0, 1): "move-r",
        (1, -1): "move-dl", (1, 0): "move-d", (1, 1): "move-dr",
    }
    return move_map.get((v_move, h_move), "rest")

# --- Ghost Turn Logic ---

def ghost_turn(ghost_id, kore, current_turn=1):
    """
    Lógica de decisión mejorada para un agente Ghost, con un comportamiento más
    estratégico y alineado con las reglas del proyecto.
    """
    # 1. PERCEPCIÓN
    ghost, current_node, visible_loot, target_layer = perceive_world_for_ghost(ghost_id, kore)
    if not ghost or not current_node:
        return "rest"

    # --- JERARQUÍA DE DECISIONES ESTRATÉGICAS ---

    # PRIORIDAD 1: CONDICIÓN DE VICTORIA
    # Si el Ghost está en la capa final y tiene botín, su única prioridad es depositarlo.
    if current_node.position_x == target_layer and ghost.money > 0:
        return f"drop-{ghost.money}"

    # PRIORIDAD 2: EXPANSIÓN INICIAL
    # En el primer turno, la replicación es la jugada más estratégica.
    if current_turn == 1 and ghost.money > 1:
        return "replicate"

    # PRIORIDAD 3: MOVIMIENTO HACIA EL OBJETIVO
    # Si el Ghost tiene botín, su principal objetivo es moverse hacia la capa final.
    if ghost.money > 0:
        path = a_star_search_for_ghost(kore, current_node, target_layer)
        if path and len(path) > 1:
            next_node_id = path[1]
            # Verifica si tiene suficiente estamina para el siguiente paso en la ruta óptima
            for conn in current_node.connections:
                if conn.node_b == next_node_id and ghost.stamina >= conn.cost:
                    return get_move_command(current_node, next_node_id)
    
    # PRIORIDAD 4: RECOLECCIÓN DE RECURSOS
    # Si no se está moviendo hacia la meta (porque no tiene botín o no puede moverse),
    # y está sobre un nodo con botín, lo recoge.
    if current_node.money > 0:
        # El Ghost siempre intentará recoger el botín si está sobre él.
        return f"take-{current_node.money}"
    
    # PRIORIDAD 5: DESATASCARSE (MOVIMIENTO EXPLORATORIO)
    # Si no tiene una ruta clara a la meta (posiblemente atrapado), hará un movimiento aleatorio.
    path_to_goal = a_star_search_for_ghost(kore, current_node, target_layer)
    if not path_to_goal or len(path_to_goal) <= 1:
        possible_moves = [conn for conn in current_node.connections if ghost.stamina >= conn.cost]
        if possible_moves:
            random_connection = random.choice(possible_moves)
            return get_move_command(current_node, random_connection.node_b)

    # PRIORIDAD 6: DESCANSO ESTRATÉGICO (ÚLTIMO RECURSO)
    # El Ghost solo descansará si no puede ejecutar ninguna otra acción útil.
    # Esto ocurre si no tiene botín, no hay botín cerca, y no puede moverse
    # (ya sea porque no tiene ruta o porque su estamina es demasiado baja para cualquier movimiento).
    return "rest"
