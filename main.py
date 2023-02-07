from sys import path
import os


def get_lib() -> None:
    path.append(os.getcwd() + "\lib")


if __name__ == "__main__":
    get_lib()
    from save import rotation
    rotation()

    # TODO functional relative paths
    # for now start from save.py file
    pass
    # oh lol just found not even that works. you have to run the save.py file but from DnD folder...
