from Node import Node, Connection
import random

class Kore:
    def __init__(self, n, m):
        self.n = n  # nodes per layer
        self.m = m  # number of layers
        self.nodes = []
        for layer in range(m):
            layer_nodes = []
            for position in range(n):
                node_id = f"{position},{layer}"
                node = Node(
                    node_id,
                    connections=[],
                    position_x=position,
                    position_y=layer
                )
                layer_nodes.append(node)
            self.nodes.append(layer_nodes)

    def create_connections(self):
        directions = [
            (1, 0), (-1, 0),
            (0, 1), (1, 1), (-1, 1),
            (0, -1), (1, -1), (-1, -1)
        ]
        for b in range(self.m):
            for a in range(self.n):
                node = self.nodes[b][a]
                for dx, dy in directions:
                    na, nb = a + dx, b + dy
                    if 0 <= na < self.n and 0 <= nb < self.m:
                        neighbor = self.nodes[nb][na]
                        cost = random.randint(1, 10)
                        connection = Connection(node.id, neighbor.id, cost)
                        node.connections.append(connection)

    def get_position(self, node_id, limit):
        result = []
        all_nodes = [node for row in self.nodes for node in row]
        node = next((n for n in all_nodes if n.id == node_id), None)
        if not node:
            return result
        for connection in node.connections:
            neighbor_id = connection.node_b if connection.node_a == node_id else connection.node_a
            neighbor = next((n for n in all_nodes if n.id == neighbor_id), None)
            if not neighbor:
                continue
            if connection.cost > limit:
                node_copy = Node(
                    node_id=neighbor.id,
                    connections=[],
                    position_x=neighbor.position_x,
                    position_y=neighbor.position_y,
                    money=0,
                    ghosts=[],
                    sentinels=[]
                )
            else:
                node_copy = Node(
                    node_id=neighbor.id,
                    connections=[],
                    position_x=neighbor.position_x,
                    position_y=neighbor.position_y,
                    money=neighbor.money,
                    ghosts=neighbor.ghosts.copy(),
                    sentinels=neighbor.sentinels.copy()
                )
            result.append(node_copy)
        return result