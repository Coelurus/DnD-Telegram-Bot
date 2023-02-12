# DnD-Telegram-Bot

### Anotace
Problémem, který řeší můj program, je nuda. Jedná se totiž o hru, a to konkrétně o hru výpravnou inspirovanou textovými adventurami a Dračím doupětem. Uživatel, tudíž hráč, se ocitne ve městě zvaném Kritraven a musí se mu podařit schovat či uprchnout dříve, než ho dopadne hlídka. Hra je rozdělena na kola a v každém z nich musí hráč pečlivě volit svá rozhodnutí a uvážit své kroky. Hráč samozřejmě není ve městě sám, ba naopak může potkat několik NPC, se kterými může interagovat, a tak ovlivnit výsledek hry.

### Přesné zadání



## Statická data
### Mapa
Mapa Kritravenu, viz obrázek, sestává ze 40 navštívitelných míst. Jedná se tedy o graf, jehož vrcholy jsou ulice a hrana mezi ulicemi (či ulicí a místem) existuje právě tehdy, když se obě ulice protínají či sbíhají.
Seznam těchto míst se načítá ze souboru streets.csv. Pro každé jedinečné ID ulice je určeno jméno místa a též seznam indexů, jež jsou spojené s hranou s daným místem.

!["obrázek mapy"](zzz_other/map/kritraven-with-streets-n-places.png)

Veškerá data o mapě a všech místech na ní jsou uloženy v souboru `streets.csv`.
Každé místo v soubotu má momentálně své jedinečné ID, jméno v češtině, popis v češtině, seznam ID míst spojených s tímto místem, možnost speciálních akcí pro toto místo a omezení přístupu 

#### Reprezentace:
+ ID
    + integer - např. `3`
+ name_cz
    + string - např. `Perlová`
+ connected_ID
    + seznam integerů oddělených středníkem - např. `2;8;10;37`
+ description_cz
    + string - např. `Perlová ulice je navzdory svému názvu známá...`
+ possibilities
    + dva stringy odděleny dvojtečkou - např. `shop:food`
    + první je vždy typ (`shop` je zatím jediná taková implementace)
    + druhé je upřesnění (typy pro `shop` se odvozují z parametru `type` v tříde `Items`)
+ access
    + string - např. `free`
    + momentálně neimplementovaná vlastnost

#### Zpracování:
O zpracovávání těchto dat se stará knihovna `map.py`, která definuje třídu `Street`, do které se uklídají veškerá data zmíněná výše. Navíc je zde třída `Map`, která v sobě ukládá všechny objekty `Street` a poskytuje metody pro práci s nimi. Mezi ně patří metoda `BFS`, jejímž jediným argumentem je výchozí místo. Metoda provádí průchod do šířky grafem mapy a vrací seznam ulic a seznam vzdáleností ulic na stejném indexu od výchozí ulice. Druhou důležitou metodou je pak `find_shortest_path`, která bere jako argumenty tyto 2 seznamy a k tomu ještě cílové místo a vrací jednu z nejkratších cest z výchozího do cílového místa.

Za zmínku též stojí funkce `read_map_from_file`, která se stará o načtení dat ze souboru a jejich uložení do objektu třídy `Map`

Zbytek funkcí a metod je i s komentáři k naleznutí v `lib/map.py`

***

### Postavy
Ve hře je momentálně 36 různých postav. Každá z nich se pohybuje a koná akce samostatně a když je to potřeba, řídí se úkoly (více viz dále)
Seznam všech postav a údaje o nich nalezneme v souboru `characters.csv`. Každá z nich má svoje jedinečné ID, jméno v češtině, ID frakce, ke které náleží, ID ulice, kde se při začátku hry ocitnou, ID ulice, kam se uchýlí, když nemají nic na práci, jejich rychlost, síla a počet peněz.

#### Reprezentace
+ ID
    +  integer
    +  např. `1`
+ name_cz
    +  string
    +  např. `Strážník Poleno`
+ fraction_ID
    +  integer
    +  např. `0` 
+ spawn_street_ID
    +  např. `35` 
+ end_street_ID
    +  integer
    +  např. `14` 
+ speed
    +  integer
    +  např. `3` 
+ strength
    +  integer
    +  např. `1` 
+ coins
    +  integer
    +  např. `40`
    +  momentálně neiplementovaná vlastnost


#### Zpracování
O zpracování těchto dat se stará knihovna `character.py`. Ta definuje třídu `NPC` do jejíchž objektů se ukládají všechny data uvedená v reprezentaci. Dále je zde třída `Society`, která ukládá všechny objekty typu `NPC` a definuje metody pro práce s nimi.
Nachází se zde též funkce `read_people_from_file`, jež se stará o načtení všech postav, jejich reprezentaci jako `NPC` a jejich uložení do objektu třídy `Society`

### Frakce
Jak již bylo naznačeno v reprezentaci postav, tak jsou v této hře definovány i takzvané frakce. Seznam všech těchto frakcí je uložen v souboru `fractions.csv`, kde je pro každou z nich definováno jedinečné ID, jméno v češtině, ID místa jejich residence a vztahy s ostatními frakcemi.

#### Reprezentace
+ ID
    + integer - např. `0`
+ name_cz
    + string - např. `Hlídka`
+ residence_ID
    + integer - např. `35`
    + momentálně neimplementovaná vlastnost
    + nikam nepatřící postavy nemají residenci `-1`
+ relations
    + řetězec integerů oddělených středníkem - např. `3;1;1;0;2;3;-1`
    + význam hodnoty vztahů
      + ` 3 ` = nasadíme za vás svůj život
      + ` 2 ` = nevadíme si
      + ` 1 ` = klidně tě udám
      + ` 0 ` = zabiju tě tady a teď
      + `-1 ` = nedefinováno (když nemá smysl určovat)

#### Zpracování
O zpracování těchto dat se stará též knihovna `character.py`, která definuje třídu `Fraction`, do které se ukládají všechny vlastnosti vypsané výše. Jako vždy je definována třída `PoliticalMap`, která v sobě ukládá všechny frakce a definuje metody pro práce s nimi.
Pro načtení a zpracování všech frakcí je zde `read_fractions_from_file`, která zkonstruuje objekt třídy `PoliticalMap` se všemi frakcemi ve formě `Fraction`.

### Úkoly
Úkoly, ruka boží, která řídí chování všech postav v této hře. Pod pojmem úkol se zde rozumí spíše úkolová linie. Ta se dělí na části, které se nazývají fáze. Linie zde však není definována jako posloupnost fázi, ale jako binární strom. Jeden syn vždy reprezentuje úspěšné splnění fáze a druhý neúspěšné. Takto uložené linie jsou k nalezení v souboru `quest-lines.txt` v následujícím formátu:
1. Na prvním řádku je počet linií zde uložených
2. Dalé jsou data k jedné linii uloženy vždy ve dvou řádcích
   1. `ID linie + "=" + jméno v češtině` 
         - Např. `5=Lov na kočku`
   2. Strom fází reprezentován jako string
         - Více informací za chvíli

#### Reprezentace - Fáze úkolů
Každá fáze je reprezentována řetězcem jako posloupnost několika modifikátorů, jež jsou od sebe odděleny znakem rovná se. Např: `0=char12=36=0=37=none=40%-1`

##### Kódové označení fáze
Hned první modifikátor měl původně jasný význam, avšak s průběhem vývoje se ukázal být nepotřebný a nahradila ho kombinace jiných modifikátorů.
První modifikátor však našel jiné využití a to označení speciálních fází. Momentálně je definována pouze jedna speciální fáze, a to terminální fáze. Pokud se postavě podaří splnit takovou tu fázi, tak končí hra a hráč prohrává. Její kód je symbolicky `666`. 

##### Kdo
Zde můžou nastat 2 varianty:
+ Fáze je určena pro určitou postavu
    + `Modifikátor := “char“ + ID všech postav oddělené středníky`
+ Fáze je pro kohokoliv z určité frakce
    + `Modifikátor := “frac“ + ID určené frakce`
+ Momentálně nedotažená funkce. Tento způsob sice funguje, ale když mise probíhá a má ji zadaná určitá náhodná postava, tak může být v dalším kole přidělena jiné postavě, musí se tedy implementovat jakési sledování, že někdo danou fázi plní. Podobně se zadáním více určitých postav.

##### Odkud
+ Pokud je určené místo, kde musí fáze započít: 
    + `Modifikátor := ID místa`
+ Pokud místo určeno není: 
    + `Modifikátor := -1`

##### Předmět
Pro určité fáze může být potřeba, aby u sebe postava, která jej vykonává, měla nějaký předmět. Ten jí bude do inventáře přidělen až se dostane na místo, kde jeho fáze začíná a když fázi splní, tak bude zase odebrán.
+ Pokud by mělo nastat, že stejný předmět bude potřeba pro více fází za sebou, tak stejně bude po každé fázi odebrán a poté přidán zpět.
+ Pokud by měla postava o přidělený předmět během mise přijít, tak je to bráno jako neúspěch.
    + Tato funkce bohužel také ještě není implementována.
+ `Modifikátor := ID předmětu`
+ `Modifikátor := -1` (pokud není určen předmět)

##### Kam
+ Pokud je přesně definováno místo, pak: 
    + `Modifikátor := ID cílového místa`
+ Může však nastat situace, že výsledné místo není přesně známo anebo se průběžně mění. V tom případě bude:
    + `Modifikátor := “?“` a výsledné místo se určí dle typu fáze jiným modifikátorem.

##### Jdi za
+ Pokud není pevně určeno výsledné ID místa, je možné, že je zapotřebí, aby postava došla za nějakou jinou. V tom případě: 
    + `Modifikátor := ID hledané postavy + “;“ + parametr akce`
+ Pokud bude výsledné místo určeno jinak: 
    + `Modifikátor := “none“`
+ Když postava zastihne jinou, tak existuje několik možností, co bude dělat dál.
    + Zab – `parametr akce := “kill“`
    + Omrač – `parametr akce := “stun“`
    + Okraď – `parametr akce := “rob“`
    + Podstrč – `parametr akce := "plant"` 
    + Nic – `parametr akce := “none“`
    + Mluv – `parametr akce := „talk“`
        + Zatím bohužel není implementována
    + Přiveď – `parametr akce := “bring“`
        + Zatím bohužel též není implementována
+ Momentálně nedotažená mechanika. Jak postava ví, kde se nachází někdo jiný? Pokud hledaná postava někam půjde, tak pro ostatní bude velmi těžké ji zastihnout.

##### Odměna
Pokud postava úspěšně dokončí fázi, tak za to dostane odměnu. Forma může být formou peněz, předmětu či obojího najednou
Ta je definována:
+ `Modifikátor := počet peněz + "%" +  ID předmětu`
    + Pokud by neměly být za fázi předány žádné peníze, tak zde bude `počet peněz = 0`
    + Pokud by neměl být předán žádný předmět, tak bude `ID předmětu = -1`

#### Reprezentace stromu fází
Strom je reprezentován pomocí závorek, které vždy ohraničují syny. První syn je větev, který následuje po úspěšném splnění předchozí fáze, druhý reprezentuje neúspěch.
Pokud již  nemá být žádný další syn, neboli jeho hodnota je `None`, tak to bude zaznačeno prádznými závorkami `()`.
Např: `Fáze(Úspěch()())(Neúspěch()())`

#### Zpracování úkolů a fází
O načtení a zpracování úkolových dat se stará knihovna `quest.py`. Ta definuje tři zásadní třídy `ModifiedQuestPhase`, `Node` a `QuestLineTrees`.
- Instance třídy `ModifiedQuestPhase` ve svých atributech ukládá veškeré údaje o fázi, jak byly popsány výše. Je na ni též reprezentována funkce `__str__`, která ji převede zpět do textové reprezentace.
- Třída `Node` je poté základní páteří úkolových stromů. Každý `Node` má svou `value`, ve které je uložen seznam řetězcových vyjádření fází.
    - Pozn. `value` je definována jako seznam, protože původní idea byla, že by fáze mohla spustit více dalších podfází, avšak to bude vyžadovat komplexnější řešení úspěchu či selhání této skupiny a její vyhodnocení pro další syny. Proto, i když se jedná o seznam, tak program vždy bere pouze první fázi a ostatní prozatím ignoruje.
- Poslední je `QuestLineTrees`, které do slovníků ukládá indexy, jména a kořeny všech úkolových stromů.
Důležité funkce této knivny jsou pak `str_to_mqp` a `mqp_to_str`, které převádějí `string` na `ModifiedQuestPhase`.
Za povšimnutí též stojí funkce `create_tree_from_str`, která rekurzivním procházením tvoří ze `stringu` strom složený z `Nodes`. Funkce pracuje tak, že řetězec vždy rozdělí dle závorek na hodnotu svojí a další syny. Podívá se na syny a pokud nějaký z nich není `None`, tak se funkce zavolá rekurzivně na něj. To pokračuje tak dlouho, dokud nejsou oba synové `None`. Poté se `Nodes` vrací až se vytvoří celý strom.
Funkce `print_tree` je poté funkcí inverzní ke `create_tree_from_str` a tvoří `string` ze stromu. Jediný rozdíl je, že výsledek pouze vytiskne, funkce tak slouží hlavně na ladění programu.
Samozřejmě zde máme i funkci `read_quest_lines_from_file`, jež načte všechny úkolové stromy a uloží je do instance třídy `QuestLineTrees`




## Dynamicky generovaná data
Jelikož se jedná o hru, tak chceme, abychom se jak my, tak ostatní postavy, mohli nějakým způsobem pohybovat po mapě a interagovat s ostatními. Abychom toho ale docílili, tak musíme vědět, kdo v každou chvíli je, proto je potřeba soubor (game_saves.txt), do kterého se bude průběžně ukládat, co se ve světě hry děje.

Jelikož hru zprostředkovává bot na telegramu, tak by mohla nastat situace, kdy by hru chtělo hrát více uživatelů najednou. Pro každého z nich musí tedy existovat právě jedno uložení postupu. Který postup patří jakému uživateli se určí dle konkrétního ID chatu, které lze získat přes bota.
Data k jedné hře tedy budou vždy uloženy ve dvou řádcích. Na prvním bude ID chatu a na druhém řetězec znaků obsahující veškeré potřebné informace, viz dále, jehož segmenty od sebe budou odděleny znakem _ (podtržítko).

### Stav hráče
Stav hráče je definován řetězcem znaků složených z více částí, jež jsou odděleny “,“ (čárkou).
+ Místo, kde se hráč nachází := “place:“ + ID místa
+ Počet peněz, jenž má := “coins:“ + počet peněz
+ Předměty := “items:“ + ID předmětů oddělené středníky (např.: “items:1;3“)
+ Síla := “str:“ + číselná hodnota síly hráče
+ Rychlost := “speed:“ + hodnota rychlosti
+ Vztah ke frakcím := “relations:“ + hodnoty(definovány stejně jako ve Frakcích) pro každou frakci oddělené ; (středníky). Hodnoty jsou ve stejném pořadí jako indexy frakcí.
+ Při spuštění nové hry se nastaví výchozí pozice na index 0 (U opilého poníka), počet peněz na 25, hráč je bez předmětů, jeho síla i rychlost je 2 a vztah se všemi frakcemi je 2.


### Stavy úkolových linií
Stavy jednotlivých linií v řetězci jsou opět rozděleny “,“ (čárkami). Stavy linií jsou uloženy postupně dle rostoucích indexů. 

Jelikož je každý linie úkolů implementována jako binární strom, kdy jeden syn značí úspěch a druhý neúspěch, tak můžeme cestu do konkrétního uzlu stromu definovat jako posloupnost písmen F a S, kdy F znamená, že v daném bodě nastal neúspěch a máme se posunout na takového syna. Naopak S pak znamená úspěšné splnění mise. 

Pokud je řetězec prázdný, znamená to, že je aktivní stále první fáze, tedy kořen stromu. 
Naopak pokud linie dospěje svého konce, tak se řetězec přepíše na znak “E“, aby se již příště nemusel zbytečně procházet.


### Stavy postav
Stav každé z postav je v řetězci oddělen “+“ (plus) a jednotlivé části každého stavu “,“ (čárkou). Postavy jsou též řazeny dle indexu.

Podobně jako u stavu hráče bude pro každou postavu definováno místo, počet peněz, předměty, které má momentálně u sebe, síla a rychlost. Vztahy pro postavy určeny nejsou, neboť se definují dle jejich příslušnosti k frakcím.

Další důležitá vlastnost každé postavy je, jaký úkol zrovna plní, jež bude uloženo následovně:
+ Linie := “line:“ + ID úkolové linie, kterou plní
+ Fáze := “phase:“ + určená modifikovaná fáze, kterou právě plní, uložená ve stejném formátu, jako bylo definováno v Liniích úkolů pro fáze definované modifikátory.
K tomu se váži možné stavy, ve kterých se tyto fáze nachází. 
+ Stav fáze := “stage:“ + konkrétní stav (viz níže)
+ Rozlišujeme 3 různé stavy:
    + Fáze ještě nezačala = postava teprve musí dojít do výchozího místa (“tostart“)
    + Fáze právě probíhá = postava se musí dostavit na určené místo (“inprogress“)
    + Fáze právě skončila = postava se dostavila na určené místo a provede zadanou akci (“ended“)
        + Ta by prakticky neměla nikdy nastat, neboť se rovnou vyhodnotí konec fáze a pokračuje se s druhou
+ Pokud postava žádný úkol neplní, tak bude za všemi klíčovými slovy a dvojtečkou -1 (úkolová část postavy pak bude vypadat následovně: “line:-1,phase:-1,stage:-1“)

Další podstatnou vlastní každé postavy je, jaký je jeho zdravotní stav: “state:“ + konkrétní stav
+ Postava je plně při vědomí = “alive“
+ Postava je omráčená, ale žije = “stun“
+ Postava je mrtvá = “dead“

### Rotace
1.	Načtení z game save souboru
2.	Zjištění hráčova stavu + výpis na GUI
3.	Zadání akcí uživatelem
4.	Reakce na dané akce
5.	Zjištění dat o postavách
6.	Kontrola, zda někdo z nich splnil úkol
7.	Aktualizace stavu průběhu úkolů na základě dat od postav
8.	Průchod nových dat úkolů 
9.	Přiřazení fází postavám
10.	Pohyb postav
11.	Akce postav
12.	Uložení stavu hráče a postav
