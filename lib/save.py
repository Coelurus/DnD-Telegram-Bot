from player import Player
from character import read_people_from_file
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

    with open("data\game_saves.json", "r", newline="") as save_file:
        # reader = csv.DictReader(save_file)
        temp_dict = json.loads(save_file.readline())

        for ID in temp_dict:
            if chat_ID == int(ID):
                return temp_dict[ID]
        return "NEW_GAME"


def get_current_player(current_save: dict[str]) -> Player:
    """
    Takes dict where player is saved and returns Player object
    """
    # player_parts = current_save.split(",")
    # parts_dict: dict[str, str] = dict()
    # for part in player_parts:
    #     key, val = part.split(":")
    #     parts_dict[key] = val

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
    )


def player_save_generator(player: Player) -> str:
    """
    Takes current state of player as Player object and returns his representation as string in needed format.
    LS: returns JSON representation
    """
    player_dict = dict()
    player.decrease_durations()

    player_dict["place"] = player.place_ID
    player_dict["coins"] = player.coins
    player_dict["items"] = player.items
    player_dict["str"] = player.strength
    player_dict["speed"] = player.speed
    player_dict["relations"] = player.relations
    player_dict["fraction"] = player.fraction_ID
    player_dict["state"] = player.state
    player_dict["duration"] = [
        key + "/" + str(player.duration[key]) for key in player.duration
    ]
    player_dict["weapons"] = player.equiped_weapons
    player_dict["quests"] = player.quests
    player_dict["progress"] = player.progress

    return json.dumps(player_dict)


def first_quests_save() -> tuple[dict[int, ModifiedQuestPhase], str]:
    """
    Firstly generates default saves for all quest lines which is empty strings
    Secondly creates dictionary that based on quest line ID returns root modified quest phase of this quest line
    """

    quest_lines = read_quest_lines_from_file(r"data\quest-lines.txt")
    # quest_lines = read_quest_lines_from_file(r"data\quest-lines.json")
    quest_states = []
    ID_to_root_quest = dict()
    for quest_ID in quest_lines.ID_to_tree:
        quest_states.append("")

        ID_to_root_quest[quest_ID] = dict_to_mqp(
            json.loads(quest_lines.ID_to_tree[quest_ID].value[0])
        )

    return ID_to_root_quest, json.dumps(quest_states)


def get_current_quests(lines_states: list[str]) -> list[str]:
    """
    Takes quest line string save and compares with trees to generate concrete phases for each line.
    Returns list of phases as string
    """
    # TODO read in some main function and then just pass as argument
    quest_lines = read_quest_lines_from_file(r"data\quest-lines.txt")
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
            current_phase_for_line.append(
                [str(dict_to_mqp(json.loads(x))) for x in node.value]
            )

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
            quest_save = str_to_mqp(current_quests_save[quest_save_idx][0])
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


def first_characters_save(quest_ID_to_MQP: dict[int, ModifiedQuestPhase]) -> str:
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

    characters = read_people_from_file(r"data\characters.csv")
    # Goes through all characters in existence and if there is a quest that should be assigned to them
    # needed attributes are set to identify the phase and line and progress
    for character in characters.people_list:
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

    return json.dumps(character_json)


def rewrite_save_file(change_line_ID: int, new_save_json: str) -> None:
    """Reads all rows and saves current saves. That rewrites string specified by ID and save new file"""

    with open("data\game_saves.json", "r", newline="") as save_file:
        line_saves = save_file.readline()
        temp_dict_json = json.loads(line_saves)

        temp_dict_json[str(change_line_ID)] = new_save_json

    with open("data\game_saves.json", "w", newline="") as save_file:
        save_file.write("{")
        for ID in temp_dict_json:
            # jsonfied = json.loads(temp_dict[ID])
            save_file.write('"' + str(ID) + '":' + new_save_json)
        save_file.write("}")


def generate_new_save(chat_ID) -> None:
    """Generating whole new save"""
    # Player introduce - set his starting position and other stuff
    spawn_player = Player(
        0,
        25,
        [7, 8, 9],
        2,
        2,
        [2, 2, 2, 2, 2, 2, 2],
        4,
        "alive",
        [],
        "",
        [
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
        ],
        ["tostart", "inprogress"],
    )
    new_player_save = player_save_generator(spawn_player)

    # Start quest lines
    root_quests_dict, new_quests_json = first_quests_save()

    # Rewrite characters to save
    new_characters_save = first_characters_save(root_quests_dict)

    first_json_save = (
        '{ "player": '
        + new_player_save
        + ', "quests": '
        + new_quests_json
        + ', "characters": '
        + new_characters_save
        + " }"
    )

    rewrite_save_file(chat_ID, first_json_save)
