import csv
import random
from character import Society, PoliticalMap, read_people_from_file, read_fractions_from_file
from map import Map, read_map_from_file
from items import Item, read_items_from_file


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

    def get_phase_by_ID(self, ID: int) -> QuestPhase:
        return self.list[ID]


class ModifiedQuestPhase:
    def __init__(self, qp_ID: str, mod_who: str, mod_from: str, mod_item: str, mod_where: str, mod_go_to: str) -> None:
        self.quest_phase_ID = int(qp_ID)
        if mod_who[0:4] == "char":
            character_list = mod_who.lstrip("char").split(";")
            # TODO odstranit random a přidat podmínku, jestli žije
        else:
            fraction_ID = int(mod_who.lstrip("frac"))
            character_list = characters.get_characters_by_fraction(fraction_ID)
        characterID = random.choice(character_list)

        self.characterID = int(characterID)

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

        else:
            go_to_char_ID, action = mod_go_to.split(";")

            # TODO musí se najít aktuální pozice postavy - tzn. až se přidají saves
            self.to_place_ID = characters.get_char_by_ID(
                int(go_to_char_ID)).spawn_street_ID
            self.action = action

    def __repr__(self):
        return f"{phases_list.get_phase_by_ID(self.quest_phase_ID).name_cz} is being done by {characters.get_char_by_ID(self.characterID).name_cz}. Starts at {map.get_street_by_ID(self.from_place_ID).name_cz} with {items.get_item_by_ID(self.item_ID).name_cz}. Goes to {map.get_street_by_ID(self.to_place_ID).name_cz} where he {self.action}(action)"

    def __str__(self):
        return f"{self.quest_phase_ID}=char{self.characterID}={self.from_place_ID}={self.item_ID}={self.to_place_ID}={self.action}"


def str_to_mqp(code_str: str) -> ModifiedQuestPhase:
    modifiers_list = code_str.split("=")
    return ModifiedQuestPhase(*modifiers_list)


def mqp_to_str(mqp_object: ModifiedQuestPhase) -> str:
    return str(mqp_object)


class Node:
    def __init__(self, value: list[str], succes=None, failure=None):
        self.value = value
        self.succes = succes
        self.failure = failure


class QuestTree:
    def __init__(self, root: Node) -> None:
        self.root = root


def print_tree(node: Node) -> None:
    if node != None:
        print(node.value, end="")

    print("(", end="")
    if node.succes != None:
        print_tree(node.succes)
    print(")", end="")

    print("(", end="")
    if node.failure != None:
        print_tree(node.failure)
    print(")", end="")


def read_quest_phases_from_file(path):
    csv_file = open(path, newline="", encoding="utf-8")
    reader = csv.DictReader(csv_file, delimiter=",")

    quest_phase_list = QuestPhaseList()
    for row in reader:
        quest_phase_list.add_phase(QuestPhase(
            row["ID"], row["name_cz"], row["legal"]))

    csv_file.close()
    return quest_phase_list


def create_tree_from_str(quest_line_str: str):

    root_quest = quest_line_str[0:quest_line_str.index("(")]
    quest_line_str = quest_line_str.lstrip(root_quest + "(")

    for idx in range(len(quest_line_str)):
        if quest_line_str[idx] == "(":
            son_value = quest_line_str[0:idx]


if __name__ == "__main__":
    phases_list = read_quest_phases_from_file(r"data\quest-phases.csv")
    # print(phases_list)
    characters = read_people_from_file(r"data\characters.csv")
    map = read_map_from_file(r"data\streets.csv")
    items = read_items_from_file(r"data\items.csv")

    """testMQP = str_to_mqp("2=frac1=*=9=?=12;bring")
    testSTR = mqp_to_str(testMQP)
    print(repr(testMQP))
    print(testMQP)"""

    selling_snuff = QuestTree(Node(["0=char12;11=36=0=37=none"], Node(
        ["0=frac1=37=1=0=none", "0=frac1=37=1=32=none", "0=frac1=37=1=33=none"]), Node(["2=frac1=*=9=?=12;bring"])))

    print(selling_snuff.root)
    print_tree(selling_snuff.root)
    create_tree_from_str(
        "0=char12;11=36=0=37=none(0=frac1=37=1=0=none,0=frac1=37=1=32=none,0=frac1=37=1=33=none()())(2=frac1=*=9=?=12;bring()())")
