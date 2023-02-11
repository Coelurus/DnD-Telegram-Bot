from map import read_map_from_file, Map, Street
from gui import *
from character_handler import ModifiedPeople, ModifiedNPC
from character import Society
from items import Item, ItemsCollection


class Player:
    def __init__(self, place_ID: str, coins: str, items: list[str], strength: str, speed: str, relations: list[str], fraction_ID: str = "4", state: str = "alive", duration: str = "", weapons: list[str] = [""]) -> None:
        self.place_ID = int(place_ID)
        self.coins = int(coins)
        self.items = [int(x) for x in items if x != ""]
        self.strength = int(strength)
        self.speed = int(speed)
        self.relations = [int(x) for x in relations]
        self.fraction_ID = int(fraction_ID)
        self.state = state

        self.duration: dict[str, int] = dict()
        if duration != "":
            for effects in duration.split(";"):
                key, val = effects.split("/")
                self.duration[key] = int(val)

        self.equiped_weapons = [int(x) for x in weapons if x != ""]

    def move(self, map=read_map_from_file("data\streets.csv")):
        connected_streets = map.get_street_by_ID(
            self.place_ID).get_connected_streets()

        output_str = ""
        output_str += "You can go to: \n"
        options: list[Street] = []
        for possible_street in connected_streets:
            output_str += map.get_street_by_ID(possible_street).name_cz + "\n"
            options.append(map.get_street_by_ID(possible_street))

        output(output_str)
        idx = choose([x.name_cz for x in options])

        self.place_ID = options[idx].ID

    def move_possibilities(self, map=read_map_from_file("data\streets.csv")) -> tuple[list[Street], Street]:
        current_street = map.get_street_by_ID(
            self.place_ID)
        connected_streets = current_street.get_connected_streets()
        options = []
        for possible_street in connected_streets:
            options.append(map.get_street_by_ID(possible_street))
        return options, current_street

    def get_actions(self, current_characters: ModifiedPeople, map=read_map_from_file("data\streets.csv")) -> tuple[dict[str, str], list[ModifiedNPC]]:
        people_here = current_characters.get_people_in_place(self.place_ID)
        possible_actions_str = map.get_street_by_ID(self.place_ID).possibilites
        action_dict = {}
        for action in possible_actions_str.split(";"):
            if action != "":
                key, val = action.split(":")
                action_dict[key] = val
        return action_dict, people_here

    def get_relationships(self, people_here: list[ModifiedNPC], society: Society) -> dict[int, int]:
        char_ID_to_realtion: dict[int, int] = dict()
        for person in people_here:
            char_ID_to_realtion[person.ID] = self.relations[society.get_char_by_ID(
                person.ID).fraction_ID]
        return char_ID_to_realtion

    def use_item(self, item: Item) -> None:
        """Takes statistics of consumable item and adds them to player's base stats. 
        It also saves duration of these effects and removes item from inventory"""
        str_modifier = f"str{item.strength_mod}"
        speed_modifier = f"speed{item.speed_mod}"
        self.duration[str_modifier] = item.duration
        self.duration[speed_modifier] = item.duration
        self.strength += item.strength_mod
        self.speed += item.speed_mod
        self.items.remove(item.ID)

    def decrease_durations(self) -> None:
        """Method goes through all temporary effects and reduced their duration by 1
        If the effect has duration 0 it removes him from effects list (duration) and removes effects from player"""
        to_pop = []
        for key in self.duration:
            self.duration[key] -= 1
            if self.duration[key] == 0:
                if key == "stun":
                    self.state = "alive"
                elif "str" in key:
                    self.strength -= int(key.lstrip("str"))
                elif "speed" in key:
                    self.speed -= int(key.lstrip("speed"))
                to_pop.append(key)
        for key in to_pop:
            self.duration.pop(key)

    def equip_weapon(self, item: Item) -> bool:
        """Method tries to add item ID to weapon list. If it is possible it returns true and removes newly equiped item from items. 
        If player has already 2 weapons equiped it returns False"""
        if len(self.equiped_weapons) < 2:
            self.equiped_weapons.append(item.ID)
            self.items.remove(item.ID)
            self.update_attributes_on_equip(item)
            return True
        return False

    def get_equiped_weapons(self, items: ItemsCollection) -> list[Item]:
        """Returns list of currently equiped weapons as Item objects"""
        return [items.get_item(item_ID) for item_ID in self.equiped_weapons]

    def swap_weapon(self, remove_item: Item, new_item: Item) -> None:
        """Method takes two Item objects. One to unequip and one to equip and swaps them between inventory and equiped items"""
        self.equiped_weapons.remove(remove_item.ID)
        self.items.remove(new_item.ID)

        self.equiped_weapons.append(new_item.ID)
        self.items.append(remove_item.ID)

        self.update_attributes_on_equip(new_item)
        self.update_attributes_on_remove(remove_item)

    def update_attributes_on_equip(self, item: Item) -> None:
        self.speed += item.speed_mod
        self.strength += item.strength_mod

    def update_attributes_on_remove(self, item: Item) -> None:
        self.speed -= item.speed_mod
        self.strength -= item.strength_mod


if __name__ == "__main__":
    map = read_map_from_file("data\streets.csv")
    spawn_player = Player(0, 25, [], 2, 2, [2, 2, 2, 2, 2, 2, 2], 4, "alive")
    for _ in range(10):
        spawn_player.move(map)
