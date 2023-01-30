from lib.map import read_map_from_file
from lib.character import read_people_from_file

if __name__ == "__main__":
    map = read_map_from_file("DnD\data\streets.csv")
    map.print_streets_and_connections()

    society = read_people_from_file("DnD\data\characters.csv")
    print(society)
