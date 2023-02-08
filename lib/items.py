import csv


class Item:
    def __init__(self, ID: str, name_cz: str, legal: str, speed_mod: str, strength_mod: str, price: str) -> None:
        self.ID = int(ID)
        self.name_cz = name_cz
        self.legal = legal
        self.speed_mod = int(speed_mod)
        self.strength_mod = int(strength_mod)
        self.price = int(price)

    def __str__(self):
        return f"[{self.ID}] - {self.name_cz} is legal? {self.legal}. Gives {self.strength_mod} strength and {self.speed_mod} speed. Is worth {self.price} coins"


class ItemsCollection:
    def __init__(self) -> None:
        self.list = []

    def __repr__(self):
        return "\n".join([str(x) for x in self.list])

    def add_item(self, item: Item):
        self.list.append(item)

    def get_item_by_ID(self, ID: int) -> Item:
        return self.list[ID]


def read_items_from_file(path):
    csv_file = open(path, newline="", encoding="utf-8")
    reader = csv.DictReader(csv_file, delimiter=",")

    items = ItemsCollection()
    for row in reader:
        items.add_item(
            Item(row["ID"], row["name_cz"], row["legal"], row["speed_mod"], row["strength_mod"], row["price"]))

    csv_file.close()
    return items


if __name__ == "__main__":
    items = read_items_from_file(r"data\items.csv")
    print(items.get_item_by_ID(3))
    # print(items)
