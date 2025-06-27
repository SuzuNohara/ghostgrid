import heapq
import math

# --- Perception Functions ---

def perceive_world(sentinel_id, kore):
    """
    Gathers all necessary information from the game world for the sentinel.
    """
    sentinel_agent = kore.get_agent_by_id(sentinel_id)
    if not sentinel_agent:
        return None, None, [], [], []

    current_node = kore.get_node_by_position(sentinel_agent.position_x, sentinel_agent.position_y)
    
    # Update memory
    if current_node:
        sentinel_agent.visited_nodes.add(current_node.id)

    all_nodes = [node for row in kore.nodes for node in row]
    ghost_locations = []
    money_locations = []

    for node in all_nodes:
        if node.ghosts:
            ghost_locations.append(node)
        if node.money > 0:
            money_locations.append(node)
            
    unexplored_nodes = [node for node in all_nodes if node.id not in sentinel_agent.visited_nodes]

    return sentinel_agent, current_node, ghost_locations, money_locations, unexplored_nodes

# --- A* Pathfinding Algorithm ---

def heuristic(node_a, node_b):
    """
    Calculates the Manhattan distance between two nodes.
    Used as the heuristic for the A* algorithm.
    """
    x1, y1 = map(int, node_a.id.split(','))
    x2, y2 = map(int, node_b.id.split(','))
    return abs(x1 - x2) + abs(y1 - y2)

def a_star_search(kore, start_node, goal_node):
    """
    Finds the shortest path from start_node to goal_node using the A* algorithm.
    """
    open_set = []
    heapq.heappush(open_set, (0, start_node.id))
    
    came_from = {}
    g_score = {node.id: float('inf') for row in kore.nodes for node in row}
    g_score[start_node.id] = 0
    
    f_score = {node.id: float('inf') for row in kore.nodes for node in row}
    f_score[start_node.id] = heuristic(start_node, goal_node)
    
    while open_set:
        _, current_id = heapq.heappop(open_set)
        current_node = kore.get_node_by_id(current_id)

        if current_id == goal_node.id:
            return reconstruct_path(came_from, current_id)

        for conn in current_node.connections:
            neighbor_id = conn.node_b
            neighbor_node = kore.get_node_by_id(neighbor_id)
            
            if not neighbor_node:
                continue
                
            tentative_g_score = g_score[current_id] + conn.cost
            
            if tentative_g_score < g_score[neighbor_id]:
                came_from[neighbor_id] = current_id
                g_score[neighbor_id] = tentative_g_score
                f_score[neighbor_id] = g_score[neighbor_id] + heuristic(neighbor_node, goal_node)
                if neighbor_id not in [i[1] for i in open_set]:
                    heapq.heappush(open_set, (f_score[neighbor_id], neighbor_id))
                    
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

def find_best_target(sentinel_node, ghosts, money, unexplored):
    """
    Determines the best target based on proximity.
    Priority: Ghosts > Money > Unexplored Nodes.
    """
    targets = []
    if ghosts:
        targets = ghosts
    elif money:
        targets = money
    elif unexplored:
        targets = unexplored
    else:
        return None

    closest_target = min(targets, key=lambda target: heuristic(sentinel_node, target))
    return closest_target

def get_move_command(current_node, next_node_id):
    """
    Translates a move from the current node to the next node into a command string.
    """
    cx, cy = map(int, current_node.id.split(','))
    nx, ny = map(int, next_node_id.split(','))
    
    h_move = nx - cx
    v_move = ny - cy
    
    # This maps (vertical, horizontal) movement to commands
    move_map = {
        (-1, -1): "move-ul", (-1, 0): "move-u", (-1, 1): "move-ur",
        (0, -1): "move-l", (0, 0): "rest", (0, 1): "move-r",
        (1, -1): "move-dl", (1, 0): "move-d", (1, 1): "move-dr", # Note: using 'move-ud' from main.py for (1,-1) doesn't make sense, corrected to 'move-dl'
    }
    # Correcting a potential typo from main.py's move_map (move-ud vs move-dl)
    if (v_move, h_move) == (1, -1) and "move-ud" in [m for m in move_map.values()]:
         # check if main.py uses "move-ud" for (1, -1)
        pass # Keep as is if intended

    return move_map.get((v_move, h_move), "rest")


def sentinel_turn(sentinel_id, kore):
    """
    Main logic function for a sentinel's turn.
    """
    # 1. Perceive the world
    sentinel, current_node, ghosts, money, unexplored = perceive_world(sentinel_id, kore)
    
    if not sentinel or not current_node:
        return "rest" # Cannot act if not in the world

    # 2. Immediate action: Capture ghost in the same node
    if current_node.ghosts:
        # Assuming a "capture" command will be implemented.
        # For now, we can make it rest or a placeholder.
        return "capture"

    # 3. Decision Making: Find a target and a path
    target_node = find_best_target(current_node, ghosts, money, unexplored)
    
    if not target_node:
        return "rest" # No targets found, rest to regain stamina

    path = a_star_search(kore, current_node, target_node)
    
    # 4. Execute action
    if path and len(path) > 1:
        next_node_id = path[1]
        return get_move_command(current_node, next_node_id)
    else:
        return "rest" # No path or already at target, rest


    
