from character import read_people_from_file, read_fractions_from_file, NPC, Society
from quest import str_to_mqp
from map import read_map_from_file, Street
from items import read_items_from_file, ItemsCollection
from random import choice

# could be improved by implemented by implemnting inheritance somehow, I guess


class ModifiedNPC:
    def __init__(self, ID: str, place: str, coins: str, items: str, str: str, speed: str, line: str, phase: str, stage: str, state: str) -> None:
        self.ID = int(ID)
        self.place_ID = int(place)
        self.coins = int(coins)
        self.strength = int(str)
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
        return f"NPC {characters_definition.people_list[self.ID]} currently at place {self.place_ID} has {self.coins} coins. Str = {self.strength}, speed = {self.speed}. Has items: {self.items}. " + line_part

    def get_name_cz(self, society: Society):
        return society.get_char_by_ID(self.ID).name_cz


class ModifiedPeople:
    def __init__(self) -> None:
        self.list: list[ModifiedNPC] = []

    def add_NPC(self, character: ModifiedNPC) -> None:
        # When character has a quest, then there is a modifier for an item
        if character.line != -1:
            item_ID = str_to_mqp(character.phase).item_ID
            # Modifier -1 stands for nothing but any other whole number is index of an item
            if item_ID != -1:
                if item_ID not in character.items:
                    character.items.append(item_ID)
        self.list.append(character)

    def __repr__(self) -> str:
        return "\n".join([str(x) for x in self.list])

    def to_str(self) -> str:
        list_to_link = []
        for NPC in self.list:
            items = ",".join([str(x) for x in NPC.items])
            list_to_link.append(
                f"place:{NPC.place_ID},coins:{NPC.coins},items:{items},str:{NPC.strength},speed:{NPC.speed},line:{NPC.line},phase:{NPC.phase},stage:{NPC.stage},state:{NPC.state}")
        return "+".join(list_to_link)

    def get_NPC(self, ID: int) -> ModifiedNPC:
        return self.list[ID]

    def get_people_in_place(self, place_ID: int) -> list[ModifiedNPC]:
        found_people = []
        for char in self.list:
            if char.place_ID == place_ID:
                found_people.append(char)
        return found_people


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
            # If there is a character who has a quest and is dead it is labeled
            # as ended and afterwards will yield in failure of this phase
            if character.state == "dead":
                character.stage = "ended"

            # Character gets to starting location
            if character.stage == "tostart" and current_phase.from_place_ID == character.place_ID:
                character.stage = "inprogress"
                print(character.ID, "is now working on", character.phase)

            # Character whose phases is dynamically generated got in the location with his target
            elif character.stage == "inprogress" and current_phase.go_to != -1 and modified_characters.get_NPC(current_phase.go_to).place_ID == character.place_ID:
                character.stage = "ended"
                print(character.ID, "just ended", character.phase)

            # Character got in the given fixed location
            elif character.stage == "inprogress" and current_phase.to_place_ID == character.place_ID:
                character.stage = "ended"
                print(character.ID, "just ended", character.phase)

            # Resolving additional actions performed by characters
            if character.stage == "ended":
                if character.state != "dead":
                    stage_failed = False
                    if current_phase.action == "kill" or current_phase.action == "stun":
                        defender = modified_characters.get_NPC(
                            current_phase.go_to)
                        # So characters can not kill already dead characters
                        if defender.state == "dead":
                            print(defender.ID, "is already dead")
                        elif defender.state == "stun":
                            if current_phase.action == "kill":
                                defender.state = "dead"
                                print(defender.ID, "was stunned and now is dead")
                            elif current_phase.action == "stun":
                                print(defender.ID, "is already stunned")
                        else:
                            modified_characters, stage_failed = fight(
                                character, defender, current_phase.action, modified_characters)

                    elif current_phase.action == "rob" or current_phase.action == "plant":
                        defender = modified_characters.get_NPC(
                            current_phase.go_to)
                        modified_characters, stage_failed = steal(
                            character, defender, current_phase.action, modified_characters)

                # Dead character automatically yields in failure
                else:
                    stage_failed = True

                # Setting characters to be able to recieve new quests
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
        # Character has a quest to follow
        if character.phase != "-1":
            current_phase = str_to_mqp(character.phase)
            # Final place is fixed
            if current_phase.go_to == -1:
                if character.stage == "tostart":
                    final_point = current_phase.from_place_ID
                else:
                    final_point = current_phase.to_place_ID
            # In case character should go to someone else, place is dynamicaly changed each turn
            else:
                final_point = modified_characters.get_NPC(
                    current_phase.go_to).place_ID

        # Character has designated end location
        elif characters_definition.get_char_by_ID(character.ID).end_street_ID != -1:
            final_point = characters_definition.get_char_by_ID(
                character.ID).end_street_ID

        # Character just moves on random
        else:
            final_point = choice(map.get_street_by_ID(
                character.place_ID).connections + [character.place_ID])

        # TODO add places and characters to avoid
        path = map.find_shortest_path(*map.BFS(map.get_street_by_ID(character.place_ID)),
                                      map.get_street_by_ID(final_point))

        if len(path) == 1:
            next_place = path[0].ID
        else:
            # Idx is 1 because first street in path is starting street
            next_place = path[1].ID

        if isinstance(next_place, int) is not True:
            print("ojojooo")
        character.place_ID = next_place

    return modified_characters


def how_char1_loves_char2(char1: NPC, char2: NPC, fractions=read_fractions_from_file(r"data\fractions.csv")) -> int:
    return fractions.get_fraction(char1.fraction_ID).relations[char2.fraction_ID]


def get_items_attributes(list_of_people: list[ModifiedNPC], type: str) -> int:
    items_collection = read_items_from_file("data\items.csv")
    lists_of_items_IDs = [person.items for person in list_of_people]
    all_items: list[int] = []
    for list in lists_of_items_IDs:
        for item in list:
            all_items.append(item)

    if type == "str":
        return sum([items_collection.get_item(
            item_ID).strength_mod for item_ID in all_items])

    elif type == "speed":
        return sum([items_collection.get_item(
            item_ID).speed_mod for item_ID in all_items])


def fight(attacker, defender: ModifiedNPC, action: str, current_characters: ModifiedPeople, attacker_bonus: int = 0) -> tuple[ModifiedPeople, bool]:
    people = read_people_from_file(r"data\characters.csv")
    fractions = read_fractions_from_file(r"data\fractions.csv")

    if isinstance(attacker, ModifiedNPC):
        attacker_NPC = people.get_char_by_ID(attacker.ID)
        attacker_fraction = attacker_NPC.fraction_ID
    else:
        attacker_fraction = attacker.fraction_ID

    defender_NPC = people.get_char_by_ID(defender.ID)

    phase_failed = False

    # attackers speed or moment of surprise inflicts advantage for him
    if attacker.speed > defender.speed + 1 or attacker_fraction == defender_NPC.fraction_ID or fractions.get_fraction(defender_NPC.fraction_ID).relations[attacker_fraction] >= 2:
        attacker_bonus = 1

    if isinstance(attacker, ModifiedNPC):
        attacker_side: list[ModifiedNPC] = []
    else:
        attacker_side: list[ModifiedNPC] = [attacker]
    defender_side: list[ModifiedNPC] = []

    for character in current_characters.list:
        if character.place_ID == attacker.place_ID:
            character_NPC = people.get_char_by_ID(character.ID)
            if isinstance(attacker, ModifiedNPC):
                likes_attacker = how_char1_loves_char2(
                    character_NPC, attacker_NPC)
            else:
                likes_attacker = attacker.get_relationships(
                    [character], people)[character.ID]
            likes_defender = how_char1_loves_char2(character_NPC, defender_NPC)
            if likes_attacker >= 3 and likes_defender >= 3:
                likes_defender = likes_attacker = 2

            if character_NPC.fraction_ID == attacker_fraction or likes_attacker >= 3:
                attacker_side.append(character)

            if character_NPC.fraction_ID == defender_NPC.fraction_ID or likes_defender >= 3:
                defender_side.append(character)

    attacker_bonus += (len(attacker_side) - len(defender_side)) * 2

    items_attacker_mod = get_items_attributes(attacker_side, "str")
    items_defender_mod = get_items_attributes(defender_side, "str")

    total_attack_power = sum([x.strength for x in attacker_side]) + \
        items_attacker_mod + attacker_bonus
    total_defend_power = sum(
        [x.strength for x in defender_side]) + items_defender_mod

    dead_list: list[ModifiedNPC] = []
    stun_list: list[ModifiedNPC] = []

    if total_attack_power > total_defend_power+1:
        if action == "kill":
            for char in defender_side:
                char.state = "dead"
                dead_list.append(char)
        elif action == "stun":
            for char in defender_side:
                char.state = "stun"
                stun_list.append(char)

    elif total_attack_power > total_defend_power:
        for char in defender_side:
            char.state = "stun"
            stun_list.append(char)

    elif total_attack_power == total_defend_power:
        for char in defender_side + attacker_side:
            char.state = "stun"
            phase_failed = True
            stun_list.append(char)

    elif total_attack_power < total_defend_power:
        if action == "kill":
            for char in attacker_side:
                char.state = "dead"
                phase_failed = True
                dead_list.append(char)
        else:
            for char in attacker_side:
                char.state = "stun"
                phase_failed = True
                stun_list.append(char)

    for char in dead_list:
        char.stage = "ended"

    if len(dead_list) > 0:
        print(", ".join([str(char.ID) if isinstance(char, ModifiedNPC)
              else "hráč" for char in dead_list]), "fought and died")
    if len(stun_list) > 0:
        print(", ".join([str(char.ID) if isinstance(char, ModifiedNPC)
              else "hráč" for char in stun_list]), "fought and got stunned")

    return current_characters, phase_failed


def steal(attacker: ModifiedNPC, defender: ModifiedNPC, action: str, current_characters: ModifiedPeople) -> tuple[ModifiedPeople, bool]:
    people = read_people_from_file(r"data\characters.csv")
    fractions = read_fractions_from_file(r"data\fractions.csv")
    attacker_NPC = people.get_char_by_ID(attacker.ID)
    defender_NPC = people.get_char_by_ID(defender.ID)

    phase_failed = False
    attacker_bonus = 0

    if how_char1_loves_char2(defender_NPC, attacker_NPC, fractions) >= 3:
        attacker_bonus += 1

    items_attacker_mod = get_items_attributes([attacker], "speed")
    items_defender_mod = get_items_attributes([defender], "speed")

    attacker_speed = attacker.speed + attacker_bonus
    defender_speed = 0 if defender.state != "alive" else defender.speed

    if attacker_speed > defender_speed:
        if action == "rob":
            stolen_items = defender.items
            defender.items = []
            attacker.items += stolen_items

            print(attacker_NPC.name_cz, "stole:",
                  stolen_items, "from", defender_NPC.name_cz)

        elif action == "plant":
            # TODO plant only the quest item and not all
            planted_items = attacker.items
            attacker.items = []
            defender.items += planted_items

            print(attacker_NPC.name_cz, "planted:",
                  planted_items, "into pockets of", defender_NPC.name_cz)

    elif attacker_speed == defender_speed:
        print(attacker_NPC.name_cz, "failed", action)
        current_characters, _ = fight(
            attacker, defender, "stun", current_characters)

    else:
        print(attacker_NPC.name_cz, "failed", action)
        current_characters, _ = fight(
            attacker, defender, "stun", current_characters, -1)

    return current_characters, phase_failed


if __name__ == "__main__":
    character_save = "place:32,state:alive,coins:11,items:,str:3,speed:2,line:-1,phase:-1,stage:-1+place:35,state:alive,coins:10,items:,str:1,speed:4,line:-1,phase:-1,stage:-1+place:35,state:alive,coins:2,items:,str:3,speed:2,line:-1,phase:-1,stage:-1+place:35,state:alive,coins:14,items:,str:3,speed:1,line:-1,phase:-1,stage:-1+place:33,state:alive,coins:0,items:,str:3,speed:2,line:-1,phase:-1,stage:-1+place:34,state:alive,coins:18,items:,str:3,speed:2,line:-1,phase:-1,stage:-1+place:17,state:alive,coins:20,items:,str:1,speed:1,line:-1,phase:-1,stage:-1+place:1,state:alive,coins:16,items:,str:1,speed:3,line:-1,phase:-1,stage:-1+place:13,state:alive,coins:13,items:,str:1,speed:4,line:-1,phase:-1,stage:-1+place:23,state:alive,coins:15,items:,str:3,speed:2,line:-1,phase:-1,stage:-1+place:23,state:alive,coins:12,items:,str:1,speed:2,line:-1,phase:-1,stage:-1+place:37,state:alive,coins:6,items:,str:1,speed:4,line:0,phase:0=char11=-1=0=37=none,stage:inprogress+place:37,state:alive,coins:0,items:,str:1,speed:4,line:-1,phase:-1,stage:-1+place:37,state:alive,coins:17,items:,str:2,speed:3,line:-1,phase:-1,stage:-1+place:37,state:alive,coins:12,items:,str:2,speed:2,line:-1,phase:-1,stage:-1+place:37,state:alive,coins:19,items:,str:1,speed:4,line:-1,phase:-1,stage:-1+place:38,state:alive,coins:5,items:,str:1,speed:2,line:-1,phase:-1,stage:-1+place:38,state:alive,coins:18,items:,str:1,speed:4,line:-1,phase:-1,stage:-1+place:38,state:alive,coins:17,items:,str:1,speed:4,line:-1,phase:-1,stage:-1+place:38,state:alive,coins:18,items:,str:3,speed:1,line:-1,phase:-1,stage:-1+place:38,state:alive,coins:5,items:,str:1,speed:4,line:-1,phase:-1,stage:-1+place:39,state:alive,coins:14,items:,str:3,speed:2,line:-1,phase:-1,stage:-1+place:39,state:alive,coins:11,items:,str:4,speed:1,line:-1,phase:-1,stage:-1+place:39,state:alive,coins:9,items:,str:2,speed:3,line:-1,phase:-1,stage:-1+place:39,state:alive,coins:18,items:,str:1,speed:4,line:-1,phase:-1,stage:-1+place:39,state:alive,coins:18,items:,str:1,speed:3,line:-1,phase:-1,stage:-1+place:39,state:alive,coins:16,items:,str:2,speed:3,line:-1,phase:-1,stage:-1"
    modified_people = get_current_characters(character_save)

    # checking if someone finished quest or is final location
    modified_people, lines_to_update = update_phases(modified_people)

    # move characters to quest
    modified_people = move_characters(modified_people)
