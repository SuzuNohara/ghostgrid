class Ghost:
    def __init__(self, ghost_id, position_x, position_y, money=0, captured=False, resting=False, stamina=100):
        self.id = ghost_id
        self.position_x = position_x
        self.position_y = position_y
        self.money = money
        self.captured = captured
        self.resting = resting
        self.stamina = stamina

    def __repr__(self):
        return (f"Ghost(id={self.id}, x={self.position_x}, y={self.position_y}, "
                f"money={self.money}, captured={self.captured}, "
                f"resting={self.resting}, stamina={self.stamina})")

    def rest(self):
        self.resting = True
        self.stamina += self.stamina * 0.05

    def captured(self):
        self.captured = True
        self.stamina = 0
        self.money = 0

    def move(self, dx, dy, cost):
        if self.stamina < cost:
            print("Not enough stamina to move.")
            return
        self.position_x = dx
        self.position_y = dy
        self.stamina -= cost

    def release_money(self, amount):
        if self.money >= amount:
            self.money -= amount
        else:
            print("Not enough money to release.")

    def take_money(self, amount):
        self.money += amount