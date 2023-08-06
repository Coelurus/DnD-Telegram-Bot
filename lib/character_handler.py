from character import read_people_from_file, read_fractions_from_file, NPC, Society
from quest import str_to_mqp
from map import read_map_from_file, Street
from items import read_items_from_file, ItemsCollection
from random import choice

import json

# could be improved by implemented by implemnting inheritance somehow, I guess


class ModifiedNPC:
    """Class to store data about current state of a character"""

    def __init__(
        self,
        ID: str,
        place: str,
        coins: str,
        items: str,
        str: str,
        speed: str,
        line: str,
        phase: str,
        stage: str,
        state: str,
    ) -> None:
        self.ID = int(ID)
        self.place_ID = int(place)
        self.coins = int(coins)
        self.strength = int(str)
        self.speed = int(speed)
        self.line = int(line)
        self.phase = phase
        self.stage = stage
        # self.items = [int(x) for x in items.split(";") if x != ""]
        self.items = [int(x) for x in items if x != ""]
        self.state = state

    def __repr__(self):
        characters_definition = read_people_from_file("data\characters.csv")
        line_part = ""
        if self.phase != "-1":
            line_part = f"Does quest line {self.line} is at phase {self.phase}. Currently at: {self.stage}"
        return (
            f"NPC {characters_definition.people_list[self.ID]} currently at place {self.place_ID} has {self.coins} coins. Str = {self.strength}, speed = {self.speed}. Has items: {self.items}. "
            + line_part
        )

    def get_name_cz(self, society: Society):
        return society.get_char_by_ID(self.ID).name_cz


class ModifiedPeople:
    """Class to store all current characters as ModifiedNPCs"""

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
        """Parse object to string thus it can be saved"""
        character_json: list[dict[str]] = list()

        list_to_link = []
        for NPC in self.list:
            character_json.append(dict())
            items = ";".join([str(x) for x in NPC.items])
            list_to_link.append(
                f"place:{NPC.place_ID},coins:{NPC.coins},items:{items},str:{NPC.strength},speed:{NPC.speed},line:{NPC.line},phase:{NPC.phase},stage:{NPC.stage},state:{NPC.state}"
            )
            character_json[-1]["place"] = NPC.place_ID
            character_json[-1]["coins"] = NPC.coins
            character_json[-1]["items"] = NPC.items
            character_json[-1]["str"] = NPC.strength
            character_json[-1]["speed"] = NPC.speed
            character_json[-1]["line"] = NPC.line
            character_json[-1]["phase"] = NPC.phase
            character_json[-1]["stage"] = NPC.stage
            character_json[-1]["state"] = NPC.state

        return "+".join(list_to_link), json.dumps(character_json)

    def get_NPC(self, ID: int) -> ModifiedNPC:
        """Get a ModifiedNPC object based on its ID"""
        return self.list[ID]

    def get_people_in_place(self, place_ID: int) -> list[ModifiedNPC]:
        """Get list of characters as ModifiedNPCs in defined place"""
        found_people = []
        for char in self.list:
            if char.place_ID == place_ID:
                found_people.append(char)
        return found_people


def get_current_characters(old_character_save: list[dict[str]]) -> ModifiedPeople:
    """
    Function takes the part of save string which has data about characters and returns ModifiedPeople object that store ModifiedNPC object for every single character
    """
    old_char_save_list = old_character_save
    current_characters = ModifiedPeople()

    for char_save_str_idx in range(len(old_char_save_list)):
        char_parts = old_char_save_list[char_save_str_idx]

        # parts_dict: dict[str, str] = dict()

        # for part in char_parts:
        #     key, val = part.split(":")
        #     parts_dict[key] = val

        current_characters.add_NPC(
            ModifiedNPC(
                char_save_str_idx,
                char_parts["place"],
                char_parts["coins"],
                char_parts["items"],
                char_parts["str"],
                char_parts["speed"],
                char_parts["line"],
                char_parts["phase"],
                char_parts["stage"],
                char_parts["state"],
            )
        )

    return current_characters


def update_phases(
    modified_characters: ModifiedPeople,
) -> tuple[ModifiedPeople, dict[int, str], bool]:
    """
    Function takes characters as Modified People object and update stages based on their location and actions and returns this modified object.
    It also returns dictionary where key is ID of a quest line of which phase was just finished and bool if one of characters finished mission that is game ending.
    """
    game_ended = False
    game_ending_str = ""

    lines_to_update: dict[int, str] = dict()
    for character in modified_characters.list:
        if character.phase != "-1":
            current_phase = str_to_mqp(character.phase)
            # If there is a character who has a quest and is dead it is labeled
            # as ended and afterwards will yield in failure of this phase
            if character.state == "dead":
                character.stage = "ended"

            # Character gets to starting location
            if (
                character.stage == "tostart"
                and current_phase.from_place_ID == character.place_ID
            ):
                character.stage = "inprogress"

            # Character whose phases is dynamically generated got in the location with his target
            elif (
                character.stage == "inprogress"
                and current_phase.go_to != -1
                and modified_characters.get_NPC(current_phase.go_to).place_ID
                == character.place_ID
            ):
                character.stage = "ended"

            # Character got in the given fixed location
            elif (
                character.stage == "inprogress"
                and current_phase.to_place_ID == character.place_ID
            ):
                character.stage = "ended"

            # Resolving additional actions performed by characters
            if character.stage == "ended":
                if character.state != "dead":
                    stage_failed = False
                    if current_phase.action == "kill" or current_phase.action == "stun":
                        defender = modified_characters.get_NPC(current_phase.go_to)
                        # So characters can not kill already dead characters
                        if defender.state == "dead":
                            pass
                        elif defender.state == "stun":
                            if current_phase.action == "kill":
                                defender.state = "dead"
                            elif current_phase.action == "stun":
                                pass
                        else:
                            modified_characters, stage_failed = fight(
                                character,
                                defender,
                                current_phase.action,
                                modified_characters,
                            )

                    elif (
                        current_phase.action == "rob" or current_phase.action == "plant"
                    ):
                        defender = modified_characters.get_NPC(current_phase.go_to)
                        modified_characters, stage_failed = steal(
                            character,
                            defender,
                            current_phase.action,
                            modified_characters,
                        )

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

                # Special case for ending game since one
                if current_phase.quest_phase_ID == 666 and stage_failed == False:
                    game_ended = True
                    # TODO ending string should be based on the quest line that it came from
                    # However since game supports only one game ending condition at the moment it works
                    game_ending_str = "Kultisti ti *zabili* kočku\.\nSvět upadl do *chaos*u\.\nVíce štěstí příště \U0001F5A4"

    return modified_characters, lines_to_update, game_ended, game_ending_str


def move_characters(modified_characters: ModifiedPeople) -> ModifiedPeople:
    """
    Function takes characters as Modified People object and move them to their designated place and returns modified ModifiedPeople
    """
    characters_definition = read_people_from_file("data\characters.csv")
    map = read_map_from_file("data\streets.csv")
    for character in modified_characters.list:
        if character.state == "alive":
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
                    if character.stage == "tostart":
                        final_point = current_phase.from_place_ID
                    else:
                        final_point = modified_characters.get_NPC(
                            current_phase.go_to
                        ).place_ID

            # Character has designated end location
            elif characters_definition.get_char_by_ID(character.ID).end_street_ID != -1:
                final_point = characters_definition.get_char_by_ID(
                    character.ID
                ).end_street_ID

            # Character just moves on random
            else:
                final_point = choice(
                    map.get_street_by_ID(character.place_ID).connections
                    + [character.place_ID]
                )

            # TODO add places and characters to avoid
            path = map.find_shortest_path(
                *map.BFS(map.get_street_by_ID(character.place_ID)),
                map.get_street_by_ID(final_point),
            )

            if len(path) == 1:
                next_place = path[0].ID
            else:
                # Idx is 1 because first street in path is starting street
                next_place = path[1].ID

            character.place_ID = next_place

    return modified_characters


def how_char1_loves_char2(
    char1: NPC, char2: NPC, fractions=read_fractions_from_file(r"data\fractions.csv")
) -> int:
    """get on which level is relationship of char 1 with char 2"""
    return fractions.get_fraction(char1.fraction_ID).relations[char2.fraction_ID]


def get_items_attributes(list_of_people: list[ModifiedNPC], type: str) -> int:
    """Return modifier defined by argument type. Function looks through items of all Modified NPCs and returns sum of their modifiers"""
    items_collection = read_items_from_file("data\items.csv")
    # TODO Does not look really nice. Should be added more obvious way to take care of player Items
    # In list can be an object of type Player. In this case we have to get modifiers from his equiped weapons
    lists_of_items_IDs = [
        person.items if isinstance(person, ModifiedNPC) else person.equiped_weapons
        for person in list_of_people
    ]
    all_items: list[int] = []
    for list in lists_of_items_IDs:
        for item in list:
            all_items.append(item)

    if type == "str":
        return sum(
            [items_collection.get_item(item_ID).strength_mod for item_ID in all_items]
        )

    elif type == "speed":
        return sum(
            [items_collection.get_item(item_ID).speed_mod for item_ID in all_items]
        )


def fight(
    attacker,
    defender: ModifiedNPC,
    action: str,
    current_characters: ModifiedPeople,
    attacker_bonus: int = 0,
) -> tuple[ModifiedPeople, bool]:
    """Function takes care of an fight between multiple characters
    might include Player as an attacker -> in that case is attacker: Player
    otherwise attacker: ModifiedNPC
    Function returns 2 values, first is list of newly modified people and second is falure/success of an attack
    """
    people = read_people_from_file(r"data\characters.csv")
    fractions = read_fractions_from_file(r"data\fractions.csv")

    # Get the fraction based on attacker type
    if isinstance(attacker, ModifiedNPC):
        attacker_NPC = people.get_char_by_ID(attacker.ID)
        attacker_fraction = attacker_NPC.fraction_ID
    else:
        attacker_fraction = attacker.fraction_ID

    defender_NPC = people.get_char_by_ID(defender.ID)

    phase_failed = False

    # attackers speed or moment of surprise inflicts advantage for him
    if (
        attacker.speed > defender.speed + 1
        or attacker_fraction == defender_NPC.fraction_ID
        or fractions.get_fraction(defender_NPC.fraction_ID).relations[attacker_fraction]
        >= 2
    ):
        attacker_bonus = 1

    # Player would not be added to the attacker list automatically since it goes only through characters in place
    if isinstance(attacker, ModifiedNPC):
        attacker_side: list[ModifiedNPC] = []
    else:
        attacker_side: list[ModifiedNPC] = [attacker]
    defender_side: list[ModifiedNPC] = []

    # Other characters might be added to the fight as well.
    # They must be in the same place and their relationship to one of the fighting sides must be on the highest level
    for character in current_characters.list:
        if character.place_ID == attacker.place_ID:
            character_NPC = people.get_char_by_ID(character.ID)
            if isinstance(attacker, ModifiedNPC):
                likes_attacker = how_char1_loves_char2(character_NPC, attacker_NPC)
            else:
                likes_attacker = attacker.get_relationships([character], people)[
                    character.ID
                ]
            likes_defender = how_char1_loves_char2(character_NPC, defender_NPC)
            if likes_attacker >= 3 and likes_defender >= 3:
                likes_defender = likes_attacker = 2

            if character_NPC.fraction_ID == attacker_fraction or likes_attacker >= 3:
                attacker_side.append(character)

            if (
                character_NPC.fraction_ID == defender_NPC.fraction_ID
                or likes_defender >= 3
            ):
                defender_side.append(character)

    # When there is more people on either side it gives an advantage to this side
    attacker_bonus += (len(attacker_side) - len(defender_side)) * 2

    items_attacker_mod = get_items_attributes(attacker_side, "str")
    items_defender_mod = get_items_attributes(defender_side, "str")

    total_attack_power = (
        sum([x.strength for x in attacker_side]) + items_attacker_mod + attacker_bonus
    )
    total_defend_power = sum([x.strength for x in defender_side]) + items_defender_mod

    dead_list: list[ModifiedNPC] = []
    stun_list: list[ModifiedNPC] = []

    # Goes through all possible outcomes of strength comparisons and based on that and the type it determines final states of characters in combat
    if total_attack_power > total_defend_power + 1:
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

    """if len(dead_list) > 0:
        print(", ".join([str(char.ID) if isinstance(char, ModifiedNPC)
              else "hráč" for char in dead_list]), "fought and died")
    if len(stun_list) > 0:
        print(", ".join([str(char.ID) if isinstance(char, ModifiedNPC)
              else "hráč" for char in stun_list]), "fought and got stunned")"""

    return current_characters, phase_failed


def steal(
    attacker, defender: ModifiedNPC, action: str, current_characters: ModifiedPeople
) -> tuple[ModifiedPeople, bool]:
    """Function takes care of an action where attacker tries to steal (or plant) items from defender
    Function returns updated ModifiedPeople and information about success/failure
    Similarly to fight, attacker might be a Player object"""
    people = read_people_from_file(r"data\characters.csv")
    fractions = read_fractions_from_file(r"data\fractions.csv")

    # Get the fraction based on attacker type
    if isinstance(attacker, ModifiedNPC):
        attacker_NPC = people.get_char_by_ID(attacker.ID)
        attacker_fraction = attacker_NPC.fraction_ID
        attacker_name = attacker_NPC.name_cz
    else:
        attacker_fraction = attacker.fraction_ID
        attacker_name = "Player"

    defender_NPC = people.get_char_by_ID(defender.ID)

    phase_failed = False
    attacker_bonus = 0

    # Get relations based on attacker type
    if isinstance(attacker, ModifiedNPC):
        if how_char1_loves_char2(defender_NPC, attacker_NPC, fractions) >= 3:
            attacker_bonus += 1
    else:
        if (
            attacker_fraction == defender_NPC.fraction_ID
            or attacker.get_relationships([defender], people)[defender.ID] >= 3
        ):
            attacker_bonus += 1

    items_attacker_mod = get_items_attributes([attacker], "speed")
    items_defender_mod = get_items_attributes([defender], "speed")

    attacker_speed = attacker.speed + attacker_bonus + items_attacker_mod
    # if defender is stunned or dead, he automatically loses
    defender_speed = (
        -69 if defender.state != "alive" else defender.speed
    ) + items_defender_mod

    # outcomes of an encounter are defined by total speed level comparison
    if attacker_speed > defender_speed:
        if action == "rob":
            stolen_items = defender.items
            defender.items = []
            attacker.items += stolen_items

            """print(attacker_name, "stole:",
                  stolen_items, "from", defender_NPC.name_cz)"""

        elif action == "plant":
            # TODO plant only the quest item and not all
            planted_items = attacker.items
            attacker.items = []
            defender.items += planted_items

            """print(attacker_name, "planted:",
                  planted_items, "into pockets of", defender_NPC.name_cz)"""

    elif attacker_speed == defender_speed:
        # print(attacker_name, "failed", action)
        phase_failed = True
        current_characters, _ = fight(attacker, defender, "stun", current_characters)

    else:
        # print(attacker_name, "failed", action)
        phase_failed = True
        current_characters, _ = fight(
            attacker, defender, "stun", current_characters, -1
        )

    return current_characters, phase_failed


if __name__ == "__main__":
    character_save = "place:32,coins:20,items:,str:3,speed:5,line:-1,phase:-1,stage:-1,state:alive+place:35,coins:15,items:,str:4,speed:1,line:-1,phase:-1,stage:-1,state:alive+place:35,coins:16,items:,str:3,speed:2,line:-1,phase:-1,stage:-1,state:alive+place:35,coins:9,items:,str:1,speed:2,line:-1,phase:-1,stage:-1,state:alive+place:33,coins:10,items:,str:4,speed:5,line:-1,phase:-1,stage:-1,state:alive+place:34,coins:20,items:,str:2,speed:3,line:-1,phase:-1,stage:-1,state:alive+place:17,coins:1,items:,str:1,speed:1,line:-1,phase:-1,stage:-1,state:alive+place:1,coins:4,items:,str:1,speed:4,line:-1,phase:-1,stage:-1,state:alive+place:13,coins:9,items:,str:1,speed:3,line:-1,phase:-1,stage:-1,state:alive+place:23,coins:19,items:,str:1,speed:3,line:-1,phase:-1,stage:-1,state:alive+place:23,coins:8,items:,str:2,speed:2,line:-1,phase:-1,stage:-1,state:alive+place:37,coins:12,items:,str:1,speed:4,line:-1,phase:-1,stage:-1,state:alive+place:37,coins:13,items:,str:3,speed:2,line:0,phase:0=char12=36=0=37=none=40%-1,stage:tostart,state:alive+place:37,coins:3,items:,str:1,speed:3,line:-1,phase:-1,stage:-1,state:alive+place:37,coins:3,items:,str:3,speed:2,line:-1,phase:-1,stage:-1,state:alive+place:37,coins:4,items:,str:2,speed:2,line:-1,phase:-1,stage:-1,state:alive+place:38,coins:15,items:,str:3,speed:1,line:-1,phase:-1,stage:-1,state:alive+place:38,coins:1,items:,str:1,speed:4,line:-1,phase:-1,stage:-1,state:alive+place:38,coins:6,items:,str:1,speed:1,line:-1,phase:-1,stage:-1,state:alive+place:38,coins:17,items:,str:4,speed:1,line:-1,phase:-1,stage:-1,state:alive+place:38,coins:16,items:,str:1,speed:1,line:-1,phase:-1,stage:-1,state:alive+place:39,coins:6,items:,str:1,speed:4,line:5,phase:0=char21=-1=-1=0=none=25%-1,stage:inprogress,state:alive+place:39,coins:6,items:,str:2,speed:3,line:6,phase:0=char22=-1=-1=6=none=25%-1,stage:inprogress,state:alive+place:39,coins:8,items:,str:4,speed:1,line:7,phase:0=char23=-1=-1=12=none=25%-1,stage:inprogress,state:alive+place:39,coins:19,items:,str:2,speed:3,line:-1,phase:-1,stage:-1,state:alive+place:39,coins:18,items:,str:2,speed:2,line:-1,phase:-1,stage:-1,state:alive+place:39,coins:3,items:,str:1,speed:4,line:-1,phase:-1,stage:-1,state:alive+place:7,coins:20,items:,str:1,speed:4,line:1,phase:7=char27=-1=9=?=30;kill=30%-1,stage:inprogress,state:alive+place:7,coins:12,items:,str:2,speed:2,line:2,phase:7=char28=-1=8=?=31;kill=30%-1,stage:inprogress,state:alive+place:7,coins:7,items:,str:1,speed:4,line:3,phase:7=char29=-1=-1=?=31;kill=30%-1,stage:inprogress,state:alive+place:1,coins:4,items:,str:1,speed:3,line:-1,phase:-1,stage:-1,state:alive+place:1,coins:12,items:,str:3,speed:2,line:-1,phase:-1,stage:-1,state:alive+place:19,coins:20,items:,str:1,speed:5,line:4,phase:9=char32=-1=7=?=33;plant=20%-1,stage:inprogress,state:alive+place:20,coins:13,items:,str:1,speed:3,line:-1,phase:-1,stage:-1,state:alive+place:3,coins:3,items:,str:3,speed:2,line:-1,phase:-1,stage:-1,state:alive"
    modified_people = get_current_characters(character_save)

    # checking if someone finished quest or is final location
    modified_people, lines_to_update, game_ended, game_ending_str = update_phases(
        modified_people
    )

    # move characters to quest
    modified_people = move_characters(modified_people)
