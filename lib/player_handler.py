from lib.player import Player


def move_player(old_player: Player) -> Player:
    old_player.place_ID += 1
    new_player = old_player
    return new_player
