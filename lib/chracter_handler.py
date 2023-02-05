from character import NPC, read_people_from_file
from quest import str_to_mqp
from map import read_map_from_file
from random import choice

# could be improved by implemented by implemnting inheritance somehow, I guess


class ModifiedNPC:
    def __init__(self, ID: str, place: str, coins: str, items: str, str: str, speed: str, line: str, phase: str, stage: str) -> None:
        self.ID = int(ID)
        self.place = int(place)
        self.coins = int(coins)
        self.str = int(str)
        self.speed = int(speed)
        self.line = int(line)
        self.phase = phase
        self.stage = stage
        self.items = [int(x) for x in items.split(";") if x != ""]

    def __str__(self):
        characters_definition = read_people_from_file("data\characters.csv")
        line_part = ""
        if self.phase != "-1":
            line_part = f"Does quest line {self.line} is at phase {self.phase}. Currently at: {self.stage}"
        return f"NPC {characters_definition.people_list[self.ID]} currently at place {self.place} has {self.coins} coins. Str = {self.str}, speed = {self.speed}. Has items: {self.items}. " + line_part


class ModifiedPeople:
    def __init__(self) -> None:
        self.list: list[ModifiedNPC] = []

    def add_NPC(self, character: ModifiedNPC) -> None:
        self.list.append(character)

    def __repr__(self) -> str:
        return "\n".join([str(x) for x in self.list])


def basic_stuff(old_character_save: str):
    old_char_save_list = old_character_save.split("+")
    current_characters = ModifiedPeople()

    for char_save_str_idx in range(len(old_char_save_list)):
        char_parts = old_char_save_list[char_save_str_idx].split(",")
        # i am so so sorry for this but i do not know how to make this more effectively
        parts_dict: dict[str, str] = dict()

        for part in char_parts:
            key, val = part.split(":")
            parts_dict[key] = val

        current_characters.add_NPC(ModifiedNPC(char_save_str_idx, parts_dict["place"], parts_dict["coins"], parts_dict["items"], parts_dict["str"],
                                               parts_dict["speed"], parts_dict["line"], parts_dict["phase"], parts_dict["stage"]))

    return current_characters


def update_phases(modified_characters: ModifiedPeople) -> ModifiedPeople:
    for character in modified_characters.list:
        if character.phase != "-1":
            current_phase = str_to_mqp(character.phase)

            if character.stage == "tostart" and current_phase.from_place_ID == character.place:
                character.stage = "inprogress"

            elif character.stage == "inprogress" and current_phase.to_place_ID == character.place:
                character.stage = "ended"

            elif character.stage == "ended":
                # TODO add the actions that NPCs can do. Modify quest save.
                pass

    return modified_characters


def move_characters(modified_characters: ModifiedPeople) -> ModifiedPeople:
    characters_definition = read_people_from_file("data\characters.csv")
    map = read_map_from_file("data\streets.csv")
    for character in modified_characters.list:
        if character.phase != "-1":
            current_phase = str_to_mqp(character.phase)
            final_point = current_phase.to_place_ID
        elif characters_definition.get_char_by_ID(character.ID).end_street_ID != -1:
            final_point = characters_definition.get_char_by_ID(
                character.ID).end_street_ID
        else:
            final_point = choice(map.get_street_by_ID(
                character.place).connections + [character.place])

        # TODO add places and characters to avoid
        path = map.find_shortest_path(*map.BFS(map.get_street_by_ID(character.place)),
                                      map.get_street_by_ID(final_point))
        next_place = path[0]
        character.place = next_place


if __name__ == "__main__":
    character_save = "place:32,coins:11,items:,str:3,speed:2,line:-1,phase:-1,stage:-1+place:35,coins:10,items:,str:1,speed:4,line:-1,phase:-1,stage:-1+place:35,coins:2,items:,str:3,speed:2,line:-1,phase:-1,stage:-1+place:35,coins:14,items:,str:3,speed:1,line:-1,phase:-1,stage:-1+place:33,coins:0,items:,str:3,speed:2,line:-1,phase:-1,stage:-1+place:34,coins:18,items:,str:3,speed:2,line:-1,phase:-1,stage:-1+place:17,coins:20,items:,str:1,speed:1,line:-1,phase:-1,stage:-1+place:1,coins:16,items:,str:1,speed:3,line:-1,phase:-1,stage:-1+place:13,coins:13,items:,str:1,speed:4,line:-1,phase:-1,stage:-1+place:23,coins:15,items:,str:3,speed:2,line:-1,phase:-1,stage:-1+place:23,coins:12,items:,str:1,speed:2,line:-1,phase:-1,stage:-1+place:37,coins:6,items:,str:1,speed:4,line:0,phase:0=char11=-1=0=37=none,stage:inprogress+place:37,coins:0,items:,str:1,speed:4,line:-1,phase:-1,stage:-1+place:37,coins:17,items:,str:2,speed:3,line:-1,phase:-1,stage:-1+place:37,coins:12,items:,str:2,speed:2,line:-1,phase:-1,stage:-1+place:37,coins:19,items:,str:1,speed:4,line:-1,phase:-1,stage:-1+place:38,coins:5,items:,str:1,speed:2,line:-1,phase:-1,stage:-1+place:38,coins:18,items:,str:1,speed:4,line:-1,phase:-1,stage:-1+place:38,coins:17,items:,str:1,speed:4,line:-1,phase:-1,stage:-1+place:38,coins:18,items:,str:3,speed:1,line:-1,phase:-1,stage:-1+place:38,coins:5,items:,str:1,speed:4,line:-1,phase:-1,stage:-1+place:39,coins:14,items:,str:3,speed:2,line:-1,phase:-1,stage:-1+place:39,coins:11,items:,str:4,speed:1,line:-1,phase:-1,stage:-1+place:39,coins:9,items:,str:2,speed:3,line:-1,phase:-1,stage:-1+place:39,coins:18,items:,str:1,speed:4,line:-1,phase:-1,stage:-1+place:39,coins:18,items:,str:1,speed:3,line:-1,phase:-1,stage:-1+place:39,coins:16,items:,str:2,speed:3,line:-1,phase:-1,stage:-1"
    modified_people = basic_stuff(character_save)

    # checking if someone finished quest or is final location
    modified_people = update_phases(modified_people)

    # move characters to quest
    modified_people = move_characters(modified_people)
