from tkinter import CURRENT
from map import read_map_from_file, Map, Street
from character_handler import ModifiedPeople, ModifiedNPC
from character import Society
from items import Item, ItemsCollection
from quest import ModifiedQuestPhase, str_to_mqp, dict_to_mqp


class Player:
    """Class to store current data about Player"""

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
        self.place_ID = int(place_ID)
        self.coins = int(coins)
        self.items = [int(x) for x in items if x != ""]
        self.strength = int(strength)
        self.speed = int(speed)
        self.relations = [int(x) for x in relations]
        self.fraction_ID = int(fraction_ID)
        self.state = state

        self.duration: list[dict[str]] = duration

        self.equiped_weapons = [int(x) for x in weapons if x != ""]

        self.quests = quests
        self.progress = progress

        self.round = round_input

    def move(self, map=read_map_from_file("data\streets.csv")):
        """Method that is NOT used. Created only for development and console control"""
        connected_streets = map.get_street_by_ID(self.place_ID).get_connected_streets()

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

        self.place_ID = options[idx].ID

    def move_possibilities(
        self, map=read_map_from_file("data\streets.csv")
    ) -> tuple[list[Street], Street]:
        """Method returns list of Streets objects where Player can move based on his current location
        and also returns Street object of place where is currently character"""
        current_street = map.get_street_by_ID(self.place_ID)
        connected_streets = current_street.get_connected_streets()
        options = []
        for possible_street in connected_streets:
            options.append(map.get_street_by_ID(possible_street))
        return options, current_street

    def get_actions(
        self,
        current_characters: ModifiedPeople,
        map=read_map_from_file("data\streets.csv")) -> tuple[list[dict[str, dict[str, str|int]]], list[ModifiedNPC]]:
        """
        Method takes current state of NPCs and returns 2 values:
        1. list of dicts of possible actions 
        2. list of all characters that are in the same location as player
        """
        people_here = current_characters.get_people_in_place(self.place_ID)
        action_dict = map.get_street_by_ID(self.place_ID).possibilites
 
        return action_dict, people_here

    def get_fraction_relation(self, fraction_ID):
        return self.relations[fraction_ID]
        

    def get_relationships(
        self, people_here: list[ModifiedNPC], society: Society
    ) -> dict[int, int]:
        """Method takes list of people in same location as player and static data about all characters.
        Returns dictionary where keys are IDs of people in the same location and values are their relationship to player
        """
        char_ID_to_relation: dict[int, int] = dict()
        for person in people_here:
            char_ID_to_relation[person.ID] = self.relations[
                society.get_char_by_ID(person.ID).fraction_ID
            ]
        return char_ID_to_relation

    def use_item(self, item: Item) -> None:
        """Takes statistics of consumable item and adds them to player's base stats.
        It also saves duration of these effects and removes item from inventory"""

        self.duration.append({"type": "str", "power": item.strength_mod, "duration": item.duration, "source": item.name_cz})
        self.duration.append({"type": "speed", "power": item.speed_mod, "duration": item.duration, "source": item.name_cz})

        self.strength += item.strength_mod
        self.speed += item.speed_mod
        self.items.remove(item.ID)

    def stun_player(self, duration: int) -> None:
        """Check if player is not already stunned and then stun him more"""
        #TODO add character name
        for idx, effect in enumerate(self.duration):
            if effect["type"] == "stun":
                self.duration[idx]["duration"] += duration
                return

        self.duration.append({"type": "stun", "duration": duration, "source": "some character"})

    def get_stun_duration(self) -> int:
        for effect in self.duration:
            if effect["type"] == "stun":
                return effect["duration"]
        return 0

    def decrease_durations(self) -> None:
        """Method goes through all temporary effects and reduced their duration by 1
        If the effect has duration 0 it removes him from effects list (duration) and removes effects from player
        """
        to_pop = []
       
        for effect_idx, effect in enumerate(self.duration):
            self.duration[effect_idx]["duration"] -= 1
            if self.duration[effect_idx]["duration"] == 0:
                if effect["type"] == "stun":
                    self.state = "alive"
                elif effect["type"] == "str":
                    self.strength -= int(effect["power"])
                elif effect["type"] == "speed":
                    self.speed -= int(effect["power"])
                to_pop.append(effect)
        for effect_to_pop in to_pop:
            self.duration.remove(effect_to_pop)

    def equip_weapon(self, item: Item) -> bool:
        """Method tries to add item ID to weapon list. If it is possible it returns true and removes newly equiped item from items.
        If player has already 2 weapons equiped it returns False"""
        if len(self.equiped_weapons) < 2:
            self.equiped_weapons.append(item.ID)
            self.items.remove(item.ID)
            self.update_attributes_on_equip(item)
            return True
        return False

    def get_equiped_weapons(self, items: ItemsCollection) -> list[Item]:
        """Returns list of currently equiped weapons as Item objects"""
        return [items.get_item(item_ID) for item_ID in self.equiped_weapons]

    def swap_weapon(self, remove_item: Item, new_item: Item) -> None:
        """Method takes two Item objects. One to unequip and one to equip and swaps them between inventory and equiped items"""
        self.equiped_weapons.remove(remove_item.ID)
        self.items.remove(new_item.ID)

        self.equiped_weapons.append(new_item.ID)
        self.items.append(remove_item.ID)

        self.update_attributes_on_equip(new_item)
        self.update_attributes_on_remove(remove_item)

    def update_attributes_on_equip(self, item: Item) -> None:
        """Updates players stats based on equiped item"""
        self.speed += item.speed_mod
        self.strength += item.strength_mod

    def update_attributes_on_remove(self, item: Item) -> None:
        """Updates players stats based on removed item"""
        self.speed -= item.speed_mod
        self.strength -= item.strength_mod

    def remove_item(self, item_ID: int):
        self.items.remove(item_ID)

    def start_quest(self, quest_index: int, quest: ModifiedQuestPhase, current_characters: ModifiedPeople) -> None:
        """Takes care of marking quest as in progress and assigning needed items"""
        self.progress[quest_index] = "inprogress"
        if quest.item_ID != -1:
            #You have to steal it, thats the point of this type of quest.
            if quest.action != "rob":
                self.items.append(quest.item_ID)
            #TODO Resolve if this is bug or function: When you get a quest to steal something from character but he does not have the item
            else:
                current_characters.give_character_item(quest.go_to, quest.item_ID)

        
    def update_quest_progresses(
        self, current_characters: ModifiedPeople
    ) -> list[ModifiedQuestPhase]:
        """Method looks through player's quests and compares them to his location. If player finished any subpart (moving to designated location) it updates progress he made.
        Method returns list of ModifieQuestPhase object of quests where player is in final location
        """
        quests_to_finish: list[ModifiedQuestPhase] = []
        for quest_idx in range(len(self.quests)):
            quest = dict_to_mqp(self.quests[quest_idx])

            # player gets to starting location or it is not defined
            if (self.progress[quest_idx] == "tostart"):
                if self.place_ID == quest.from_place_ID:
                    self.start_quest(quest_idx, quest, current_characters)
                elif quest.from_place_ID == -1:
                    self.start_quest(quest_idx, quest, current_characters)

            # player gets to final location of the quest
            if (self.progress[quest_idx] == "inprogress"):
                if quest.go_to != -1:
                    if self.place_ID == current_characters.get_NPC(quest.go_to).place_ID:
                            self.progress[quest_idx] = "infinal"
                else:
                    if self.place_ID == quest.to_place_ID:
                        self.progress[quest_idx] = "infinal"        

            # if player decides to leave final location without completing the quest
            if (self.progress[quest_idx] == "infinal"):
                if quest.go_to != -1:
                    if self.place_ID != current_characters.get_NPC(quest.go_to).place_ID:
                        self.progress[quest_idx] = "inprogress"
                else:
                    if self.place_ID != quest.to_place_ID:
                        self.progress[quest_idx] = "inprogress"
            
            # check if needed action was completed and append special interactions
            if self.progress[quest_idx] == "infinal":
                if self.action_completed(quest, current_characters.get_NPC(quest.go_to)):
                    self.progress[quest_idx] = "ended"
                quests_to_finish.append(quest)

        return quests_to_finish

    def action_completed(self, quest: ModifiedQuestPhase, character: ModifiedNPC) -> bool:
        """Checks if required action that should be performed on another character is already finished"""

        #Attack actions
        if quest.action == character.state:
            return True
        elif quest.action == "stun" and character.state == "dead":
            #TODO soft / hard condition
            return True

        #Sleight of hand actions - fight me on it - if you have to steal a generic item u can as well already have it in your pockets 
        if quest.action == "rob" and quest.item_ID in self.items:
            return True
        elif quest.action == "plant" and quest.item_ID in character.items:
            return True

        return False

    def check_quest_action_complete(
        self, current_characters: ModifiedPeople
    ) -> list[str]:
        """Goes through all quests player has. If player is in final location and condition of completing
        the quest is fulfiled than the progres of quest is set to ended"""
        ended_quests = []
        for quest_idx in range(len(self.quests)):
            quest = dict_to_mqp(self.quests[quest_idx])
            if (
                quest.action == "kill"
                and current_characters.get_NPC(quest.go_to).state == "dead"
                and self.progress[quest_idx] == "infinal"
            ):
                self.progress[quest_idx] = "ended"
            elif (
                quest.action == "stun"
                and current_characters.get_NPC(quest.go_to).state == "stun"
                and self.progress[quest_idx] == "infinal"
            ):
                self.progress[quest_idx] = "ended"
            # The player was supposed to steal certain item. However he if has the item who cares how he got it.
            elif quest.action == "rob" and (
                quest.item_ID in self.items or quest.item_ID in self.equiped_weapons
            ):
                self.progress[quest_idx] = "ended"
            elif (
                quest.action == "plant"
                and quest.item_ID in current_characters.get_NPC(quest.go_to).items
                and self.progress[quest_idx] == "infinal"
            ):
                self.progress[quest_idx] = "ended"
            elif quest.action == "None" and self.progress[quest_idx] == "infinal":
                self.progress[quest_idx] = "ended"

            if self.progress[quest_idx] == "ended":
                ended_quests.append(self.quests[quest_idx])
        return ended_quests
