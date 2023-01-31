import csv


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

    print(phases_list)
