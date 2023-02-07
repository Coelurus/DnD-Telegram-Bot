# DnD-Telegram-Bot
Still WIP but my deadline is kinda on the 12th of february so RIP i guess or idk
Made by Filip Vopálenský

### Anotace
Problémem, který řeší můj program, je nuda. Jedná se totiž o hru, a to konkrétně o hru výpravnou inspirovanou textovými adventurami a Dračím doupětem. Uživatel, tudíž hráč, se ocitne ve městě zvaném Kritraven a musí se mu podařit schovat či uprchnout dříve, než ho dopadne hlídka. Hra je rozdělena na kola a v každém z nich musí hráč pečlivě volit svá rozhodnutí a uvážit své kroky. Hráč samozřejmě není ve městě sám, ba naopak může potkat několik NPC, se kterými může interagovat, a tak ovlivnit výsledek hry.

### Přesné zadání



## Načítaná data ze souborů
### Mapa
Mapa Kritravenu, viz obrázek, sestává ze 40 navštívitelných míst. Jedná se tedy o graf, jehož vrcholy jsou ulice a hrana mezi ulicemi (či ulicí a místem) existuje právě tehdy, když se obě ulice protínají či sbíhají.
Seznam těchto míst se načítá ze souboru streets.csv. Pro každé jedinečné ID ulice je určeno jméno místa a též seznam indexů, jež jsou spojené s hranou s daným místem


### Postavy
Seznam všech postav a údaje o nich nalezneme v souboru characters.csv. Každá z nich má svoje jedinečné ID, jméno v češtině, seznam ID úkolů, které musí splnit, ID ulice ve které začíná a ID ulice či místa kam půjde, pokud vše splní. Pokud bude v end_street_ID hodnota -1, znamená to, že postava se bude dále volně a náhodně pohybovat po městě. Dále je pro každou postavu určena její rychlost, síla a počet peněz, jež má u sebe a index frakce, do které patří.


### Frakce
Další nezanedbatelnou charakteristikou každé postavy je frakce, pro kterou pracuje. Seznam všech lze nalézt v souboru fractions.csv. Mimo ID a jména v češtině zde můžeme nalézt i vztahy mezi frakcemi a ID místa jejich základny.
Ohodnocení vztahů: 3 = nasadíme za vás svůj život, 2 = nevadíme si, 1 = klidně tě udám, 0 = zabiju tě tady a teď, -1 = nedefinováno (když nemá smysl určovat).
Výjimky: nikam nepatřící postavy nemají residenci (ID = -1)


### Úkoly
Seznam všech úkolů a jejich všemožné podrobnosti jsou uloženy v souborech quests-lines.txt a quest-phases. Řekl bych, že se jedná o nejkomplexnější vstupní data ze všech. Lze zde totiž určit mnoho modifikátorů, které přesně určí, jak mají jaké úkoly (a jejich fáze) probíhat a jak se mají postavy tento úkol plnící chovat.

#### Fáze úkolů
Každý, jakkoliv komplikovaně dosažitelný cíl se dá rozložit na posloupnost několika fází. A když postupně tyto fáze splníme, dosáhneme určitého vyššího cíle.

#### Linie úkolů
Když dáme dohromady více fází vzejde nám schéma nějakého většího plánu. Avšak každá fáze může mít výsledek buď pozitivní či negativní. Řekněme, že poslíček dostane předmět, aby ho doručil na určené místo. Pokud tak udělá, dostane výměnou za to jiný předmět, který má donést zpět. Pokud by mu však něco zabránilo v doručení tohoto balíčku, tak rozhodně nedostane nový balíček, ale nejspíš i někdo začne řešit, kam se balíček či poslíček poděl.
Linie úkolů jsou tedy implementovány jako stromy, kdy každý prvek má dva syny, z nichž jeden zastupuje další krok v případě úspěšného provedení fáze a druhý zastupuje následující krok při neúspěchu jeho rodiče.
Mějme tedy strom, jehož každý vrchol sestává z fáze úkolu, ke které je přidruženo několik modifikátorů, které specifikují například kdo, co a jak má provést danou fázi.

##### Modifikátory
Všechny modifikátory jsou reprezentovány řetězcem znaků. 
+ Zde můžou nastat 2 varianty:
    + Fáze je určena pro určitou postavu
        + Modifikátor := “char“ + ID všech postav oddělené středníky
    + Fáze je pro kohokoliv z určité frakce
    	+ Modifikátor := “frac“ + ID určené frakce
    + Momentálně nedotažená funkce. Tento způsob sice funguje, ale když mise probíhá a má ji zadaná určitá náhodná postava, tak může být v dalším kole přidělena jiné postavě, musí se tedy implementovat jakési sledování, že někdo danou fázi plní. Podobně se zadáním více určitých postav.
