def output(text: str) -> None:
    print(text)


def choose(choices: list[str]) -> int:
    print("U have choices:", ", ".join(choices))
    choice = input("Write your choice: ")
    index = choices.index(choice)
    return index
