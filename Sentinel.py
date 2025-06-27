class Sentinel:
    def __init__(self, sentinel_id, position_x, position_y, money=0, capturing=False, resting=False, stamina=100):
        self.id = sentinel_id
        self.position_x = position_x
        self.position_y = position_y
        self.money = money
        self.capturing = capturing
        self.resting = resting
        self.stamina = stamina

        # A set to store IDs of visited nodes of memory
        self.visited_nodes = set()

    def __repr__(self):
        return (f"Sentinel(id={self.id}, x={self.position_x}, y={self.position_y}, "
                f"money={self.money}, capturing={self.capturing}, "
                f"resting={self.resting}, stamina={self.stamina})")

    def rest(self):
        self.resting = True
        self.stamina += self.stamina * 0.05

    def capturing(self):
        self.capturing = True

    def move(self, dx, dy, cost):
        if self.stamina < cost:
            print("Not enough stamina to move.")
            return
        self.position_x = dx
        self.position_y = dy
        self.stamina -= cost

    def take_money(self, amount):
        self.money += amount
