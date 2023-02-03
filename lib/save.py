from player import Player
from character import read_people_from_file
from quest import read_quest_lines_from_file
import csv


def get_chat_ID() -> int:  # TODO
    return 69


def read_current_save(chat_ID: int) -> str:  # TODO
    save_file = open("data\game_saves.txt")
    lines = save_file.readlines()

    for chat_idx in range(0, len(lines), 2):
        if int(lines[chat_idx].rstrip("\n")) == chat_ID:
            return lines[chat_idx+1].rstrip("\n")

    return "smth"


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


def first_quests_save() -> str:
    quest_lines = read_quest_lines_from_file(r"data\quest-lines.txt")
    quest_states = []
    for quest_line_idx in quest_lines.ID_to_name:
        quest_states.append("")
    quest_save_line = ",".join(quest_states)
    return quest_save_line


def quests_save_generator(previous_save: str) -> str:  # TODO
    return "Le quest"


def first_characters_save() -> str:
    characters = read_people_from_file(r"data\characters.csv")
    characters_str_save = ""
    for character in characters.people_list:
        items_str = ";".join([str(x) for x in character.items])
        characters_str_save += f"place:{character.spawn_street_ID},coins:{character.coins},items:{items_str},str:{character.strength},speed:{character.speed}"
    return characters_str_save


def characters_save_generator(previous_save: str) -> str:  # TODO
    return "peple"


def game_save_generator() -> str:
    save_string = ""
    save_string += player_save_generator() + "="
    save_string += quests_save_generator() + "="
    save_string += characters_save_generator()
    return save_string


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
        print(new_player_save)

        # Start quest lines
        new_quest_lines_save = first_quests_save()
        print("Qust_lines_save:'" + new_quest_lines_save + "'")

        # Rewrite characters to save
        new_characters_save = first_characters_save()
        print(new_characters_save)

        with open("data\game_saves.csv", "a", newline='') as save_file:
            writer = csv.DictWriter(save_file, ["ID", "save"])
            writer.writerow({"ID": 666, "save": "femboy"})
