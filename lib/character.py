import csv
import json

class Fraction:
    """Class to store static data about Fractions"""
    base_relation = 2

    def __init__(self, ID: str, name_cz: str, residence_ID: str, relations: str) -> None:
        self.ID = int(ID)
        self.name_cz = name_cz
        self.residence_ID = int(residence_ID)
        self.relations = [int(x) for x in relations.split(";")]

    def __str__(self):
        residence = "doesnt exist"
        if self.residence_ID != -1:
            residence = self.residence_ID
        return f"[{self.ID}] - {self.name_cz}: residence: {residence}. Relationships are: {self.relations}"

    def __repr__(self):
        return str(self)


class PoliticalMap:
    """Class to store all Fractions objects"""

    fractions = []

    def __init__(self) -> None:
        pass

    @staticmethod
    def add_fraction(fraction: Fraction) -> None:
        PoliticalMap.fractions.append(fraction)

    @staticmethod
    def __repr__():
        return "\n".join([str(x) for x in PoliticalMap.fractions])

    @staticmethod
    def get_fraction(ID: int) -> Fraction:
        return PoliticalMap.fractions[ID]


class NPC:
    """Class to store static data about characters"""

    def __init__(self, ID: str, name_cz: str, fraction_ID: str, spawn_street_ID: str, end_street_ID: str, speed: str, strentgh: str, coins: str, items=[], special_action = {}) -> None:
        self.ID = int(ID)
        self.name_cz = name_cz
        self.fraction_ID = int(fraction_ID)
        self.spawn_street_ID = int(spawn_street_ID)
        self.end_street_ID = int(end_street_ID)
        self.items = [int(x) for x in items]
        self.coins = int(coins)
        self.speed = speed
        self.strength = strentgh
        self.special_action = special_action

    def __repr__(self) -> str:
        return str(self)

    def __str__(self) -> str:
        end = "not defined"
        if self.end_street_ID != -1:
            end = self.end_street_ID
        return f"[{self.ID}] - {self.name_cz}: is from: {self.spawn_street_ID}, ends in: {end}, is in fraction: {self.fraction_ID}, has items: {self.items}, has {self.coins} coins"


class Society:
    """Class to store all NPC objects"""

    people_list: list[NPC] = []
    name_cz_to_ID: dict[str, int] = dict()
    """Dict to easily get NPC's ID based on his name"""

    def __init__(self) -> None:
        pass
    
    @staticmethod
    def add_person(person: NPC) -> None:
        Society.people_list.append(person)
        Society.name_cz_to_ID[person.name_cz] = person.ID

    @staticmethod
    def __repr__() -> str:
        return "\n".join([str(x) for x in Society.people_list])
    
    @staticmethod
    def get_char_by_ID(ID: int) -> NPC:
        """
        The method return Street object identified by ID. If it were to fail method returns False
        """

        if ID < len(Society.people_list):
            return Society.people_list[ID]
        return False
    
    @staticmethod
    def convert_IDs_to_NPCs(ID_list: list[int]) -> list[NPC]:
        """
        The method takes list of IDs and returns list of NPCs based on these IDs. If the ID is invalid, method acts like it do not exist.
        """
        return [Society.get_char_by_ID(ID) for ID in ID_list if Society.get_char_by_ID(ID) is not False]
    
    @staticmethod
    def get_characters_by_fraction(fraction_ID: int) -> list[int]:
        """
        The method takes ID of fraction and returns list of IDs of characters that belong in the fraction.
        """
        character_IDs_by_fraction = []
        for character in Society.people_list:
            if character.fraction_ID == fraction_ID:
                character_IDs_by_fraction.append(character.ID)
        return character_IDs_by_fraction


def read_people_from_file(path: str):
    """Function to read data about characters from csv file.
    Function returns Society object where all NPCs are saved"""
    csv_file = open(path, newline="", encoding="utf-8")
    reader = csv.DictReader(csv_file, delimiter=",")

    with open("data\special_actions.json", "r", encoding="utf-8") as save_file:
        json_data = save_file.read()
        dict_data: dict[str, dict[str, str|int]] = json.loads(json_data)

    Society.people_list = []
    Society.name_cz_to_ID = dict()

    for row in reader:
        special_action = dict_data[row["ID"]] if row["ID"] in dict_data else dict()
        Society.add_person(NPC(row["ID"], row["name_cz"], row["fraction_ID"], row["spawn_street_ID"], row["end_street_ID"], row["speed"], row["strength"], row["coins"], [], special_action))

    csv_file.close()


def read_fractions_from_file(path: str):
    """Function to read data about fractions from csv file.
    Function returns PoliticalMap object where all fractions are saved"""
    csv_file = open(path, newline="", encoding="utf-8")
    reader = csv.DictReader(csv_file, delimiter=",")

    PoliticalMap.fractions = []

    for row in reader:
        PoliticalMap.add_fraction(
            Fraction(row["ID"], row["name_cz"], row["residence_ID"], row["relations"]))

    csv_file.close()


if __name__ == "__main__":
    society = read_people_from_file(r"data\characters.csv")
    print("========== Society ==========")
    print(society)

    fractions = read_fractions_from_file(r"data\fractions.csv")
    print("========== Politics ==========")
    print(fractions)
