import csv
import random
from character import (
    Society,
    PoliticalMap,
    read_people_from_file,
    read_fractions_from_file,
)
from map import Map, read_map_from_file
from items import Item, read_items_from_file
import json


class ModifiedQuestPhase:
    """Class to represent modifiers of phases of Quest Lines"""

    def __init__(
        self,
        qp_ID: str,
        mod_who: str,
        mod_from: str,
        mod_item: str,
        mod_where: str,
        mod_go_to: str,
        rewards_str: str,
    ) -> None:
        # More on all the modifiers in docs
        characters = read_people_from_file(r"data\characters.csv")

        if isinstance(mod_who, int):
            self.quest_phase_ID = qp_ID
            self.characterID = mod_who
            self.from_place_ID = mod_from
            self.item_ID = mod_item
            if mod_where != "?":
                self.to_place_ID = int(mod_where)
                """ID of place where quest ends"""
                self.action = "None"
                self.go_to = -1
            else:
                go_to_char_ID, action = mod_go_to.split(";")
                self.to_place_ID = characters.get_char_by_ID(
                    int(go_to_char_ID)
                ).spawn_street_ID
                self.action = action
                self.go_to = int(go_to_char_ID)

            coins, item = [int(x) for x in rewards_str.split("%")]
            self.reward: dict[str, int] = {"coins": coins, "item": item}

        else:
            self.quest_phase_ID = int(qp_ID)
            # Executor of phase can be defined by ID or fraction
            if mod_who[0:4] == "char":
                character_list = mod_who.lstrip("char").split(";")
                # TODO add condition that only one character can do one phase
            else:
                fraction_ID = int(mod_who.lstrip("frac"))
                character_list = characters.get_characters_by_fraction(fraction_ID)
            characterID = random.choice(character_list)

            self.characterID = int(characterID)

            self.from_place_ID = int(mod_from)

            self.item_ID = int(mod_item)

            # The case where final place of phase is specifically defined by phase itself
            if mod_where != "?":
                self.to_place_ID = int(mod_where)
                """ID of place where quest ends"""

                self.action = "None"

                self.go_to = -1
                """ID of character to find\n
                -1 => final place is static"""

            # Final phase is based on location of another character
            else:
                go_to_char_ID, action = mod_go_to.split(";")

                self.to_place_ID = characters.get_char_by_ID(
                    int(go_to_char_ID)
                ).spawn_street_ID
                self.action = action
                self.go_to = int(go_to_char_ID)

            coins, item = [int(x) for x in rewards_str.split("%")]
            self.reward: dict[str, int] = {"coins": coins, "item": item}

    def __repr__(self):
        characters = read_people_from_file(r"data\characters.csv")
        map = read_map_from_file(r"data\streets.csv")
        items = read_items_from_file(r"data\items.csv")
        return f"{self.quest_phase_ID} is being done by {characters.get_char_by_ID(self.characterID).name_cz}. Starts at {map.get_street_by_ID(self.from_place_ID).name_cz} with {items.get_item(self.item_ID).name_cz}. Goes to {map.get_street_by_ID(self.to_place_ID).name_cz} where he {self.action}(action)"

    def __str__(self):
        if self.go_to == -1:
            return f"{self.quest_phase_ID}=char{self.characterID}={self.from_place_ID}={self.item_ID}={self.to_place_ID}={self.action}={self.reward['coins']}%{self.reward['item']}"
        else:
            return f"{self.quest_phase_ID}=char{self.characterID}={self.from_place_ID}={self.item_ID}=?={    self.go_to};{self.action}={self.reward['coins']}%{self.reward['item']}"

    def to_json(self) -> dict[str]:
        json_dict = dict()
        json_dict["ID"] = self.quest_phase_ID
        json_dict["char"] = self.characterID
        json_dict["from"] = self.from_place_ID
        json_dict["item"] = self.item_ID
        json_dict["reward"] = f"{self.reward['coins']}%{self.reward['item']}"
        json_dict["coin_reward"] = self.reward["coins"]
        json_dict["item_reward"] = self.reward["item"]

        if self.go_to == -1:
            json_dict["to_place"] = self.to_place_ID
            json_dict["action"] = self.action
            json_dict["go_to"] = "None"
        else:
            json_dict["to_place"] = "?"
            json_dict["action"] = f"{self.go_to};{self.action}"
            json_dict["go_to"] = self.go_to

        return json_dict


def dict_to_mqp(dict_quest: dict[str]) -> ModifiedQuestPhase:
    return ModifiedQuestPhase(
        dict_quest["ID"],
        dict_quest["char"],
        dict_quest["from"],
        dict_quest["item"],
        dict_quest["to_place"],
        dict_quest["action"],
        dict_quest["reward"],
    )


def str_to_mqp(code_str: str) -> ModifiedQuestPhase:
    """Function to create ModifiedQuestPhase object based on save string"""
    # modifiers_list = code_str.split("=")
    return ModifiedQuestPhase(*code_str.split("="))


def mqp_to_str(mqp_object: ModifiedQuestPhase) -> str:
    """Function to get string based on data from ModifiedQuestPhase"""
    return str(mqp_object)


def mqp_to_json(mqp_object: ModifiedQuestPhase) -> dict[str]:
    return mqp_object.to_json()


class Node:
    """Class to save each phase of quest line"""

    def __init__(self, value: list[str], succes="None", failure="None"):
        self.value = value
        """value = list of string represantations of modified quest phases"""
        self.succes = succes
        self.failure = failure

    def __repr__(self):
        return (
            f" My {self.value}: (on succes = {self.succes}), (on fail = {self.failure})"
        )


class QuestLineTrees:
    """Class to save phases of quest line and how they follow each other"""

    def __init__(self) -> None:
        self.ID_to_name: dict[int, str] = dict()
        """Get name of quest line based on ID"""
        self.ID_to_tree: dict[int, Node] = dict()
        """Get the root Node of Tree based on ID"""

    def add_tree(self, ID: int, name: str, tree: Node) -> None:
        self.ID_to_name[ID] = name
        self.ID_to_tree[ID] = tree


def read_quest_lines_from_file(path: str) -> QuestLineTrees:
    """Function to read data about Trees from txt file.
    Function returns QuestLineTrees object where all modified quest phases are saved"""
    file = open(path, "r", encoding="utf-8")
    lines = file.readlines()
    number_of_line_quests = int(lines[0])

    quest_lines = QuestLineTrees()

    # Goes through all lines in quest-lines.txt and get the ID, name and string representation of a Quest tree
    for line_idx in range(1, number_of_line_quests * 2, 2):
        quest_line_ID, quest_line_name = lines[line_idx].split("=")
        quest_line_ID = int(quest_line_ID)
        quest_line_name = quest_line_name.rstrip("\n")
        quest_line_code_str = lines[line_idx + 1].rstrip("\n")
        quest_line_tree = create_tree_from_str(quest_line_code_str)

        quest_lines.add_tree(quest_line_ID, quest_line_name, quest_line_tree)

    return quest_lines


def print_tree(node: Node) -> None:
    """Visualize tree"""
    if node != "None":
        print(node.value, end="")

    print("(", end="")
    if node.succes != "None":
        print_tree(node.succes)
    print(")", end="")

    print("(", end="")
    if node.failure != "None":
        print_tree(node.failure)
    print(")", end="")


def create_tree_from_str(quest_line_str: str) -> Node:
    """Reads string representation of tree and returns root Node of this tree"""
    # separating modified quest part from sons
    root_quest = quest_line_str[0 : quest_line_str.index("(")]
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
        left_son = "None"
    else:
        left_son = create_tree_from_str(left_son)

    if right_son == "":
        right_son = "None"
    else:
        right_son = create_tree_from_str(right_son)

    return Node(root_quest.split("&"), left_son, right_son)


if __name__ == "__main__":
    # forest = read_quest_lines_from_file("data\quest-lines.txt")
    # for treeID in forest.ID_to_name:
    #     print(treeID)
    #     print(forest.ID_to_name[treeID])
    #     print_tree(forest.ID_to_tree[treeID])
    str_quest = "9=char34=-1=-1=?=33;rob=25%-1"
    mqp_quest = str_to_mqp(str_quest)
    json_quest = mqp_to_json(mqp_quest)
    print(json_quest)
