from player import Player
from character import read_people_from_file
from quest import read_quest_lines_from_file, str_to_mqp, ModifiedQuestPhase
import csv


def get_chat_ID() -> int:  # TODO
    return 69


def read_current_save(chat_ID: int) -> str:
    """
    Method takes int parameter to identify save string of defined chat and returns this save string.
    If game has not started yet it returns "NEW_GAME" so program knows to start a new game
    """

    with open("data\game_saves.csv", "r", newline='') as save_file:
        reader = csv.DictReader(save_file)
        temp_dict = {}
        for row in reader:
            temp_dict[int(row["ID"])] = row["save"]
        if chat_ID in temp_dict:
            return temp_dict[chat_ID]
        return "NEW_GAME"


def get_current_player(previous_save: str) -> Player:
    """
    Takes string where player is saved and returns Player object
    """
    player_parts = previous_save.split(",")
    for part in player_parts:
        key, val = part.split(":")
        if key == "place":
            place = val
        elif key == "coins":
            coins = val
        elif key == "items":
            items = val
        elif key == "str":
            strength = val
        elif key == "speed":
            speed = val
        elif key == "relations":
            relations = val

    return Player(place, coins, items.split(";"), strength, speed, relations.split(";"))


def player_save_generator(player: Player) -> str:  # TODO
    """
    Takes current state of player as Player object and returns his representation as string.
    """
    items_str = ";".join([str(x) for x in player.items])
    relations_str = ";".join([str(x) for x in player.relations])
    return f"place:{player.place_ID},coins:{player.coins},items:{items_str},str:{player.strength},speed:{player.speed},relations:{relations_str}"


def first_quests_save() -> tuple[str, dict[int, ModifiedQuestPhase]]:
    """
    Firstly generates default saves for all quest lines which is empty strings
    Secondly creates dictionary that based on quest line ID returns root modified quest phase of this quest line
    """
    quest_lines = read_quest_lines_from_file(r"data\quest-lines.txt")
    quest_states = []
    ID_to_root_quest = dict()
    for quest_ID in quest_lines.ID_to_tree:
        quest_states.append("")
        ID_to_root_quest[quest_ID] = str_to_mqp(
            quest_lines.ID_to_tree[quest_ID].value)
    quest_save_line = ",".join(quest_states)

    return quest_save_line, ID_to_root_quest


def quests_save_generator(previous_save: str) -> str:  # TODO
    return previous_save


def first_characters_save(quest_ID_to_MQP: dict[int, ModifiedQuestPhase]) -> str:
    """
    Method takes dictionary where key is quest line ID and value is ModifiedQuestPhase to write quests to character saves
    Based on that and characters.csv method creates string with saves for all characters
    """
    character_ID_to_line_ID: dict[int, int] = dict()
    # looking for characters that will have assigned quests
    for quest_line_ID in quest_ID_to_MQP:
        character_ID_to_do_quest = quest_ID_to_MQP[quest_line_ID].characterID
        character_ID_to_line_ID[character_ID_to_do_quest] = quest_line_ID

    characters = read_people_from_file(r"data\characters.csv")
    characters_str_save = ""
    for character in characters.people_list:
        if character.ID in character_ID_to_line_ID:
            line = character_ID_to_line_ID[character.ID]
            phase = str(quest_ID_to_MQP[line])
            if quest_ID_to_MQP[line].from_place_ID == -1 or quest_ID_to_MQP[line].from_place_ID == character.spawn_street_ID:
                stage = "inprogress"
            else:
                stage = "tostart"
        else:
            line = phase = stage = ""

        items_str = ";".join([str(x) for x in character.items])
        characters_str_save += f"place:{character.spawn_street_ID},coins:{character.coins},items:{items_str},str:{character.strength},speed:{character.speed},line:{line},phase:{phase},stage:{stage}+"
    return characters_str_save.rstrip("+")


def characters_save_generator(previous_save: str) -> str:  # TODO
    return previous_save


def rewrite_save_file(change_line_ID: int, new_save_str: str) -> None:
    """Reads all rows and saves current saves. That rewrites string specified by ID and save new file"""
    with open("data\game_saves.csv", "r", newline='') as save_file:
        reader = csv.DictReader(save_file)
        temp_dict = {}
        for row in reader:
            temp_dict[int(row["ID"])] = row["save"]
        temp_dict[change_line_ID] = new_save_str

    with open("data\game_saves.csv", "w", newline='') as save_file:
        writer = csv.DictWriter(save_file, ["ID", "save"])
        writer.writeheader()
        for ID in temp_dict:
            writer.writerow({"ID": ID, "save": temp_dict[ID]})


def generate_new_save(chat_ID) -> None:
    """Generating whole new save"""
    # Player introduce - set his starting position and other stuff
    spawn_player = Player(0, 25, [], 2, 2, [2, 2, 2, 2, 2, 2, 2])
    new_player_save = player_save_generator(spawn_player)

    # Start quest lines
    new_quest_lines_save, root_quests_dict = first_quests_save()

    # Rewrite characters to save
    new_characters_save = first_characters_save(root_quests_dict)

    first_save_line = new_player_save + "_" + \
        new_quest_lines_save + "_" + new_characters_save

    rewrite_save_file(chat_ID, first_save_line)


if __name__ == "__main__":
    chat_ID = get_chat_ID()
    current_save = read_current_save(chat_ID)
    if current_save != "NEW_GAME":
        current_player_str, current_quests_str, current_characters_str = current_save.split(
            "_")

        current_player = get_current_player(current_player_str)
        current_player.move()
        new_player_save = player_save_generator(current_player)

        new_quests_save = quests_save_generator(current_quests_str)
        # check all characters if finished

        new_characters_save = characters_save_generator(current_characters_str)
        # move all characters

        combined_save = f"{new_player_save}_{new_quests_save}_{new_characters_save}"
        rewrite_save_file(chat_ID, combined_save)

    else:
        """Generate new starting save"""
        generate_new_save(chat_ID)
