class Node:
    def __init__(self, node_id, connections=None, position_x=0, position_y=0, money=0, ghosts=None, sentinels=None):
        self.id = node_id
        self.connections = connections if connections is not None else []
        self.position_x = position_x
        self.position_y = position_y
        self.money = money
        self.ghosts = ghosts if ghosts is not None else []
        self.sentinels = sentinels if sentinels is not None else []

    def __repr__(self):
        return (f"Node(id={self.id}, connections={self.connections}, x={self.position_x}, y={self.position_y}, "
                f"money={self.money}, ghosts={self.ghosts}, sentinels={self.sentinels})")

class Connection:
    def __init__(self, node_a, node_b, cost=1):
        self.node_a = node_a
        self.node_b = node_b
        self.cost = cost

    def __repr__(self):
        return (f"Connection(node_a={self.node_a}, node_b={self.node_b}, cost={self.cost})")