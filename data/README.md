# Ukl�d�n� dat

## Statick� data
### Mapa
Mapa Kritravenu, viz obr�zek, sest�v� ze 40 nav�t�viteln�ch m�st. Jedn� se tedy o graf, jeho� vrcholy jsou ulice a hrana mezi ulicemi (�i ulic� a m�stem) existuje pr�v� tehdy, kdy� se ob� ulice prot�naj� �i sb�haj�.
Seznam t�chto m�st se na��t� ze souboru streets.csv. Pro ka�d� jedine�n� ID ulice je ur�eno jm�no m�sta a t� seznam index�, je� jsou spojen� s hranou s dan�m m�stem.

!["obr�zek mapy"](zzz_other/map/kritraven-with-streets-n-places.png)

Ve�ker� data o map� a v�ech m�stech na n� jsou ulo�eny v souboru `streets.csv`.
Ka�d� m�sto v souboru m� moment�ln� sv� jedine�n� ID, jm�no v �e�tin�, popis v �e�tin�, seznam ID m�st spojen�ch s t�mto m�stem, mo�nost speci�ln�ch akc� pro toto m�sto a omezen� p��stupu 

#### Reprezentace:
+ ID
    + `integer` - nap�. `3`
+ name_cz
    + `string` - nap�. `Perlov�`
+ connected_ID
    + `seznam integer� odd�len�ch ";"` - nap�. `2;8;10;37`
+ description_cz
    + `string` - nap�. `Perlov� ulice je navzdory sv�mu n�zvu zn�m�...`
+ access
    + `string` - nap�. `free`
    + st�le neimplementovan� vlastnost


### Postavy
Ve h�e je moment�ln� 36 r�zn�ch postav. Ka�d� z nich se pohybuje a kon� akce samostatn� a kdy� je to pot�eba, ��d� se �koly (v�ce viz d�le)
Seznam v�ech postav a �daje o nich nalezneme v souboru `characters.csv`. Ka�d� z nich m� svoje jedine�n� ID, jm�no v �e�tin�, ID frakce, ke kter� n�le��, ID ulice, kde se p�i za��tku hry ocitnou, ID ulice, kam se uch�l�, kdy� nemaj� nic na pr�ci, jejich rychlost, s�la a po�et pen�z.

#### Reprezentace
+ ID
    +  `integer` - nap�. `1`
+ name_cz
    +  `string` - nap�. `Str�n�k Poleno`
+ fraction_ID
    +  `integer` - nap�. `0` 
+ spawn_street_ID 
    +  `integer` - nap�. `35` 
+ end_street_ID
    +  `integer` - nap�. `14` 
+ speed
    +  `integer` - nap�. `3` 
+ strength
    +  `integer` - nap�. `1` 
+ coins
    +  `integer`- nap�. `40`
    +  moment�ln� neiplementovan� vlastnost


### Frakce
Jak ji� bylo nazna�eno v reprezentaci postav, tak jsou v t�to h�e definov�ny i takzvan� frakce. Seznam v�ech t�chto frakc� je ulo�en v souboru `fractions.csv`, kde je pro ka�dou z nich definov�no jedine�n� ID, jm�no v �e�tin�, ID m�sta jejich residence a vztahy s ostatn�mi frakcemi.

#### Reprezentace
+ ID
    + integer - nap�. `0`
+ name_cz
    + string - nap�. `Hl�dka`
+ residence_ID
    + integer - nap�. `35`
    + moment�ln� neimplementovan� vlastnost
    + nikam nepat��c� postavy nemaj� residenci `-1`
+ relations
    + �et�zec integer� odd�len�ch st�edn�kem - nap�. `3;1;1;0;2;3;-1`
    + v�znam hodnoty vztah�
      + `3`  = nasad�me za v�s sv�j �ivot
      + `2`  = nevad�me si
      + `1`  = klidn� t� ud�m
      + `0`  = zabiju t� tady a te�
      + `-1` = nedefinov�no (kdy� nem� smysl ur�ovat)


### �koly
�koly, ruka bo��, kter� ��d� chov�n� v�ech postav v t�to h�e. Pod pojmem �kol se zde rozum� sp�e �kolov� linie. Ta se d�l� na ��sti, kter� se naz�vaj� f�ze. Linie zde v�ak nen� definov�na jako posloupnost f�zi, ale jako bin�rn� strom. Jeden syn v�dy reprezentuje �sp�n� spln�n� f�ze a druh� ne�sp�n�. Takto ulo�en� linie jsou k nalezen� v souboru `quest-lines.json` ve form�tu JSON.
1. �koly jsou ulo�eny jako slovn�ky.
2. V�echny slovn�ky jsou se�azeny v poli v souboru `quest-lines.json`.
3. Ka�d� �kol m� 2 kl��e: `name` a `root_quest`, kter� maj� jako hodnoty n�zev �kolu a z�kladn� f�zi

### F�ze �kol�
Ka�d� f�ze je ulo�ena ve slovn�ku, kter� m� n�sleduj�c� kl��e:
`"ID"`, `"char"`, `"from"`, `"item"`, `"reward"`, `"coin_reward"`, `"item_reward"`, `"to_place"`, `"action"`, `"go_to"`, `"on_success"`

#### Vysv�tlen� hodnot ulo�en�ch pod kl��i

##### ID f�ze
Pro v�t�inu �kol� je nicne��kaj�c�, av�ak m��e ur�it, �e se jedn� o termin�ln� f�zi, kter� ukon�� hru.
Pokud se postav� poda�� splnit takovou tu f�zi, tak kon�� hra a hr�� prohr�v�. Jej� k�d je symbolicky `666`. 
+ Kl��: `"ID"`
+ Hodnota: `ID`

##### Kdo
+ Kl��: `char`
+ ID postavy, kter� �kol prov�d� 
+ v p��pad� �kolu zadan�ho hr��i, se jedn� o postavu, kter� �kol zadala

##### Odkud
+ Kl��: `"from"`
+ Pokud je ur�en� m�sto, kde mus� f�ze zapo��t: 
    + `ID m�sta`
+ Pokud m�sto ur�eno nen�: 
    + `-1`
  
##### P�edm�t
Pro ur�it� f�ze m��e b�t pot�eba, aby u sebe postava, kter� jej vykon�v�, m�la n�jak� p�edm�t. Ten j� bude do invent��e p�id�len a� se dostane na m�sto, kde jeho f�ze za��n� a kdy� f�zi spln�, tak bude zase odebr�n.
+ Pokud by m�lo nastat, �e stejn� p�edm�t bude pot�eba pro v�ce f�z� za sebou, tak stejn� bude po ka�d� f�zi odebr�n a pot� p�id�n zp�t.
+ Pokud by m�la postava o p�id�len� p�edm�t b�hem mise p�ij�t, tak je to br�no jako ne�sp�ch.

+ Kl��: `"item"`
+ Hodnota: `ID p�edm�tu` nebo `-1` (pokud nen� ur�en p�edm�t)

##### Kam
+ Kl��: `"to_place"`
+ Pokud je p�esn� definov�no m�sto, pak: 
    + `ID c�lov�ho m�sta`
+ M��e v�ak nastat situace, �e v�sledn� m�sto nen� p�esn� zn�mo anebo se pr�b�n� m�n�. V tom p��pad� bude:
    + `�?�` a v�sledn� m�sto se ur�� dle typu f�ze jin�m modifik�torem.

##### Jdi za
+ Pokud nen� pevn� ur�eno v�sledn� ID m�sta, je mo�n�, �e je zapot�eb�, aby postava do�la za n�jakou jinou. V tom p��pad�: 
+ Kl��: `"go_to"`
+ Hodnota: `ID hledan� postavy`
+ Pokud bude v�sledn� m�sto ur�eno jinak: 
    + `�none�`

##### Akce
+ Kdy� postava zastihne jinou, tak existuje n�kolik mo�nost�, co bude d�lat d�l.
+ Kl��: `"action"`
+ Hodnota:
    + Zab � `�kill�`
    + Omra� � `�stun�`
    + Okra� � `�rob�`
    + Podstr� � `"plant"` 
    + Nic � `�none�`

+ Lehce nedota�en� mechanika. Jak postava v�, kde se nach�z� n�kdo jin�? Pokud hledan� postava n�kam p�jde, tak pro ostatn� bude velmi t�k� ji zastihnout.

##### Odm�na
Pokud postava �sp�n� dokon�� f�zi, tak za to dostane odm�nu. Forma m��e b�t formou pen�z, p�edm�tu �i oboj�ho najednou
Jsou definov�ny:
+ Kl��: `"coin_reward"`
+ Hodnota: `po�et pen�z`

+ Kl��: `"item_reward"`
+ Hodnota: `ID p�edm�tu`
+ + Pokud by nem�l b�t p�ed�n ��dn� p�edm�t, tak bude `-1`

#### Reprezentace stromu f�z�
Na ur�en� f�ze, kter� bude n�sledovat po skon�en� aktu�ln� jsou zde 2 kl��e: `"on_success"` a `"on_fail"`.
Hodnota zde ulo�en� je pole slovn�k� n�sledn�ch f�z�.



## Dynamicky generovan� data
Jeliko� se jedn� o hru, tak chceme, abychom se jak my, tak ostatn� postavy, mohli n�jak�m zp�sobem pohybovat po map� a interagovat s ostatn�mi. Abychom toho ale doc�lili, tak mus�me v�d�t, kdo v ka�dou chv�li je. Z tohoto d�vodu existuje soubor `game_saves.json`, ve kter�m je ulo�en aktu�ln� stav jak hr��e, tak v�ech postav, a i progres �kolov�ch lini�.

Jeliko� hru zprost�edkov�v� bot na telegramu, tak by mohla nastat situace, kdy by hru cht�lo hr�t v�ce u�ivatel� najednou. Pro ka�d�ho z nich mus� tedy existovat pr�v� jedno ulo�en� postupu. Kter� postup pat�� jak�mu u�ivateli se ur�� dle konkr�tn�ho ID chatu, kter� lze z�skat p�es bota.
Data v�ech her se ukl�daj� ve zm�n�n�m souboru v `JSON` form�tu. Jedn� se o slovn�k, kde jsou kl��e ID chatu (tzn. hry) a hodnota je slovn�k s daty.

O programov� zpracov�n� v�ech t�chto dat se star� knihovna `save.py` je� vyu��v� i n�kter� dal�� knihovny (viz d�le).
Nutno je zm�nit funkci `read_current_save`, kter� na z�klad� ID chatu vr�t� slovn�k se v�emi ulo�en�mi daty pot�ebn�mi k na�ten� stavu hry.

### Stav hr��e
Je ulo�en pod kl��em `"player"`, jeho� hodnota je dal�� slovn�k, kter� m� v�echny informace o stavu hr��e.
Jmenovit� to jsou: `"place"`, `"coins"`, `"items"`, `"str"`, `"speed"`, `"relations"`, `"fraction"`, `"state"`, `"duration"`, `"weapons"`, `"quests"` , `"progress"` a `"round"`
V�t�ina z nich vrac� `int` a jsou pochopiteln�.
Jedin� v�jimky jsou:
 + `"itemes"` - `pole int�` ID p�edm�t�, je� m� hr�� u sebe
 + `"relations"` - `pole int�` vztah� hr��e s frakcemi
 + `"state"` - `string` stavu hr��e (`"alive"`, `"stun"`, `"dead"`)
 + `"duration"` - `pole slovn�k�` pom�jiv�ch stav� ovliv�uj�c�ch hr��e
 + `"weapons"` - `pole int�` ID zbran�, je� m� hr�� vybaven�
 + `"quests"` - `pole slovn�k�` f�z� �kol� (ve stejn�m form�tu jako v��e), kter� m� hr�� moment�ln� aktivn� 
 + `"progress"` - `pole string�` popisuj�c�ch pr�b�ch hr��ov�ch f�z� �kol�
    + Rozli�ujeme 3 r�zn� stavy:
        + F�ze je�t� neza�ala = postava teprve mus� doj�t do v�choz�ho m�sta `�tostart�`
        + F�ze pr�v� prob�h� = postava se mus� dostavit na ur�en� m�sto `�inprogress�`
        + F�ze pr�v� skon�ila = postava se dostavila na ur�en� m�sto a provede zadanou akci `�ended�`

### Stav questov�ch lini�
Je ulo�en pod kl��em `"quests"` a ukl�d� pole `string�`, kter� monitoruj� pr�b�h �kolov�ch lini�.
Jeliko� je ka�d� linie �kol� implementov�na jako bin�rn� strom, kdy jeden syn zna�� �sp�ch a druh� ne�sp�ch, tak m��eme cestu do konkr�tn�ho uzlu stromu definovat jako posloupnost p�smen `"F"` a `"S"`, kdy `"F"` znamen�, �e v dan�m bod� nastal ne�sp�ch a m�me se posunout na takov�ho syna. Naopak `"S"` pak znamen� �sp�n� spln�n� mise. 

Pokud je �et�zec pr�zdn�, znamen� to, �e je aktivn� st�le prvn� f�ze, tedy ko�en stromu. 

### Stav postav
Je ulo�en pod kl��em `"characters"`, jeho� hodnota je pole slovn�k� a ka�d� z nich odpov�d� a ukl�d� data o jedn� postav� ve h�e.
Ka�d� postava m� ulo�eno n�sleduj�c�:
 + `"place"` - `int` - ID m�sta, kde pr�v� stoj�
 + `"coins"` - `int` - po�et pen�z, co m� u sebe
 + `"items"` - `list int�` - ID p�edm�t�, co m� postava u sebe
 + `"str"` - `int` - s�la postavy
 + `"speed"` - `int` - rychlost postavy
 + `"line"` - `int` - ID �kolov� linie, kterou pr�v� postava pln� (`-1` pokud nem� ��dn� �kol)
 + `"phase"` - `dict` - f�ze �kolu (viz v��e)
 + `"stage"` - `string` - pr�b�h �kolu
 + `"state"` - `string` - stav postavy (stejn� jako u hr��e)
 + `"duration"` - `int` - pro odpo��t�n� doby, po kterou bude postava omr��ena
 + `"player_relation"` - `int` - osobn� vztah postavy k hr��i



















