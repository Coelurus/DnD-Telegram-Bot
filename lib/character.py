import csv


class Fraction:
    """Class to store static data about Fractions"""

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

    def __init__(self) -> None:
        self.fractions = []

    def add_fraction(self, fraction: Fraction) -> None:
        self.fractions.append(fraction)

    def __repr__(self):
        return "\n".join([str(x) for x in self.fractions])

    def get_fraction(self, ID: int) -> Fraction:
        return self.fractions[ID]


class NPC:
    """Class to store static data about characters"""

    def __init__(self, ID: str, name_cz: str, fraction_ID: str, spawn_street_ID: str, end_street_ID: str, speed: str, strentgh: str, coins: str, items=[]) -> None:
        self.ID = int(ID)
        self.name_cz = name_cz
        self.fraction_ID = int(fraction_ID)
        self.spawn_street_ID = int(spawn_street_ID)
        self.end_street_ID = int(end_street_ID)
        self.items = [int(x) for x in items]
        self.coins = int(coins)
        self.speed = speed
        self.strength = strentgh

    def __repr__(self) -> str:
        return str(self)

    def __str__(self) -> str:
        end = "not defined"
        if self.end_street_ID != -1:
            end = self.end_street_ID
        return f"[{self.ID}] - {self.name_cz}: is from: {self.spawn_street_ID}, ends in: {end}, is in fraction: {self.fraction_ID}, has items: {self.items}, has {self.coins} coins"


class Society:
    """Class to store all NPC objects"""

    def __init__(self) -> None:
        self.people_list: list[NPC] = []
        self.name_cz_to_ID: dict[str, int] = dict()
        """Dict to easily get NPC's ID based on his name"""

    def add_person(self, person: NPC) -> None:
        self.people_list.append(person)
        self.name_cz_to_ID[person.name_cz] = person.ID

    def __repr__(self) -> str:
        return "\n".join([str(x) for x in self.people_list])

    def get_char_by_ID(self, ID: int) -> NPC:
        """
        The method return Street object identified by ID. If it were to fail method returns False
        """
        if ID < len(self.people_list):
            return self.people_list[ID]
        return False

    def convert_IDs_to_NPCs(self, ID_list: list[int]) -> list[NPC]:
        """
        The method takes list of IDs and returns list of NPCs based on these IDs. If the ID is invalid, method acts like it do not exist.
        """
        return [self.get_char_by_ID(ID) for ID in ID_list if self.get_char_by_ID(ID) is not False]

    def get_characters_by_fraction(self, fraction_ID: int) -> list[int]:
        """
        The method takes ID of fraction and returns list of IDs of characters that belong in the fraction.
        """
        character_IDs_by_fraction = []
        for character in self.people_list:
            if character.fraction_ID == fraction_ID:
                character_IDs_by_fraction.append(character.ID)
        return character_IDs_by_fraction


def read_people_from_file(path: str) -> Society:
    """Function to read data about characters from csv file.
    Function returns Society object where all NPCs are saved"""
    csv_file = open(path, newline="", encoding="utf-8")
    reader = csv.DictReader(csv_file, delimiter=",")

    society = Society()
    for row in reader:
        society.add_person(NPC(
            *[row[x] for x in ["ID", "name_cz", "fraction_ID", "spawn_street_ID", "end_street_ID", "speed", "strength", "coins"]]))

    csv_file.close()
    return society


def read_fractions_from_file(path: str) -> PoliticalMap:
    """Function to read data about fractions from csv file.
    Function returns PoliticalMap object where all fractions are saved"""
    csv_file = open(path, newline="", encoding="utf-8")
    reader = csv.DictReader(csv_file, delimiter=",")

    political_map = PoliticalMap()
    for row in reader:
        political_map.add_fraction(
            Fraction(row["ID"], row["name_cz"], row["residence_ID"], row["relations"]))

    csv_file.close()
    return political_map


if __name__ == "__main__":
    society = read_people_from_file(r"data\characters.csv")
    print("========== Society ==========")
    print(society)

    fractions = read_fractions_from_file(r"data\fractions.csv")
    print("========== Politics ==========")
    print(fractions)
