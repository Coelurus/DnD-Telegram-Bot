from tkinter import CURRENT
from map import read_map_from_file, Map, Street
from character_handler import ModifiedPeople, ModifiedNPC
from character import Society
from items import Item, ItemsCollection
from quest import ModifiedQuestPhase, str_to_mqp, dict_to_mqp


class Player:
    """Class to store current data about Player"""
   
    #region
    place_ID = 0
    coins = 25
    items = [7, 8, 9]
    strength = 2-2
    speed = 2-2
    relations = [3, 0, 1, 2, 2, 3, 3]
    fraction_ID = 4
    state = "alive"
    duration = []
    equiped_weapons = ""
    quests = [
            {
                "ID": 0,
                "char": 12,
                "from": 37,
                "item": 1,
                "to_place": 32,
                "action": "None",
                "go_to": -1,
                "reward": "40%-1",
                "coin_reward": 40,
                "item_reward": -1,
            },
            {
                "ID": 7,
                "char": 29,
                "from": -1,
                "item": -1,
                "to_place": "?",
                "action": "31;stun",
                "go_to": 31,
                "reward": "14%14",
                "coin_reward": 14,
                "item_reward": 14,
            },
            {
                "ID": 45,
                "char": 15,
                "from": -1,
                "item": 3,
                "to_place": "?",
                "action": "32;rob",
                "go_to": 32,
                "reward": "21%13",
                "coin_reward": 21,
                "item_reward": 13,
            },
            {
                "ID": 17,
                "char": 13,
                "from": -1,
                "item": 7,
                "to_place": "?",
                "action": "2;plant",
                "go_to": 2,
                "reward": "33%5",
                "coin_reward": 33,
                "item_reward": 5,
            },
        ],
    progress = ["tostart", "inprogress", "tostart", "tostart"]
    round = 1
    #endregion

    def __init__(
        self,
        place_ID: str,
        coins: str,
        items: list[str],
        strength: str,
        speed: str,
        relations: list[str],
        fraction_ID: str = "4",
        state: str = "alive",
        duration: list[dict[str]] = [],
        weapons: list[str] = [""],
        quests: list[str] = [],
        progress: list[str] = [],
        round_input: int = 1
    ) -> None:
        Player.place_ID = int(place_ID)
        Player.coins = int(coins)
        Player.items = [int(x) for x in items if x != ""]
        Player.strength = int(strength)
        Player.speed = int(speed)
        Player.relations = [int(x) for x in relations]
        Player.fraction_ID = int(fraction_ID)
        Player.state = state

        Player.duration: list[dict[str]] = duration

        Player.equiped_weapons = [int(x) for x in weapons if x != ""]

        Player.quests = quests
        Player.progress = progress

        Player.round = round_input

    @staticmethod
    def move(map=read_map_from_file("data\streets.csv")):
        """Method that is NOT used. Created only for development and console control"""
        connected_streets = map.get_street_by_ID(Player.place_ID).get_connected_streets()

        output_str = ""
        output_str += "You can go to: \n"
        options: list[Street] = []
        for possible_street in connected_streets:
            output_str += map.get_street_by_ID(possible_street).name_cz + "\n"
            options.append(map.get_street_by_ID(possible_street))

        print(output_str)
        choices = [x.name_cz for x in options]
        print("U have choices:", ", ".join(choices))
        choice = input("Write your choice: ")
        idx = choices.index(choice)

        Player.place_ID = options[idx].ID

    @staticmethod
    def move_possibilities(map=read_map_from_file("data\streets.csv")) -> tuple[list[Street], Street]:
        """Method returns list of Streets objects where Player can move based on his current location
        and also returns Street object of place where is currently character"""
        current_street = map.get_street_by_ID(Player.place_ID)
        connected_streets = current_street.get_connected_streets()
        options = []
        for possible_street in connected_streets:
            options.append(map.get_street_by_ID(possible_street))
        return options, current_street

    @staticmethod
    def get_actions(current_characters: ModifiedPeople, map=read_map_from_file("data\streets.csv")) -> tuple[list[dict[str, dict[str, str|int]]], list[ModifiedNPC]]:
        """
        Method takes current state of NPCs and returns 2 values:
        1. list of dicts of possible actions 
        2. list of all characters that are in the same location as player
        """
        people_here = current_characters.get_people_in_place(Player.place_ID)
        action_dict = map.get_street_by_ID(Player.place_ID).possibilites
 
        return action_dict, people_here

    @staticmethod
    def get_fraction_relation(fraction_ID):
        return Player.relations[fraction_ID]
        
    @staticmethod
    def get_relationships(people_here: list[ModifiedNPC], society: Society) -> dict[int, int]:
        """Method takes list of people in same location as player and static data about all characters.
        Returns dictionary where keys are IDs of people in the same location and values are their relationship to player
        """
        char_ID_to_relation: dict[int, int] = dict()
        for person in people_here:
            char_ID_to_relation[person.ID] = Player.relations[
                society.get_char_by_ID(person.ID).fraction_ID
            ]
        return char_ID_to_relation

    @staticmethod
    def use_item(item: Item) -> None:
        """Takes statistics of consumable item and adds them to player's base stats.
        It also saves duration of these effects and removes item from inventory"""

        Player.duration.append({"type": "str", "power": item.strength_mod, "duration": item.duration, "source": item.name_cz})
        Player.duration.append({"type": "speed", "power": item.speed_mod, "duration": item.duration, "source": item.name_cz})

        Player.strength += item.strength_mod
        Player.speed += item.speed_mod
        Player.items.remove(item.ID)

    @staticmethod
    def stun_player(duration: int) -> None:
        """Check if player is not already stunned and then stun him more"""
        #TODO add character name
        for idx, effect in enumerate(Player.duration):
            if effect["type"] == "stun":
                Player.duration[idx]["duration"] += duration
                return

        Player.duration.append({"type": "stun", "duration": duration, "source": "some character"})

    @staticmethod
    def get_stun_duration() -> int:
        for effect in Player.duration:
            if effect["type"] == "stun":
                return effect["duration"]
        return 0

    @staticmethod
    def decrease_durations() -> None:
        """Method goes through all temporary effects and reduced their duration by 1
        If the effect has duration 0 it removes him from effects list (duration) and removes effects from player
        """
        to_pop = []
       
        for effect_idx, effect in enumerate(Player.duration):
            Player.duration[effect_idx]["duration"] -= 1
            if Player.duration[effect_idx]["duration"] == 0:
                if effect["type"] == "stun":
                    Player.state = "alive"
                elif effect["type"] == "str":
                    Player.strength -= int(effect["power"])
                elif effect["type"] == "speed":
                    Player.speed -= int(effect["power"])
                to_pop.append(effect)
        for effect_to_pop in to_pop:
            Player.duration.remove(effect_to_pop)

    @staticmethod
    def equip_weapon(item: Item) -> bool:
        """Method tries to add item ID to weapon list. If it is possible it returns true and removes newly equiped item from items.
        If player has already 2 weapons equiped it returns False"""
        if len(Player.equiped_weapons) < 2:
            Player.equiped_weapons.append(item.ID)
            Player.items.remove(item.ID)
            Player.update_attributes_on_equip(item)
            return True
        return False

    @staticmethod
    def get_equiped_weapons(items: ItemsCollection) -> list[Item]:
        """Returns list of currently equiped weapons as Item objects"""
        return [items.get_item(item_ID) for item_ID in Player.equiped_weapons]

    @staticmethod
    def swap_weapon(remove_item: Item, new_item: Item) -> None:
        """Method takes two Item objects. One to unequip and one to equip and swaps them between inventory and equiped items"""
        Player.equiped_weapons.remove(remove_item.ID)
        Player.items.remove(new_item.ID)

        Player.equiped_weapons.append(new_item.ID)
        Player.items.append(remove_item.ID)

        Player.update_attributes_on_equip(new_item)
        Player.update_attributes_on_remove(remove_item)

    @staticmethod
    def update_attributes_on_equip(item: Item) -> None:
        """Updates players stats based on equiped item"""
        Player.speed += item.speed_mod
        Player.strength += item.strength_mod

    @staticmethod
    def update_attributes_on_remove(item: Item) -> None:
        """Updates players stats based on removed item"""
        Player.speed -= item.speed_mod
        Player.strength -= item.strength_mod

    @staticmethod
    def remove_item(item_ID: int):
        Player.items.remove(item_ID)

    @staticmethod
    def start_quest(quest_index: int, quest: ModifiedQuestPhase, current_characters: ModifiedPeople) -> None:
        """Takes care of marking quest as in progress and assigning needed items"""
        Player.progress[quest_index] = "inprogress"
        if quest.item_ID != -1:
            #You have to steal it, thats the point of this type of quest.
            if quest.action != "rob":
                Player.items.append(quest.item_ID)
            #TODO Resolve if this is bug or function: When you get a quest to steal something from character but he does not have the item
            else:
                current_characters.give_character_item(quest.go_to, quest.item_ID)

    @staticmethod
    def update_quest_progresses(current_characters: ModifiedPeople) -> list[ModifiedQuestPhase]:
        """Method looks through player's quests and compares them to his location. If player finished any subpart (moving to designated location) it updates progress he made.
        Method returns list of ModifieQuestPhase object of quests where player is in final location
        """
        quests_to_finish: list[ModifiedQuestPhase] = []
        for quest_idx in range(len(Player.quests)):
            quest = dict_to_mqp(Player.quests[quest_idx])

            # player gets to starting location or it is not defined
            if (Player.progress[quest_idx] == "tostart"):
                if Player.place_ID == quest.from_place_ID:
                    Player.start_quest(quest_idx, quest, current_characters)
                elif quest.from_place_ID == -1:
                    Player.start_quest(quest_idx, quest, current_characters)

            # player gets to final location of the quest
            if (Player.progress[quest_idx] == "inprogress"):
                if quest.go_to != -1:
                    if Player.place_ID == current_characters.get_NPC(quest.go_to).place_ID:
                            Player.progress[quest_idx] = "infinal"
                else:
                    if Player.place_ID == quest.to_place_ID:
                        Player.progress[quest_idx] = "infinal"        

            # if player decides to leave final location without completing the quest
            if (Player.progress[quest_idx] == "infinal"):
                if quest.go_to != -1:
                    if Player.place_ID != current_characters.get_NPC(quest.go_to).place_ID:
                        Player.progress[quest_idx] = "inprogress"
                else:
                    if Player.place_ID != quest.to_place_ID:
                        Player.progress[quest_idx] = "inprogress"
            
            # check if needed action was completed and append special interactions
            if Player.progress[quest_idx] == "infinal":
                if Player.action_completed(quest, current_characters.get_NPC(quest.go_to)):
                    Player.progress[quest_idx] = "ended"
                quests_to_finish.append(quest)

        return quests_to_finish

    @staticmethod
    def action_completed(quest: ModifiedQuestPhase, character: ModifiedNPC) -> bool:
        """Checks if required action that should be performed on another character is already finished"""

        #Attack actions
        if quest.action == character.state:
            return True
        elif quest.action == "stun" and character.state == "dead":
            #TODO soft / hard condition
            return True

        #Sleight of hand actions - fight me on it - if you have to steal a generic item u can as well already have it in your pockets 
        if quest.action == "rob" and quest.item_ID in Player.items:
            return True
        elif quest.action == "plant" and quest.item_ID in character.items:
            return True

        return False

    @staticmethod
    def check_quest_action_complete(current_characters: ModifiedPeople) -> list[str]:
        """Goes through all quests player has. If player is in final location and condition of completing
        the quest is fulfiled than the progres of quest is set to ended"""
        ended_quests = []
        for quest_idx in range(len(Player.quests)):
            quest = dict_to_mqp(Player.quests[quest_idx])
            if (
                quest.action == "kill"
                and current_characters.get_NPC(quest.go_to).state == "dead"
                and Player.progress[quest_idx] == "infinal"
            ):
                Player.progress[quest_idx] = "ended"
            elif (
                quest.action == "stun"
                and current_characters.get_NPC(quest.go_to).state == "stun"
                and Player.progress[quest_idx] == "infinal"
            ):
                Player.progress[quest_idx] = "ended"
            # The player was supposed to steal certain item. However he if has the item who cares how he got it.
            elif quest.action == "rob" and (
                quest.item_ID in Player.items or quest.item_ID in Player.equiped_weapons
            ):
                Player.progress[quest_idx] = "ended"
            elif (
                quest.action == "plant"
                and quest.item_ID in current_characters.get_NPC(quest.go_to).items
                and Player.progress[quest_idx] == "infinal"
            ):
                Player.progress[quest_idx] = "ended"
            elif quest.action == "None" and Player.progress[quest_idx] == "infinal":
                Player.progress[quest_idx] = "ended"

            if Player.progress[quest_idx] == "ended":
                ended_quests.append(Player.quests[quest_idx])
        return ended_quests

    @staticmethod
    def get_name_cz(_):
        return "*TY*"