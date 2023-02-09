from player import Player
from character import read_people_from_file
from quest import read_quest_lines_from_file, str_to_mqp, mqp_to_str, ModifiedQuestPhase
from character_handler import update_phases, get_current_characters, move_characters, ModifiedPeople
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
    parts_dict: dict[str, str] = dict()
    for part in player_parts:
        key, val = part.split(":")
        parts_dict[key] = val

    return Player(parts_dict["place"], parts_dict["coins"], parts_dict["items"].split(";"), parts_dict["str"], parts_dict["speed"], parts_dict["relations"].split(";"))


def player_save_generator(player: Player) -> str:
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
            quest_lines.ID_to_tree[quest_ID].value[0])  # TODO only taking the first possible phase...
    quest_save_line = ",".join(quest_states)

    return quest_save_line, ID_to_root_quest


def get_current_quests(previous_save: str) -> list[str]:
    """
    Takes quest line save and compares with trees to generate concrete phases for each line.
    """
    # TODO read in some main function and then just pass as argument
    quest_lines = read_quest_lines_from_file(r"data\quest-lines.txt")
    lines_states = previous_save.split(",")
    current_phase_for_line: list[str] = []

    for quest_line_ID in quest_lines.ID_to_tree:
        node = quest_lines.ID_to_tree[quest_line_ID]
        for line_progres in lines_states[quest_line_ID]:
            if node != None:
                if line_progres == "S":
                    node = node.succes
                elif line_progres == "F":
                    node = node.failure
            if node == None:  # the quest line ends here
                current_phase_for_line.append(None)
                break
        else:
            current_phase_for_line.append(
                [str(str_to_mqp(x)) for x in node.value])

    return current_phase_for_line


def update_quests(current_quests_str: str, lines_to_update: dict[int, str]):
    quest_lines = current_quests_str.split(",")
    for quest_line_idx in range(len(quest_lines)):
        if quest_line_idx in lines_to_update:
            quest_lines[quest_line_idx] += lines_to_update[quest_line_idx]

    return ",".join(quest_lines)


def assign_quests(current_characters: ModifiedPeople, current_quests_save: list[list[str]]):
    char_ID_to_quest: dict[int, list[list[ModifiedQuestPhase], int]] = dict()
    for quest_save_idx in range(len(current_quests_save)):
        # TODO unfinished feature. Quest phases are in fact saves as a list of strings,
        # thus can be trigerred multiple phases at once, however I have not figured
        # simple enough way to track them and how to manage their overall failure vs succes.

        if current_quests_save[quest_save_idx] is not None:
            quest_save = str_to_mqp(current_quests_save[quest_save_idx][0])
            if quest_save is not None:
                char_ID_to_quest[quest_save.characterID] = [
                    quest_save, quest_save_idx]

    for char_ID in char_ID_to_quest:
        if current_characters.list[char_ID].line == -1:
            current_characters.list[char_ID].line = char_ID_to_quest[char_ID][1]
            current_characters.list[char_ID].phase = mqp_to_str(
                char_ID_to_quest[char_ID][0])

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
            line = phase = stage = "-1"

        items_str = ";".join([str(x) for x in character.items])
        characters_str_save += f"place:{character.spawn_street_ID},coins:{character.coins},items:{items_str},str:{character.strength},speed:{character.speed},line:{line},phase:{phase},stage:{stage},state:alive+"
    return characters_str_save.rstrip("+")


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


def rotation(chat_ID=get_chat_ID()):
 # 1
    current_save = read_current_save(chat_ID)
    if current_save != "NEW_GAME":
        current_player_str, current_quests_str, current_characters_str = current_save.split(
            "_")

        # 2
        current_player = get_current_player(current_player_str)
        # 3 TODO player action
        current_player.move()
        # 4 TODO reaction on action

        # 5
        current_characters = get_current_characters(current_characters_str)
        # 6
        current_characters, lines_to_update = update_phases(current_characters)
        # 7 TODO updating quest line saves
        new_quests_str = update_quests(current_quests_str, lines_to_update)
        # 8
        current_quests_save = get_current_quests(new_quests_str)
        # 9 TODO adding phases to characters
        current_characters = assign_quests(
            current_characters, current_quests_save)
        # 10
        current_characters = move_characters(current_characters).to_str()
        # 11 TODO

        # 12
        new_player_save = player_save_generator(current_player)
        combined_save = f"{new_player_save}_{new_quests_str}_{current_characters}"
        rewrite_save_file(chat_ID, combined_save)

    else:
        """Generate new starting save"""
        generate_new_save(chat_ID)


if __name__ == "__main__":
    rotation()
