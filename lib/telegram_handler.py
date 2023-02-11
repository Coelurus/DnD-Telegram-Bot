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

    context.user_data["current_quests_str"] = current_quests_str

    current_player = save.get_current_player(current_player_str)
    context.user_data["player"] = current_player

    current_characters = save.get_current_characters(current_chars_str)
    context.user_data["current_people"] = current_characters


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


async def rotation(chat_ID: int, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Function take care of handling movement of NPC, making them follow missions etc. 
    It also updates questlines progresses and assign phases to NPCs based on it"""
    current_characters: ModifiedPeople = context.user_data["current_people"]
    current_quests_str: str = context.user_data["current_quests_str"]
    player: Player = context.user_data["player"]

    current_characters, lines_to_update = save.update_phases(
        current_characters)

    new_quests_str = save.update_quests(current_quests_str, lines_to_update)

    current_quests_save = save.get_current_quests(new_quests_str)

    current_characters = save.assign_quests(
        current_characters, current_quests_save)

    current_characters_str = save.move_characters(current_characters).to_str()

    new_player_save = save.player_save_generator(player)

    context.user_data["current_quests_str"] = new_quests_str

    combined_save = f"{new_player_save}_{new_quests_str}_{current_characters_str}"

    save.rewrite_save_file(chat_ID, combined_save)

    if player.state == "stun" and player.duration["stun"] >= 1:
        print("ando nce more")
        await rotation(chat_ID, context)


async def move_character(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Function that offers player choice of places where he can move."""
    player: Player = context.user_data["player"]

    move_options, current_street = player.move_possibilities()

    reply_keyboard = [[current_street.name_cz + " (zůstat a přeskočit kolo)"]
                      ] + [[x.name_cz] for x in move_options] + [["Zpět do menu"]]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)

    await update.message.reply_text("Do jaké ulice se chceš přesunout?", reply_markup=markup)

    return "character_move"


async def change_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Function that determines which place player chose to move to and moves him there."""
    town_map: Map = context.user_data["map"]
    player: Player = context.user_data["player"]
    street_name = update.message.text.split(" (")[0]
    new_street_ID = town_map.name_cz_to_ID[street_name]
    player.place_ID = new_street_ID

    if len(street_name) == len(update.message.text):
        await update.message.reply_text(town_map.get_street_by_ID(new_street_ID).description_cz)
    else:
        await update.message.reply_text("Svět se hnul, ale tys zůstal na místě.")

    await rotation(update.message.chat.id, context)

    return await basic_window(update)


async def inspect_player(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Function returns data about characters current state."""
    town_map = context.user_data["map"]
    player: Player = context.user_data["player"]
    items_collection: ItemsCollection = items.read_items_from_file(
        "data\items.csv")
    chat_ID = update.message.chat.id
    current_save = save.read_current_save(chat_ID)
    player_information = f"Místo, kde se nacházíš, se jmenuje {town_map.get_street_by_ID(player.place_ID).name_cz}.\nMomentálně u sebe máš {player.coins} peněz a následující předměty: {', '.join([items_collection.get_item(x).name_cz for x in player.items])}\nTvoje síla je na úrovni {player.strength} a rychlost na úrovni {player.speed}"
    await context.bot.send_message(chat_ID, player_information)

    reply_keyboard = [
        ["Inventář"],
        ["Úkoly"],
        ["Zpět"]
    ]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)

    await update.message.reply_text("Co víc bys rád?", reply_markup=markup)

    return "inspect_player"


async def open_inventory(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Function creates menu with items that player has in inventory with type tag consumable/equipable"""
    i_c: ItemsCollection = context.user_data["items"]
    player: Player = context.user_data["player"]

    if len(player.items) != 0:
        reply_keyboard = [[i_c.get_item(x).name_cz + (" (spotřebovatelný)" if i_c.get_item(
            x).usage == "consume" else " (nasaditelný)" if i_c.get_item(x).usage == "equip" else "")] for x in player.items]
        markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
        await update.message.reply_text("Který předmět tě zajímá?", reply_markup=markup)
        return "choose_item"

    else:
        await update.message.reply_text("Tvůj inventář bohužel zeje prázdnotou.")
        return await basic_window(update)


async def choose_item(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Funciton creates a part of dialogue where is player asked if he wants to use chosen item"""
    player: Player = context.user_data["player"]
    items_col: ItemsCollection = context.user_data["items"]
    # Get rid of the usage tag
    chosen_item_name = update.message.text.split(" (")[0]
    item_ID = items_col.name_cz_to_ID[chosen_item_name]
    item = items_col.get_item(item_ID)

    if item.usage == "consume":
        usage_text = "Je pouze na jednou použití."
        question_text = "Přeješ si ho tedy použít?"
        reply_keyboard = [["Použít"], ["Návrat"]]
        context.user_data["item"] = item

    elif item.usage == "equip":
        usage_text = "Předmět je potřeba si nasadit."
        question_text = "Přeješ si ho nasadit?"
        reply_keyboard = [["Nasadit"], ["Návrat"]]
        context.user_data["item"] = item

    elif item.usage == "none":
        usage_text = "Předmět nelze momentálně nijak použít."
        question_text = "Zpět do inventáře?"
        reply_keyboard = [["Návrat"]]

    await update.message.reply_text(f"{chosen_item_name}\n{item.description_cz}\n{usage_text}\nPoskytuje následující:\n{item.speed_mod} k rychlosti\n{item.strength_mod} k síle")
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    await update.message.reply_text(question_text, reply_markup=markup)

    return "inspect_item"


async def use_item(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Function takes reads item chosen by player and applies its effects on him"""
    player: Player = context.user_data["player"]
    # Get rid of the usage tag
    item: Item = context.user_data["item"]

    player.use_item(item)

    await update.message.reply_text(f"Použil jsi {item.name_cz}.")

    return await basic_window(update)


async def equip_item(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Function takes care of case when player chose and equipable item from his inventory"""
    player: Player = context.user_data["player"]
    equip_succes = player.equip_weapon(context.user_data["item"])
    if equip_succes:
        return await basic_window(update)
    else:
        equiped = player.get_equiped_weapons(
            context.user_data["items"])
        reply_keyboard = [
            [f"{item.name_cz} ({item.strength_mod} síla) ({item.speed_mod} rychlost)"] for item in equiped]
        markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
        await update.message.reply_text("Bohužel už máš vybavené dva předměty. Proto jeden z nich musíš vyměnit. Který to bude?", reply_markup=markup)
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
    return await basic_window(update)


async def open_quests(update: Update, context: ContextTypes.DEFAULT_TYPE):
    player: Player = context.user_data["player"]
    map: Map = context.user_data["map"]
    society: Society = context.user_data["people"]

    quest_ID_to_str: dict[int, str] = dict()

    if len(player.quests) != 0:

        reply_keyboard = []
        for quest_str_idx in range(len(player.quests)):
            quest_str = player.quests[quest_str_idx]
            mqp = quest.str_to_mqp(quest_str)
            if mqp.go_to == -1:
                reply_keyboard += [
                    [f"{quest_str_idx+1}. Dostav se na místo {map.get_street_by_ID(mqp.to_place_ID).name_cz}"]]
            else:
                reply_keyboard += [
                    [f"{quest_str_idx+1}. Najdi postavu {society.get_char_by_ID(mqp.go_to).name_cz}"]]

            quest_ID_to_str[quest_str_idx+1] = quest_str

        context.user_data["player_quests"] = quest_ID_to_str

        markup = ReplyKeyboardMarkup(
            reply_keyboard + [["Zpět"]], one_time_keyboard=True)
        await update.message.reply_text("Jaká z úkolů tě zajímá?", reply_markup=markup)
        return "get_quest"

    return await basic_window(update)


async def get_quest(update: Update, context: ContextTypes.DEFAULT_TYPE):
    map: Map = context.user_data["map"]
    items: ItemsCollection = context.user_data["items"]
    society: Society = context.user_data["people"]
    quest_ID_to_str: dict[int, str] = context.user_data["player_quests"]
    # Get a quest definition string based on ordinal number before quest
    quest_str = quest_ID_to_str[int(update.message.text.split(". ")[0])]
    quest_mqp = quest.str_to_mqp(quest_str)

    from_txt = "" if quest_mqp.from_place_ID == - \
        1 else f"\nNejdřív se dostav sem: {map.get_street_by_ID(quest_mqp.from_place_ID).name_cz}"

    item_txt = "" if quest_mqp.item_ID == - \
        1 else f"\nDostaneš k tomu tenhle předmět: {items.get_item(quest_mqp.item_ID).name_cz}. Hlavně ho neztrať!"

    to_txt = f"Dojdi do: {map.get_street_by_ID(quest_mqp.to_place_ID).name_cz}" if quest_mqp.go_to == - \
        1 else f"Dojdi za: {society.get_char_by_ID(quest_mqp.go_to).name_cz}"

    action_txt = "" if quest_mqp.action == "none" else "...a tu osobu zab" if quest_mqp.action == "kill" else "...a tu osobu omrač" if quest_mqp.action == "stun" else "...a tu osobu okraď" if quest_mqp.action == "rob" else f"{quest_mqp.action}"

    text = f"Více informací:{from_txt}{item_txt}\n{to_txt}\n{action_txt}"

    await update.message.reply_text(text)

    return await basic_window(update)


async def make_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Opens menu for player to choose an action he wants to perform. If there is no option available it returns him to main menu"""
    chat_ID = update.message.chat.id
    current_save = save.read_current_save(chat_ID)

    town_map: Map = context.user_data["map"]
    player: Player = context.user_data["player"]
    item_collection: ItemsCollection = context.user_data["items"]
    society: Society = context.user_data["people"]
    current_characters: ModifiedPeople = context.user_data["current_people"]
    current_place: map.Street = town_map.get_street_by_ID(
        player.place_ID)

    action_dict, people_here = player.get_actions(
        current_characters, town_map)

    char_ID_to_relation = player.get_relationships(
        people_here, society)

    context.user_data["char_ID_to_relation"] = char_ID_to_relation

    reply_keyboard = []
    if len(action_dict) > 0:
        context.user_data["action_dict"] = action_dict
        reply_keyboard.append(["Nakoupit v obchodě"])
    if len(people_here) > 0:
        context.user_data["people_here"] = people_here
        reply_keyboard.append(["Mluvit s člověkem"])

    if len(reply_keyboard) > 0:
        markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
        await update.message.reply_text("Co si přeješ udělat?", reply_markup=markup)
        return "choose_action"
    else:
        await update.message.reply_text("Bohužel, zrovna tady na tebe žádné dobrodružství nečeká.")
        return await basic_window(update)


async def choose_person(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Function summons window all characters present in the same place as player."""
    people_list = context.user_data["people_here"]
    society = context.user_data["people"]
    if len(people_list) != 0:
        reply_keyboard = [
            [person.get_name_cz(society)] for person in people_list] + [["Zpět do menu"]]
        markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)

        await update.message.reply_text("S kým chceš mluvit?", reply_markup=markup)

        return "person_to_talk"
    else:
        await update.message.reply_text("Nikdo tu bohužel není :(")
        return await basic_window(update)


async def talk_to_person(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start interaction with chosen NPC"""
    player: Player = context.user_data["player"]
    char_ID_to_relation = context.user_data["char_ID_to_relation"]
    society: Society = context.user_data["people"]
    char_ID = society.name_cz_to_ID[update.message.text]
    context.user_data["char_ID"] = char_ID

    char_relation = char_ID_to_relation[char_ID]
    context.user_data["char_relation"] = char_relation
    await update.message.reply_text(f"{update.message.text} k tobě má vztah na úrovni {char_relation}")

    reply_keyboard = [
        ["Zeptat se na cestu"],
        ["Zeptat se na postavu"],
        ["Zaútočit na postavu"]
    ]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    await update.message.reply_text("Co si přeješ udělat?", reply_markup=markup)
    return "NPC_interaction"


async def open_shop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Function summons window where with options of buyable items"""
    items_colection: ItemsCollection = context.user_data["items"]
    action_dict: dict[str, str] = context.user_data["action_dict"]
    type = action_dict["shop"]
    items_to_sell = items_colection.items_by_type(type)

    reply_keyboard = [
        [item.name_cz + " (" + str(item.price) + ")"] for item in items_to_sell]
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
        await update.message.reply_text(f"Úspěšně sis zakoupil {chosen_item_name}. Kdybys tento předmět náhodou hledal, tak ho najdeš v inventáři.")

    return await basic_window(update)


async def ask_for_path(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Player asks NPC if he could help him with finding a way to street. Answer is based on their relationship"""
    town_map: Map = context.user_data["map"]
    char_relation = context.user_data["char_relation"]
    if char_relation == 0:
        await update.message.reply_text("To si snad děláš srandu? Po tom cos udělal našim lidem (BOJ ČAS)")
        # TODO add fight
        return await basic_window(update)
    elif char_relation == 1:
        await update.message.reply_text("Promiň kámo, ale fakt ti nepomůžu...")
        return await basic_window(update)
    elif char_relation == 3:
        text = "'Jasně kámo, kam pádíš?'"
        context.user_data["num_of_streets"] = 2
    else:
        text = "'Uhh...asi bych věděl...podle toho kam?'"
        context.user_data["num_of_streets"] = 1

    reply_keyboard = [[x.name_cz] for x in town_map.streets]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    await update.message.reply_text(text, reply_markup=markup)
    return "look_for_path"


async def find_path_to(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Based on how much does NPC like player he hints him how to get to find the person"""
    town_map: Map = context.user_data["map"]
    start_place_ID: int = context.user_data["player"].place_ID
    num_of_streets: int = context.user_data["num_of_streets"]
    final_place_ID: int = town_map.name_cz_to_ID[update.message.text]
    path = town_map.shortest_path(start_place_ID, final_place_ID)
    revealed_path = path[1:num_of_streets+1]

    if len(revealed_path) == 0:
        await update.message.reply_text("Vítej v cíli chytráku...")
    elif len(path)-2 > len(revealed_path):
        await update.message.reply_text("Jo tak to první bude " + " a pak".join([town_map.get_street_by_ID(x).name_cz for x in revealed_path]) + " a pak to už nějak najdeš")
    elif len(path)-2 <= len(revealed_path):
        await update.message.reply_text("Jo tak to první bude " + " a pak".join([town_map.get_street_by_ID(x).name_cz for x in revealed_path]) + ". No a jsi tam.")

    return await basic_window(update)


async def ask_for_person(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Player asks NPC if he could help him finding another NPC. Answer is based on their relationship"""
    town_map: Map = context.user_data["map"]
    society: Society = context.user_data["people"]
    char_relation = context.user_data["char_relation"]
    if char_relation == 0:
        await update.message.reply_text("To si snad děláš srandu? Po tom cos udělal našim lidem (BOJ ČAS)")
        # TODO add fight
        return await basic_window(update)
    elif char_relation == 1:
        await update.message.reply_text("Promiň kámo, ale fakt ti nepomůžu...")
        return await basic_window(update)
    elif char_relation == 3:
        text = "'Jasně kámo, kam pádíš?'"
        context.user_data["num_of_streets"] = 2
    else:
        text = "'Uhh...asi bych věděl...podle toho kam?'"
        context.user_data["num_of_streets"] = 1

    reply_keyboard = [[x.name_cz] for x in society.people_list]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    await update.message.reply_text(text, reply_markup=markup)
    return "look_for_person"


async def path_to_person(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Based on how much does NPC like player he hints him how to get to find the person"""
    town_map: Map = context.user_data["map"]
    society: Society = context.user_data["people"]
    current_chars: ModifiedPeople = context.user_data["current_people"]
    start_place_ID: int = context.user_data["player"].place_ID
    num_of_streets: int = context.user_data["num_of_streets"]
    final_place_ID: int = current_chars.get_NPC(
        society.name_cz_to_ID[update.message.text]).place_ID
    path = town_map.shortest_path(start_place_ID, final_place_ID)
    revealed_path = path[1:num_of_streets+1]

    if len(revealed_path) == 0:
        await update.message.reply_text("To jsem já ty blboune...")
    elif len(path)-2 > len(revealed_path):
        await update.message.reply_text("Jo tak to první bude " + " a pak".join([town_map.get_street_by_ID(x).name_cz for x in revealed_path]) + " a pak to už nějak najdeš")
    elif len(path)-2 <= len(revealed_path):
        await update.message.reply_text("Jo tak to první bude " + " a pak".join([town_map.get_street_by_ID(x).name_cz for x in revealed_path]) + ". No a jsi tam.")

    return await basic_window(update)


async def attack_on_person(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Function that takes care of fight between a player and NPC. 
    Successful attack knocks the NPC out whereas failed knocks out Player for 2 rounds
    """
    player: Player = context.user_data["player"]
    society: Society = context.user_data["people"]
    current_chars: ModifiedPeople = context.user_data["current_people"]
    defender_ID = context.user_data["char_ID"]
    defender = current_chars.get_NPC(defender_ID)

    current_characters, failed = handler.fight(
        player, defender, "stun", current_chars)

    context.user_data["current_people"] = current_characters
    if failed:
        await update.message.reply_text("Tak tohle se ti moc nepovedlo a bohužel na chvíli ztrácíš vědomí.")
        player.state = "stun"
        player.duration["stun"] = 2
        await rotation(update.message.chat.id, context)
    else:
        await update.message.reply_text(f"Úspěšně se ti podařilo omráčit postavu. {society.get_char_by_ID(defender_ID).name_cz} tu teď leží v mrákotách.")

    return await basic_window(update)


async def basic_window(update: Update, context=None) -> str:
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
                    filters.Regex("Začít"), start_new_game
                ),
                MessageHandler(
                    filters.Regex("Nezačínat"), read_old_game
                )
            ],
            "player_actions": [
                MessageHandler(
                    filters.Regex("Provést"), make_action
                ),
                MessageHandler(
                    filters.Regex("statistiky"), inspect_player
                ),
                MessageHandler(
                    filters.Regex("Jít"), move_character
                )
            ],
            "character_move": [
                MessageHandler(
                    filters.Regex("Zpět"), basic_window
                ),
                MessageHandler(
                    filters.TEXT, change_location
                )
            ],
            "person_to_talk": [
                MessageHandler(
                    filters.Regex("Zpět"), basic_window
                ),
                MessageHandler(
                    filters.TEXT, talk_to_person
                )
            ],
            "choose_action": [
                MessageHandler(
                    filters.Regex("Mluvit"), choose_person
                ),
                MessageHandler(
                    filters.Regex("Nakoupit"), open_shop
                )
            ],
            "buy_item": [
                MessageHandler(
                    filters.Regex("Zpět"), basic_window
                ),
                MessageHandler(
                    filters.TEXT, buy_item
                )
            ],
            "NPC_interaction": [
                MessageHandler(
                    filters.Regex("na cestu"), ask_for_path
                ),
                MessageHandler(
                    filters.Regex("na postavu") & ~(filters.Regex(
                        "Zaútoč")), ask_for_person
                ),
                MessageHandler(
                    filters.Regex("Zaútoč"), attack_on_person
                )

            ],
            "look_for_path": [
                MessageHandler(
                    filters.TEXT, find_path_to
                )
            ],
            "look_for_person": [
                MessageHandler(
                    filters.TEXT, path_to_person
                )
            ],
            "inspect_player": [
                MessageHandler(
                    filters.Regex("Inventář"), open_inventory
                ),
                MessageHandler(
                    filters.Regex("Úkoly"), open_quests
                ),
                MessageHandler(
                    filters.Regex("Zpět"), basic_window
                )
            ],
            "choose_item": [
                MessageHandler(
                    filters.TEXT, choose_item
                )
            ],
            "inspect_item": [
                MessageHandler(
                    filters.Regex("Použít"), use_item
                ),
                MessageHandler(
                    filters.Regex("Nasadit"), equip_item
                ),
                MessageHandler(
                    filters.Regex("Návrat"), inspect_player
                )
            ],
            "replace_item": [
                MessageHandler(
                    filters.Regex("Zpět"), open_inventory
                ),
                MessageHandler(
                    filters.TEXT, replace_item
                )
            ],
            "get_quest": [
                MessageHandler(
                    filters.Regex("Zpět"), inspect_player
                ),
                MessageHandler(
                    filters.TEXT, get_quest
                )
            ]

        },
        fallbacks=[CommandHandler("start", start)]
    )

    application.add_handler(conversation_handler)

    application.run_polling()


if __name__ == "__main__":

    main()
