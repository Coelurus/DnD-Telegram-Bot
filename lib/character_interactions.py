from character_handler import ModifiedNPC, ModifiedPeople
from character import read_people_from_file, read_fractions_from_file, NPC


def how_char1_loves_char2(char1: NPC, char2: NPC, fractions=read_fractions_from_file(r"data\fractions.csv")) -> int:
    return fractions.get_fraction(char1.fraction_ID).relations[char2.fraction_ID]


def fight(attacker: ModifiedNPC, defender: ModifiedNPC, action: str, current_characters: ModifiedPeople) -> ModifiedPeople:
    people = read_people_from_file(r"data\characters.csv")
    fractions = read_fractions_from_file(r"data\fractions.csv")
    attacker_NPC = people.get_char_by_ID(attacker.ID)
    defender_NPC = people.get_char_by_ID(defender.ID)

    attacker_bonus = 0

    # attackers speed or moment of surprise inflicts advantage for him
    if attacker.speed > defender.speed + 1 or attacker_NPC.fraction_ID == defender_NPC.fraction_ID or how_char1_loves_char2(defender_NPC, attacker_NPC, fractions) >= 2:
        attacker_bonus = 1

    attacker_side: list[ModifiedNPC] = []
    defender_side: list[ModifiedNPC] = []

    for character in current_characters.list:
        if character.place == attacker.place:
            character_NPC = people.get_char_by_ID(character.ID)
            likes_attacker = how_char1_loves_char2(character_NPC, attacker_NPC)
            likes_defender = how_char1_loves_char2(character_NPC, defender_NPC)
            if likes_attacker >= 3 and likes_defender >= 3:
                likes_defender = likes_attacker = 2

            if character_NPC.fraction_ID == attacker_NPC.fraction_ID or likes_attacker >= 3:
                attacker_side.append(character)

            if character_NPC.fraction_ID == defender_NPC.fraction_ID or likes_defender >= 3:
                defender_side.append(character)

    attacker_bonus += (len(attacker_side) - len(defender_side)) * 2

    total_attack_power = sum([x.str for x in attacker_side]) + attacker_bonus
    total_defend_power = sum([x.str for x in defender_side])

    if total_attack_power > total_defend_power+1:
        if action == "kill":
            for char in defender_side:
                char.state = "dead"
        else:
            for char in defender_side:
                char.state = "stun"

    if total_attack_power > total_defend_power:
        for char in defender_side:
            char.state = "stun"

    if total_attack_power == total_defend_power:
        for char in defender_side + attacker_side:
            char.state = "stun"

    if total_attack_power < total_defend_power:
        if action == "kill":
            for char in attacker_side:
                char.state = "dead"
        else:
            for char in attacker_side:
                char.state = "stun"

    return current_characters


def steal(attacker: ModifiedNPC, defender: ModifiedNPC, action: str, current_characters: ModifiedPeople) -> ModifiedPeople:
    people = read_people_from_file(r"data\characters.csv")
    fractions = read_fractions_from_file(r"data\fractions.csv")
    attacker_NPC = people.get_char_by_ID(attacker.ID)
    defender_NPC = people.get_char_by_ID(defender.ID)

    attacker_bonus = 0

    if how_char1_loves_char2(defender_NPC, attacker_NPC, fractions) >= 3:
        attacker_bonus += 1

    attacker_speed = attacker.speed + attacker_bonus
    defender_speed = 0 if defender.state != "alive" else defender.speed

    if attacker_speed > defender_speed:
        stolen_items = defender.items
        defender.items = []
        attacker.items += stolen_items

    elif attacker_speed == defender_speed:
        current_characters = fight(
            attacker, defender, "stun", current_characters)

    else:
        defender.str += 1
        current_characters = fight(
            attacker, defender, "stun", current_characters)

    return current_characters
