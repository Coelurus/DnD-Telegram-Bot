# DnD-Telegram-Bot

## Jak hru spustit?
Je to velice jednoduché!
1. Jelikož se jedná o `bota` na Telegramu, tak si budete muset založit účet na Telegramu.
2. Najděte si na Telegramu uživatele `@dnd_zapocet_bot` (https://t.me/dnd_zapocet_bot)
3. Napište první zprávu ve tvaru `/start`
4. Užijte si to!
   
- Pokud se stane, že bot najednou nereaguje, zkuste zadat `/start`. Je možné, že se ve vaší nepřítomnosti restartoval.

## Jak sám spustit bota?
1. Opět na to budete potřebovat Telegram.
2. Napište uživateli `@BotFather` (https://t.me/BotFather)
3. Nechte si vytvořit `bota`.
4. Zkopírujte si jeho `HTTP API`.
5. Najděte ve složce `data` soubor `token.txt` a vložte do něj token.
6. Dále budete potřebovat Python, pokud ho nemáte, stáhněte zde: https://www.python.org/downloads/
7. Otevřete příkazovou řádku a napište:
   `pip install python-telegram-bot --upgrade`
8. Pokud vám příkazová řádka hlásí, že nemáte pip, naistaujte si ho, dle postupu zde: https://pypi.org/project/pip/
   - Znovu napište `pip install python-telegram-bot --upgrade`
9. Stáhněte si kód z githubu
10. Dekomprimujte složku
11. V příkazové řádce si otevřete dekomprimovanou složku `DnD-Telegram-Bot-master`, ve které jsou přímo všechny další složky jako `data` a `lib`.
12. Zadejte `python lib\main.py`, čímž spustíte program.
13. Váš `bot` teď běží a můžete se řídit postupem v `Jak hru spustit?` Jediný rozdíl bude, že musíte napsat svému botovi, kterého jste si vytvořili.
14. `Bot` bude reagovat a odpovídat na vaše zprávy, dokud budete mít zaplý program. Pokud ho ukončíte, přestane vám v chatu odpovídat.
15. Pokud chcete `bota` ukončit stiskněte Ctrl-C

***

## Vlastní dokumentace

### Anotace
Problémem, který řeší můj program, je nuda. Jedná se totiž o hru, a to konkrétně o hru výpravnou inspirovanou textovými adventurami a Dračím doupětem. Uživatel, tudíž hráč, se ocitne ve městě zvaném Kritraven a musí se mu podařit schovat či uprchnout dříve, než ho dopadne hlídka. Hra je rozdělena na kola a v každém z nich musí hráč pečlivě volit svá rozhodnutí a uvážit své kroky. Hráč samozřejmě není ve městě sám, ba naopak může potkat několik NPC, se kterými může interagovat, a tak ovlivnit výsledek hry.

### Přesné zadání
Zimní semestr: Cílem programu je vytvořit hru, kterou bude zprostředkovávat bot na Telegramu. Hra je inspirovaná jak Dračím doupětem, tak textovými adventurami. Hlavní myšlenkou je, že je zde minimum naskriptovaných věcí. Hráč sám se ocitne ve městě, kde je několik dalších postav, kterým sice někdo zadal, co mají dělat. Ale co když jim v tom někdo zabrání? V tom případě budou muset podniknout něco jiného? Co když postava uvidí, jak někdo útočí na jeho kamaráda. No pomůžeme, ale co když při tom náhodou zemře, její vlastní povinnosti pak už nikdo nesplní.

Letní semestr: Cílem mé práce je refaktorovat a zlepšit kvalitu stávajícího programu. Jednak se jedná o zlepšení způsobů ukládání, používání funkcí a tříd a jednak o přčehlednější výstup pro hráče.

## Průběh hry a herní rozhraní

O řízení hry i herního rozhraní se stará soubor `main.py`. Už jen kvůli množství různých funkcí není v mých silách všechny je zde vypsat, zmíním tak jen ty nejdůležitější, jelikož zbytek je stejně okomontován přímo v kódu.

### Průběh hry

Stejně jako `Dračí Doupě`, tato hra funguje na kola. Začíná hráč. Každé kolo je ukončeno hráčovým pohybem na jiné místo. Avšak během svého kola může udělat kolik akcí jen chce. Může si měnit předměty, nakupovat, pokud zrocna stojí u obchodu, bavit se s postavami, pokud tam jsou, nebo s nimi bojovat. Avšak, když se hráč pohne, tak jsou na řadě postavy.
To, co se poté děje, a jak se to děje, řídí hlavně funkce `rotation`. Ta si nejdříve načte všechna aktuální data o postavách a průběhu úkolů. Zkontroluje, zda nějaká postava nesplnila nějaký úkol, aktualizuje postupy a přiřadí nové fáze ostatním.


```python
async def rotation(chat_ID: int, context: ContextTypes.DEFAULT_TYPE, update: Update) -> None:
    """Function take care of handling movement of NPC, making them follow missions etc.
    It also updates questlines progresses and assign phases to NPCs based on it"""

    # Getting current data that are potentially changed by player inputs from last time
    current_characters: ModifiedPeople = context.user_data["current_people"]
    current_quests_list: list[str] = context.user_data["current_quests_list"]

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
    current_characters_json = save.move_characters(current_characters).to_json()

    # Updates progress and gets list of quests completable in this place.
    quests_to_finish = context.user_data['player'].update_quest_progresses(current_characters)
    context.user_data["additional_actions"] = quests_to_finish
    if len(quests_to_finish) > 0:
        await update.message.reply_text("\u2757 Máš zde úkol \u2757")

    json_dict_player = save.player_save_generator(context.user_data['player'])

    context.user_data["current_quests_list"] = new_quests

    json_dict_save = dict()
    json_dict_save["player"] = json_dict_player
    json_dict_save["quests"] = new_quests
    json_dict_save["characters"] = current_characters_json

    save.rewrite_save_file(chat_ID, json_dict_save)

    # When player is not capable of moving proceed to next round and move characters again
    if context.user_data['player'].state == "stun":
        context.user_data['player'].round += 1

        # Show round counter last round before ending stun
        if context.user_data['player'].get_stun_duration() == 1:
            await update.message.reply_text(f"\u2728 *{context.user_data['player'].round}*\. kolo \u2728", parse_mode="MarkdownV2")

        await rotation(chat_ID, context, update)

```

Ve zdrojovém kódu si můžete povšimnout, že využívá metod a funkcí z ostatních knihoven. Více o nich v README.md ve složce lib.
Když doběhne funkce `rotation`, tak je opět na řadě hráč.


### Herní rozhraní 

Zaměřili jsme se na vše, co se děje v pozadí a teď se pojďme zaměřit na to, jak může hráč ovládat svou postavu.
Nejprve je nutno zmínit, že mimo všechny mou napsané knihovny, jež jsem zde zmiňoval, hra též používá externí knihovnu `python-telegram-bot`.
Vše začíná funkcí `main` z `main.py`
První se pomocí tokenu program spojí s botem na telegramu, a tak může komunikovat přes Telegram místo konzole.
Dalším krokem je vytvoření objektu `ConversationHadler`. Díky tomuto je vytvořena komunikace mezi hráčem a programem.
Ve výsledku to funguje tak, že program dá hráči vždy na výběr z několik možností a v závislosti na tom, jakou možnost hráč vybere, se zavolá nějaká funkce. V tom spočívá krása zmiňovaného `ConversationHandleru`, neboť řeší hráčovy vstupy v různých situacích.
Zmíním zde alespoň jednu funkci, a to `start`.

```python
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

```
Podobně vypadá většina dialogových oken generovaných v tomto souboru.
1. `reply_keyboard` ukládá po řádcích možnosti, které pak bude mít hráč na výběr.
2. Poté se zavolá konstruktor třídy `ReplyKeyboardMarkup`, aby se vytvořila tato klávesnice.
3. Pošle se zpráva s přiloženou klávesnicí.
4. Návratová hodnota se přiřadí na hodnotu, kterou poté zpracuje `ConversationHandler`

```python
conversation_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            "starting_new_game": [
                MessageHandler(
                    filters.Regex("Začít"), start_new_game
                ),
                MessageHandler(
                    filters.Regex("Nezačínat"), read_old_game
                ),
                MessageHandler(
                    filters.Regex("Ukončit"), end_game
                )
            ]

        },
        fallbacks=[CommandHandler("start", start)]
    )

```
5. Funkce `start` nám ve skutečnosti vrací stav `"starting_new_game"`.
6. V závislosti na tom, jaká zpráva byla poslána, se zavolá určitá funkce.


## Závěrem
Zimní semestr: Určitě je toho spousta, co jsem nestihl dokončit. Moje plány byly velké. Už jen z komentářů a všemožných TODO je vidět, kde všude by to ještě chtělo vylepšit. Na druhou stranu si myslím, že aktuální stav pěkně ilustruje, že herní svět nefunguje zas tak špatně. Momentální největší slabinu vidím v tom, že hráč nemůže dostat úkoly od postav ve městě a také to, že když hráč někomu nastražuje předmět, tak mu odevzdá všechno co má u sebe. Interakce s postavami by také mohly být trošku lepší, aby nebyly tak holé a stejné.
Na druhou stranu si říkám, že tvoření této malé hříčky mě velmi bavilo a pokusím se ji dále vylepšovat.

Letní semestr: Budu se opakovat, když začnu tím, že jsem toho opět nestihl. Nejvíc mě asi mrzí ty věci, které jsem neměl už napoprvé a ani teď jsem je nedokázal naimplementovat.
Na druhou stranu jsem strávil spoustu času na refactoringu, a to hlavně způsobu ukládání dat, které bylo v první verzi příšerné, ale teď je již mnnohem přehlednější. Navíc bylo opravdu obtížné vrátit se po tak dlouhé době k mému kódu a navíc vidět všechny ty věci, co jsem tehdy udělal špatně. A to všechno korunoval fakt, že Python sice je jazyk jednoduchý, avšak zjišťovat chyby až při běhu je pro stavovou hru nepříjemné, neboť se tam člověk musí vždy proklikat, aby si ověřil, že vše funguje.
Na druhou stranu jsem rád, že jsem se mohl kje hře takkto vrátit, i když mě stále mrzí, že je velmi holá a nezábavná.