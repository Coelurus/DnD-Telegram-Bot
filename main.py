from sys import path
import os


def get_lib() -> None:
    path.append(os.getcwd() + "\lib")


if __name__ == "__main__":
    get_lib()
    from save import rotation
    print("======= LOGS =======")
    for i in range(20):
        print(str(i)+".")
        rotation()
        print("="*20)

    # TODO functional relative paths
