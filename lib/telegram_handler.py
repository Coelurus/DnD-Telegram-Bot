import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters
)
import save
import map
import player
import items
import character
import character_handler as handler

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """When user send /start it sends welcome message and choices"""
    reply_keyboard = [
        ["Začít novou hru (přemaže starou)"], [
            "Nezačínat novou hru (návrat k předchozí pokud existuje)"]
    ]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)

    await update.message.reply_text(
        "Zdravíčko, přeješ si začít novou epickou kampaň?",
        reply_markup=markup,
    )
    return "starting_new_game"


def load_static_data(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Function to read data from csv files and saving them in user data thus they don't have to be loaded from files again and again"""
    context.user_data["map"] = map.read_map_from_file(r"data\streets.csv")
    context.user_data["items"] = items.read_items_from_file(r"data\items.csv")
    context.user_data["fractions"] = character.read_fractions_from_file(
        r"data\fractions.csv")
    context.user_data["people"] = character.read_people_from_file(
        r"data\characters.csv")


def load_dynamic_data(context: ContextTypes.DEFAULT_TYPE, current_save: str) -> None:
    """Function to read current player and other characters data as they are needed to generate possibilities for player"""
    current_player_str, current_quests_str, current_chars_str = current_save.split(
        "_")

    current_player = save.get_current_player(current_player_str)
    context.user_data["player"] = current_player

    current_characters = save.get_current_characters(current_chars_str)
    context.user_data["current_people"] = current_characters

    # Character movement and other things
    """
    current_characters, lines_to_update = save.update_phases(
        current_characters)

    new_quests_str = save.update_quests(current_quests_str, lines_to_update)

    current_quests_save = save.get_current_quests(new_quests_str)

    current_characters = save.assign_quests(current_characters, current_quests_save)
    
    current_characters = move_characters(current_characters).to_str()

    new_player_save = player_save_generator(current_player)

    combined_save = f"{new_player_save}_{new_quests_str}_{current_characters}"

    rewrite_save_file(chat_ID, combined_save)
    """


async def start_new_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Function to start gain from round one. If game have not existed before it will be created. If it did the progress will be lost"""
    chat_ID = update.message.chat.id
    save.generate_new_save(chat_ID)

    # saving Player data with up-to-date data to a user-specific dict
    current_save = save.read_current_save(chat_ID)
    load_static_data(context)
    load_dynamic_data(context, current_save)

    return await basic_window(update)


async def read_old_game(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Function reads a game save based on chat ID. If the save does not exist it will terminate the programme"""
    chat_ID = update.message.chat.id
    current_save = save.read_current_save(chat_ID)
    if current_save == "NEW_GAME":
        await update.message.reply_text(text="Škoda...\n...tak třeba jindy", reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END

    # saving Player data with up-to-date data to a user-specific dict
    load_static_data(context)
    load_dynamic_data(context, current_save)

    return await basic_window(update)


async def move_character(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Function that offers player choice of places where he can move."""
    current_player = context.user_data["player"]

    move_options = current_player.move_possibilities()

    reply_keyboard = [[x.name_cz] for x in move_options]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)

    await update.message.reply_text("Do jaké ulice se chceš přesunout?", reply_markup=markup)

    return "character_move"


async def change_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Function that determines which place player chose to move to and moves him there."""
    town_map: map.Map = context.user_data["map"]
    current_player: player.Player = context.user_data["player"]
    new_street_ID = town_map.name_cz_to_ID[update.message.text]
    current_player.place_ID = new_street_ID

    await update.message.reply_text(town_map.get_street_by_ID(new_street_ID).description_cz)

    return await basic_window(update)


async def inspect_player(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Function returns data about characters current state."""
    town_map = context.user_data["map"]
    current_player: player.Player = context.user_data["player"]
    items_collection: items.ItemsCollection = items.read_items_from_file(
        "data\items.csv")
    chat_ID = update.message.chat.id
    current_save = save.read_current_save(chat_ID)
    player_information = f"Místo, kde se nacházíš, se jmenuje {town_map.get_street_by_ID(current_player.place_ID).name_cz}.\nMomentálně u sebe máš {current_player.coins} peněz a následující předměty: {', '.join([items_collection.get_item_by_ID(x).name_cz for x in current_player.items])}\nTvoje síla je na úrovni {current_player.strength} a rychlost na úrovni {current_player.speed}"
    await context.bot.send_message(chat_ID, player_information)

    return await basic_window(update)


async def make_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_ID = update.message.chat.id
    current_save = save.read_current_save(chat_ID)

    town_map: map.Map = context.user_data["map"]
    current_player: player.Player = context.user_data["player"]
    item_collection: items.ItemsCollection = context.user_data["items"]
    society: character.Society = context.user_data["people"]
    current_characters: handler.ModifiedPeople = context.user_data["current_people"]
    current_place: map.Street = town_map.get_street_by_ID(
        current_player.place_ID)

    action_dict, people_here = current_player.get_actions(
        current_characters, town_map)

    char_ID_to_relation = current_player.get_relationships(
        people_here, society)

    context.user_data["char_ID_to_relation"] = char_ID_to_relation
    context.user_data["people_here"] = people_here

    reply_keyboard = [
        ["Mluvit s člověkem"],
    ]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    await update.message.reply_text("Co si přeješ udělat?", reply_markup=markup)
    return "choose"


async def talk_to_person(update: Update, context: ContextTypes.DEFAULT_TYPE):
    current_player: player.Player = context.user_data["player"]
    char_ID_to_relation = context.user_data["char_ID_to_relation"]
    society: character.Society = context.user_data["people"]
    char_relation = char_ID_to_relation[society.name_cz_to_ID[
        update.message.text]]

    await update.message.reply_text(f"{update.message.text} k tobě má vztah na úrovni {char_relation}")

    return await basic_window(update)


async def choose_person(update: Update, context: ContextTypes.DEFAULT_TYPE):
    people_list = context.user_data["people_here"]
    society = context.user_data["people"]
    if len(people_list) != 0:
        reply_keyboard = [
            [person.get_name_cz(society)] for person in people_list]
        print("aaa", reply_keyboard)
        markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)

        await update.message.reply_text("S kým chceš mluvit?", reply_markup=markup)

        return "person_to_talk"
    else:
        await update.message.reply_text("Nikdo tu bohužel není :(")
        return await basic_window(update)


async def basic_window(update: Update) -> str:
    """Function creates basic menu with choices for player about what he wants to do next"""
    reply_keyboard = [
        ["Provést akci zde"],
        ["Mé statistiky"],
        ["Jít dál"]
    ]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    await update.message.reply_text("Co si přeješ udělat?", reply_markup=markup)
    return "player_actions"


def main() -> None:
    """Run the bot"""

    application = Application.builder().token(
        "5825497496:AAHWw228oPxR4Ybc4pV0PwTayjQ7ywUfA_I").build()

    conversation_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            "starting_new_game": [
                MessageHandler(
                    filters.Regex(
                        "Začít"), start_new_game
                ),
                MessageHandler(
                    filters.Regex(
                        "Nezačínat"), read_old_game
                )
            ],
            "player_actions": [
                MessageHandler(
                    filters.Regex(
                        "Provést"), make_action
                ),
                MessageHandler(
                    filters.Regex(
                        "statistiky"), inspect_player
                ),
                MessageHandler(
                    filters.Regex(
                        "Jít"), move_character
                )
            ],
            "character_move": [
                MessageHandler(
                    filters.TEXT, change_location
                )
            ],
            "person_to_talk": [
                MessageHandler(
                    filters.TEXT, talk_to_person
                )
            ], "choose": [
                MessageHandler(
                    filters.TEXT, choose_person
                )
            ]

        },
        fallbacks=[CommandHandler("start", start)]
    )

    application.add_handler(conversation_handler)

    application.run_polling()


if __name__ == "__main__":

    main()
