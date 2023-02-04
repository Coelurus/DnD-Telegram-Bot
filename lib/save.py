from player import Player
from character import read_people_from_file
from quest import read_quest_lines_from_file, str_to_mqp, ModifiedQuestPhase
import csv


def get_chat_ID() -> int:  # TODO
    return 69


def read_current_save(chat_ID: int) -> str:  # TODO
    save_file = open("data\game_saves.txt")
    lines = save_file.readlines()

    for chat_idx in range(0, len(lines), 2):
        if int(lines[chat_idx].rstrip("\n")) == chat_ID:
            return lines[chat_idx+1].rstrip("\n")

    return "NEW_GAME"


def get_current_player(previous_save: str) -> Player:
    player_parts = previous_save.split(",")
    for part in player_parts:
        key, val = part.split(":")
        if key == "place":
            place = val
        elif key == "coins":
            coins = val
        elif key == "items":
            items = val
        elif key == "strength":
            strength = val
        elif key == "speed":
            speed = val
        elif key == "relations":
            relations = val

    return Player(place, coins, items.split(";"), strength, speed, relations.split(";"))


def player_save_generator(player: Player) -> str:  # TODO
    items_str = ";".join([str(x) for x in player.items])
    relations_str = ";".join([str(x) for x in player.relations])
    return f"place:{player.place_ID},coins:{player.coins},items:{items_str},str:{player.strength},speed:{player.speed},relations:{relations_str}"


def first_quests_save() -> tuple[str, dict[int, ModifiedQuestPhase]]:
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
    return "Le quest"


def first_characters_save(root_quests_dict: dict[int, ModifiedQuestPhase]) -> str:
    character_ID_to_line_ID = dict()
    for quest_line_ID in root_quests_dict:
        character_ID_to_do_quest = root_quests_dict[quest_line_ID].characterID
        character_ID_to_line_ID[character_ID_to_do_quest] = quest_line_ID

    print(character_ID_to_line_ID)

    characters = read_people_from_file(r"data\characters.csv")
    characters_str_save = ""
    for character in characters.people_list:
        if character.ID in character_ID_to_line_ID:
            line = character_ID_to_line_ID[character.ID]
            phase = str(root_quests_dict[line])
            stage = "tostart"
        else:
            line = phase = stage = ""

        items_str = ";".join([str(x) for x in character.items])
        characters_str_save += f"place:{character.spawn_street_ID},coins:{character.coins},items:{items_str},str:{character.strength},speed:{character.speed},line:{line},phase:{phase},stage:{stage}+"
    return characters_str_save.rstrip("+")


def characters_save_generator(previous_save: str) -> str:  # TODO
    return "peple"


def rewrite_save_file(change_line_ID: int, new_save_str: str) -> None:
    with open("data\game_saves.csv", "r", newline='') as save_file:
        reader = csv.DictReader(save_file)
        temp_dict = {}
        for row in reader:
            temp_dict[int(row["ID"])] = row["save"]
        temp_dict[chat_ID] = first_save_line

    with open("data\game_saves.csv", "w", newline='') as save_file:
        writer = csv.DictWriter(save_file, ["ID", "save"])
        writer.writeheader()
        for ID in temp_dict:
            writer.writerow({"ID": ID, "save": temp_dict[ID]})


if __name__ == "__main__":
    chat_ID = get_chat_ID()
    current_save = read_current_save(chat_ID)
    if current_save != "NEW_GAME":
        current_player, current_quests, current_characters = current_save.split(
            "=")
        new_player_save = player_save_generator(current_player)

        new_quests_save = quests_save_generator(current_quests)

        new_characters_save = characters_save_generator(current_characters)
    else:
        # Player introduce
        spawn_player = Player(0, 25, [], 2, 2, [2, 2, 2, 2, 2, 2, 2])
        new_player_save = player_save_generator(spawn_player)

        # Start quest lines
        new_quest_lines_save, root_quests_dict = first_quests_save()

        print(root_quests_dict)

        # Rewrite characters to save
        new_characters_save = first_characters_save(root_quests_dict)

        first_save_line = new_player_save + "=" + \
            new_quest_lines_save + "=" + new_characters_save

        rewrite_save_file(chat_ID, first_save_line)
