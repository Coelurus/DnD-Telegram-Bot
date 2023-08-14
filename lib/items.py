import csv


class Item:
    """Class to store specific static data about Item"""

    def __init__(self, ID: str, name_cz: str, legal: str, speed_mod: str, strength_mod: str, price: str, description_cz: str, type: str, usage: str, duration: str = 0) -> None:
        self.ID = int(ID)
        self.name_cz = name_cz
        self.legal = legal
        self.speed_mod = int(speed_mod)
        self.strength_mod = int(strength_mod)
        self.price = int(price)
        self.description_cz = description_cz
        self.type = type
        self.usage = usage
        self.duration = int(duration)

    def __str__(self):
        return f"[{self.ID}] - {self.name_cz}. Is legal? {self.legal}. Gives {self.strength_mod} strength and {self.speed_mod} speed. Is worth {self.price} coins. Type is {self.type}. Is used as {self.usage}. Described as: {self.description_cz}"


class ItemsCollection:
    """Class to store all Item objects"""

    def __init__(self) -> None:
        self.list: list[Item] = []
        self.name_cz_to_ID: dict[str, int] = dict()
        """Dict to easily get Item's ID based on his name"""

    def __repr__(self):
        return "\n".join([str(x) for x in self.list])

    def add_item(self, item: Item):
        self.list.append(item)
        self.name_cz_to_ID[item.name_cz] = item.ID

    def get_item(self, ID: int) -> Item:
        return self.list[ID]

    def get_item_from_name(self, name: str) -> Item:
        return self.get_item(self.name_cz_to_ID[name])

    def items_by_type(self, type: str) -> list[Item]:
        "Returns list of all game items of certain type"
        type_list = []
        for item in self.list:
            if item.type == type:
                type_list.append(item)
        return type_list


def read_items_from_file(path: str) -> ItemsCollection:
    """Function to read data about items from csv file.
    Function returns ItemsCollection object where all Items are saved"""
    csv_file = open(path, newline="", encoding="utf-8")
    reader = csv.DictReader(csv_file, delimiter=",")

    items = ItemsCollection()
    for row in reader:
        items.add_item(
            Item(row["ID"], row["name_cz"], row["legal"], row["speed_mod"], row["strength_mod"], row["price"], row["description_cz"], row["type"], row["usage"], row["duration"]))

    csv_file.close()
    return items


if __name__ == "__main__":
    items = read_items_from_file(r"data\items.csv")
    print(items)
