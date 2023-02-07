from character import read_people_from_file, read_fractions_from_file, NPC
from quest import str_to_mqp
from map import read_map_from_file
from random import choice

# could be improved by implemented by implemnting inheritance somehow, I guess


class ModifiedNPC:
    def __init__(self, ID: str, place: str, coins: str, items: str, str: str, speed: str, line: str, phase: str, stage: str, state: str) -> None:
        self.ID = int(ID)
        self.place = int(place)
        self.coins = int(coins)
        self.str = int(str)
        self.speed = int(speed)
        self.line = int(line)
        self.phase = phase
        self.stage = stage
        self.items = [int(x) for x in items.split(";") if x != ""]
        self.state = state

    def __repr__(self):  # changed it from str might break smth else
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

    def to_str(self) -> str:
        list_to_link = []
        for NPC in self.list:
            items = ",".join([str(x) for x in NPC.items])
            list_to_link.append(
                f"place:{NPC.place.ID},coins:{NPC.coins},items:{items},str:{NPC.str},speed:{NPC.speed},line:{NPC.line},phase:{NPC.phase},stage:{NPC.stage},state:{NPC.state}")
        return "+".join(list_to_link)

    def get_NPC(self, ID: int) -> ModifiedNPC:
        return self.list[ID]


def get_current_characters(old_character_save: str) -> ModifiedPeople:
    """
    Function takes the part of save string which has data about characters and returns ModifiedPeople object that store ModifiedNPC object for every single character
    """
    old_char_save_list = old_character_save.split("+")
    current_characters = ModifiedPeople()

    for char_save_str_idx in range(len(old_char_save_list)):
        char_parts = old_char_save_list[char_save_str_idx].split(",")
        parts_dict: dict[str, str] = dict()

        for part in char_parts:
            key, val = part.split(":")
            parts_dict[key] = val

        current_characters.add_NPC(ModifiedNPC(char_save_str_idx, parts_dict["place"], parts_dict["coins"], parts_dict["items"], parts_dict["str"],
                                               parts_dict["speed"], parts_dict["line"], parts_dict["phase"], parts_dict["stage"], parts_dict["state"]))

    return current_characters


def update_phases(modified_characters: ModifiedPeople) -> tuple[ModifiedPeople, dict[int, str]]:
    """
    Function takes characters as Modified People object and update stages based on their location and actions and returns this modified object.
    It also returns dictionary where key is ID of a quest line of which phase was just finished.
    """
    lines_to_update: dict[int, str] = dict()
    for character in modified_characters.list:
        if character.phase != "-1":
            current_phase = str_to_mqp(character.phase)

            if character.stage == "tostart" and current_phase.from_place_ID == character.place:
                character.stage = "inprogress"

            elif character.stage == "inprogress" and current_phase.to_place_ID == character.place:
                character.stage = "ended"

            if character.stage == "ended":
                # TODO add the actions that NPCs can do. Returns Fail if failed
                if current_phase.action == "kill" or current_phase.action == "stun":
                    defender = modified_characters.get_NPC(current_phase.go_to)
                    modified_characters = fight(
                        character, defender, current_phase.action, modified_characters)

                stage_failed = choice([True, False])

                if stage_failed == True:
                    lines_to_update[character.line] = "F"
                    character.stage = "-1"
                    character.line = -1
                    character.phase = "-1"
                else:
                    lines_to_update[character.line] = "S"
                    character.stage = "-1"
                    character.line = -1
                    character.phase = "-1"

    return modified_characters, lines_to_update


def move_characters(modified_characters: ModifiedPeople) -> ModifiedPeople:
    """
    Function takes characters as Modified People object and move them to their designated place and returns modified ModifiedPeople
    """
    characters_definition = read_people_from_file("data\characters.csv")
    map = read_map_from_file("data\streets.csv")
    for character in modified_characters.list:
        if character.phase != "-1":
            current_phase = str_to_mqp(character.phase)
            if character.stage == "tostart":
                final_point = current_phase.from_place_ID
            else:
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

        if len(path) == 1:
            next_place = path[0]
        else:
            # Idx is 1 because first street in path is starting street
            next_place = path[1]
        character.place = next_place

    return modified_characters


"""originaly in character_interactions but circular import :("""


def how_char1_loves_char2(char1: NPC, char2: NPC, fractions=read_fractions_from_file(r"data\fractions.csv")) -> int:
    return fractions.get_fraction(char1.fraction_ID).relations[char2.fraction_ID]


def fight(attacker: ModifiedNPC, defender: ModifiedNPC, action: str, current_characters: ModifiedPeople) -> ModifiedPeople:
    people = read_people_from_file(r"data\characters.csv")
    fractions = read_fractions_from_file(r"data\fractions.csv")
    attacker_NPC = people.get_char_by_ID(attacker.ID)
    defender_NPC = people.get_char_by_ID(defender.ID)

    attacker_bonus = 0

    # attackers speed or moment of surprise inflicts advantage for him
    if attacker.speed > defender.speed + 1 or attacker_NPC.fraction_ID == defender_NPC.fraction_ID or fractions.get_fraction(defender_NPC.fraction_ID).relations[attacker_NPC.fraction_ID] >= 2:
        attacker_bonus = 1

    attacker_side: list[ModifiedNPC] = []
    defender_side: list[ModifiedNPC] = []

    for character in current_characters.list:
        if character.place == attacker.place:
            character_NPC = people.get_char_by_ID(character.ID)
            likes_attacker = how_char1_loves_char2(character_NPC, attacker_NPC)
            likes_defender = how_char1_loves_char2(character_NPC, defender_NPC)
            if likes_attacker >= 3 and likes_defender >= 3:
                likes_defender = likes_attacker = 2

            if character_NPC.fraction_ID == attacker_NPC.fraction_ID or likes_attacker >= 3:
                attacker_side.append(character)

            if character_NPC.fraction_ID == defender_NPC.fraction_ID or likes_defender >= 3:
                defender_side.append(character)

    attacker_bonus += (len(attacker_side) - len(defender_side)) * 2

    total_attack_power = sum([x.str for x in attacker_side]) + attacker_bonus
    total_defend_power = sum([x.str for x in defender_side])

    print("attack power:", total_attack_power,
          "defend power:", total_defend_power)

    if total_attack_power > total_defend_power+1:
        if action == "kill":
            for char in defender_side:
                char.state = "dead"
                print(char.ID, char.state)
        else:
            for char in defender_side:
                char.state = "stun"
                print(char.ID, char.state)

    elif total_attack_power > total_defend_power:
        for char in defender_side:
            char.state = "stun"
            print(char.ID, char.state)

    elif total_attack_power == total_defend_power:
        for char in defender_side + attacker_side:
            char.state = "stun"
            print(char.ID, char.state)

    elif total_attack_power < total_defend_power:
        if action == "kill":
            for char in attacker_side:
                char.state = "dead"
                print(char.ID, char.state)
        else:
            for char in attacker_side:
                char.state = "stun"
                print(char.ID, char.state)

    return current_characters


if __name__ == "__main__":
    character_save = "place:32,state:alive,coins:11,items:,str:3,speed:2,line:-1,phase:-1,stage:-1+place:35,state:alive,coins:10,items:,str:1,speed:4,line:-1,phase:-1,stage:-1+place:35,state:alive,coins:2,items:,str:3,speed:2,line:-1,phase:-1,stage:-1+place:35,state:alive,coins:14,items:,str:3,speed:1,line:-1,phase:-1,stage:-1+place:33,state:alive,coins:0,items:,str:3,speed:2,line:-1,phase:-1,stage:-1+place:34,state:alive,coins:18,items:,str:3,speed:2,line:-1,phase:-1,stage:-1+place:17,state:alive,coins:20,items:,str:1,speed:1,line:-1,phase:-1,stage:-1+place:1,state:alive,coins:16,items:,str:1,speed:3,line:-1,phase:-1,stage:-1+place:13,state:alive,coins:13,items:,str:1,speed:4,line:-1,phase:-1,stage:-1+place:23,state:alive,coins:15,items:,str:3,speed:2,line:-1,phase:-1,stage:-1+place:23,state:alive,coins:12,items:,str:1,speed:2,line:-1,phase:-1,stage:-1+place:37,state:alive,coins:6,items:,str:1,speed:4,line:0,phase:0=char11=-1=0=37=none,stage:inprogress+place:37,state:alive,coins:0,items:,str:1,speed:4,line:-1,phase:-1,stage:-1+place:37,state:alive,coins:17,items:,str:2,speed:3,line:-1,phase:-1,stage:-1+place:37,state:alive,coins:12,items:,str:2,speed:2,line:-1,phase:-1,stage:-1+place:37,state:alive,coins:19,items:,str:1,speed:4,line:-1,phase:-1,stage:-1+place:38,state:alive,coins:5,items:,str:1,speed:2,line:-1,phase:-1,stage:-1+place:38,state:alive,coins:18,items:,str:1,speed:4,line:-1,phase:-1,stage:-1+place:38,state:alive,coins:17,items:,str:1,speed:4,line:-1,phase:-1,stage:-1+place:38,state:alive,coins:18,items:,str:3,speed:1,line:-1,phase:-1,stage:-1+place:38,state:alive,coins:5,items:,str:1,speed:4,line:-1,phase:-1,stage:-1+place:39,state:alive,coins:14,items:,str:3,speed:2,line:-1,phase:-1,stage:-1+place:39,state:alive,coins:11,items:,str:4,speed:1,line:-1,phase:-1,stage:-1+place:39,state:alive,coins:9,items:,str:2,speed:3,line:-1,phase:-1,stage:-1+place:39,state:alive,coins:18,items:,str:1,speed:4,line:-1,phase:-1,stage:-1+place:39,state:alive,coins:18,items:,str:1,speed:3,line:-1,phase:-1,stage:-1+place:39,state:alive,coins:16,items:,str:2,speed:3,line:-1,phase:-1,stage:-1"
    modified_people = get_current_characters(character_save)

    # checking if someone finished quest or is final location
    modified_people, lines_to_update = update_phases(modified_people)

    # move characters to quest
    modified_people = move_characters(modified_people)
