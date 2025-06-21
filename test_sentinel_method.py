import unittest
from sentinel_method import sentinel_turn, a_star_search

# --- Mock Classes for Testing ---

class MockConnection:
    def __init__(self, node_a, node_b, cost=1):
        self.node_a = node_a
        self.node_b = node_b
        self.cost = cost

class MockNode:
    def __init__(self, node_id, ghosts=None, money=0):
        self.id = node_id
        self.position_x, self.position_y = map(int, node_id.split(','))
        self.ghosts = ghosts if ghosts is not None else []
        self.money = money
        self.connections = []

class MockSentinel:
    def __init__(self, sentinel_id, position_node_id):
        self.id = sentinel_id
        self.position_x, self.position_y = map(int, position_node_id.split(','))
        self.visited_nodes = set()

class MockKore:
    def __init__(self, grid_size_x, grid_size_y):
        self.nodes = [
            [MockNode(f"{x},{y}") for x in range(grid_size_x)]
            for y in range(grid_size_y)
        ]
        self.agents = {}
    
    def get_node_by_id(self, node_id):
        try:
            x, y = map(int, node_id.split(','))
            return self.nodes[y][x]
        except (ValueError, IndexError):
            return None
    
    def get_node_by_position(self, pos_x, pos_y):
        return self.get_node_by_id(f"{pos_x},{pos_y}")

    def get_agent_by_id(self, agent_id):
        return self.agents.get(agent_id)

    def add_agent(self, agent):
        self.agents[agent.id] = agent

    def add_connection(self, id1, id2, cost=1):
        node1 = self.get_node_by_id(id1)
        node2 = self.get_node_by_id(id2)
        if node1 and node2:
            node1.connections.append(MockConnection(id1, id2, cost))
            node2.connections.append(MockConnection(id2, id1, cost))

class TestSentinelLogic(unittest.TestCase):

    def setUp(self):
        """Set up a mock environment for each test."""
        self.kore = MockKore(5, 5)
        # Create a simple grid graph
        for y in range(5):
            for x in range(5):
                if x < 4: self.kore.add_connection(f"{x},{y}", f"{x+1},{y}")
                if y < 4: self.kore.add_connection(f"{x},{y}", f"{x},{y+1}")

    def test_a_star_simple_path(self):
        """Test A* algorithm on a simple, direct path."""
        print("TEST: A* algorithm with a simple direct path")
        start_node = self.kore.get_node_by_id("0,0")
        goal_node = self.kore.get_node_by_id("3,0")
        path = a_star_search(self.kore, start_node, goal_node)
        self.assertIsNotNone(path)
        self.assertEqual(path, ["0,0", "1,0", "2,0", "3,0"])

    def test_a_star_with_obstacles(self):
        """Test A* can navigate around a missing connection."""
        # Remove a connection to create an obstacle
        print("TEST: A* algorithm navigating around missing connections")
        node1 = self.kore.get_node_by_id("1,1")
        node2 = self.kore.get_node_by_id("2,1")
        node1.connections = [c for c in node1.connections if c.node_b != "2,1"]
        node2.connections = [c for c in node2.connections if c.node_b != "1,1"]
        
        start_node = self.kore.get_node_by_id("0,1")
        goal_node = self.kore.get_node_by_id("3,1")
        path = a_star_search(self.kore, start_node, goal_node)
        
        # The path should go around the obstacle, e.g., (0,1)->(1,1)->(1,2)->(2,2)->(2,1)->(3,1) or similar
        self.assertIsNotNone(path)
        self.assertNotEqual(path, ["0,1", "1,1", "2,1", "3,1"]) # Should not be the straight path
        self.assertEqual(path[-1], "3,1") # Should still reach the goal

    def test_sentinel_turn_decision_move_to_ghost(self):
        """Test that the sentinel decides to move towards the closest ghost."""
        print("TEST: Check Sentinel decision move to ghost, should move to the closest ghost")
        sentinel = MockSentinel("S1", "0,0")
        self.kore.add_agent(sentinel)
        self.kore.get_node_by_id("4,4").ghosts.append("G1") # Add a ghost far away
        
        command = sentinel_turn("S1", self.kore)
        self.assertEqual(command, "move-d") # Should move down towards the ghost at (4,4)

    def test_sentinel_turn_decision_move_to_money(self):
        """Test that the sentinel moves towards money if no ghosts are present."""
        print("TEST: Check Sentinel decision move to money, should move to the money if there are no ghosts")
        sentinel = MockSentinel("S1", "2,2")
        self.kore.add_agent(sentinel)
        self.kore.get_node_by_id("2,0").money = 50
        
        command = sentinel_turn("S1", self.kore)
        self.assertEqual(command, "move-u") # Should move up towards the money

    def test_sentinel_turn_decision_explore(self):
        """Test that the sentinel moves to an unexplored node if no targets exist."""
        print("TEST: Check Sentinel decision move if there is no targets")
        sentinel = MockSentinel("S1", "0,0")
        sentinel.visited_nodes = {"0,0", "0,1", "1,0"}
        self.kore.add_agent(sentinel)

        command = sentinel_turn("S1", self.kore)
        # The closest unexplored node is (1,1) or (0,2) or (2,0). Moves towards (1,1) is 'move-dr'. Let's check.
        # Path to (1,1) is ["0,0", "1,0", "1,1"] (move-r) or ["0,0", "0,1", "1,1"] (move-d).
        # Let's assume it picks the first one it finds.
        self.assertIn(command, ["move-r", "move-d"])
    
    def test_sentinel_turn_decision_rest(self):
        """Test that the sentinel rests if there's nowhere to go."""
        print("TEST: In case there is no path available to go, sentinel rests and do not move")
        # Mark all nodes as visited
        sentinel = MockSentinel("S1", "0,0")
        sentinel.visited_nodes = {node.id for row in self.kore.nodes for node in row}
        self.kore.add_agent(sentinel)

        command = sentinel_turn("S1", self.kore)
        self.assertEqual(command, "rest")

if __name__ == '__main__':
    unittest.main()
