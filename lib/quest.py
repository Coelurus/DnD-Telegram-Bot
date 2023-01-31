import csv
import random
from character import Society, PoliticalMap, read_people_from_file, read_fractions_from_file


class QuestPhase:
    def __init__(self, ID: str, name_cz: str, legal: str) -> None:
        self.ID = int(ID)
        self.name_cz = name_cz
        self.legal = legal

    def __str__(self) -> str:
        return f"[{self.ID}] - {self.name_cz}: Is it legal? {self.legal}"

    def __repr__(self) -> str:
        return str(self)


class QuestPhaseList:
    def __init__(self):
        self.list = []

    def __repr__(self) -> str:
        return "\n".join([str(x) for x in self.list])

    def add_phase(self, phase: QuestPhase):
        self.list.append(phase)


class ModifiedQuestPhase:
    def __init__(self, qp_ID: str, mod_who: str, mod_from: str, mod_item: str, mod_where: str, mod_go_to: str, characters: Society) -> None:
        self.quest_phase_ID = int(qp_ID)
        if mod_who[0:4] == "char":
            character_list = mod_who.lstrip("char").split(";")
            # TODO odstranit random a přidat podmínku, jestli žije
        else:
            fraction_ID = int(mod_who.lstrip("frac"))
            character_list = characters.get_characters_by_fraction(fraction_ID)
        characterID = random.choice(character_list)

        self.characterID = characterID

        if mod_from == "*":
            # TODO zjistit aktuální pozici charactedID a nastavit začátek questu tam
            from_ID = random.randint(0, 36)
        else:
            from_ID = int(mod_from)

        self.from_place_ID = int(from_ID)

        self.item_ID = int(mod_item)

        if mod_where != "?":
            self.to_place_ID = int(mod_where)
            self.action = "none"

        elif mod_go_to != "x":
            go_to_char_ID, action = mod_go_to.split(";")

            # TODO musí se najít aktuální pozice postavy - tzn. až se přidají saves
            self.to_place_ID = characters.get_char_by_ID(
                int(go_to_char_ID)).spawn_street_ID
            self.action = action

    def __repr__(self):
        return f"phase[{self.quest_phase_ID}] - is being done by char[{self.characterID}]. Starts at street[{self.from_place_ID}] with item[{self.item_ID}]. Goes to street[{self.to_place_ID}] where he {self.action}(action)"


class QuestLine:
    def __init__(self) -> None:
        pass


class QuestLineList:
    def __init__(self) -> None:
        self.list = []


def read_quest_phases_from_file(path):
    csv_file = open(path, newline="", encoding="utf-8")
    reader = csv.DictReader(csv_file, delimiter=",")

    quest_phase_list = QuestPhaseList()
    for row in reader:
        quest_phase_list.add_phase(QuestPhase(
            row["ID"], row["name_cz"], row["legal"]))

    csv_file.close()
    return quest_phase_list


if __name__ == "__main__":
    phases_list = read_quest_phases_from_file(r"data\quest-phases.csv")
    # print(phases_list)
    characters = read_people_from_file(r"data\characters.csv")

    test = ModifiedQuestPhase("0", "char1;3", "15",
                              "0", "17", "x", characters)
    # print(test)
