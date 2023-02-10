from map import read_map_from_file, Map, Street
from gui import *
from character_handler import ModifiedPeople, ModifiedNPC
from character import Society


class Player:
    def __init__(self, place_ID: str, coins: str, items: list[str], strength: str, speed: str, relations: list[str]) -> None:
        self.place_ID = int(place_ID)
        self.coins = int(coins)
        if items == [""]:
            self.items = []
        else:
            self.items = [int(x) for x in items]
        self.strength = int(strength)
        self.speed = int(speed)
        self.relations = [int(x) for x in relations]

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


if __name__ == "__main__":
    map = read_map_from_file("data\streets.csv")
    spawn_player = Player(0, 25, [], 2, 2, [2, 2, 2, 2, 2, 2, 2])
    for _ in range(10):
        spawn_player.move(map)
