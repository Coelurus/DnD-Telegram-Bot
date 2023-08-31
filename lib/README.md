# Knihovny pro spu�t�n�

## Mapa a ulice
O zpracov�v�n� t�chto dat se star� knihovna `map.py`, kter� definuje t��du `Street`, do kter� se ukl�daj� ve�ker� data zm�n�n� v��e. Nav�c je zde t��da `Map`, kter� v sob� ukl�d� v�echny objekty `Street` a poskytuje metody pro pr�ci s nimi. Mezi n� pat�� metoda `BFS`, jej�m� jedin�m argumentem je v�choz� m�sto. Metoda prov�d� pr�chod do ���ky grafem mapy a vrac� seznam ulic a seznam vzd�lenost� ulic na stejn�m indexu od v�choz� ulice. Druhou d�le�itou metodou je pak `find_shortest_path`, kter� bere jako argumenty tyto 2 seznamy a k tomu je�t� c�lov� m�sto a vrac� jednu z nejkrat��ch cest z v�choz�ho do c�lov�ho m�sta.

Za zm�nku t� stoj� funkce `read_map_from_file`, kter� se star� o na�ten� dat ze souboru a jejich ulo�en� do objektu t��dy `Map`

Zbytek funkc� a metod je i s koment��i k naleznut� v `lib/map.py`

***

## Postavy
O zpracov�n� dat t�kaj�c�ch se postav se star� knihovna `character.py`. Ta definuje t��du `NPC` do jej�ch� objekt� se ukl�daj� v�echny data uveden� v reprezentaci. D�le je zde t��da `Society`, kter� ukl�d� v�echny objekty typu `NPC` a definuje metody pro pr�ce s nimi.
Nach�z� se zde t� funkce `read_people_from_file`, je� se star� o na�ten� v�ech postav, jejich reprezentaci jako `NPC` a jejich ulo�en� do objektu t��dy `Society`

***

## Frakce
O zpracov�n� dat ohledn� frakc� se star� t� knihovna `character.py`, kter� definuje t��du `Fraction`, do kter� se ukl�daj� v�echny vlastnosti vypsan� v��e. Jako v�dy je definov�na t��da `PoliticalMap`, kter� v sob� ukl�d� v�echny frakce a definuje metody pro pr�ce s nimi.
Pro na�ten� a zpracov�n� v�ech frakc� je zde `read_fractions_from_file`, kter� zkonstruuje objekt t��dy `PoliticalMap` se v�emi frakcemi ve form� `Fraction`.

***

## �koly a f�ze
O na�ten� a zpracov�n� �kolov�ch dat se star� knihovna `quest.py`. Ta definuje t�i z�sadn� t��dy `ModifiedQuestPhase`, `Node` a `QuestLineTrees`.
- Instance t��dy `ModifiedQuestPhase` ve sv�ch atributech ukl�d� ve�ker� �daje o f�zi, jak byly pops�ny v��e. Je na ni t� reprezentov�na funkce `__str__`, kter� ji p�evede zp�t do textov� reprezentace.
- T��da `Node` je pot� z�kladn� p�te�� �kolov�ch strom�. Ka�d� `Node` m� svou `value`, ve kter� je ulo�en seznam �et�zcov�ch vyj�d�en� f�z�.
    - Pozn. `value` je definov�na jako seznam, proto�e p�vodn� idea byla, �e by f�ze mohla spustit v�ce dal��ch podf�z�, av�ak to bude vy�adovat komplexn�j�� �e�en� �sp�chu �i selh�n� t�to skupiny a jej� vyhodnocen� pro dal�� syny. Proto, i kdy� se jedn� o seznam, tak program v�dy bere pouze prvn� f�zi a ostatn� prozat�m ignoruje.
- Posledn� je `QuestLineTrees`, kter� do slovn�k� ukl�d� indexy, jm�na a ko�eny v�ech �kolov�ch strom�.
D�le�it� funkce t�to knivny jsou pak `dict_to_mqp` a `mqp_to_dict`, kter� p�ev�d�j� `dict` s �kolem na `ModifiedQuestPhase`.
Samoz�ejm� zde m�me i funkci `read_quest_lines_from_file`, je� na�te v�echny �kolov� stromy a ulo�� je do instance t��dy `QuestLineTrees`

## Hr��
Na ulo�en� v�ech dat ohledn� hr��e je v knihovn� `player.py` definov�na t��da `Player`. Pro tuto t��du je zde pot� definov�no plno metod (jako nap��klad pohyb, pou��v�n� p�edm�t�), d�ky kter�m m��e hr�� hru hr�t. Ne� je tady v�echny vypisovat, tak doporu��m pod�vat se do `player.py`.
V knihovn� `save.py` jsou pot� funkce, je� zpracuj� vstupn� save data a vytvo�� z nich instanci objektu `Player`. Na tuto specifickou akci je zde funkce `get_current_player`. 
Opa�nou funkci pln� funkce `player_save_generator`, kter� objekt `Player` p�etvo�� na `dict`, kter� se pak ulo�� do `JSON` souboru.

## �koly
Pro operov�n� s daty o pr�b�hu �kol� op�t pou�ijeme knihovnu `save.py`. Je zde pro to n�kolik funkc�, ale za zm�nku stoj� hlavn� `get_current_quests`, kter� dle �et�zc� progresu slo�en�ch z `"F"` a `"S"` proch�z� �kolov� stromy, a nakonec vr�t� aktu�ln� f�zi, je� prob�h�. Dal�� funkce je `assign_quests`, kter� proch�z� aktu�ln� f�ze z�skan� p�edchoz� f�z� a p�i�azuje je postav�m, kter� je pak budou vykon�vat.

## Stavy postav
Je pravda, �e i zde se vyu�ije p�r funkc� ze `save.py`, ale hlavn� podpora pro pr�ci s t�mito daty se nach�z� v knihovn� `character_handler.py`. Zde jsou definov�ny dv� t��dy. Prvn� z nich je `ModifiedNPC`, do kter�ho se ka�d� kolo ukl�daj� v�echny stavov� data postavy na�ten� ze save file. Pro p��stup ke v�em `ModifiedNPC` je zde t��da `ModifiedPeople`, kter� i definuje metody pro p�ijemn�j�� pr�ci s nimi.
Mimo t��dy je nutno zm�nit funkci `get_current_characters`, kter� se star� o na�ten� aktu�ln�ch dat v�ech postav. Pak se zde nach�z� spousta dal��ch funkc� na pr�ci s postavami, jako nap��klad jejich pohyb, souboj a podobn�. V�e je podrobn� okomentov�no v samotn�m `character_handler.py`.
