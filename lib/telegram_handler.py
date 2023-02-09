import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
)
import save

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Sends message on /start ad starts the whole thing"""

    user = update.message.from_user

    logger.info("User %s started the conversation.", user.first_name)

    keyboard = [
        [
            InlineKeyboardButton("ANO !", callback_data="new_game"),
            InlineKeyboardButton("NE :(", callback_data="old_game")

        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text("Přeješ si započít novou hru?", reply_markup=reply_markup)

    return "starting_new_game"


async def start_new_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("new")
    chat_ID = update.callback_query.message.chat.id
    save.generate_new_save(chat_ID)


async def read_old_game(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    print("old")
    query = update.callback_query
    chat_ID = query.message.chat.id
    current_save = save.read_current_save(chat_ID)
    if current_save == "NEW_GAME":
        await query.edit_message_text(text="Škoda...\n...tak třeba jindy")
        return ConversationHandler.END
    else:
        save.rotation(chat_ID)


def main() -> None:
    """Run the bot"""

    application = Application.builder().token(
        "5825497496:AAHWw228oPxR4Ybc4pV0PwTayjQ7ywUfA_I").build()

    conversation_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            "starting_new_game": [
                CallbackQueryHandler(start_new_game, pattern="^new_game$"),
                CallbackQueryHandler(read_old_game, pattern="^old_game$")
            ]

        },
        fallbacks=[CommandHandler("start", start)]
    )

    application.add_handler(conversation_handler)

    application.run_polling()


if __name__ == "__main__":
    main()
