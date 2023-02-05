from __future__ import annotations
import csv


class Map:
    def __init__(self) -> None:
        self.streets = []

    def add_street(self, street: Street) -> None:
        self.streets.append(street)
        # TODO unordered csv file

    def print_streets_and_connections(self) -> None:
        """
        Prints out all streets and possibilities where to get from them.
        Only dev function to check if everything fits acording to map.
        """
        for street in self.streets:
            print(street.get_name_cz(), " -> ", ", ".join([
                  self.streets[x].get_name_cz() for x in street.get_connected_streets()]))

    def find_shortest_path(self, BFS_streets: list[Street], BFS_depths: list[int], to_street: Street) -> list[Street]:
        STREET = 0
        DEPTH = 1
        BFS_combined = list(zip(BFS_streets, BFS_depths))
        while BFS_combined[-1][STREET] != to_street:
            BFS_combined.pop()

        current_street, distance_to_start = BFS_combined.pop()
        reversed_path = [current_street]
        distance_to_start -= 1

        for street_idx in range(len(BFS_combined)-1, -1, -1):
            if BFS_combined[street_idx][STREET].ID in reversed_path[-1].get_connected_streets() and BFS_combined[street_idx][DEPTH] == distance_to_start:
                reversed_path.append(BFS_combined[street_idx][STREET])
                distance_to_start -= 1

        path = list(reversed(reversed_path))
        return path

    def BFS(self, from_street: Street) -> tuple[list[Street], list[int]]:
        """
        Method takes 1 argument and that is Street type from where the search starts. 
        Method returns tuple of two list where first list are Streets in BFS and second list are 
        distances from the starting street on the exact same indexes as streets.
        """
        queue = [from_street] + self.convert_IDs_to_streets(
            from_street.get_connected_streets())
        depth = [0] + [1] * (len(queue)-1)

        place_idx = 0
        while place_idx < len(queue):
            for neighbourID in queue[place_idx].get_connected_streets():
                neighbour_street = self.get_street_by_ID(neighbourID)
                if neighbour_street not in queue:
                    queue.append(neighbour_street)
                    depth.append(depth[place_idx] + 1)
            place_idx += 1

        return queue, depth

    def get_street_by_ID(self, ID: int) -> Street:
        """
        The method return Street object identified by ID. If it were to fail method returns False
        """
        if ID < len(self.streets):
            return self.streets[ID]
        return False

    def convert_IDs_to_streets(self, ID_list: list[int]) -> list[Street]:
        """
        The method takes list of IDs and returns list of Streets based on these IDs. If the ID is invalid, method acts like it do not exist.
        """
        return [self.get_street_by_ID(ID) for ID in ID_list if self.get_street_by_ID(ID) is not False]


class Street:
    """Haha"""

    def __init__(self, ID: str, name_cz: str, connections: str) -> None:
        self.ID = int(ID)
        self.name_cz = name_cz
        self.connections = [int(x) for x in connections.split(";")]

    def __repr__(self):
        return f"ID[{self.ID}] - {self.name_cz} is connected to: {self.connections}"

    def get_connected_streets(self) -> list[int]:
        return self.connections

    def get_name_cz(self) -> str:
        return self.name_cz


def read_map_from_file(path: str) -> Map:
    csv_file = open(path, newline="", encoding="utf-8")
    reader = csv.DictReader(csv_file, delimiter=",")

    map = Map()
    for row in reader:
        map.add_street(Street(row["ID"], row["name_cz"], row["connected_ID"]))
    return map


if __name__ == "__main__":
    map = read_map_from_file("data\streets.csv")

    # map.print_streets_and_connections()
    streetList, depth = map.BFS(map.streets[3])
    for routeIdx in range(len(streetList)):
        print(depth[routeIdx], streetList[routeIdx].get_name_cz())

    for i in map.find_shortest_path(streetList, depth, map.streets[20]):
        print(i.get_name_cz())
