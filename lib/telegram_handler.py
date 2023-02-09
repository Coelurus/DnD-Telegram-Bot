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


async def start_new_game(update: Update, context: ContextTypes.DEFAULT_TYPE):

    chat_ID = update.message.chat.id
    save.generate_new_save(chat_ID)

    reply_keyboard = [
        ["Provést akci zde"],
        ["Mé statistiky"],
        ["Jít dál"]
    ]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)

    # saving Player data with up-to-date data to a user-specific dict
    chat_ID = update.message.chat.id
    current_save = save.read_current_save(chat_ID)
    current_player_str = current_save.split("_")[0]
    current_player: player.Player = save.get_current_player(current_player_str)
    context.user_data["player"] = current_player

    await update.message.reply_text("Co si přeješ udělat?", reply_markup=markup)

    return "player_actions"


async def read_old_game(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    chat_ID = update.message.chat.id
    current_save = save.read_current_save(chat_ID)
    if current_save == "NEW_GAME":
        await update.message.reply_text(text="Škoda...\n...tak třeba jindy", reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END
    else:
        reply_keyboard = [
            ["Provést akci zde"],
            ["Mé statistiky"],
            ["Jít dál"]
        ]
        markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)

        # saving Player data with up-to-date data to a user-specific dict
        chat_ID = update.message.chat.id
        current_save = save.read_current_save(chat_ID)
        current_player_str, current_quests_str, current_chars_str = current_save.split(
            "_")
        current_player = save.get_current_player(current_player_str)
        current_characters = save.get_current_characters(current_chars_str)
        context.user_data["player"] = current_player

    await update.message.reply_text("Co si přeješ udělat?", reply_markup=markup)

    return "player_actions"


async def move_character(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    current_player = context.user_data["player"]

    move_options = current_player.move_possibilities()

    reply_keyboard = [[x.name_cz] for x in move_options]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)

    await update.message.reply_text("Do jaké ulice se chceš přesunout?", reply_markup=markup)

    return "character_move"


async def change_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    town_map = map.read_map_from_file("data\streets.csv")
    new_street_ID = town_map.name_cz_to_ID[update.message.text]
    current_player: player.Player = context.user_data["player"]
    current_player.place_ID = new_street_ID
    print(context.user_data["player"].place_ID, new_street_ID)

    reply_keyboard = [
        ["Provést akci zde"],
        ["Mé statistiky"],
        ["Jít dál"]
    ]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    await update.message.reply_text("Co si přeješ udělat?", reply_markup=markup)
    return "player_actions"


async def inspect_player(update: Update, context: ContextTypes.DEFAULT_TYPE):
    town_map = map.read_map_from_file("data\streets.csv")
    current_player: player.Player = context.user_data["player"]
    items_collection: items.ItemsCollection = items.read_items_from_file(
        "data\items.csv")
    chat_ID = update.message.chat.id
    current_save = save.read_current_save(chat_ID)
    player_information = f"Místo, kde se nacházíš, se jmenuje {town_map.get_street_by_ID(current_player.place_ID).name_cz}\nMomentálně u sebe máš {current_player.coins} peněz a následující předměty: {', '.join([items_collection.get_item_by_ID(x).name_cz for x in current_player.items])}\nTvoje síla je na úrovni {current_player.strength} a rychlost na úrovni {current_player.speed}"
    await context.bot.send_message(chat_ID, player_information)

    reply_keyboard = [
        ["Provést akci zde"],
        ["Mé statistiky"],
        ["Jít dál"]
    ]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    await update.message.reply_text("Co si přeješ udělat?", reply_markup=markup)
    return "player_actions"


async def make_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_ID = update.message.chat.id
    current_save = save.read_current_save(chat_ID)
    await context.bot.send_message(chat_ID, "action these nuts")
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
            ]

        },
        fallbacks=[CommandHandler("start", start)]
    )

    application.add_handler(conversation_handler)

    application.run_polling()


if __name__ == "__main__":

    main()
