def get_chat_ID() -> int:  # TODO
    return 69


def read_current_save(chat_ID: int) -> str:  # TODO
    return "smth"


def player_save_generator(previous_save: str) -> str:  # TODO
    # Part 1 - read where he at

    # Part 2 - player move

    # Part 3 - create new state

    return "player lol"


def quests_save_generator(previous_save: str) -> str:  # TODO
    return "Le quest"


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
    current_player, current_quests, current_characters = current_save.split(
        "=")

    new_player_save = player_save_generator(current_player)

    new_quests_save = quests_save_generator(current_quests)

    new_characters_save = characters_save_generator(current_characters)
