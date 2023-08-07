from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    Update,
)

from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)
import save
import map
from map import Map
import player
from player import Player
import items
from items import Item, ItemsCollection
import character
from character import Society
import character_handler as handler
from character_handler import ModifiedPeople
import quest
from quest import ModifiedQuestPhase
import json


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """When user send /start it sends welcome message and choices"""
    reply_keyboard = [
        ["Začít novou hru (přemaže starou)"],
        ["Nezačínat novou hru (návrat k předchozí pokud existuje)"],
    ]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)

    await update.message.reply_text(
        "Zdravíčko, přeješ si začít novou epickou kampaň?",
        reply_markup=markup,
    )
    return "starting_new_game"


def load_static_data(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Function to read data from csv files and saving them in dict user_data that is available from every function called by Conversation Handler.
    Thus game data do not have to be rewritten into the save file after every single action
    """
    context.user_data["map"] = map.read_map_from_file(r"data\streets.csv")
    context.user_data["items"] = items.read_items_from_file(r"data\items.csv")
    context.user_data["fractions"] = character.read_fractions_from_file(
        r"data\fractions.csv"
    )
    context.user_data["people"] = character.read_people_from_file(
        r"data\characters.csv"
    )


def load_dynamic_data(context: ContextTypes.DEFAULT_TYPE, current_save: dict) -> None:
    """Function to read dynamic data and saving them in dict user_data that is available from every function called by Conversation Handler.
    Thus game data do not have to be rewritten into the save file after every single action.
    Compared to load_static_data, this function stores data that change after almost every action
    """

    current_player_dict = current_save["player"]
    current_quests_list = current_save["quests"]
    current_chars_list = current_save["characters"]

    context.user_data["current_quests_list"] = current_quests_list

    current_player = save.get_current_player(current_player_dict)
    context.user_data["player"] = current_player

    current_characters = save.get_current_characters(current_chars_list)
    context.user_data["current_people"] = current_characters

    quests_to_finish = current_player.update_quest_progresses(current_characters)
    context.user_data["additional_actions"] = quests_to_finish

    # Dict where key is an ID of character(int) and val is list of tuples of text to output for this choice(str) and code of action(str)
    context.user_data["character_specific_actions"] = {0: [["Mňau", "meow"]]}


async def start_new_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Function to start game from round one.\n
    If game have not existed before it will be created.\n
    If it did the progress will be lost"""

    chat_ID = update.message.chat.id
    save.generate_new_save(chat_ID)

    # saving Player data with up-to-date data to a user-specific dict
    current_save = save.read_current_save(chat_ID)
    load_static_data(context)
    load_dynamic_data(context, current_save)

    await update.message.reply_text(
        "Probudil ses...u...U Oplého poníka? Co tu dělám?......Sakra už vím! Utekla nám kočka. Ale ne, musím ji jít najít."
    )
    await update.message.reply_text(
        'V tom ti však někdo zaklepe na rameno: "Nezapomeň, o co ses vsadil s těmi kultisty. Že prý kočku najdeš dřív než oni...a teď tu vyspáváš v hospodě. No tak utíkej. DĚLEJ!"'
    )

    return await basic_window(update, context)


async def read_old_game(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Function reads a game save based on chat ID. If the save does not exist it will terminate the programme"""
    chat_ID = update.message.chat.id
    current_save = save.read_current_save(chat_ID)
    if current_save == "NEW_GAME":
        await update.message.reply_text(
            text="Škoda...\n...tak třeba jindy", reply_markup=ReplyKeyboardRemove()
        )
        return ConversationHandler.END

    # saving Player data with up-to-date data to a user-specific dict
    load_static_data(context)
    load_dynamic_data(context, current_save)

    return await basic_window(update, context)


async def end_game(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    end_text: str = "Snad se ještě někdy potkáme\.\.\.",
):
    """Function generate reply menu for endgame situations and gives player a possibility to start a new game"""
    reply_keyboard = [["Začít znovu"]]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    await update.message.reply_text(
        end_text, reply_markup=markup, parse_mode="MarkdownV2"
    )
    return "starting_new_game"


async def rotation(
    chat_ID: int, context: ContextTypes.DEFAULT_TYPE, update: Update
) -> None:
    """Function take care of handling movement of NPC, making them follow missions etc.
    It also updates questlines progresses and assign phases to NPCs based on it"""

    # Getting current data that are potentially changed by player inputs from last time
    current_characters: ModifiedPeople = context.user_data["current_people"]

    # TODO funi nacitani
    current_quests_list: list[str] = context.user_data["current_quests_list"]
    player: Player = context.user_data["player"]

    # Updating quest lines for characters. If game ending line has finished, the game ends
    (
        current_characters,
        lines_to_update,
        game_ended,
        game_ending_str,
    ) = save.update_phases(current_characters)
    if game_ended:
        return await end_game(update, context, game_ending_str)

    new_quests = save.update_quests(current_quests_list, lines_to_update)

    current_quests_save = save.get_current_quests(new_quests)

    current_characters = save.assign_quests(current_characters, current_quests_save)

    # Make characters follow their quests and then parse to string so the progress can be saved
    current_characters_str = save.move_characters(current_characters).to_str()

    # Updates progress and gets list of quests completable in this place.
    quests_to_finish = player.update_quest_progresses(current_characters)
    context.user_data["additional_actions"] = quests_to_finish
    if len(quests_to_finish) > 0:
        await update.message.reply_text("\u2757 Máš zde úkol \u2757")

    json_dict_player = save.player_save_generator(player)

    context.user_data["current_quests_list"] = new_quests

    combined_save_json = f'{{ "player": {json_dict_player}, "quests": {json.dumps(new_quests)}, "characters": {current_characters_str[1]} }}'

    save.rewrite_save_file(chat_ID, combined_save_json)

    # When player is not capable of moving proceed to next round and move characters again
    # TODO change from recursion to loop
    if player.state == "stun" and player.duration["stun"] >= 1:
        await rotation(chat_ID, context, update)


async def move_character(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Function that offers player choice of places where he can move."""
    player: Player = context.user_data["player"]

    move_options, current_street = player.move_possibilities()

    # Show menu of possible places to move to
    reply_keyboard = (
        [[current_street.name_cz + " (zůstat a přeskočit kolo)"]]
        + [[x.name_cz] for x in move_options]
        + [["Zpět do menu"]]
    )
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    await update.message.reply_text(
        "Do jaké ulice se chceš přesunout?", reply_markup=markup
    )
    return "character_move"


async def change_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Function that determines which place player chose to move to and moves him there."""
    town_map: Map = context.user_data["map"]
    player: Player = context.user_data["player"]
    street_name = update.message.text.split(" (")[0]
    move_options, current_street = player.move_possibilities()

    # Check if player chose a place where he can actually move to
    if street_name in [street.name_cz for street in move_options + [current_street]]:
        new_street_ID = town_map.name_cz_to_ID[street_name]
        player.place_ID = new_street_ID

        # Check if street name was tagged with "(stay here)" thus player stayed on the same place and went for another round
        if len(street_name) == len(update.message.text):
            await update.message.reply_text(
                town_map.get_street_by_ID(new_street_ID).description_cz
            )
        else:
            await update.message.reply_text("Svět se hnul, ale tys zůstal na místě.")

        # Since rotation is in recursion we have to backtrack to be able to return ending string
        # TODO I believe there might a better way to do this.
        game_end = await rotation(update.message.chat.id, context, update)
        if game_end == "starting_new_game":
            return "starting_new_game"
        return await basic_window(update, context)

    # Player has sent invalid input
    else:
        # Give player streets choices once more
        reply_keyboard = (
            [[current_street.name_cz + " (zůstat a přeskočit kolo)"]]
            + [[x.name_cz] for x in move_options]
            + [["Zpět do menu"]]
        )
        markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
        await update.message.reply_text(
            "Do jaké ulice se chceš přesunout?", reply_markup=markup
        )
        return "character_move"


async def inspect_player(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Function returns data about characters current state and creates menu for a of other choices."""
    town_map = context.user_data["map"]
    player: Player = context.user_data["player"]
    items_collection: ItemsCollection = items.read_items_from_file("data\items.csv")
    chat_ID = update.message.chat.id
    current_save = save.read_current_save(chat_ID)
    player_information = f"Místo, kde se nacházíš, se jmenuje *{town_map.get_street_by_ID(player.place_ID).name_cz}*\.\n\nMomentálně u sebe máš:\n`{player.coins}` peněz\n{', '.join([f'_{items_collection.get_item(x).name_cz}_' for x in player.items])}\n\n`Úroveň rychlosti: {player.speed}\nÚroveň síly: {player.strength}`\n\nMomentálně máš vybavené tyto zbraně:\n{', '.join([f'_{items_collection.get_item(x).name_cz}_' for x in player.equiped_weapons])}"
    await context.bot.send_message(chat_ID, player_information, parse_mode="MarkdownV2")

    # Creating menu for other choices
    reply_keyboard = [["Inventář"], ["Úkoly"], ["Zpět"]]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    await update.message.reply_text("Co víc bys rád?", reply_markup=markup)
    return "inspect_player"


async def open_inventory(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Function creates menu with items that player has in inventory tagged with consumable/equipable"""
    i_c: ItemsCollection = context.user_data["items"]
    player: Player = context.user_data["player"]

    # If character owns at least one item it shows them and add tag
    if len(player.items) != 0:
        reply_keyboard = [
            [
                i_c.get_item(x).name_cz
                + (
                    " (spotřebovatelný)"
                    if i_c.get_item(x).usage == "consume"
                    else " (nasaditelný)"
                    if i_c.get_item(x).usage == "equip"
                    else ""
                )
            ]
            for x in player.items
        ]
        markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
        await update.message.reply_text("Který předmět tě zajímá?", reply_markup=markup)
        return "choose_item"

    else:
        await update.message.reply_text("Tvůj inventář bohužel zeje prázdnotou.")
        return await basic_window(update, context)


async def choose_item(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Funciton creates a part of dialogue where is player asked if he wants to use chosen item"""
    player: Player = context.user_data["player"]
    items_col: ItemsCollection = context.user_data["items"]
    # Get rid of the usage tag
    chosen_item_name = update.message.text.split(" (")[0]
    item_ID = items_col.name_cz_to_ID[chosen_item_name]
    item = items_col.get_item(item_ID)

    # Generates item description based on type
    if item.usage == "consume":
        usage_text = "Je pouze na jednou použití\."
        question_text = "Přeješ si ho tedy použít?"
        reply_keyboard = [["Použít"], ["Návrat"]]
        context.user_data["item"] = item

    elif item.usage == "equip":
        usage_text = "Předmět je potřeba si nasadit\."
        question_text = "Přeješ si ho nasadit?"
        reply_keyboard = [["Nasadit"], ["Návrat"]]
        context.user_data["item"] = item

    elif item.usage == "None":
        usage_text = "Předmět nelze momentálně nijak použít\."
        question_text = "Zpět do inventáře?"
        reply_keyboard = [["Návrat"]]

    # Since text that is being printed is formatted using MarkdownV2 from Telegram, most of the special signs such as . or - or + must be escaped with \
    # * text * -> makes text bold
    # _ text _ -> makes text italic
    # ` text ` -> makes text monospace
    desc = item.description_cz.replace(".", "\.")
    speed = ("\+" if item.speed_mod >= 0 else "") + str(item.speed_mod).replace(
        "-", "\-"
    )
    strength = ("\+" if item.strength_mod >= 0 else "") + str(
        item.strength_mod
    ).replace("-", "\-")

    await update.message.reply_text(
        f"*{chosen_item_name}*\n_{desc}_\n{usage_text}\n\n*Poskytuje následující:*\n`{speed} k rychlosti\n{strength} k síle`",
        parse_mode="MarkdownV2",
    )
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    await update.message.reply_text(question_text, reply_markup=markup)

    return "inspect_item"


async def use_item(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Function reads item chosen by player and applies its effects on him"""
    player: Player = context.user_data["player"]
    # Get rid of the usage tag
    item: Item = context.user_data["item"]

    player.use_item(item)

    await update.message.reply_text(f"Použil jsi {item.name_cz}.")

    return await basic_window(update, context)


async def equip_item(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Function takes care of case when player chose and equipable item from his inventory"""
    player: Player = context.user_data["player"]
    equip_succes = player.equip_weapon(context.user_data["item"])
    if equip_succes:
        return await basic_window(update, context)
    # Player already has 2 weapons equiped
    else:
        # Generating menu to choose which weapon to replace
        equiped = player.get_equiped_weapons(context.user_data["items"])
        reply_keyboard = [
            [f"{item.name_cz} ({item.strength_mod} síla) ({item.speed_mod} rychlost)"]
            for item in equiped
        ]
        markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
        await update.message.reply_text(
            "Bohužel už máš vybavené dva předměty. Proto jeden z nich musíš vyměnit. Který to bude?",
            reply_markup=markup,
        )
        return "replace_item"


async def replace_item(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Function takes care of situation where player had already 2 weapons equiped,
    thus have to swap this new one with different one"""
    items_col: ItemsCollection = context.user_data["items"]
    item_name = update.message.text.split(" (")[0]
    item_ID = items_col.name_cz_to_ID[item_name]
    replace_item = items_col.get_item(item_ID)

    player: Player = context.user_data["player"]
    player.swap_weapon(replace_item, context.user_data["item"])
    return await basic_window(update, context)


async def open_quests(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Function generates menu with all the quests player has available"""
    player: Player = context.user_data["player"]
    map: Map = context.user_data["map"]
    society: Society = context.user_data["people"]

    # Create dictionary to be able to identify quest definition by ID od that quest
    quest_ID_to_str: dict[int, str] = dict()

    if len(player.quests) != 0:
        # When there is at least one quest
        # Shows quest in order as they are saved in player.quests and
        # assigns them an order number (index of quest + 1) so it can be tracked afterwards
        reply_keyboard = []
        for quest_str_idx in range(len(player.quests)):
            quest_str = player.quests[quest_str_idx]
            mqp = quest.dict_to_mqp(quest_str)
            # Final place is static
            if mqp.go_to == -1:
                reply_keyboard += [
                    [
                        f"{quest_str_idx+1}. Dostav se na místo {map.get_street_by_ID(mqp.to_place_ID).name_cz}"
                    ]
                ]
            # Final place is based on character
            else:
                reply_keyboard += [
                    [
                        f"{quest_str_idx+1}. Najdi postavu {society.get_char_by_ID(mqp.go_to).name_cz}"
                    ]
                ]

            quest_ID_to_str[quest_str_idx + 1] = quest_str

        context.user_data["player_quests"] = quest_ID_to_str

        # Choose exact quest to get more info
        markup = ReplyKeyboardMarkup(
            reply_keyboard + [["Zpět"]], one_time_keyboard=True
        )
        await update.message.reply_text("Jaký z úkolů tě zajímá?", reply_markup=markup)
        return "get_quest"

    return await basic_window(update, context)


async def get_quest(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Function to output specification of chosen quest and to track the progress player did"""
    # TODO printing out this window should lead to return on quests summaries not the basic window
    map: Map = context.user_data["map"]
    items: ItemsCollection = context.user_data["items"]
    society: Society = context.user_data["people"]
    player: Player = context.user_data["player"]
    quest_ID_to_str: dict[int, str] = context.user_data["player_quests"]
    # Get a quest definition string based on ordinal number before quest
    visual_quest_ID = int(update.message.text.split(". ")[0])
    quest_str = quest_ID_to_str[visual_quest_ID]
    quest_mqp = quest.dict_to_mqp(quest_str)

    progress = player.progress[visual_quest_ID - 1]

    # Final message is based from multiple parts.
    # Each part starts with emoji which is based on the if player already finished this part
    # It is followed by description of that part
    from_txt = (
        ""
        if quest_mqp.from_place_ID == -1
        else "\u2705 "
        if progress != "tostart"
        else "\u2716 "
    )

    from_txt += (
        ""
        if quest_mqp.from_place_ID == -1
        else f"Dostav se sem: _{map.get_street_by_ID(quest_mqp.from_place_ID).name_cz}_\n"
    )

    item_txt = (
        ""
        if quest_mqp.from_place_ID == -1
        else "\u2705 "
        if progress != "tostart"
        else "\u2716 "
    )

    item_txt += (
        ""
        if quest_mqp.item_ID == -1
        else f"Převezmi předmět: _{items.get_item(quest_mqp.item_ID).name_cz}_\n"
    )

    to_txt = "\u2705 " if progress == "ended" or progress == "infinal" else "\u2716 "

    to_txt += (
        f"Dojdi do: _{map.get_street_by_ID(quest_mqp.to_place_ID).name_cz}_"
        if quest_mqp.go_to == -1
        else f"Cílem je: _{society.get_char_by_ID(quest_mqp.go_to).name_cz}_"
    )

    action_txt = (
        ""
        if quest_mqp.action == "None"
        else "\u2705 "
        if progress == "ended"
        else "\u2716 "
    )

    action_txt += (
        ""
        if quest_mqp.action == "None"
        else "Zab cíl"
        if quest_mqp.action == "kill"
        else "Omrač cíl"
        if quest_mqp.action == "stun"
        else "Okraď cíl"
        if quest_mqp.action == "rob"
        else f"{quest_mqp.action}"
    )

    reward_txt = (
        "" if progress != "ended" else "\n\U0001F4B2 Jdi si vybrat odměnu k zadavateli"
    )

    client_txt = (
        f"Úkol ti zadal/a: _{society.get_char_by_ID(quest_mqp.characterID).name_cz}_"
    )

    text = f"*Více informací:*\n{from_txt}{item_txt}{to_txt}\n{action_txt}{reward_txt}\n{client_txt}"

    await update.message.reply_text(text, parse_mode="MarkdownV2")

    return await basic_window(update, context)


async def make_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Opens menu for player to choose an action he wants to perform. If there is no option available it returns him to main menu"""
    town_map: Map = context.user_data["map"]
    player: Player = context.user_data["player"]
    society: Society = context.user_data["people"]
    current_characters: ModifiedPeople = context.user_data["current_people"]

    action_dict, people_here = player.get_actions(current_characters, town_map)

    char_ID_to_relation = player.get_relationships(people_here, society)

    # Save relations with characters since it is gonna be needed while interacting with them
    context.user_data["char_ID_to_relation"] = char_ID_to_relation

    # Add possibility of action only if there is the possibility
    reply_keyboard = []
    if len(action_dict) > 0:
        context.user_data["action_dict"] = action_dict
        reply_keyboard.append(["Nakoupit v obchodě"])
    if len(people_here) > 0:
        context.user_data["people_here"] = people_here
        reply_keyboard.append(["Interagovat s ostatními"])

    # When there is at least one action, new menu is opened to choose one of these actions
    if len(reply_keyboard) > 0:
        markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
        await update.message.reply_text("Co si přeješ udělat?", reply_markup=markup)
        return "choose_action"
    else:
        await update.message.reply_text(
            "Bohužel, zrovna tady na tebe žádné dobrodružství nečeká."
        )
        return await basic_window(update, context)


async def choose_person(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Function summons window with all characters present in the same place as player."""
    # TODO should add the state of character
    people_list = context.user_data["people_here"]
    society = context.user_data["people"]
    # Possibility to interact with them and window with possible choices
    # gets created only when there is someone in the same place
    if len(people_list) != 0:
        reply_keyboard = [[person.get_name_cz(society)] for person in people_list] + [
            ["Zpět do menu"]
        ]
        markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)

        await update.message.reply_text("S kým chceš mluvit?", reply_markup=markup)

        return "person_to_talk"
    else:
        await update.message.reply_text("Nikdo tu bohužel není :(")
        return await basic_window(update, context)


async def talk_to_person(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start interaction with chosen NPC"""
    player: Player = context.user_data["player"]
    char_ID_to_relation = context.user_data["char_ID_to_relation"]
    society: Society = context.user_data["people"]
    char_ID = society.name_cz_to_ID[update.message.text]

    # Each character can have his own defined specific interactions with player,
    # such as giving him his reward for quest
    character_specific_actions: dict[int, list[tuple[str, str]]] = context.user_data[
        "character_specific_actions"
    ]
    context.user_data["char_ID"] = char_ID

    # TODO should modify character interactions based on state of character
    char_relation = char_ID_to_relation[char_ID]
    context.user_data["char_relation"] = char_relation

    text = (
        "se netváří dvakrát nadšeně."
        if char_relation == 1
        else "tě probodává pohledem."
        if char_relation == 0
        else "tě sleduje zamyšleným pohledem."
        if char_relation == 2
        else "se na tebe usmívá."
    )
    await update.message.reply_text(f"{update.message.text} {text}")

    # Adding specific actions to characters
    # TODO There is bug when there was possibility to redeem the quest 12 times?
    if char_ID in character_specific_actions:
        added_possibility = [[x[0]] for x in character_specific_actions[char_ID]]
    else:
        added_possibility = []

    reply_keyboard = [
        ["Zeptat se na cestu"],
        ["Zeptat se na postavu"],
        ["Zabít postavu", "Omráčit postavu"],
        ["Okrást postavu", "Nastražit předmět"],
    ] + added_possibility
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    await update.message.reply_text("Co si přeješ udělat?", reply_markup=markup)
    return "NPC_interaction"


async def open_shop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Function summons window with options of buyable items"""
    items_colection: ItemsCollection = context.user_data["items"]
    action_dict: dict[str, str] = context.user_data["action_dict"]
    type = action_dict["shop"]
    items_to_sell = items_colection.items_by_type(type)

    # Creates menu of all items that can be bought with a price tag
    reply_keyboard = [
        [item.name_cz + " (" + str(item.price) + ")"] for item in items_to_sell
    ]
    reply_keyboard.append(["Zpět do menu"])
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    await update.message.reply_text("Co bys sis rád koupil?", reply_markup=markup)
    return "buy_item"


async def buy_item(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Function to check if player can afford the item ho chose and following adding this item into his inventory"""
    player: Player = context.user_data["player"]
    items_col: ItemsCollection = context.user_data["items"]
    # Get rid of the price tag
    chosen_item_name = update.message.text.split(" (")[0]
    item_ID = items_col.name_cz_to_ID[chosen_item_name]
    item = items_col.get_item(item_ID)
    if item.price > player.coins:
        await update.message.reply_text("Předmět je na tebe bohužel moc drahý")
    else:
        player.coins -= item.price
        player.items.append(item_ID)
        await update.message.reply_text(
            f"Úspěšně sis zakoupil {chosen_item_name}. Kdybys tento předmět náhodou hledal, tak na tebe bude čekat v inventáři."
        )

    return await basic_window(update, context)


async def ask_for_path(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Player asks NPC if he could help him with finding a way to another place. Answer is based on their relationship"""
    town_map: Map = context.user_data["map"]
    char_relation = context.user_data["char_relation"]
    if char_relation == 0:
        await update.message.reply_text(
            "To si snad děláš srandu? Po tom cos udělal našim lidem. Padej!"
        )
        # TODO add some reaction from character, probably fight
        return await basic_window(update, context)
    elif char_relation == 1:
        await update.message.reply_text("Promiň kámo, ale fakt ti nepomůžu...")
        return await basic_window(update, context)
    elif char_relation == 3:
        text = "'Jasně kámo, kam pádíš?'"
        context.user_data["num_of_streets"] = 4
    else:
        text = "'Uhh...asi bych věděl...podle toho kam?'"
        context.user_data["num_of_streets"] = 3

    reply_keyboard = [[x.name_cz] for x in town_map.streets]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    await update.message.reply_text(text, reply_markup=markup)
    return "look_for_path"


async def find_path_to(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Based on how much does NPC like player he hints him how to get to player's desired place and describes part of the path"""
    town_map: Map = context.user_data["map"]
    start_place_ID: int = context.user_data["player"].place_ID
    num_of_streets: int = context.user_data["num_of_streets"]
    final_place_ID: int = town_map.name_cz_to_ID[update.message.text]
    path = town_map.shortest_path(start_place_ID, final_place_ID)
    revealed_path = path[1 : num_of_streets + 1]

    # Answer is based on realtionship and length of path
    if len(revealed_path) == 0:
        await update.message.reply_text("Vítej v cíli chytráku...")
    elif len(path) - 2 > len(revealed_path):
        await update.message.reply_text(
            "Jo tak to první bude "
            + " a pak ".join(
                [town_map.get_street_by_ID(x).name_cz for x in revealed_path]
            )
            + " a pak to už nějak najdeš..."
        )
    elif len(path) - 2 <= len(revealed_path):
        await update.message.reply_text(
            "Jo tak to první bude "
            + " a pak ".join(
                [town_map.get_street_by_ID(x).name_cz for x in revealed_path]
            )
            + ". No a jsi tam."
        )

    return await basic_window(update, context)


async def ask_for_person(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Player asks NPC if he could help him finding another NPC. Answer is based on their relationship"""
    society: Society = context.user_data["people"]
    char_relation = context.user_data["char_relation"]
    # Answer based on relationship
    if char_relation == 0:
        await update.message.reply_text(
            "To si snad děláš srandu? Po tom cos udělal našim lidem (BOJ ČAS)"
        )
        # TODO add fight
        return await basic_window(update, context)
    elif char_relation == 1:
        await update.message.reply_text("Promiň kámo, ale fakt ti nepomůžu...")
        return await basic_window(update, context)
    elif char_relation == 3:
        text = "'Jasně kámo, za kým pádíš?'"
        context.user_data["num_of_streets"] = 2
    else:
        text = "'Uhh...asi bych věděl...podle toho za kým míříš?'"
        context.user_data["num_of_streets"] = 1

    # Choose person to follow
    reply_keyboard = [[x.name_cz] for x in society.people_list]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    await update.message.reply_text(text, reply_markup=markup)
    return "look_for_person"


async def path_to_person(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Based on how much does NPC like player he hints him how to get to find the person"""
    # TODO too similar to finding path, maybe should change this to getting the name of street where character is at the moment
    town_map: Map = context.user_data["map"]
    society: Society = context.user_data["people"]
    current_chars: ModifiedPeople = context.user_data["current_people"]
    start_place_ID: int = context.user_data["player"].place_ID
    num_of_streets: int = context.user_data["num_of_streets"]
    final_place_ID: int = current_chars.get_NPC(
        society.name_cz_to_ID[update.message.text]
    ).place_ID
    path = town_map.shortest_path(start_place_ID, final_place_ID)
    revealed_path = path[1 : num_of_streets + 1]

    # Answer is based on realtionship and length of path
    if len(revealed_path) == 0:
        await update.message.reply_text("Rozhlídni se kolem...")
    elif len(path) - 2 > len(revealed_path):
        await update.message.reply_text(
            "Jo tak to první bude "
            + " a pak".join(
                [town_map.get_street_by_ID(x).name_cz for x in revealed_path]
            )
            + " a pak to už nějak najdeš"
        )
    elif len(path) - 2 <= len(revealed_path):
        await update.message.reply_text(
            "Jo tak to první bude "
            + " a pak".join(
                [town_map.get_street_by_ID(x).name_cz for x in revealed_path]
            )
            + ". No a tam snad bude."
        )

    return await basic_window(update, context)


async def attack_on_person(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Function that takes care of fight between a player and NPC.
    Successful attack knocks the NPC out whereas failed knocks out Player for 2 rounds
    """

    # TODO solve through some argument not like this
    if update.message.text == "Zabít postavu":
        action = "kill"
    elif update.message.text == "Omráčit postavu":
        action = "stun"

    player: Player = context.user_data["player"]
    society: Society = context.user_data["people"]
    current_chars: ModifiedPeople = context.user_data["current_people"]
    defender_ID = context.user_data["char_ID"]
    defender = current_chars.get_NPC(defender_ID)

    current_characters, failed = handler.fight(player, defender, action, current_chars)
    context.user_data["current_people"] = current_characters

    # Resolving consequences of players actions
    if failed:
        # An eye for an eye princip: if player tried to kill the character and failed he is gonna die
        if action == "kill":
            await update.message.reply_text(
                "Tak tohle se ti moc nepovedlo a bohužel *je po tobě*\.",
                parse_mode="MarkdownV2",
            )
            return await end_game(update, context)
        elif action == "stun":
            await update.message.reply_text(
                "Tak tohle se ti moc nepovedlo a bohužel na chvíli *ztrácíš vědomí*\.",
                parse_mode="MarkdownV2",
            )
            player.state = "stun"
            player.duration["stun"] = 2
            await rotation(update.message.chat.id, context, update)
    else:
        if action == "kill":
            await update.message.reply_text(
                f"*Úspěšně se ti podařilo zlikvidovat postavu\.*\n_{society.get_char_by_ID(defender_ID).name_cz}_ tu teď leží v kaluži krve\.",
                parse_mode="MarkdownV2",
            )
        elif action == "stun":
            await update.message.reply_text(
                f"*Úspěšně se ti podařilo omráčit postavu\.*\n_{society.get_char_by_ID(defender_ID).name_cz}_ tu teď leží v mrákotách\.",
                parse_mode="MarkdownV2",
            )

    return await basic_window(update, context)


async def steal_from_person(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Function takes care of player's attempt to steal from a character"""
    # TODO solve through some argument not like this
    if update.message.text == "Okrást postavu":
        action = "rob"
    elif update.message.text == "Nastražit předmět":
        action = "plant"

    player: Player = context.user_data["player"]
    current_chars: ModifiedPeople = context.user_data["current_people"]
    defender_ID = context.user_data["char_ID"]
    defender = current_chars.get_NPC(defender_ID)

    # TODO currently the biggest flaw. On planting, player puts ALL of his items into defender's inventory
    # To solve issue (make choice possibilites) I believe I would neeed to open a new dialogue window to not break the flow of code in steal action.
    """
    if action == "plant":
        print("wut")
        await choose_item_to_plant(
            update, context, player.items + player.equiped_weapons)
    """

    current_characters, failed = handler.steal(player, defender, action, current_chars)

    context.user_data["current_people"] = current_characters

    # On failure, player gets stunned for 2 rounds
    if failed:
        if player.state == "stun":
            await update.message.reply_text(
                "Tak tohle se ti moc nepovedlo a bohužel na chvíli *ztrácíš vědomí*\.",
                parse_mode="MarkdownV2",
            )
            player.duration["stun"] = 2
            await rotation(update.message.chat.id, context, update)

    else:
        # TODO output which items player stole/planted
        if action == "rob":
            await update.message.reply_text(f"Úspěšně jsi okradl svou oběť.")
        elif action == "plant":
            await update.message.reply_text(f"Úspěšně ses zbavil všech svých předmětů.")

    return await basic_window(update, context)


# TODO currently the biggest flaw. On planting, player puts ALL of his items into defender's inventory
# To solve issue (make choice possibilites) I believe I would neeed to open a new dialogue window to not break the flow of code in steal action.


async def choose_item_to_plant(
    update: Update, context: ContextTypes.DEFAULT_TYPE, items: list[int]
):
    """TODO not working not implemented"""
    i_c: ItemsCollection = context.user_data["items"]

    await update.message.reply_text("Který předmět nastražíš?", reply_markup=markup)

    reply_keyboard = [[i_c.get_item(item).name_cz] for item in items]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    return "item_to_plant"


async def item_to_plant(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """TODO not working not implemented"""
    items_col: ItemsCollection = context.user_data["items"]
    return items_col.name_cz_to_ID[update.message.text]


async def specific_opration(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Function takes care of what happens when player has chosen an specific operation"""
    player: Player = context.user_data["player"]
    char_ID: int = context.user_data["char_ID"]
    character_specific_actions: list[tuple[str, str]] = context.user_data[
        "character_specific_actions"
    ][char_ID]
    # Function takes text from message and based on that finds specific action to perform
    for specific_action in character_specific_actions:
        if specific_action[0] == update.message.text:
            action = specific_action[1]
            break

    # This is actually end of a game.
    if action == "meow":
        await update.message.reply_text("\U0001F63BNAŠEL JSI KOČKU\U0001F63B")

        reply_keyboard = [["Začít znovu"], ["Ukončit"]]
        markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
        await update.message.reply_text(
            "Hra skončila. Co bude dál?", reply_markup=markup
        )

        return "starting_new_game"

    # TODO I believe this could be solved better by passing some argument.
    # Goes through all quests player has and if the ID of client is the same as an ID of character
    # with which player interacts player gets a reward for this quest
    # Quest and progress is then removed
    elif action == "quest_reward":
        for quest_idx in range(len(player.quests)):
            quest_mqp = quest.dict_to_mqp(player.quests[quest_idx])
            if quest_mqp.characterID == char_ID:
                await update.message.reply_text(f"Úspěšně sis vyzvedl odměnu.")
                player.coins += quest_mqp.reward["coins"]
                if quest_mqp.reward["item"] != -1:
                    player.items.append(quest_mqp.reward["item"])
                player.quests.pop(quest_idx)
                player.progress.pop(quest_idx)
                character_specific_actions.remove([update.message.text, action])
                break
        return await basic_window(update, context)


async def basic_window(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Function creates basic menu with choices for player about what he wants to do next"""
    # Check if any quest has ended
    player: Player = context.user_data["player"]
    current_people: ModifiedPeople = context.user_data["current_people"]
    # Player can finish quest in place and it might happen next phase is also here
    # Therefore quest progress should be refreshed after players every action
    completed_quests = player.check_quest_action_complete(current_people)
    await generate_quest_finishes(context, completed_quests)
    reply_keyboard = [["Provést akci"], ["Postava"], ["Jít dál"]]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    await update.message.reply_text("Co si přeješ udělat?", reply_markup=markup)
    return "player_actions"


async def generate_quest_finishes(
    context: ContextTypes.DEFAULT_TYPE, completed_quests: list[str]
) -> None:
    """Takes care of generating specific actions to redeem quest rewards from character"""
    character_specific_actions: dict[int, list[tuple[str, str]]] = context.user_data[
        "character_specific_actions"
    ]
    for quest_str in completed_quests:
        cur_quest = quest.dict_to_mqp(quest_str)
        # If character has no other specific action
        if cur_quest.characterID not in character_specific_actions:
            character_specific_actions[cur_quest.characterID] = [
                ["Shrábnout odměnu", "quest_reward"]
            ]
        # Character has another specific action that is not quest rewarding
        elif ["Shrábnout odměnu", "quest_reward"] not in character_specific_actions[
            cur_quest.characterID
        ]:
            character_specific_actions[cur_quest.characterID].append(
                ["Shrábnout odměnu", "quest_reward"]
            )


def get_token():
    """Read token from file"""
    file = open(r"data\token.txt")
    token = file.readlines()[0].rstrip("\n")
    return token


def main() -> None:
    """Run the bot"""
    # Used to connect to the bot and and start communication with this program
    api_key = get_token()
    application = Application.builder().token(api_key).build()
    print("Starting bot...")
    # Creates conversation handler that is used to take care of player's inputs and reacting on them
    # It defines condition to start conversation and fallback
    # Then defines reactions on different player messages in different contexts
    conversation_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            "starting_new_game": [
                MessageHandler(filters.Regex("Začít"), start_new_game),
                MessageHandler(filters.Regex("Nezačínat"), read_old_game),
                MessageHandler(filters.Regex("Ukončit"), end_game),
            ],
            "player_actions": [
                MessageHandler(filters.Regex("Provést"), make_action),
                MessageHandler(filters.Regex("Postava"), inspect_player),
                MessageHandler(filters.Regex("Jít"), move_character),
            ],
            "character_move": [
                MessageHandler(filters.Regex("Zpět"), basic_window),
                MessageHandler(filters.TEXT, change_location),
            ],
            "person_to_talk": [
                MessageHandler(filters.Regex("Zpět"), basic_window),
                MessageHandler(filters.TEXT, talk_to_person),
            ],
            "choose_action": [
                MessageHandler(filters.Regex("Interagovat"), choose_person),
                MessageHandler(filters.Regex("Nakoupit"), open_shop),
            ],
            "buy_item": [
                MessageHandler(filters.Regex("Zpět"), basic_window),
                MessageHandler(filters.TEXT, buy_item),
            ],
            "NPC_interaction": [
                MessageHandler(filters.Regex("na cestu"), ask_for_path),
                MessageHandler(
                    filters.Regex("na postavu") & ~(filters.Regex("Zabít|Omráčit")),
                    ask_for_person,
                ),
                MessageHandler(filters.Regex("Zabít|Omráčit"), attack_on_person),
                MessageHandler(filters.Regex("Okrást|Nastražit"), steal_from_person),
                MessageHandler(filters.TEXT, specific_opration),
            ],
            "item_to_plant": [MessageHandler(filters.TEXT, item_to_plant)],
            "look_for_path": [MessageHandler(filters.TEXT, find_path_to)],
            "look_for_person": [MessageHandler(filters.TEXT, path_to_person)],
            "inspect_player": [
                MessageHandler(filters.Regex("Inventář"), open_inventory),
                MessageHandler(filters.Regex("Úkoly"), open_quests),
                MessageHandler(filters.Regex("Zpět"), basic_window),
            ],
            "choose_item": [MessageHandler(filters.TEXT, choose_item)],
            "inspect_item": [
                MessageHandler(filters.Regex("Použít"), use_item),
                MessageHandler(filters.Regex("Nasadit"), equip_item),
                MessageHandler(filters.Regex("Návrat"), inspect_player),
            ],
            "replace_item": [
                MessageHandler(filters.Regex("Zpět"), open_inventory),
                MessageHandler(filters.TEXT, replace_item),
            ],
            "get_quest": [
                MessageHandler(filters.Regex("Zpět"), inspect_player),
                MessageHandler(filters.TEXT, get_quest),
            ],
        },
        fallbacks=[CommandHandler("start", start)],
    )

    application.add_handler(conversation_handler)

    # Run the bot until the user kills it (Ctrl-C)
    print("Bot is running!")
    print("To end him press Ctrl-C")
    application.run_polling()


if __name__ == "__main__":
    print("Starting...")
    main()
