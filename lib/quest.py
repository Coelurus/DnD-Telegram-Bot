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
        characters = read_people_from_file(r"data\characters.csv")
        self.quest_phase_ID = int(qp_ID)
        if mod_who[0:4] == "char":
            character_list = mod_who.lstrip("char").split(";")
            # TODO add condition that only one character can do one phase + remove random
        else:
            fraction_ID = int(mod_who.lstrip("frac"))
            character_list = characters.get_characters_by_fraction(fraction_ID)
        characterID = random.choice(character_list)

        self.characterID = int(characterID)

        from_ID = int(mod_from)

        self.from_place_ID = int(from_ID)

        self.item_ID = int(mod_item)

        # The case where final place of phase is specifically defined by phase itself
        if mod_where != "?":
            self.to_place_ID = int(mod_where)
            self.action = "none"
            self.go_to = -1

        # Final phase is based on location of another character
        else:
            go_to_char_ID, action = mod_go_to.split(";")

            self.to_place_ID = characters.get_char_by_ID(
                int(go_to_char_ID)).spawn_street_ID
            self.action = action
            self.go_to = int(go_to_char_ID)

    def __repr__(self):
        phases_list = read_quest_phases_from_file(r"data\quest-phases.csv")
        characters = read_people_from_file(r"data\characters.csv")
        map = read_map_from_file(r"data\streets.csv")
        items = read_items_from_file(r"data\items.csv")
        return f"{phases_list.get_phase_by_ID(self.quest_phase_ID).name_cz} is being done by {characters.get_char_by_ID(self.characterID).name_cz}. Starts at {map.get_street_by_ID(self.from_place_ID).name_cz} with {items.get_item(self.item_ID).name_cz}. Goes to {map.get_street_by_ID(self.to_place_ID).name_cz} where he {self.action}(action)"

    def __str__(self):
        if self.go_to == -1:
            return f"{self.quest_phase_ID}=char{self.characterID}={self.from_place_ID}={self.item_ID}={self.to_place_ID}={self.action}"
        else:
            return f"{self.quest_phase_ID}=char{self.characterID}={self.from_place_ID}={self.item_ID}=?={self.go_to};{self.action}"


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

    def __repr__(self):
        return f" My {self.value}: (on succes = {self.succes}), (on fail = {self.failure})"


class QuestLineTrees:
    def __init__(self) -> None:
        self.ID_to_name: dict[int, str] = dict()
        self.ID_to_tree: dict[int, Node] = dict()

    def add_tree(self, ID: int, name: str, tree: Node) -> None:
        self.ID_to_name[ID] = name
        self.ID_to_tree[ID] = tree


def read_quest_lines_from_file(path: str) -> QuestLineTrees:
    file = open(path, "r", encoding="utf-8")
    lines = file.readlines()
    number_of_line_quests = int(lines[0])

    quest_lines = QuestLineTrees()

    for line_idx in range(1, number_of_line_quests*2, 2):
        quest_line_ID, quest_line_name = lines[line_idx].split("=")
        quest_line_ID = int(quest_line_ID)
        quest_line_name = quest_line_name.rstrip("\n")
        quest_line_code_str = lines[line_idx+1].rstrip("\n")
        quest_line_tree = create_tree_from_str(quest_line_code_str)

        quest_lines.add_tree(quest_line_ID, quest_line_name, quest_line_tree)

    return quest_lines


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
    # separating modified quest part from sons
    root_quest = quest_line_str[0:quest_line_str.index("(")]
    strip_len = len(root_quest + "(")
    quest_line_str = quest_line_str[strip_len:]

    # Looking for left son string size by identifying closing bracket
    brackets = 1
    for idx in range(len(quest_line_str)):
        if quest_line_str[idx] == "(":
            brackets += 1
        elif quest_line_str[idx] == ")":
            brackets -= 1

        if brackets == 0:
            break

    left_son = quest_line_str[0:idx]
    strip_len = len(left_son + ")(")
    quest_line_str = quest_line_str[strip_len:]

    # right son is what remains
    right_son = quest_line_str[0:-1]

    if left_son == "":
        left_son = None
    else:
        left_son = create_tree_from_str(left_son)

    if right_son == "":
        right_son = None
    else:
        right_son = create_tree_from_str(right_son)

    return Node(root_quest.split(","), left_son, right_son)


if __name__ == "__main__":
    """testMQP = str_to_mqp("2=frac1=*=9=?=12;bring")
    testSTR = mqp_to_str(testMQP)
    print(repr(testMQP))
    print(testMQP)"""

    #selling_snuff = Node(["0=char12;11=36=0=37=none"], Node(["0=frac1=37=1=0=none", "0=frac1=37=1=32=none", "0=frac1=37=1=33=none"]), Node(["2=frac1=*=9=?=12;bring"]))

    # print(selling_snuff)
    # print_tree(selling_snuff)
    # create_tree_from_str("0=char12;11=36=0=37=none(0=frac1=37=1=0=none,0=frac1=37=1=32=none,0=frac1=37=1=33=none()())(2=frac1=*=9=?=12;bring()())")

    forest = read_quest_lines_from_file("data\quest-lines.txt")
    for treeID in forest.ID_to_name:
        print(treeID)
        print(forest.ID_to_name[treeID])
        print_tree(forest.ID_to_tree[treeID])
