import csv


class Fraction:
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
    def __init__(self) -> None:
        self.fractions = []

    def add_fraction(self, fraction: Fraction) -> None:
        self.fractions.append(fraction)

    def __repr__(self):
        return "\n".join([str(x) for x in self.fractions])


class NPC:
    def __init__(self, ID: str, name_cz: str, fraction_ID: str, quest_line_ID: str, spawn_street_ID: str, end_street_ID: str) -> None:
        self.ID = int(ID)
        self.name_cz = name_cz
        self.fraction_ID = int(fraction_ID)
        self.quest_line_ID = int(quest_line_ID)
        self.spawn_street_ID = int(spawn_street_ID)
        self.end_street_ID = int(end_street_ID)

    def __repr__(self) -> str:
        return str(self)

    def __str__(self) -> str:
        end = "not defined"
        if self.end_street_ID != -1:
            end = self.end_street_ID
        return f"[{self.ID}] - {self.name_cz}: is from: {self.spawn_street_ID}, ends in: {end}, does: {self.quest_line_ID}, is in fraction: {self.fraction_ID}"


class Society:
    def __init__(self) -> None:
        self.people_list = []

    def add_person(self, person: NPC) -> None:
        self.people_list.append(person)

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


def read_people_from_file(path):
    csv_file = open(path, newline="", encoding="utf-8")
    reader = csv.DictReader(csv_file, delimiter=",")

    society = Society()
    for row in reader:
        society.add_person(NPC(
            *[row[x] for x in ["ID", "name_cz", "fraction_ID", "quest_line_ID", "spawn_street_ID", "end_street_ID"]]))

    csv_file.close()
    return society


def read_fractions_from_file(path):
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
    print(society)

    fractions = read_fractions_from_file(r"data\fractions.csv")
    print(fractions)
