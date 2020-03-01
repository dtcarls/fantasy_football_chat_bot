def all_played(lineup):
    for i in lineup:
        if i.slot_position != 'BE' and i.game_played < 100:
            return False
    return True