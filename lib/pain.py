"""from quest import Node, print_tree


def create_tree_from_str(quest_line_str: str):
    # separating modified quest part from sons
    root_quest = quest_line_str[0:quest_line_str.index("(")]
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
        left_son = None
    else:
        left_son = create_tree_from_str(left_son)

    if right_son == "":
        right_son = None
    else:
        right_son = create_tree_from_str(right_son)

    return Node(root_quest, left_son, right_son)


if __name__ == "__main__":
    tree_root = create_tree_from_str(
        "0=char12;11=36=0=37=none(0=frac1=37=1=0=none,0=frac1=37=1=32=none,0=frac1=37=1=33=none()())(2=frac1=*=9=?=12;bring()())")
    print_tree(tree_root)
"""
