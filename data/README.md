# Ukládání dat

## Statická data
### Mapa
Mapa Kritravenu, viz obrázek, sestává ze 40 navštívitelných míst. Jedná se tedy o graf, jehož vrcholy jsou ulice a hrana mezi ulicemi (èi ulicí a místem) existuje právì tehdy, když se obì ulice protínají èi sbíhají.
Seznam tìchto míst se naèítá ze souboru streets.csv. Pro každé jedineèné ID ulice je urèeno jméno místa a též seznam indexù, jež jsou spojené s hranou s daným místem.

!["obrázek mapy"](zzz_other/map/kritraven-with-streets-n-places.png)

Veškerá data o mapì a všech místech na ní jsou uloženy v souboru `streets.csv`.
Každé místo v souboru má momentálnì své jedineèné ID, jméno v èeštinì, popis v èeštinì, seznam ID míst spojených s tímto místem, možnost speciálních akcí pro toto místo a omezení pøístupu 

#### Reprezentace:
+ ID
    + `integer` - napø. `3`
+ name_cz
    + `string` - napø. `Perlová`
+ connected_ID
    + `seznam integerù oddìlených ";"` - napø. `2;8;10;37`
+ description_cz
    + `string` - napø. `Perlová ulice je navzdory svému názvu známá...`
+ access
    + `string` - napø. `free`
    + stále neimplementovaná vlastnost


### Postavy
Ve høe je momentálnì 36 rùzných postav. Každá z nich se pohybuje a koná akce samostatnì a když je to potøeba, øídí se úkoly (více viz dále)
Seznam všech postav a údaje o nich nalezneme v souboru `characters.csv`. Každá z nich má svoje jedineèné ID, jméno v èeštinì, ID frakce, ke které náleží, ID ulice, kde se pøi zaèátku hry ocitnou, ID ulice, kam se uchýlí, když nemají nic na práci, jejich rychlost, síla a poèet penìz.

#### Reprezentace
+ ID
    +  `integer` - napø. `1`
+ name_cz
    +  `string` - napø. `Strážník Poleno`
+ fraction_ID
    +  `integer` - napø. `0` 
+ spawn_street_ID 
    +  `integer` - napø. `35` 
+ end_street_ID
    +  `integer` - napø. `14` 
+ speed
    +  `integer` - napø. `3` 
+ strength
    +  `integer` - napø. `1` 
+ coins
    +  `integer`- napø. `40`
    +  momentálnì neiplementovaná vlastnost


### Frakce
Jak již bylo naznaèeno v reprezentaci postav, tak jsou v této høe definovány i takzvané frakce. Seznam všech tìchto frakcí je uložen v souboru `fractions.csv`, kde je pro každou z nich definováno jedineèné ID, jméno v èeštinì, ID místa jejich residence a vztahy s ostatními frakcemi.

#### Reprezentace
+ ID
    + integer - napø. `0`
+ name_cz
    + string - napø. `Hlídka`
+ residence_ID
    + integer - napø. `35`
    + momentálnì neimplementovaná vlastnost
    + nikam nepatøící postavy nemají residenci `-1`
+ relations
    + øetìzec integerù oddìlených støedníkem - napø. `3;1;1;0;2;3;-1`
    + význam hodnoty vztahù
      + `3`  = nasadíme za vás svùj život
      + `2`  = nevadíme si
      + `1`  = klidnì tì udám
      + `0`  = zabiju tì tady a teï
      + `-1` = nedefinováno (když nemá smysl urèovat)


### Úkoly
Úkoly, ruka boží, která øídí chování všech postav v této høe. Pod pojmem úkol se zde rozumí spíše úkolová linie. Ta se dìlí na èásti, které se nazývají fáze. Linie zde však není definována jako posloupnost fázi, ale jako binární strom. Jeden syn vždy reprezentuje úspìšné splnìní fáze a druhý neúspìšné. Takto uložené linie jsou k nalezení v souboru `quest-lines.json` ve formátu JSON.
1. Úkoly jsou uloženy jako slovníky.
2. Všechny slovníky jsou sežazeny v poli v souboru `quest-lines.json`.
3. Každý úkol má 2 klíèe: `name` a `root_quest`, které mají jako hodnoty název úkolu a základní fázi

### Fáze úkolù
Každá fáze je uložena ve slovníku, který má následující klíèe:
`"ID"`, `"char"`, `"from"`, `"item"`, `"reward"`, `"coin_reward"`, `"item_reward"`, `"to_place"`, `"action"`, `"go_to"`, `"on_success"`

#### Vysvìtlení hodnot uložených pod klíèi

##### ID fáze
Pro vìtšinu úkolù je nicneøíkající, avšak mùže urèit, že se jedná o terminální fázi, která ukonèí hru.
Pokud se postavì podaøí splnit takovou tu fázi, tak konèí hra a hráè prohrává. Její kód je symbolicky `666`. 
+ Klíè: `"ID"`
+ Hodnota: `ID`

##### Kdo
+ Klíè: `char`
+ ID postavy, která úkol provádí 
+ v pøípadì úkolu zadaného hráèi, se jedná o postavu, která úkol zadala

##### Odkud
+ Klíè: `"from"`
+ Pokud je urèené místo, kde musí fáze zapoèít: 
    + `ID místa`
+ Pokud místo urèeno není: 
    + `-1`
  
##### Pøedmìt
Pro urèité fáze mùže být potøeba, aby u sebe postava, která jej vykonává, mìla nìjaký pøedmìt. Ten jí bude do inventáøe pøidìlen až se dostane na místo, kde jeho fáze zaèíná a když fázi splní, tak bude zase odebrán.
+ Pokud by mìlo nastat, že stejný pøedmìt bude potøeba pro více fází za sebou, tak stejnì bude po každé fázi odebrán a poté pøidán zpìt.
+ Pokud by mìla postava o pøidìlený pøedmìt bìhem mise pøijít, tak je to bráno jako neúspìch.

+ Klíè: `"item"`
+ Hodnota: `ID pøedmìtu` nebo `-1` (pokud není urèen pøedmìt)

##### Kam
+ Klíè: `"to_place"`
+ Pokud je pøesnì definováno místo, pak: 
    + `ID cílového místa`
+ Mùže však nastat situace, že výsledné místo není pøesnì známo anebo se prùbìžnì mìní. V tom pøípadì bude:
    + `“?“` a výsledné místo se urèí dle typu fáze jiným modifikátorem.

##### Jdi za
+ Pokud není pevnì urèeno výsledné ID místa, je možné, že je zapotøebí, aby postava došla za nìjakou jinou. V tom pøípadì: 
+ Klíè: `"go_to"`
+ Hodnota: `ID hledané postavy`
+ Pokud bude výsledné místo urèeno jinak: 
    + `“none“`

##### Akce
+ Když postava zastihne jinou, tak existuje nìkolik možností, co bude dìlat dál.
+ Klíè: `"action"`
+ Hodnota:
    + Zab – `“kill“`
    + Omraè – `“stun“`
    + Okraï – `“rob“`
    + Podstrè – `"plant"` 
    + Nic – `“none“`

+ Lehce nedotažená mechanika. Jak postava ví, kde se nachází nìkdo jiný? Pokud hledaná postava nìkam pùjde, tak pro ostatní bude velmi tìžké ji zastihnout.

##### Odmìna
Pokud postava úspìšnì dokonèí fázi, tak za to dostane odmìnu. Forma mùže být formou penìz, pøedmìtu èi obojího najednou
Jsou definovány:
+ Klíè: `"coin_reward"`
+ Hodnota: `poèet penìz`

+ Klíè: `"item_reward"`
+ Hodnota: `ID pøedmìtu`
+ + Pokud by nemìl být pøedán žádný pøedmìt, tak bude `-1`

#### Reprezentace stromu fází
Na urèení fáze, která bude následovat po skonèení aktuální jsou zde 2 klíèe: `"on_success"` a `"on_fail"`.
Hodnota zde uložená je pole slovníkù následných fází.



## Dynamicky generovaná data
Jelikož se jedná o hru, tak chceme, abychom se jak my, tak ostatní postavy, mohli nìjakým zpùsobem pohybovat po mapì a interagovat s ostatními. Abychom toho ale docílili, tak musíme vìdìt, kdo v každou chvíli je. Z tohoto dùvodu existuje soubor `game_saves.json`, ve kterém je uložen aktuální stav jak hráèe, tak všech postav, a i progres úkolových linií.

Jelikož hru zprostøedkovává bot na telegramu, tak by mohla nastat situace, kdy by hru chtìlo hrát více uživatelù najednou. Pro každého z nich musí tedy existovat právì jedno uložení postupu. Který postup patøí jakému uživateli se urèí dle konkrétního ID chatu, které lze získat pøes bota.
Data všech her se ukládají ve zmínìném souboru v `JSON` formátu. Jedná se o slovník, kde jsou klíèe ID chatu (tzn. hry) a hodnota je slovník s daty.

O programové zpracování všech tìchto dat se stará knihovna `save.py` jež využívá i nìkteré další knihovny (viz dále).
Nutno je zmínit funkci `read_current_save`, která na základì ID chatu vrátí slovník se všemi uloženými daty potøebnými k naètení stavu hry.

### Stav hráèe
Je uložen pod klíèem `"player"`, jehož hodnota je další slovník, který má všechny informace o stavu hráèe.
Jmenovitì to jsou: `"place"`, `"coins"`, `"items"`, `"str"`, `"speed"`, `"relations"`, `"fraction"`, `"state"`, `"duration"`, `"weapons"`, `"quests"` , `"progress"` a `"round"`
Vìtšina z nich vrací `int` a jsou pochopitelné.
Jediné výjimky jsou:
 + `"itemes"` - `pole intù` ID pøedmìtù, jež má hráè u sebe
 + `"relations"` - `pole intù` vztahù hráèe s frakcemi
 + `"state"` - `string` stavu hráèe (`"alive"`, `"stun"`, `"dead"`)
 + `"duration"` - `pole slovníkù` pomíjivých stavù ovlivòujících hráèe
 + `"weapons"` - `pole intù` ID zbraní, jež má hráè vybavené
 + `"quests"` - `pole slovníkù` fází úkolù (ve stejném formátu jako výše), které má hráè momentálnì aktivní 
 + `"progress"` - `pole stringù` popisujících prùbìch hráèových fází úkolù
    + Rozlišujeme 3 rùzné stavy:
        + Fáze ještì nezaèala = postava teprve musí dojít do výchozího místa `“tostart“`
        + Fáze právì probíhá = postava se musí dostavit na urèené místo `“inprogress“`
        + Fáze právì skonèila = postava se dostavila na urèené místo a provede zadanou akci `“ended“`

### Stav questových linií
Je uložen pod klíèem `"quests"` a ukládá pole `stringù`, které monitorují prùbìh úkolových linií.
Jelikož je každý linie úkolù implementována jako binární strom, kdy jeden syn znaèí úspìch a druhý neúspìch, tak mùžeme cestu do konkrétního uzlu stromu definovat jako posloupnost písmen `"F"` a `"S"`, kdy `"F"` znamená, že v daném bodì nastal neúspìch a máme se posunout na takového syna. Naopak `"S"` pak znamená úspìšné splnìní mise. 

Pokud je øetìzec prázdný, znamená to, že je aktivní stále první fáze, tedy koøen stromu. 

### Stav postav
Je uložen pod klíèem `"characters"`, jehož hodnota je pole slovníkù a každý z nich odpovídá a ukládá data o jedné postavì ve høe.
Každá postava má uloženo následující:
 + `"place"` - `int` - ID místa, kde právì stojí
 + `"coins"` - `int` - poèet penìz, co má u sebe
 + `"items"` - `list intù` - ID pøedmìtù, co má postava u sebe
 + `"str"` - `int` - síla postavy
 + `"speed"` - `int` - rychlost postavy
 + `"line"` - `int` - ID úkolové linie, kterou právì postava plní (`-1` pokud nemá žádný úkol)
 + `"phase"` - `dict` - fáze úkolu (viz výše)
 + `"stage"` - `string` - prùbìh úkolu
 + `"state"` - `string` - stav postavy (stejné jako u hráèe)
 + `"duration"` - `int` - pro odpoèítání doby, po kterou bude postava omráèena
 + `"player_relation"` - `int` - osobní vztah postavy k hráèi



















