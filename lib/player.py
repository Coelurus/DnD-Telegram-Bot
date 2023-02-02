class Player:
    def __init__(self, place_ID: str, coins: str, items: list[str], strength: str, speed: str, relations: list[str]) -> None:
        self.place_ID = int(place_ID)
        self.coins = int(coins)
        self.items = [int(x) for x in items]
        self.strength = int(strength)
        self.speed = int(speed)
        self.relations = [int(x) for x in relations]
