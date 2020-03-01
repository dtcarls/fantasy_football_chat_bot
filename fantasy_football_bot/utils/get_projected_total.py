def get_projected_total(lineup):
    total_projected = 0
    for i in lineup:
        if i.slot_position != 'BE':
            if i.points != 0:
                total_projected += i.points
            else:
                total_projected += i.projected_points
    return total_projected