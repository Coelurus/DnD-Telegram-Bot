# Knihovny pro spuštìní

## Mapa a ulice
O zpracovávání tìchto dat se stará knihovna `map.py`, která definuje tøídu `Street`, do které se ukládají veškerá data zmínìná výše. Navíc je zde tøída `Map`, která v sobì ukládá všechny objekty `Street` a poskytuje metody pro práci s nimi. Mezi nì patøí metoda `BFS`, jejímž jediným argumentem je výchozí místo. Metoda provádí prùchod do šíøky grafem mapy a vrací seznam ulic a seznam vzdáleností ulic na stejném indexu od výchozí ulice. Druhou dùležitou metodou je pak `find_shortest_path`, která bere jako argumenty tyto 2 seznamy a k tomu ještì cílové místo a vrací jednu z nejkratších cest z výchozího do cílového místa.

Za zmínku též stojí funkce `read_map_from_file`, která se stará o naètení dat ze souboru a jejich uložení do objektu tøídy `Map`

Zbytek funkcí a metod je i s komentáøi k naleznutí v `lib/map.py`

***

## Postavy
O zpracování dat týkajících se postav se stará knihovna `character.py`. Ta definuje tøídu `NPC` do jejíchž objektù se ukládají všechny data uvedená v reprezentaci. Dále je zde tøída `Society`, která ukládá všechny objekty typu `NPC` a definuje metody pro práce s nimi.
Nachází se zde též funkce `read_people_from_file`, jež se stará o naètení všech postav, jejich reprezentaci jako `NPC` a jejich uložení do objektu tøídy `Society`

***

## Frakce
O zpracování dat ohlednì frakcí se stará též knihovna `character.py`, která definuje tøídu `Fraction`, do které se ukládají všechny vlastnosti vypsané výše. Jako vždy je definována tøída `PoliticalMap`, která v sobì ukládá všechny frakce a definuje metody pro práce s nimi.
Pro naètení a zpracování všech frakcí je zde `read_fractions_from_file`, která zkonstruuje objekt tøídy `PoliticalMap` se všemi frakcemi ve formì `Fraction`.

***

## Úkoly a fáze
O naètení a zpracování úkolových dat se stará knihovna `quest.py`. Ta definuje tøi zásadní tøídy `ModifiedQuestPhase`, `Node` a `QuestLineTrees`.
- Instance tøídy `ModifiedQuestPhase` ve svých atributech ukládá veškeré údaje o fázi, jak byly popsány výše. Je na ni též reprezentována funkce `__str__`, která ji pøevede zpìt do textové reprezentace.
- Tøída `Node` je poté základní páteøí úkolových stromù. Každý `Node` má svou `value`, ve které je uložen seznam øetìzcových vyjádøení fází.
    - Pozn. `value` je definována jako seznam, protože pùvodní idea byla, že by fáze mohla spustit více dalších podfází, avšak to bude vyžadovat komplexnìjší øešení úspìchu èi selhání této skupiny a její vyhodnocení pro další syny. Proto, i když se jedná o seznam, tak program vždy bere pouze první fázi a ostatní prozatím ignoruje.
- Poslední je `QuestLineTrees`, které do slovníkù ukládá indexy, jména a koøeny všech úkolových stromù.
Dùležité funkce této knivny jsou pak `dict_to_mqp` a `mqp_to_dict`, které pøevádìjí `dict` s úkolem na `ModifiedQuestPhase`.
Samozøejmì zde máme i funkci `read_quest_lines_from_file`, jež naète všechny úkolové stromy a uloží je do instance tøídy `QuestLineTrees`

## Hráè
Na uložení všech dat ohlednì hráèe je v knihovnì `player.py` definována tøída `Player`. Pro tuto tøídu je zde poté definováno plno metod (jako napøíklad pohyb, používání pøedmìtù), díky kterým mùže hráè hru hrát. Než je tady všechny vypisovat, tak doporuèím podívat se do `player.py`.
V knihovnì `save.py` jsou poté funkce, jež zpracují vstupní save data a vytvoøí z nich instanci objektu `Player`. Na tuto specifickou akci je zde funkce `get_current_player`. 
Opaènou funkci plní funkce `player_save_generator`, která objekt `Player` pøetvoøí na `dict`, který se pak uloží do `JSON` souboru.

## Úkoly
Pro operování s daty o prùbìhu úkolù opìt použijeme knihovnu `save.py`. Je zde pro to nìkolik funkcí, ale za zmínku stojí hlavnì `get_current_quests`, která dle øetìzcù progresu složených z `"F"` a `"S"` prochází úkolové stromy, a nakonec vrátí aktuální fázi, jež probíhá. Další funkce je `assign_quests`, která prochází aktuální fáze získané pøedchozí fází a pøiøazuje je postavám, které je pak budou vykonávat.

## Stavy postav
Je pravda, že i zde se využije pár funkcí ze `save.py`, ale hlavní podpora pro práci s tìmito daty se nachází v knihovnì `character_handler.py`. Zde jsou definovány dvì tøídy. První z nich je `ModifiedNPC`, do kterého se každé kolo ukládají všechny stavová data postavy naètené ze save file. Pro pøístup ke všem `ModifiedNPC` je zde tøída `ModifiedPeople`, která i definuje metody pro pøijemnìjší práci s nimi.
Mimo tøídy je nutno zmínit funkci `get_current_characters`, která se stará o naètení aktuálních dat všech postav. Pak se zde nachází spousta dalších funkcí na práci s postavami, jako napøíklad jejich pohyb, souboj a podobnì. Vše je podrobnì okomentováno v samotném `character_handler.py`.
