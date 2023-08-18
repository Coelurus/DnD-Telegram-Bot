from player import Player
from character import Society
from quest import (
    read_quest_lines_from_file,
    str_to_mqp,
    mqp_to_str,
    dict_to_mqp,
    mqp_to_json,
    ModifiedQuestPhase,
)
from character_handler import (
    update_phases,
    get_current_characters,
    move_characters,
    ModifiedPeople,
)
import csv
import json


def read_current_save(chat_ID: int) -> str:
    """
    Method takes int parameter to identify save string of defined chat and returns this save string.
    If game has not started yet it returns "NEW_GAME" so program knows to start a new game
    """

    with open("data\game_saves.json", "r", encoding="utf-8") as file:
        json_data = file.read()
        dict_data: dict[int, dict] = json.loads(json_data)
        for ID in dict_data:
            if chat_ID == int(ID):
                return dict_data[ID]
        return "NEW_GAME"


def get_current_player(current_save: dict[str]) -> Player:
    """
    Takes dict where player is saved and returns Player object
    """

    return Player(
        current_save["place"],
        current_save["coins"],
        current_save["items"],
        current_save["str"],
        current_save["speed"],
        current_save["relations"],
        current_save["fraction"],
        current_save["state"],
        current_save["duration"],
        current_save["weapons"],
        current_save["quests"],
        current_save["progress"],
        current_save["round"]
    )


def player_save_generator() -> dict[str]:
    """
    Takes current state of player as Player object and returns his JSON representation.
    """
    player_dict = dict()
    Player.decrease_durations()

    player_dict["place"] = Player.place_ID
    player_dict["coins"] = Player.coins
    player_dict["items"] = Player.items
    player_dict["str"] = Player.strength
    player_dict["speed"] = Player.speed
    player_dict["relations"] = Player.relations
    player_dict["fraction"] = Player.fraction_ID
    player_dict["state"] = Player.state
    player_dict["duration"] = Player.duration
    player_dict["weapons"] = Player.equiped_weapons
    player_dict["quests"] = Player.quests
    player_dict["progress"] = Player.progress
    player_dict["round"] = Player.round

    return player_dict


def first_player_save():
    Player.place_ID = 0
    Player.coins = 25
    Player.items = [7, 8, 9]
    Player.strength = 2
    Player.speed = 2
    Player.relations = [3, 0, 1, 2, 2, 3, 3]
    Player.fraction_ID = 4
    Player.state = "alive"
    Player.duration = []
    Player.equiped_weapons = ""
    Player.quests = [
            {
                "ID": 0,
                "char": 12,
                "from": 37,
                "item": 1,
                "to_place": 32,
                "action": "None",
                "go_to": -1,
                "reward": "40%-1",
                "coin_reward": 40,
                "item_reward": -1,
            },
            {
                "ID": 7,
                "char": 29,
                "from": -1,
                "item": -1,
                "to_place": "?",
                "action": "31;stun",
                "go_to": 31,
                "reward": "14%14",
                "coin_reward": 14,
                "item_reward": 14,
            },
            {
                "ID": 45,
                "char": 15,
                "from": -1,
                "item": 3,
                "to_place": "?",
                "action": "32;rob",
                "go_to": 32,
                "reward": "21%13",
                "coin_reward": 21,
                "item_reward": 13,
            },
            {
                "ID": 17,
                "char": 13,
                "from": -1,
                "item": 7,
                "to_place": "?",
                "action": "2;plant",
                "go_to": 2,
                "reward": "33%5",
                "coin_reward": 33,
                "item_reward": 5,
            }
        ]
    Player.progress = ["tostart", "inprogress", "tostart", "tostart"]
    Player.round = 1


def first_quests_save() -> tuple[dict[int, ModifiedQuestPhase], list]:
    """
    Firstly generates default saves for all quest lines which is empty strings
    Secondly creates dictionary that based on quest line ID returns root modified quest phase of this quest line
    """

    quest_lines = read_quest_lines_from_file(r"data\quest-lines.json")
    quest_states = []
    ID_to_root_quest = dict()
    for quest_ID in quest_lines.ID_to_tree:
        quest_states.append("")

        ID_to_root_quest[quest_ID] = dict_to_mqp(quest_lines.ID_to_tree[quest_ID].value)

    return ID_to_root_quest, quest_states


def get_current_quests(lines_states: list[str]) -> list[str]:
    """
    Takes quest line string save and compares with trees to generate concrete phases for each line.
    Returns list of phases as string
    """
    # TODO read in some main function and then just pass as argument
    quest_lines = read_quest_lines_from_file(r"data\quest-lines.json")
    current_phase_for_line: list[str] = []

    # Goes through tree and quest line progress. When there is S it goes to succes son. Repeat until no more progress or end of the tree
    for quest_line_ID in quest_lines.ID_to_tree:
        node = quest_lines.ID_to_tree[quest_line_ID]
        for line_progres in lines_states[quest_line_ID]:
            if node != "None":
                if line_progres == "S":
                    node = node.succes
                elif line_progres == "F":
                    node = node.failure
            if node == "None":  # the quest line ends here
                current_phase_for_line.append("None")
                break
            else:
                node = node[0]
            # TODO check if it nedělá bordel
        else:
            for phase_node in node.value:
                # for phase_node in node.value:
                current_phase_for_line.append(str(dict_to_mqp(phase_node)))

    return current_phase_for_line


def update_quests(quest_lines: list[str], lines_to_update: dict[int, str]) -> str:
    """Creates updated string that tracks progression of all quest line"""
    # If there was progress in any of the quest lines it will be in lines_to_update dict
    # and added to current quest progress

    for quest_line_idx in range(len(quest_lines)):
        if quest_line_idx in lines_to_update:
            quest_lines[quest_line_idx] += lines_to_update[quest_line_idx]

    return quest_lines


def assign_quests(
    current_characters: ModifiedPeople, current_quests_save: list[list[str]]
) -> ModifiedPeople:
    """Looks through all current quest phases and assign them to specified characters if they are not currently doing anything"""
    char_ID_to_quest: dict[int, list[list[ModifiedQuestPhase], int]] = dict()
    for quest_save_idx in range(len(current_quests_save)):
        # TODO unfinished feature. Quest phases are in fact saves as a list of strings,
        # thus can be trigerred multiple phases at once, however I havn't yet figured
        # simple enough way to track them and how to manage their overall failure vs succes.

        # If a line has not finished yet, look in current phase and save it to a dict where key
        # is assigned character to this phase and value is the save and its index
        if current_quests_save[quest_save_idx] != "None":
            quest_save = str_to_mqp(current_quests_save[quest_save_idx])
            if quest_save != "None":
                char_ID_to_quest[quest_save.characterID] = [quest_save, quest_save_idx]

    # Goes through all characters that can get new assigned phase
    for char_ID in char_ID_to_quest:
        # If they are not doing another phase currently
        if current_characters.list[char_ID].line == -1:
            current_characters.list[char_ID].line = char_ID_to_quest[char_ID][1]
            # current_characters.list[char_ID].phase = mqp_to_str(
            #     char_ID_to_quest[char_ID][0]
            # )

            current_characters.list[char_ID].phase = mqp_to_json(
                char_ID_to_quest[char_ID][0]
            )

            # If quest does not have defined from_place modifier progress is set to inprogress
            if char_ID_to_quest[char_ID][0].from_place_ID == -1:
                current_characters.list[char_ID].stage = "inprogress"
            else:
                current_characters.list[char_ID].stage = "tostart"

    return current_characters


def first_characters_save(quest_ID_to_MQP: dict[int, ModifiedQuestPhase]) -> list[dict[str]]:
    """
    Method takes dictionary where key is quest line ID and value is ModifiedQuestPhase to write quests to character saves
    Based on that and characters.csv method creates string with saves for all characters
    """

    character_json: list[dict[str]] = list()

    character_ID_to_line_ID: dict[int, int] = dict()
    # looking for characters that will have assigned quests
    for quest_line_ID in quest_ID_to_MQP:
        character_ID_to_do_quest = quest_ID_to_MQP[quest_line_ID].characterID
        character_ID_to_line_ID[character_ID_to_do_quest] = quest_line_ID

    # Goes through all characters in existence and if there is a quest that should be assigned to them
    # needed attributes are set to identify the phase and line and progress
    for character in Society.people_list:
        character_json.append(dict())

        if character.ID in character_ID_to_line_ID:
            line = character_ID_to_line_ID[character.ID]
            phase = mqp_to_json(quest_ID_to_MQP[line])
            # phase = str(quest_ID_to_MQP[line])
            if (
                quest_ID_to_MQP[line].from_place_ID == -1
                or quest_ID_to_MQP[line].from_place_ID == character.spawn_street_ID
            ):
                stage = "inprogress"
            else:
                stage = "tostart"
        else:
            line = phase = stage = "-1"

        character_json[-1]["place"] = character.spawn_street_ID
        character_json[-1]["coins"] = character.coins
        character_json[-1]["items"] = character.items
        character_json[-1]["str"] = character.strength
        character_json[-1]["speed"] = character.speed
        character_json[-1]["line"] = line
        character_json[-1]["phase"] = phase
        character_json[-1]["stage"] = stage
        character_json[-1]["state"] = "alive"
        character_json[-1]["duration"] = 0

    return character_json


def rewrite_save_file(change_line_ID: int, new_save_json: dict) -> None:
    """Reads all rows and saves current saves. That rewrites string specified by ID and save new file"""

    with open("data\game_saves.json", "r", encoding="utf-8") as save_file:
        json_data = save_file.read()
        dict_data: dict[str] = json.loads(json_data)
        dict_data[str(change_line_ID)] = new_save_json

    with open("data\game_saves.json", "w", encoding="utf8") as save_file:
        save_file.write(json.dumps(dict_data, indent=4, ensure_ascii=False))



def generate_new_save(chat_ID) -> None:
    """Generating whole new save"""
    # Player introduce - set his starting position and other stuff
    
    first_player_save()
    new_player_save = player_save_generator()

    # Start quest lines
    root_quests_dict, new_quests_json = first_quests_save()

    # Rewrite characters to save
    new_characters_save = first_characters_save(root_quests_dict)

    save_dict = dict()
    save_dict["player"] = new_player_save
    save_dict["quests"] = new_quests_json
    save_dict["characters"] = new_characters_save

    rewrite_save_file(chat_ID, save_dict)
