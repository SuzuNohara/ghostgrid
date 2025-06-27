import heapq
import math
import random

# --- Perception Functions ---

def perceive_world_for_ghost(ghost_id, kore):
    """
    Gathers all necessary information from the game world for the ghost.
    A ghost can see loot in its current node and adjacent nodes.
    """
    ghost_agent = kore.get_agent_by_id(ghost_id)
    if not ghost_agent:
        return None, None, [], 0

    current_node = kore.get_node_by_position(ghost_agent.position_x, ghost_agent.position_y)
    
    # A ghost remembers where it left loot
    if current_node.money > 0 and current_node.id not in ghost_agent.known_loot_nodes:
         ghost_agent.known_loot_nodes.add(current_node.id)

    # Perception is limited to the current node and its direct connections
    visible_loot_nodes = []
    if current_node.money > 0:
        visible_loot_nodes.append(current_node)
    
    for conn in current_node.connections:
        neighbor_node = kore.get_node_by_id(conn.node_b)
        if neighbor_node and neighbor_node.money > 0:
            visible_loot_nodes.append(neighbor_node)

    # The goal is to reach the final layer
    target_layer_index = len(kore.nodes[0]) - 1

    return ghost_agent, current_node, visible_loot_nodes, target_layer_index

# --- A* Pathfinding Algorithm (Reused and Adapted) ---

def ghost_heuristic(node_a, goal_layer_index, kore):
    """
    Heuristic for the Ghost. It combines Manhattan distance with a strong
    incentive to move towards the final layer (n).
    This represents the "reward signal" for approaching the goal.
    """
    x1, y1 = map(int, node_a.id.split(','))
    
    # Manhattan distance to the closest point in the goal layer
    distance_to_goal_layer = abs(goal_layer_index - x1)
    
    # We add a small factor of the vertical distance to break ties,
    # encouraging exploration within the same layer if horizontal distance is equal.
    # The main driver is to reduce the distance to the final layer.
    return distance_to_goal_layer + (y1 * 0.1)


def a_star_search_for_ghost(kore, start_node, goal_layer_index):
    """
    Finds the shortest path from start_node to any node in the goal layer (n).
    The heuristic guides the search towards that layer.
    """
    open_set = []
    # The f_score is the first element for priority queue comparison
    initial_heuristic = ghost_heuristic(start_node, goal_layer_index, kore)
    heapq.heappush(open_set, (initial_heuristic, start_node.id))
    
    came_from = {}
    g_score = {node.id: float('inf') for row in kore.nodes for node in row}
    g_score[start_node.id] = 0
    
    while open_set:
        _, current_id = heapq.heappop(open_set)
        current_node = kore.get_node_by_id(current_id)

        # If the ghost reaches the target layer, the path is successful
        if current_node.position_x == goal_layer_index:
            return reconstruct_path(came_from, current_id)

        for conn in current_node.connections:
            neighbor_id = conn.node_b
            neighbor_node = kore.get_node_by_id(neighbor_id)
            
            if not neighbor_node:
                continue
                
            tentative_g_score = g_score[current_id] + conn.cost
            
            if tentative_g_score < g_score.get(neighbor_id, float('inf')):
                came_from[neighbor_id] = neighbor_id
                g_score[neighbor_id] = tentative_g_score
                # f_score is g_score + heuristic
                f_score = tentative_g_score + ghost_heuristic(neighbor_node, goal_layer_index, kore)
                heapq.heappush(open_set, (f_score, neighbor_id))
                    
    return None # No path found

def reconstruct_path(came_from, current_id):
    """
    Reconstructs the path from the came_from dictionary.
    """
    total_path = [current_id]
    while current_id in came_from:
        current_id = came_from[current_id]
        total_path.insert(0, current_id)
    return total_path

# --- Decision Making & Main Turn Function ---

def get_move_command(current_node, next_node_id):
    """
    Translates a move from the current node to the next node into a command string.
    (This function can be shared between ghost and sentinel logic)
    """
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


def ghost_turn(ghost_id, kore, current_turn=1):
    """
    Main logic function for a ghost's turn.
    """
    # 1. Perceive the world
    ghost, current_node, visible_loot, target_layer = perceive_world_for_ghost(ghost_id, kore)
    
    if not ghost or not current_node:
        return "rest" # Cannot act if not in the world

    # 2. First Turn Logic: Replicate
    # The Ghost will try to replicate if it's the first turn and has enough loot.
    if current_turn == 1 and ghost.money > 1:
        # This is a strategic choice. A simple implementation is to always replicate once.
        # A more advanced one could decide based on the number of neighbors.
        # The command "replicate" should be handled by the command_processor.
        return "replicate"

    # 3. Goal-Oriented Action: Deposit loot if at the final layer
    if current_node.position_x == target_layer and ghost.money > 0:
        return f"drop-{ghost.money}"

    # 4. Resource Management: Take nearby loot if low on energy or carrying nothing
    # This encourages ghosts to pick up fuel for their journey.
    if ghost.stamina < 50 or ghost.money == 0:
        for loot_node in visible_loot:
            if loot_node.id == current_node.id:
                 return f"take-{loot_node.money}"

    # 5. Strategic Movement: Find a path to the goal
    # If the ghost has energy and loot, its main goal is to move.
    if ghost.stamina > 10 and ghost.money > 0: # Threshold to ensure it can make a move
        path = a_star_search_for_ghost(kore, current_node, target_layer)
        
        if path and len(path) > 1:
            next_node_id = path[1]
            # Check if it has enough stamina for the next specific move
            for conn in current_node.connections:
                if conn.node_b == next_node_id and ghost.stamina >= conn.cost:
                    return get_move_command(current_node, next_node_id)
    
    # 6. Default Action: Rest
    # If no other action is taken (low stamina, no path, etc.), rest to recover energy.
    return "rest"
